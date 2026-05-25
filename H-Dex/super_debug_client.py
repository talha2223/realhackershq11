import asyncio
import websockets
import json
import os
import sys
import platform
import socket
import subprocess
import time
import ssl
import hashlib
import random

# --- CONFIGURATION ---
SERVER_URI = "wss://realmrhacker-h-dex.hf.space/ws"
CLIENT_TAG = "SUPER-DEBUG"
# ---------------------

class DebugClient:
    def __init__(self):
        self.running = True
        self.websocket = None
        print(f"[!] DEBUG CLIENT STARTING...")
        print(f"[*] Target Server: {SERVER_URI}")
        print(f"[*] Platform: {platform.system()} {platform.release()}")

    def get_hwid(self):
        try:
            guid = platform.node() + platform.processor() + platform.machine()
            return hashlib.sha256(guid.encode()).hexdigest()[:12].upper()
        except:
            return "DEBUG-TEMP-ID"

    async def connect(self):
        while self.running:
            try:
                print(f"[*] Attempting connection to {SERVER_URI}...")
                ssl_context = ssl._create_unverified_context()
                
                async with websockets.connect(SERVER_URI, ssl=ssl_context) as ws:
                    self.websocket = ws
                    print("[+] CONNECTED to server successfully!")
                    
                    info = {
                        "id": self.get_hwid(),
                        "name": f"DEBUG-{platform.node()}",
                        "tag": CLIENT_TAG,
                        "os": platform.system(),
                        "debug_mode": True
                    }
                    
                    print(f"[*] Sending registration: {info['id']}")
                    await ws.send(json.dumps({"type": "register_device", "info": info}))
                    print("[+] Registration sent!")
                    
                    async for message in ws:
                        print(f"[<] Received message: {message[:100]}...")
                        data = json.loads(message)
                        if data.get("type") == "ping":
                            await ws.send(json.dumps({"type": "pong"}))
                            
            except Exception as e:
                print(f"[!] ERROR: {e}")
                print("[*] Retrying in 5 seconds...")
                await asyncio.sleep(5)

if __name__ == "__main__":
    client = DebugClient()
    try:
        asyncio.run(client.connect())
    except KeyboardInterrupt:
        print("[!] Client stopped by user.")
