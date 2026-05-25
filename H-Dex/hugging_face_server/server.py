import asyncio
import websockets
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Store connected clients
connected_devices = {}
dashboard_ws = None

async def register_device(websocket, data):
    device_info = data.get("info", {})
    connected_devices[websocket] = device_info
    logging.info(f"Device registered: {device_info.get('name')} ({websocket.remote_address})")
    await broadcast_device_list()

async def unregister_device(websocket):
    if websocket in connected_devices:
        del connected_devices[websocket]
        logging.info(f"Device disconnected: {websocket.remote_address}")
        await broadcast_device_list()

async def broadcast_device_list():
    if dashboard_ws:
        devices_list = []
        for ws, info in connected_devices.items():
            devices_list.append({
                "id": str(ws.remote_address),
                "name": info.get("name", "Unknown"),
                "country": info.get("country", "Unknown"),
                "ip": info.get("ip", "Unknown"),
                "weather": info.get("weather", "Unknown"),
                "status": "Online"
            })
        try:
            await dashboard_ws.send(json.dumps({"type": "device_list", "devices": devices_list}))
        except:
            pass

async def handle_dashboard_message(message):
    data = json.loads(message)
    target_id = data.get("target_id")
    target_ws = None
    for ws in connected_devices:
        if str(ws.remote_address) == target_id:
            target_ws = ws
            break
    if target_ws:
        await target_ws.send(json.dumps(data))

async def handler(websocket):
    global dashboard_ws
    logging.info(f"New connection from {websocket.remote_address}")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get("type")
                if msg_type == "register_dashboard":
                    dashboard_ws = websocket
                    logging.info("Dashboard registered.")
                    await broadcast_device_list()
                elif msg_type == "register_device":
                    await register_device(websocket, data)
                elif msg_type == "ping":
                    await websocket.send(json.dumps({"type": "pong"}))
                else:
                    # Allow all other messages to pass through if target_id is present or if it's a direct message
                    # But we strictly route based on logic.
                    # Let's just pass everything that isn't a system message.
                    if websocket == dashboard_ws:
                        await handle_dashboard_message(message)
                    elif websocket in connected_devices:
                        data["sender_id"] = str(websocket.remote_address)
                        if dashboard_ws:
                            await dashboard_ws.send(json.dumps(data))
            except:
                pass
    except:
        pass
    finally:
        if websocket == dashboard_ws:
            dashboard_ws = None
        else:
            await unregister_device(websocket)

async def main():
    # Hugging Face sets PORT to 7860
    port = int(os.environ.get("PORT", 7860))
    logging.info(f"Starting Server on port {port}...")
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
