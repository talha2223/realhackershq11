import asyncio
import websockets
import json
import ssl

async def test_dashboard():
    uri = "wss://realmrhacker-h-dex.hf.space/ws"
    token = "hdex_admin_2026"
    print(f"[*] Testing Dashboard connection to: {uri}")
    
    try:
        ssl_context = ssl._create_unverified_context()
        async with websockets.connect(uri, ssl=ssl_context) as ws:
            print("[+] Connected! Sending auth...")
            await ws.send(json.dumps({"type": "register_dashboard", "token": token}))
            
            # Wait for response
            response = await ws.recv()
            print(f"[<] Received: {response}")
            data = json.loads(response)
            
            if data.get("type") == "auth_success":
                print("[!!!] AUTH SUCCESSFUL!")
            else:
                print(f"[?] Auth response: {data}")
                
            # Wait for device list
            response = await ws.recv()
            print(f"[<] Device list: {response}")
            
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_dashboard())
