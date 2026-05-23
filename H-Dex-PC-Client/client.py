import asyncio
import json
import os
import platform
import socket
import time
import uuid
from typing import Any, Dict

try:
    import psutil
    import requests
    import websockets
except ImportError:
    print("Error: Missing dependencies. Please run: pip install psutil requests websockets")
    exit(1)

# --- CONFIGURATION ---
# Replace with your Hugging Face Space URL
BASE_URL = "https://talhasss-adex-backend.hf.space"
WS_URL = "wss://talhasss-adex-backend.hf.space/ws"
# A unique ID for your PC
DEVICE_ID = f"PC-{socket.gethostname()}-{uuid.getnode()}"

class HDexPCClient:
    def __init__(self):
        self.device_token = None
        self.ws = None
        self.running = True

    async def start(self):
        print(f"[*] Starting H-Dex Transparent Monitor...")
        print(f"[*] Device ID: {DEVICE_ID}")
        
        # 1. Handshake with backend to get token
        if not self.handshake():
            print("[!] Handshake failed. Retrying in 10s...")
            await asyncio.sleep(10)
            return

        # 2. Connect to WebSocket for real-time commands
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
            "androidVersion": platform.version(), # Using field for OS info
            "appVersion": "1.0.0-PC"
        }
        try:
            response = requests.post(f"{BASE_URL}/api/v1/pairing/code", json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.device_token = data.get("deviceToken")
                print(f"[+] Handshake successful. Token acquired.")
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
            
            # Identify
            hello = {
                "type": "device.hello",
                "deviceId": DEVICE_ID,
                "deviceToken": self.device_token,
                "name": socket.gethostname(),
                "model": platform.processor(),
                "androidVersion": platform.system()
            }
            await ws.send(json.dumps(hello))

            # Start heartbeat and telemetry tasks
            asyncio.create_task(self.heartbeat_loop())
            asyncio.create_task(self.telemetry_loop())

            # Listen for commands
            async for message in ws:
                data = json.loads(message)
                if data.get("type") == "server.command":
                    await self.handle_command(data)

    async def heartbeat_loop(self):
        while self.ws and not self.ws.closed:
            await self.ws.send(json.dumps({"type": "device.heartbeat"}))
            await asyncio.sleep(30)

    async def telemetry_loop(self):
        print("[*] Starting telemetry stream...")
        while self.ws and not self.ws.closed:
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            
            event = {
                "type": "device.event",
                "action": "device.event.sys_stats",
                "metadata": {
                    "cpu": cpu,
                    "ram": ram,
                    "text": f"CPU: {cpu}% | RAM: {ram}%"
                }
            }
            await self.ws.send(json.dumps(event))
            await asyncio.sleep(5)

    async def handle_command(self, data: Dict[str, Any]):
        cmd_name = data.get("commandName")
        cmd_id = data.get("commandId")
        print(f"[*] Received command: {cmd_name}")

        result_payload = {"status": "success", "data": "Command executed"}

        if cmd_name == "message":
            text = data.get("payload", {}).get("text", "Hello from HQ")
            print(f"\n[!!!] MESSAGE FROM HQ: {text}\n")
            # In a real app, use tkinter or win32api to show a popup
            result_payload["data"] = f"User saw message: {text}"
        
        elif cmd_name == "beep":
            print("\a") # PC Beep
            result_payload["data"] = "Beep sounded"

        elif cmd_name == "info":
            result_payload["data"] = {
                "os": platform.system(),
                "node": platform.node(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total
            }

        # Send result back
        result = {
            "type": "device.result",
            "commandId": cmd_id,
            "status": "success",
            "data": result_payload["data"]
        }
        await self.ws.send(json.dumps(result))

if __name__ == "__main__":
    client = HDexPCClient()
    try:
        asyncio.run(client.start())
    except KeyboardInterrupt:
        print("\n[*] Stopping client...")
