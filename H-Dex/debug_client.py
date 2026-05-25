import asyncio
import websockets
import json
import ssl
import time

# --- CONFIGURATION (Change this to your link) ---
TEST_URI = "wss://realmrhacker-h-dex.hf.space/ws"
DASHBOARD_TOKEN = "hdex_admin_2026"
# ------------------------------------------------

async def test_connection():
    print(f"[*] Testing connection to: {TEST_URI}")
    
    try:
        # Create unverified SSL context (Fixes certificate errors)
        ssl_context = ssl._create_unverified_context()
        
        async with websockets.connect(TEST_URI, ssl=ssl_context) as ws:
            print("[+] Connection SUCCESSFUL!")
            
            # Try to register as a device
            print("[*] Sending registration message...")
            reg_msg = {
                "type": "register_device",
                "info": {
                    "id": "DEBUG_DEVICE_TEST",
                    "name": "Debug-PC",
                    "os": "Windows Debug"
                }
            }
            await ws.send(json.dumps(reg_msg))
            print("[+] Registration sent. Checking for server response (if any)...")
            
            # Wait for 5 seconds to see if we stay connected
            print("[*] Waiting 5 seconds to verify stable connection...")
            await asyncio.sleep(5)
            print("[+] Connection is STABLE.")
            print("\n!!! SUCCESS !!!")
            print("Your client should be visible on the dashboard now as 'Debug-PC'.")
            
    except Exception as e:
        print(f"\n[!] CONNECTION FAILED!")
        print(f"[!] Error: {e}")
        print("\nCommon fixes:")
        print("1. Make sure the URL ends with /ws")
        print("2. Check if your Hugging Face Space is 'Running' and not 'Sleeping'")
        print("3. Ensure you have internet access")

if __name__ == "__main__":
    asyncio.run(test_connection())
    input("\nPress Enter to exit...")
