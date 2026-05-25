"""
H-DEX Server v3.0 ULTRA - Enhanced & Optimized
- Heartbeat mechanism (30s ping, 90s timeout)
- Log rotation (5 files x 5MB)
- HTTP /health endpoint
- Connection health tracking
- Graceful shutdown
- Audit logging
"""

import asyncio
import websockets
import json
import logging
import os
import time
import sys
import signal
from datetime import datetime
from collections import deque
from logging.handlers import RotatingFileHandler
from http import HTTPStatus
from functools import partial

# Configure logging with rotation
LOG_FORMAT = '%(asctime)s | %(levelname)-8s | %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Create logs directory
if not os.path.exists('logs'):
    os.makedirs('logs')

# Rotating file handler (5 files x 5MB each)
file_handler = RotatingFileHandler(
    'logs/server.log',
    maxBytes=5*1024*1024,  # 5MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

# Console handler with colors (Windows compatible)
class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(ColoredFormatter(LOG_FORMAT, DATE_FORMAT))

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger('H-DEX Server')

# Configuration
DASHBOARD_TOKEN = os.environ.get('DASHBOARD_TOKEN', 'hdex_admin_2026')
MAX_LOG_ENTRIES = 1000
HEARTBEAT_INTERVAL = 30  # seconds
HEARTBEAT_TIMEOUT = 90   # seconds


# Database Setup
import sqlite3

class Database:
    def __init__(self, db_path="hdex_data.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Devices table
        cur.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id TEXT PRIMARY KEY,
            name TEXT,
            ip TEXT,
            os TEXT,
            first_seen DATETIME,
            last_seen DATETIME,
            status TEXT,
            tags TEXT
        )
        ''')
        
        # Audit Log table
        cur.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            action TEXT,
            details TEXT,
            source_ip TEXT
        )
        ''')
        
        conn.commit()
        conn.close()

    def update_device(self, dev_info):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        now = datetime.now().isoformat()
        
        cur.execute('''
        INSERT INTO devices (id, name, ip, os, first_seen, last_seen, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            ip=excluded.ip,
            last_seen=excluded.last_seen,
            status=excluded.status
        ''', (
            dev_info.get('id'),
            dev_info.get('name'),
            dev_info.get('ip'),
            dev_info.get('os'),
            now,
            now,
            'online'
        ))
        conn.commit()
        conn.close()

    def log_action(self, action, details, source_ip=""):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute('INSERT INTO audit_log (timestamp, action, details, source_ip) VALUES (?, ?, ?, ?)',
                    (datetime.now().isoformat(), action, details, source_ip))
        conn.commit()
        conn.close()

    def get_all_devices(self):
        conn = sqlite3.connect(self.db_path)
        # Using row_factory to get dict-like access
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('SELECT * FROM devices')
        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]

db = Database()

class HDexServer:
    def __init__(self):
        self.clients = {}           # {device_id: {"websocket": ws, "info": {...}}}
        self.dashboards = set()     # {websocket}
        self.port = int(os.environ.get('PORT', 8765))
        self.start_time = time.time()
        self.message_count = 0
        self.power_save_mode = True
        self.activity_log = deque(maxlen=MAX_LOG_ENTRIES)
        self.running = True
        self.heartbeat_task = None
        self.db = db  # Attach database instance

        
        # Connection health tracking
        self.connection_health = {}  # {device_id: {"last_pong": time, "health": 0-100}}
        
        # Stats
        self.stats = {
            'total_connections': 0,
            'total_messages': 0,
            'peak_clients': 0,
            'peak_dashboards': 0,
            'heartbeat_sent': 0,
            'heartbeat_failed': 0
        }

    def log_activity(self, action: str, details: str = ""):
        """Log activity with timestamp"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details
        }
        self.activity_log.append(entry)
        return entry

    def get_memory_usage(self):
        """Get approximate memory usage"""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return f"{process.memory_info().rss / 1024 / 1024:.1f} MB"
        except:
            return "N/A"

    def get_uptime_str(self):
        """Get formatted uptime string"""
        seconds = int(time.time() - self.start_time)
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        else:
            return f"{minutes}m {seconds}s"

    async def register_device(self, websocket, data):
        """Register a new device connection"""
        info = data.get("info", {})
        
        # Generate STABLE unique ID based on MAC or Name+IP
        # We remove timestamp to allow re-connection with same ID
        if "id" not in info:
            if info.get("mac"):
                # Use MAC address for best stability
                clean_mac = info.get("mac").replace(":", "").replace("-", "")
                info["id"] = f"{info.get('name', 'Dev')}_{clean_mac}"
            else:
                # Fallback to Name + IP
                clean_ip = info.get("ip", "0.0.0.0").replace(".", "-")
                info["id"] = f"{info.get('name', 'Device')}_{clean_ip}"
        
        device_id = info["id"]
        
        # If device already exists, close old connection? 
        # Or just overwrite. Overwriting is standard.
        if device_id in self.clients:
            logger.info(f"♻️  Device re-connected: {device_id}")
            try:
                # Optional: Close old socket if it's different and open
                old_ws = self.clients[device_id].get("websocket")
                if old_ws and old_ws != websocket and not old_ws.closed:
                    await old_ws.close()
            except: pass

        self.clients[device_id] = {
            "websocket": websocket,
            "info": info,
            "connected_at": time.time()
        }
        
        # Update stats
        self.stats['total_connections'] += 1
        self.stats['peak_clients'] = max(self.stats['peak_clients'], len(self.clients))
        
        # Exit power save mode
        if self.power_save_mode:
            self.power_save_mode = False
            logger.info("⚡ Exiting power-save mode")
        
        logger.info(f"🖥️  Device Connected: {device_id}")
        logger.info(f"   └─ Name: {info.get('name', 'Unknown')} | IP: {info.get('ip', 'Unknown')}")
        
        self.log_activity('DEVICE_CONNECTED', f"{info.get('name')} ({info.get('ip')})")
        
        # Update DB
        try:
            self.db.update_device(info)
            self.db.log_action('DEVICE_CONNECT', f"Device connected: {device_id}", info.get('ip'))
        except Exception as e:
            logger.error(f"DB Error: {e}")

        # Save device info to text file
        self.save_device_to_file(info)

        await self.broadcast_device_list()

    def save_device_to_file(self, info):
        """Save device information to a text file in 'device_logs' folder"""
        try:
            # Create device_logs folder if it doesn't exist
            logs_dir = os.path.join(os.path.dirname(__file__), 'device_logs')
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
                logger.info(f"📁 Created device_logs folder at {logs_dir}")
            
            # Create filename from device name and IP (sanitized)
            device_name = info.get('name', 'Unknown').replace(' ', '_').replace('/', '_').replace('\\', '_')
            device_ip = info.get('ip', '0.0.0.0').replace('.', '-')
            filename = f"{device_name}_{device_ip}.txt"
            filepath = os.path.join(logs_dir, filename)
            
            # Prepare device info text
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            content = f"""================================================================================
                          H-DEX DEVICE CONNECTION LOG
================================================================================

📱 DEVICE INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Device ID:      {info.get('id', 'N/A')}
Device Name:    {info.get('name', 'Unknown')}
IP Address:     {info.get('ip', 'Unknown')}
Operating Sys:  {info.get('os', 'Unknown')}
Username:       {info.get('username', 'Unknown')}
Hostname:       {info.get('hostname', 'Unknown')}
Architecture:   {info.get('arch', 'Unknown')}
Processor:      {info.get('processor', 'Unknown')}

🌐 NETWORK INFO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Public IP:      {info.get('public_ip', info.get('ip', 'Unknown'))}
Local IP:       {info.get('local_ip', 'Unknown')}
MAC Address:    {info.get('mac', 'Unknown')}
ISP:            {info.get('isp', 'Unknown')}
Country:        {info.get('country', 'Unknown')}
City:           {info.get('city', 'Unknown')}
Region:         {info.get('region', 'Unknown')}
Timezone:       {info.get('timezone', 'Unknown')}

💻 SYSTEM SPECS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RAM Total:      {info.get('ram_total', 'Unknown')}
RAM Available:  {info.get('ram_available', 'Unknown')}
CPU Cores:      {info.get('cpu_cores', 'Unknown')}
Disk Space:     {info.get('disk_total', 'Unknown')}
GPU:            {info.get('gpu', 'Unknown')}

📝 CONNECTION HISTORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
            
            # Check if file exists to append connection history
            if os.path.exists(filepath):
                # Read existing content and extract connection history
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing = f.read()
                
                # Find connection history section and append
                if "CONNECTION HISTORY" in existing:
                    history_start = existing.find("CONNECTION HISTORY")
                    history_section = existing[history_start:]
                    # Count existing connections
                    connection_count = history_section.count("[CONNECTED]") + 1
                    content += f"[{connection_count}] [{current_time}] [CONNECTED] - Session Started\n"
                else:
                    content += f"[1] [{current_time}] [CONNECTED] - First Connection\n"
            else:
                content += f"[1] [{current_time}] [CONNECTED] - First Connection\n"
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"📄 Device info saved to: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save device info: {e}")


    async def unregister_device(self, websocket):
        """Unregister a device"""
        device_id_to_remove = None
        device_info = None
        
        # Use list() to iterate safely
        for device_id, client_data in list(self.clients.items()):
            if client_data["websocket"] == websocket:
                device_id_to_remove = device_id
                device_info = client_data.get("info", {})
                break
        
        if device_id_to_remove:
            del self.clients[device_id_to_remove]
            logger.info(f"🔌 Device Disconnected: {device_id_to_remove}")
            self.log_activity('DEVICE_DISCONNECTED', f"{device_info.get('name', 'Unknown')}")
            
            # Update DB status
            try:
                conn = sqlite3.connect(self.db.db_path)
                cur = conn.cursor()
                cur.execute('UPDATE devices SET status=?, last_seen=? WHERE id=?', 
                           ('offline', datetime.now().isoformat(), device_id_to_remove))
                conn.commit()
                conn.close()
                self.db.log_action('DEVICE_DISCONNECT', f"Device disconnected: {device_id_to_remove}")
            except Exception as e:
                logger.error(f"DB Error: {e}")
            
            await self.broadcast_device_list()
            
            # Enter power save mode if no clients
            if not self.clients and not self.dashboards:
                self.power_save_mode = True
                logger.info("💤 Entering power-save mode (no active connections)")

    async def register_dashboard(self, websocket, data):
        """Register a dashboard connection"""
        token = data.get("token")
        
        if token != DASHBOARD_TOKEN:
            logger.warning(f"🚫 Unauthorized dashboard attempt from {websocket.remote_address}")
            await websocket.send(json.dumps({
                "type": "auth_failed",
                "message": "Invalid dashboard token"
            }))
            await websocket.close()
            return

        self.dashboards.add(websocket)
        self.stats['peak_dashboards'] = max(self.stats['peak_dashboards'], len(self.dashboards))
        
        # Exit power save mode
        if self.power_save_mode:
            self.power_save_mode = False
            logger.info("⚡ Exiting power-save mode")
        
        logger.info(f"🎛️  Dashboard Connected: {websocket.remote_address}")
        self.log_activity('DASHBOARD_CONNECTED', str(websocket.remote_address))
        
        await websocket.send(json.dumps({"type": "auth_success"}))
        await self.send_device_list(websocket)

    async def unregister_dashboard(self, websocket):
        """Unregister a dashboard"""
        if websocket in self.dashboards:
            self.dashboards.remove(websocket)
            logger.info(f"🔌 Dashboard Disconnected: {websocket.remote_address}")
            self.log_activity('DASHBOARD_DISCONNECTED', str(websocket.remote_address))
            
            # Enter power save mode if no connections
            if not self.clients and not self.dashboards:
                self.power_save_mode = True
                logger.info("💤 Entering power-save mode (no active connections)")

    async def broadcast_device_list(self):
        """Send device list to all dashboards"""
        if not self.dashboards:
            return
        
        device_list = []
        for dev_id, data in self.clients.items():
            info = data["info"]
            device_list.append({
                "id": dev_id,
                "name": info.get("name", "Unknown"),
                "ip": info.get("ip", "Unknown"),
                "tag": info.get("tag", ""),
                "status": "Online",
                "connected_at": data.get("connected_at", 0)
            })
        
        message = json.dumps({"type": "device_list", "devices": device_list})
        await self.send_to_all_dashboards(message)

    async def send_device_list(self, websocket):
        """Send device list to a specific dashboard"""
        device_list = []
        for dev_id, data in self.clients.items():
            info = data["info"]
            device_list.append({
                "id": dev_id,
                "name": info.get("name", "Unknown"),
                "ip": info.get("ip", "Unknown"),
                "tag": info.get("tag", ""),
                "status": "Online"
            })
        
        try:
            await websocket.send(json.dumps({
                "type": "device_list",
                "devices": device_list
            }))
        except:
            pass

    async def send_to_all_dashboards(self, message):
        """Send message to all connected dashboards"""
        disconnected = set()
        
        # Iterate over COPY of set
        for dashboard in list(self.dashboards):
            try:
                await dashboard.send(message)
            except:
                disconnected.add(dashboard)
        
        for d in disconnected:
            await self.unregister_dashboard(d)

    async def get_server_status(self):
        """Get detailed server status"""
        return {
            "type": "server_status",
            "clients_count": len(self.clients),
            "dashboards_count": len(self.dashboards),
            "uptime": int(time.time() - self.start_time),
            "uptime_str": self.get_uptime_str(),
            "memory": self.get_memory_usage(),
            "power_save": self.power_save_mode,
            "stats": self.stats,
            "total_messages": self.message_count,
            "recent_activity": list(self.activity_log)[-20:]  # Last 20 entries
        }

    async def handler(self, websocket):
        """Main WebSocket handler"""
        try:
            async for message in websocket:
                try:
                    self.message_count += 1
                    self.stats['total_messages'] += 1
                    
                    data = json.loads(message)
                    msg_type = data.get("type")

                    # Registration messages
                    if msg_type == "register_device":
                        await self.register_device(websocket, data)

                    elif msg_type == "register_dashboard":
                        await self.register_dashboard(websocket, data)

                    # Server status request
                    elif msg_type == "get_server_status":
                        status = await self.get_server_status()
                        await websocket.send(json.dumps(status))

                    # Get activity logs
                    elif msg_type == "get_logs":
                        if websocket in self.dashboards:
                            count = data.get("count", 50)
                            logs = list(self.activity_log)[-count:]
                            await websocket.send(json.dumps({
                                "type": "activity_logs",
                                "logs": logs
                            }))

                    # Broadcast to all devices
                    elif msg_type == "broadcast_to_devices":
                        if websocket not in self.dashboards:
                            continue
                        
                        cmd_type = data.get("command_type")
                        logger.info(f"📢 Broadcasting: {cmd_type} to {len(self.clients)} devices")
                        self.log_activity('BROADCAST', f"{cmd_type} to {len(self.clients)} devices")
                        
                        for dev_id, client_data in self.clients.items():
                            try:
                                cmd_data = data.get("data", {})
                                cmd_data["type"] = cmd_type
                                await client_data["websocket"].send(json.dumps(cmd_data))
                            except:
                                pass

                    # Route to specific device
                    elif "target_id" in data:
                        target_id = data["target_id"]
                        
                        if target_id in self.clients:
                            # Log command routing (but not screen frames to reduce noise)
                            if msg_type not in ['start_screen_stream', 'stop_screen_stream', 'mouse_move']:
                                logger.debug(f"➡️  Routing: {msg_type} → {target_id[:20]}...")
                            
                            try:
                                await self.clients[target_id]["websocket"].send(message)
                            except:
                                await self.unregister_device(self.clients[target_id]["websocket"])
                        else:
                            logger.warning(f"⚠️  Target not found: {target_id[:20]}...")

                    # Message from device to dashboards
                    else:
                        sender_id = next(
                            (id for id, c in self.clients.items() if c["websocket"] == websocket),
                            None
                        )
                        if sender_id:
                            data["sender_id"] = sender_id
                            await self.send_to_all_dashboards(json.dumps(data))

                except json.JSONDecodeError:
                    logger.error("❌ Invalid JSON received")
                except Exception as e:
                    logger.error(f"❌ Error handling message: {e}")

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_device(websocket)
            await self.unregister_dashboard(websocket)

    async def heartbeat_loop(self):
        """Send periodic heartbeat pings to all clients"""
        while self.running:
            await asyncio.sleep(HEARTBEAT_INTERVAL)
            
            if not self.clients:
                continue
            
            current_time = time.time()
            disconnected = []
            
            for device_id, client_data in list(self.clients.items()):
                try:
                    # Check for timeout
                    last_pong = self.connection_health.get(device_id, {}).get('last_pong', current_time)
                    if current_time - last_pong > HEARTBEAT_TIMEOUT:
                        logger.warning(f"⚠️ Heartbeat timeout: {device_id[:20]}...")
                        disconnected.append(device_id)
                        continue
                    
                    # Send ping
                    await client_data['websocket'].send(json.dumps({
                        'type': 'ping',
                        'timestamp': current_time
                    }))
                    self.stats['heartbeat_sent'] += 1
                    
                except Exception as e:
                    logger.error(f"❌ Heartbeat failed for {device_id[:20]}: {e}")
                    self.stats['heartbeat_failed'] += 1
                    disconnected.append(device_id)
            
            # Remove disconnected clients
            for device_id in disconnected:
                if device_id in self.clients:
                    await self.unregister_device(self.clients[device_id]['websocket'])

    async def process_health_request(self, path, request_headers):
        """HTTP health endpoint handler"""
        if path == '/health':
            health_data = {
                'status': 'healthy',
                'uptime': self.get_uptime_str(),
                'clients': len(self.clients),
                'dashboards': len(self.dashboards),
                'messages': self.stats['total_messages']
            }
            return HTTPStatus.OK, [('Content-Type', 'application/json')], json.dumps(health_data).encode()
        
        if path == '/metrics':
            # Prometheus-style metrics
            metrics = [
                f'hdex_uptime_seconds {int(time.time() - self.start_time)}',
                f'hdex_clients_total {len(self.clients)}',
                f'hdex_dashboards_total {len(self.dashboards)}',
                f'hdex_messages_total {self.stats["total_messages"]}',
                f'hdex_heartbeat_sent_total {self.stats["heartbeat_sent"]}',
                f'hdex_heartbeat_failed_total {self.stats["heartbeat_failed"]}',
            ]
            return HTTPStatus.OK, [('Content-Type', 'text/plain')], '\n'.join(metrics).encode()
        
        return None  # Let WebSocket handler process

    async def graceful_shutdown(self):
        """Gracefully shutdown server"""
        logger.info("🛑 Initiating graceful shutdown...")
        self.running = False
        
        # Notify all clients
        shutdown_msg = json.dumps({'type': 'server_shutdown'})
        
        for device_id, client_data in list(self.clients.items()):
            try:
                await client_data['websocket'].send(shutdown_msg)
                await client_data['websocket'].close()
            except:
                pass
        
        for dashboard in list(self.dashboards):
            try:
                await dashboard.send(shutdown_msg)
                await dashboard.close()
            except:
                pass
        
        logger.info("✅ Shutdown complete")

    async def start(self):
        """Start the WebSocket server"""
        print("\n" + "="*60)
        print("  🚀 H-DEX SERVER v3.0 ULTRA")
        print("="*60)
        print(f"  Port: {self.port}")
        print(f"  Token: {DASHBOARD_TOKEN[:10]}...")
        print(f"  Heartbeat: {HEARTBEAT_INTERVAL}s interval, {HEARTBEAT_TIMEOUT}s timeout")
        print(f"  Log Rotation: 5 files x 5MB")
        print(f"  Health Endpoint: http://0.0.0.0:{self.port}/health")
        print("="*60 + "\n")
        
        # Start heartbeat task
        self.heartbeat_task = asyncio.create_task(self.heartbeat_loop())
        
        async with websockets.serve(
            self.handler, 
            "0.0.0.0", 
            self.port,
            process_request=self.process_health_request,
            max_size=10*1024*1024,
            ping_interval=15,
            ping_timeout=15
        ):
            logger.info(f"✅ Server started on port {self.port}")
            logger.info("💤 Starting in power-save mode (waiting for connections)")
            
            # Wait until stopped
            while self.running:
                await asyncio.sleep(1)


if __name__ == "__main__":
    server = HDexServer()
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        asyncio.create_task(server.graceful_shutdown())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        logger.info("⏹️  Server stopped by user")
