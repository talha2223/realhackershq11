# Architecture — Real Hackers HQ

## System Overview

```
                    ┌─────────────────────────────────────────┐
                    │            Website (React/Vite)          │
                    │     Firebase Auth + Leaflet Map + UI     │
                    └──────────────┬──────────────────────────┘
                                   │ HTTPS
                    ┌──────────────▼──────────────────────────┐
                    │       Firebase Hosting (Static)          │
                    └─────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                          A-Dex Ecosystem                                 │
│                                                                          │
│  ┌──────────────┐     WebSocket      ┌──────────────────┐               │
│  │ Android App  │◄──────────────────►│  A-Dex Backend   │               │
│  │ (Kotlin)     │  device.hello      │  (Express/Node)  │               │
│  │              │  device.result     │  SQLite (WAL)    │               │
│  │              │  device.event      │  Media Storage    │               │
│  └──────────────┘                    └────────▲─────────┘               │
│                                               │                         │
│                                      REST + WebSocket                   │
│                                               │                         │
│  ┌──────────────────────────────────────────┐ │                         │
│  │         A-Dex Discord Bot                │ │                         │
│  │    (discord.js / discord.py)             ├─┘                         │
│  │    HMAC-signed API calls                 │                           │
│  └──────────────────────────────────────────┘                           │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                          H-Dex Ecosystem                                 │
│                                                                          │
│  ┌──────────────┐     WebSocket      ┌──────────────────┐               │
│  │ Windows PC   │◄──────────────────►│  H-Dex HF Server │               │
│  │ Client       │  register_device   │  (FastAPI)       │               │
│  │              │  data harvest      │  SQLite          │               │
│  │              │  keylog sync       │  File Manager    │               │
│  └──────────────┘                    └────────▲─────────┘               │
│                                               │                         │
│                                    WebSocket + HTTP API                 │
│                                               │                         │
│  ┌──────────────────────────────────────────┐ │                         │
│  │         H-Dex Discord Bot                │ │                         │
│  │         (discord.py)                     ├─┘                         │
│  │    Dashboard token auth                  │                           │
│  └──────────────────────────────────────────┘                           │
│                                                                          │
│  ┌──────────────────────────────────────────┐                           │
│  │         Open-Claw AI Agent               │                           │
│  │    (FastAPI + Llama-3/Mistral)           │                           │
│  │    Natural language → JSON commands       │                           │
│  └──────────────────────────────────────────┘                           │
└──────────────────────────────────────────────────────────────────────────┘
```

## A-Dex Backend — Detailed Flow

### Authentication Layers

```
Request → [rateLimiter] → [helmet/cors] → [json.parse + rawBody] → [route]

Route auth chain:
  botAuth    → HMAC-SHA256 or static token (timing-safe)
  deviceAuth → Bearer token + device ID lookup in SQLite
  guildAdmin → guild_id + discord_user_id in guild_admins table
```

### WebSocket Protocol

```
Device connects → ws://server/ws
  ↓
device.hello {deviceId, deviceToken, model, ...}
  ↓
server validates token via SQLite
  ↓
server.device.ready + flush queued commands
  ↓
device.command {commandId, commandName, payload}  ← server sends
  ↓
device.result {commandId, status, data}           → server receives
  ↓
bot.command_result fanout to all bot subscribers
```

### Command Lifecycle

```
Discord user → slash command → Bot → POST /api/v1/command
  ↓
Bot sends: guildId, channelId, discordUserId, deviceId, commandName, payload
  ↓
Backend validates: Zod schema → guild admin check → device exists
  ↓
Command created in SQLite (status: queued, expiresAt: now + 90s)
  ↓
If device online: WebSocket dispatch (status: dispatched)
If device offline: remains queued (flushed on reconnect)
  ↓
Device executes, sends result via WebSocket
  ↓
Command marked completed/failed, result stored, fanout to bots
  ↓
Cleanup: commands expired after 90s, media pruned after 24h
```

## H-Dex Server — Detailed Flow

### WebSocket Protocol

```
Client connects → ws://server:7860/ws
  ↓
register_device {info: {id, name, ip, os, ...}}
  ↓
Server checks: kill_switch? banned? 
  ↓
Stores client, updates SQLite, broadcasts device_list to dashboards
  ↓
Dashboard connects → register_dashboard {token}
  ↓
Dashboard sends commands → server routes to target device
  ↓
Device sends data back → server harvests sensitive types → broadcasts to dashboards
```

### Data Harvest Flow

```
Device sends sensitive data (browser_passwords, discord_tokens, etc.)
  ↓
Server identifies sensitive type via hardcoded list
  ↓
save_harvest() → SQLite harvested_records table
  ↓
broadcast_to_dashboards() → all connected dashboards receive data
  ↓
Dashboard can export via /export/harvest (JSON or CSV)
```

## Tech Stack

| Component | Language | Framework | Database | Key Libraries |
|-----------|----------|-----------|----------|---------------|
| A-Dex Backend | Node.js (CommonJS) | Express 4.x | SQLite (WAL) | helmet, cors, zod, multer, ws, morgan |
| A-Dex Bot (JS) | JavaScript | discord.js | — | axios, ws |
| A-Dex Bot (Python) | Python | discord.py | — | aiohttp |
| A-Dex Android | Kotlin | Android SDK | Room | OkHttp |
| H-Dex HF Server | Python | FastAPI | SQLite | uvicorn, psutil, websockets |
| H-Dex Standalone | Python | websockets | SQLite | psutil |
| H-Dex Bot | Python | discord.py | — | websockets, requests |
| Open-Claw | Python | FastAPI | — | huggingface_hub |
| Website | TypeScript | React 19 + Vite 8 | Firebase | firebase/auth, react-router, leaflet, framer-motion |

## File Structure

```
Real-Hackers-Hq-Final-updated-repo/
├── A-Dex/
│   ├── android-app/              # Kotlin Android client
│   ├── backend/
│   │   ├── migrations/init.sql   # SQLite schema (9 tables)
│   │   ├── src/
│   │   │   ├── config.js         # Env-based config with secret validation
│   │   │   ├── db.js             # SQLite init (WAL, foreign keys)
│   │   │   ├── server.js         # Express app + middleware chain
│   │   │   ├── routes/api.js     # All REST endpoints
│   │   │   ├── services/
│   │   │   │   ├── auth.js       # Bot/Device/GuildAdmin middleware
│   │   │   │   ├── store.js      # Data access layer (all SQL)
│   │   │   │   └── realtimeHub.js # WebSocket hub
│   │   │   └── utils/            # signature, random, mail, time
│   │   └── tests/api.test.js
│   ├── discord-bot/
│   │   ├── src/                  # Node.js implementation
│   │   └── bot/                  # Python implementation
│   ├── deploy/huggingface/       # HF Spaces deployment
│   └── Dockerfile
├── H-Dex/
│   ├── H-dex Server/server.py    # Standalone WebSocket server
│   ├── H-Dex-Final-HF-Server/    # FastAPI HF server
│   │   └── app.py                # 911-line server with all endpoints
│   ├── H-Dex Bot/bot.py          # Discord bot (1100+ lines)
│   ├── Open-Claw-Space/app.py    # AI agent
│   ├── admin_dashboard.py        # Desktop GUI (Tkinter)
│   └── config.json               # Client config
├── website/
│   ├── src/
│   │   ├── App.tsx               # Route definitions
│   │   ├── firebase.ts           # Firebase config
│   │   ├── components/
│   │   │   ├── AuthContext.tsx    # Firebase auth
│   │   │   └── phishing/         # Phishing templates
│   │   └── pages/                # Page components
│   └── firebase.json
├── .env.example                  # Environment variable template
├── PRD.md                        # This file
├── Architecture.md               # This file
├── Rules.md
├── Phases.md
├── Design.md
└── Memory.md
```

## Database Schemas

### A-Dex (9 tables)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `devices` | Registered Android devices | id, token, name, model, status |
| `pairing_codes` | Temporary pairing tokens | code, device_id, expires_at, claimed_at |
| `guild_admins` | Authorized Discord users per guild | guild_id, discord_user_id |
| `channel_device_bindings` | Discord channel ↔ device mapping | channel_id, guild_id, device_id |
| `guild_devices` | Device ownership per guild | guild_id, device_id |
| `commands` | Command queue with expiry | id, device_id, command_name, status, expires_at |
| `command_results` | Command execution results | id, command_id, status, data_json |
| `media_files` | Uploaded media with retention | id, command_id, file_path, mime_type |
| `audit_logs` | Immutable audit trail | guild_id, discord_user_id, action, target |

### H-Dex (5 tables)

| Table | Purpose |
|-------|---------|
| `devices` | Registered Windows devices with full system info |
| `blacklist` | Banned device HWIDs |
| `events` | Activity log (connections, commands, data) |
| `harvested_records` | Captured passwords, cookies, tokens, keys |
| `pending_tasks` | Queued commands for offline devices |
| `payloads` | Registered downloadable files |
