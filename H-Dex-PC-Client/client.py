import asyncio
import json
import os
import platform
import socket
import subprocess
import time
import uuid
import ctypes
import base64
from io import BytesIO
from typing import Any, Dict

try:
    import psutil
    import requests
    import websockets
    import mss
    import pyperclip
    from PIL import Image
except ImportError:
    print("Error: Missing dependencies. Please run: pip install -r requirements.txt")
    exit(1)

# --- CONFIGURATION ---
BASE_URL = "https://talhasss-adex-backend.hf.space"
WS_URL = "wss://talhasss-adex-backend.hf.space/ws"
DEVICE_ID = f"PC-{socket.gethostname()}-{uuid.getnode()}"
TOKEN_FILE = ".device_token"

class HDexPCClient:
    def __init__(self):
        self.device_token = self.load_token()
        self.ws = None
        self.running = True

    def load_token(self):
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as f:
                return f.read().strip()
        return None

    def save_token(self, token):
        with open(TOKEN_FILE, "w") as f:
            f.write(token)

    async def start(self):
        print(f"[*] Starting H-Dex Transparent Monitor (Elite)...")
        print(f"[*] Device ID: {DEVICE_ID}")
        
        if not self.device_token:
            if not self.handshake():
                print("[!] Handshake failed. Retrying in 10s...")
                await asyncio.sleep(10)
                return

        while self.running:
            try:
                await self.connect_ws()
            except Exception as e:
                print(f"[!] WebSocket error: {e}. Reconnecting in 5s...")
                await asyncio.sleep(5)

    def handshake(self) -> bool:
        print(f"[*] Registering with backend: {BASE_URL}")
        payload = {
            "deviceId": DEVICE_ID,
            "name": socket.gethostname(),
            "model": f"{platform.system()} {platform.release()}",
            "androidVersion": platform.version(),
            "appVersion": "1.0.0-PC-ELITE"
        }
        try:
            response = requests.post(f"{BASE_URL}/api/v1/pairing/code", json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.device_token = data.get("deviceToken")
                self.save_token(self.device_token)
                print(f"[+] Handshake successful. Token cached.")
                return True
            else:
                print(f"[!] Handshake HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"[!] Connection error during handshake: {e}")
            return False

    async def connect_ws(self):
        async with websockets.connect(WS_URL) as ws:
            self.ws = ws
            print(f"[+] Connected to command channel: {WS_URL}")
            
            hello = {
                "type": "device.hello",
                "deviceId": DEVICE_ID,
                "deviceToken": self.device_token,
                "name": socket.gethostname(),
                "model": platform.processor(),
                "androidVersion": platform.system(),
                "appVersion": "1.0.0-PC-ELITE"
            }
            await ws.send(json.dumps(hello))

            asyncio.create_task(self.heartbeat_loop())
            asyncio.create_task(self.telemetry_loop())

            async for message in ws:
                data = json.loads(message)
                if data.get("type") == "server.command":
                    asyncio.create_task(self.handle_command(data))

    async def heartbeat_loop(self):
        while self.ws and not self.ws.closed:
            try:
                await self.ws.send(json.dumps({"type": "device.heartbeat"}))
            except: break
            await asyncio.sleep(30)

    async def telemetry_loop(self):
        while self.ws and not self.ws.closed:
            try:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                event = {
                    "type": "device.event",
                    "action": "device.event.sys_stats",
                    "metadata": {"cpu": cpu, "ram": ram, "text": f"CPU: {cpu}% | RAM: {ram}%"}
                }
                await self.ws.send(json.dumps(event))
            except: break
            await asyncio.sleep(5)

    async def handle_command(self, data: Dict[str, Any]):
        cmd_name = data.get("commandName")
        cmd_id = data.get("commandId")
        payload = data.get("payload", {})
        print(f"[*] Executing: {cmd_name}")

        result = {"type": "device.result", "commandId": cmd_id, "status": "success", "data": ""}

        try:
            if cmd_name == "shell":
                query = payload.get("command", "dir")
                proc = subprocess.Popen(query, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                stdout, stderr = proc.communicate()
                result["data"] = (stdout + stderr).decode('utf-8', errors='replace')

            elif cmd_name == "screenshot":
                with mss.mss() as sct:
                    filename = sct.shot(mon=-1, output="sct.png")
                    with open(filename, "rb") as f:
                        img_data = f.read()
                    # For H-Dex, we send as base64 in data or upload if backend supports
                    result["data"] = "data:image/png;base64," + base64.b64encode(img_data).decode()
                    os.remove(filename)

            elif cmd_name == "getclipboard":
                result["data"] = pyperclip.paste()

            elif cmd_name == "lock":
                if platform.system() == "Windows":
                    ctypes.windll.user32.LockWorkStation()
                    result["data"] = "Workstation locked"
                else:
                    result["status"] = "error"
                    result["data"] = "Lock only supported on Windows"

            elif cmd_name == "openlink":
                url = payload.get("url", "https://google.com")
                if platform.system() == "Windows":
                    os.startfile(url)
                else:
                    subprocess.Popen(['xdg-open', url])
                result["data"] = f"Opened: {url}"

            elif cmd_name == "message":
                text = payload.get("text", "System Alert")
                if platform.system() == "Windows":
                    ctypes.windll.user32.MessageBoxW(0, text, "HQ_ALERT", 0x40 | 0x1)
                print(f"[HQ_MSG] {text}")
                result["data"] = "Message displayed"

            elif cmd_name == "files":
                path = payload.get("path", ".")
                files = []
                for item in os.listdir(path):
                    full = os.path.join(path, item)
                    files.append({
                        "name": item,
                        "path": os.path.abspath(full),
                        "isDirectory": os.path.isdir(full)
                    })
                result["data"] = {"path": os.path.abspath(path), "files": files}

            elif cmd_name == "shutdown":
                result["data"] = "Shutdown initiated"
                await self.ws.send(json.dumps(result))
                if platform.system() == "Windows":
                    os.system("shutdown /s /t 1")
                else:
                    os.system("shutdown now")
                return

        except Exception as e:
            result["status"] = "error"
            result["data"] = str(e)

        await self.ws.send(json.dumps(result))

if __name__ == "__main__":
    client = HDexPCClient()
    try:
        asyncio.run(client.start())
    except KeyboardInterrupt:
        print("\n[*] Stopping client...")
