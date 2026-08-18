# Real Hackers HQ - Complete Project Analysis

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [A-Dex Backend Server Analysis](#a-dex-backend-server)
4. [A-Dex Android App Analysis](#a-dex-android-app)
5. [A-Dex Discord Bot Analysis](#a-dex-discord-bot)
6. [Website Frontend Analysis](#website-frontend)
7. [H-Dex Platform Analysis](#h-dex-platform)
8. [Server ↔ Website Function Matching](#server--website-matching)
9. [Bug Report Summary](#bug-report)
10. [Security Concerns](#security-concerns)

---

## Project Overview

The repository contains **3 major platforms**:

| Platform | Tech Stack | Purpose |
|----------|-----------|---------|
| **A-Dex** | Node.js/Express + Kotlin/Android + Python Discord Bot | Android device management/surveillance |
| **Website** | React + Vite + TypeScript + Firebase | Admin dashboard & phishing tools |
| **H-Dex** | Python WebSockets + Tkinter + Discord Bot | PC device management/control |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    WEBSITE (React + Firebase)                     │
│  Pages: HomePage, ADexPage, HDexPage, PhishingPage, OSINT, etc  │
│  Auth: Firebase Auth (hacker@gmail.com / admin123)              │
└───────────┬──────────────────────┬──────────────────────────────┘
            │ REST (axios)         │ WebSocket (fetch)
            ▼                     ▼
┌───────────────────┐  ┌──────────────────────┐
│  A-Dex Backend    │  │  H-Dex Server         │
│  (Node.js/Express)│  │  (Python WebSockets)  │
│  Port: varies     │  │  Port: 7860/8452      │
└────────┬──────────┘  └────────┬─────────────┘
         │ HMAC-signed HTTP     │ WebSocket
         │ + WebSocket          │
         ▼                     ▼
┌───────────────────┐  ┌──────────────────────┐
│  Android App      │  │  H-Dex Client         │
│  (Kotlin)         │  │  (Python/PyInstaller) │
│  80+ commands     │  │  5937 lines           │
└───────────────────┘  └──────────────────────┘
         ▲                       ▲
         │                       │
┌────────┴───────────────────────┴─────────────┐
│          Discord Bots (Python)                │
│  A-Dex Bot (2149 lines) + H-Dex Bot (2732)   │
│  Slash commands + WebSocket event forwarding  │
└──────────────────────────────────────────────┘
```

---

## A-Dex Backend Server

### File: `backend/src/server.js`
**Purpose:** Express HTTP server entry point + WebSocket setup.

**Key Functions:**
- `createApp()` - Creates Express app with middleware
- In-memory sliding-window IP rate limiter (120 req/min)
- CORS, Helmet (CSP disabled), JSON body parsing with raw body for HMAC
- Creates `RealtimeHub` WebSocket server on `/ws`
- Mounts API routes at `/api/v1`

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| Low | Rate limiter `setInterval` has no `unref()` - prevents clean shutdown |
| Low | `req.requestId` set but never sent in response headers |

---

### File: `backend/src/config.js`
**Purpose:** Loads `.env` config, validates secrets, creates directories.

**Key Config Values:**
- `botHmacSecret` - HMAC signing secret (required in production)
- `botWsToken` - WebSocket auth token (required in production)
- `autoEnrollToken` - Device auto-enrollment token
- `dbPath` - SQLite database path
- `mediaDir` - Media file storage path

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| Medium | `autoEnrollToken` silently defaults to `''` - no warning in production |
| Low | Side effects at import time (`fs.mkdirSync`) |

---

### File: `backend/src/db.js`
**Purpose:** SQLite database initialization using `node:sqlite` (Node 22.5+).

**Tables Created (10 total):**
1. `devices` - Device registry with token, status, metadata
2. `pairing_codes` - Temporary codes for device pairing
3. `guild_admins` - Per-guild admin users
4. `channel_device_bindings` - Discord channel ↔ device mapping
5. `guild_devices` - Guild ↔ device many-to-many
6. `commands` - Command queue (queued → dispatched → completed/failed/timed_out)
7. `command_results` - Results from devices
8. `media_files` - Uploaded media files
9. `locked_apps` - Per-device locked app packages
10. `audit_logs` - Action audit trail

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| Medium | `ALTER TABLE` migration is fragile - no versioning system |
| Low | No index on `command_results.command_id` - slow JOINs |

---

### File: `backend/src/routes/api.js`
**Purpose:** All REST API endpoints.

**API Endpoints:**

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/health` | None | Server health + stats |
| `GET` | `/capabilities` | None | Supported commands list |
| `POST` | `/config/auto-enroll` | Bot | Set auto-enroll guild |
| `POST` | `/pairing/code` | None | Device registers → pairing code |
| `POST` | `/pairing/claim` | Bot | Discord user claims pairing code |
| `POST` | `/commands` | Bot+Admin | Dispatch command to device |
| `POST` | `/commands/:id/media` | Device | Upload media result |
| `GET` | `/media/:mediaId` | Bot | Download media |
| `POST` | `/admins` | Bot+Admin | Add guild admin |
| `DELETE` | `/admins/:userId` | Bot+Admin | Remove guild admin |
| `POST` | `/channel-bindings` | Bot+Admin | Bind device to channel |
| `DELETE` | `/channel-bindings/:channelId` | Bot+Admin | Unbind channel |
| `GET` | `/devices` | Bot | List devices |
| `GET` | `/devices/:id/events` | Bot | Device event history |
| `GET` | `/devices/:id/commands/results` | Bot | Command results |
| `GET` | `/intel` | Bot | All command results |
| `GET` | `/logs` | Bot | Audit logs |
| `GET` | `/commands` | Bot | All commands |

**Supported Device Commands (20+):**
```
screenshot, camera_snap, location, ring, vibrate, toast, flash,
lock, shutdown, reboot, send_sms, dial, open_url, open_app,
getcontacts, getsms, getcalllogs, getpasswords, getwhatsapp,
recordaudio, silentcapture, getaccounts, getclipboard, getimages, gethistory
```

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| High | `GET /devices` for `hq-guild` returns ALL devices across ALL guilds |
| Medium | No pagination cursors - list endpoints can't do infinite scroll |
| Medium | `limit` query param not validated - `NaN` passed to SQLite |
| Low | `DELETE /admins/:userId` mutates `req.body` |

---

### File: `backend/src/services/auth.js`
**Purpose:** Three auth middlewares.

**Auth Methods:**
1. **Bot Auth** - Static token (`x-adex-bot-token`) OR HMAC signature
2. **Device Auth** - Bearer token + device ID
3. **Guild Admin** - Checks `guild_admins` table

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| High | Static token bypasses HMAC - replay vulnerability |
| Medium | HMAC only works with JSON body - latent issue for future GET routes |

---

### File: `backend/src/services/realtimeHub.js`
**Purpose:** WebSocket hub for device ↔ bot communication.

**WebSocket Message Types:**
| Direction | Type | Purpose |
|-----------|------|---------|
| Device → Server | `device.hello` | Auth + register |
| Device → Server | `device.heartbeat` | Keep-alive |
| Device → Server | `device.result` | Command result |
| Device → Server | `device.event` | Device event |
| Bot → Server | `bot.subscribe` | Subscribe to events |
| Server → Device | `device.command` | Send command |
| Server → Bot | `bot.command_result` | Forward result |
| Server → Bot | `bot.device_status` | Device online/offline |
| Server → Bot | `bot.device_event` | Device event |

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| High | Bot WS auth uses `!==` instead of `safeCompare` - timing attack |
| Medium | No message size limit - memory exhaustion possible |
| Medium | No heartbeat timeout - zombie connections not detected |
| Low | `setInterval` timers lack `unref()` |

---

### File: `backend/src/services/store.js`
**Purpose:** Data access layer with 30+ methods wrapping all SQL operations.

**Key Methods:**
- `registerOrRefreshDevice`, `validateDeviceToken`
- `createPairingCode`, `claimPairingCode`
- `createCommand`, `markCommandDispatched`, `completeCommand`
- `expireTimedOutCommands`
- `saveMediaForCommand`, `getMediaById`
- `pruneMediaFiles`, `pruneExpiredPairCodes`

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| Medium | `pruneMediaFiles` deletes file before DB row - orphan risk |
| Low | `completeCommand` calls `getCommandById` twice |

---

### File: `backend/src/utils/mail.js`
**Purpose:** Email utility via nodemailer.

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| **DEAD CODE** | Never imported or used anywhere |
| Low | Creates new SMTP transporter per call |

---

### File: `backend/migrations/init.sql`
**Purpose:** Database schema definition.

**Missing Indexes:**
- `command_results.command_id` (slow JOINs)
- `commands.device_id` alone (only composite index exists)

---

## A-Dex Android App

### File: `service/CommandModels.kt`
**Purpose:** Data classes for WebSocket protocol.

```kotlin
data class DeviceCommand(commandId, requestId, commandName, payload, expiresAt)
data class CommandResult(commandId, status, data, errorCode, errorMessage, mediaId)
```

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| Medium | `expiresAt` is never checked - expired commands still executed |

---

### File: `service/BackendApiClient.kt`
**Purpose:** HTTP client for device pairing.

**API Calls:**
- `POST /api/v1/pairing/code` - Register device + get pairing code

**Payload:**
```json
{
  "deviceId": "...",
  "deviceToken": "...",
  "enrollmentToken": "...",
  "name": "System Update",
  "model": "...",
  "androidVersion": "...",
  "appVersion": "...",
  "metadata": { "camera": bool, "location": bool, "sms": bool, ... }
}
```

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| Medium | Device name hardcoded as `"System Update"` - deceptive |
| Low | No retry logic - fails on transient network issues |

---

### File: `service/DeviceWebSocketManager.kt`
**Purpose:** WebSocket lifecycle management with reconnection.

**WebSocket Messages:**
| Sent | Received |
|------|----------|
| `device.hello` | `device.command` |
| `device.heartbeat` | |
| `device.result` | |
| `device.event` | |

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| Medium | Degraded mode has no recovery path - permanent after 10 failures |
| Low | Race condition on `webSocket` reference |

---

### File: `service/CommandDispatcher.kt` (2001 lines)
**Purpose:** Maps 80+ command names to Android system actions.

**Commands by Category:**

| Category | Commands |
|----------|----------|
| **System** | `shutdown`, `reboot`, `lock`, `volume`, `ringtoneprofile`, `screentimeoutset` |
| **Communication** | `say`, `sayurdu`, `sayscary`, `sayscaryurdu`, `smsdraft`, `dial`, `message`, `fakecallui` |
| **Surveillance** | `screenshot`, `camerasnap`, `silentcapture`, `location`, `getsms`, `getcalllogs`, `getpasswords`, `getwhatsapp`, `getaccounts`, `getclipboard`, `getimages`, `gethistory`, `recordaudio` |
| **File Operations** | `files`, `filestat`, `mkdir`, `rename`, `move`, `delete`, `uploadfile`, `readtext`, `download` |
| **App Control** | `apps`, `open`, `lockapp`, `unlockapp`, `lockedapps`, `usage`, `installapp` |
| **Media** | `playaudio`, `stopaudio`, `pauseaudio`, `resumeaudio`, `audiostatus`, `mediacontrol`, `torchpattern` |
| **Pranks** | `prank`, `prankscreen`, `prank_mode`, `show`, `flashtext`, `soundfx`, `beep`, `countdownoverlay` |
| **Utility** | `wallpaper`, `bluetooth`, `spoof`, `setpin`, `openlink`, `remote_input`, `shakealert` |
| **Data Harvest** | `sysinfo_full`, `permstatus`, `setupcheck`, `contactlookup`, `quicklaunch`, `fileshareintent` |

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| High | `handleGetPasswords()` and `handleGetHistory()` are surveillance features |
| High | `handleInstallApp()` - remote APK install without user consent |
| Medium | `ImageReader` never properly closed in `captureSilentInBackground()` |
| Medium | No input sanitization on file paths - `../` traversal possible |
| Low | `ToneGenerator` may leak if coroutine cancelled |

---

### File: `MainActivity.kt`
**Purpose:** Main activity with permission setup and service startup.

**Key Behavior:**
- Sequential permission check: runtime → overlay → accessibility → usage stats → device admin → files
- Auto-hides app icon after first successful setup
- Starts `ADexForegroundService`

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| High | App auto-hides after setup - user can't find/uninstall |
| Medium | `RECEIVER_EXPORTED` flag - any app can send broadcasts |
| Low | `updatePairStatus(code)` is empty stub |

---

## A-Dex Discord Bot

### File: `bot/main.py` (2149 lines)
**Purpose:** Main Discord bot with 80+ slash commands.

**Slash Commands (80+):**
```
backendstatus, apps, open, lock, say, sayurdu, playaudio, stopaudio,
pauseaudio, resumeaudio, audiostatus, parentpin, shield, screenshot,
files, filestat, mkdir, rename, move, delete, uploadfile, readtext,
download, volume, info, permstatus, setupcheck, location, camerasnap,
contactlookup, smsdraft, fileshareintent, quicklaunch, torchpattern,
ringtoneprofile, screentimeoutset, mediacontrol, randomquote, fakecallui,
silentcapture, shakealert, vibratepattern, beep, countdownoverlay,
flashtext, coinflip, diceroll, randomnumber, quicktimer, soundfx,
prankscreen, show, message, lockapp, lockapp_picker, unlockapp,
lockedapps, usage, prank, getsms, getcalllogs, recordaudio, installapp,
getclipboard, getaccounts, sysinfo_full, gethistory, getpasswords,
sayscary, sayscaryurdu, getwhatsapp, sendwhatsapp, bluetooth, pair,
bind, unbind, admins, devices, setmain, addusernotify, wallpaper,
prank_mode, spoof, setpin, openlink, getimages, id, button, logs
```

**UI Components:**
- `FileBrowserView` - Interactive file browser with buttons
- `LockAppPickerView` - App lock/unlock with search
- `RemoteControlView` - D-pad navigation control

**Backend API Calls:**
| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/capabilities` | Load supported commands |
| `POST /api/v1/config/auto-enroll` | Set auto-enrollment |
| `POST /api/v1/commands` | Queue commands |
| `POST /api/v1/pairing/claim` | Pair devices |
| `POST/DELETE /api/v1/channel-bindings` | Channel bindings |
| `POST/DELETE /api/v1/admins` | Admin management |
| `GET /api/v1/devices` | List devices |
| `GET /api/v1/devices/:id/events` | Device events |
| `GET /api/v1/media/:id` | Download media |

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| **CRITICAL** | `view.render_text()` called but method doesn't exist - `/files` and `/lockapp_picker` crash |
| High | `message_content` intent disabled - legacy prefix commands broken |
| Medium | Hardcoded `"Pakistani Guitar Store"` in error messages |
| Low | `_notify_user_ids` set not persisted - lost on restart |

---

### File: `bot/backend_client.py`
**Purpose:** HTTP + WebSocket client for A-Dex backend.

**WebSocket Messages Handled:**
- `bot.command_result` - Command results
- `bot.device_status` - Device online/offline
- `bot.device_event` - Device events

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| Low | WebSocket reconnect silently swallows all errors |
| Low | No rate limiting on HTTP requests |

---

### File: `bot/command_parser.py`
**Purpose:** Legacy text-prefix command parser (`!command`).

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| Medium | snake_case/camelCase payload key mismatch with backend |
| Medium | Missing commands - stale/legacy file |
| Low | Fragile body serialization coupling with signature.py |

---

## Website Frontend

### File: `src/firebase.ts`
**Purpose:** Firebase SDK initialization.

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| **CRITICAL** | Firebase API key hardcoded in source |

---

### File: `src/components/AuthContext.tsx`
**Purpose:** Firebase authentication context.

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| **CRITICAL** | Hardcoded admin credentials: `hacker@gmail.com` / `admin123` |
| High | Auto-creates admin account on failed login with weak password |

---

### File: `src/App.tsx`
**Purpose:** Root component with routing.

**Routes:**
| Path | Component | Auth Required |
|------|-----------|---------------|
| `/` | HomePage | Yes (MainLayout) |
| `/adex` | ADexPage | Yes |
| `/hdex` | HDexPage | Yes |
| `/phishing` | PhishingPage | Yes |
| `/osint` | OSINTPage | Yes |
| `/files` | FileManagerPage | Yes |
| `/danger` | DangerPage | Yes |
| `/admin` | AdminPage | Yes |
| `/hex` | HexPage | Yes |
| `/about` | AboutPage | Yes |
| `/credits` | CreditsPage | Yes |
| `/contact` | ContactPage | Yes |
| `/docs` | DocsPage | Yes |
| `/p/:templateId` | LivePhishPage | **NO** |
| `*` | NotFoundPage | No |

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| Medium | `/p/:templateId` has NO auth guard - accessible to anyone |

---

### File: `src/pages/ADexPage.tsx`
**Purpose:** Mobile device surveillance dashboard.

**API Calls:**
- `GET /api/v1/devices` - Fetch device list
- `GET /api/v1/devices/:id/commands/results` - Poll results
- `GET /api/v1/devices/:id/events` - Poll events
- `POST /api/v1/commands` - Send commands

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| Medium | Polling 3 endpoints every 8 seconds - rate limit risk |
| Medium | `logs` dependency in `useCallback` causes stale closure |
| Low | All catch blocks silently swallow errors |

---

### File: `src/pages/HDexPage.tsx` (1110 lines)
**Purpose:** PC surveillance/control dashboard via WebSocket.

**WebSocket Messages:**
| Sent | Received |
|------|----------|
| `register_dashboard` | `device_list` |
| `command` | `screen_frame` |
| | `webcam_frame` |
| | `process_list` |
| | `command_output` |
| | `clipboard_content` |
| | `live_keylog` |
| | `keylog_dump` |
| | `dir_list` |
| | `sys_info` |
| | `battery_status` |
| | `network_info` |
| | `heartbeat` |

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| Medium | `connectWS` in useEffect deps causes reconnection loops |
| Low | File manager fetch missing auth header |

---

### File: `src/pages/HomePage.tsx`
**Purpose:** Dashboard landing page.

**API Calls:**
- `GET /api/v1/devices` with bot token header

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| Low | Empty catch block - errors silently swallowed |

---

### Phishing Templates Analysis

| Template | Captures Data | Bug |
|----------|--------------|-----|
| `GoogleLogin.tsx` | Yes | "Show password" checkbox doesn't toggle |
| `FacebookLogin.tsx` | Yes | None |
| `InstagramLogin.tsx` | Yes | None |
| `TwitterTemplate.tsx` | **NO** | `onSuccess` never called - broken |
| `SecurityTemplate.tsx` | **NO** | `onSuccess` never called - broken |
| `StartpageTemplate.tsx` | **NO** | `onSuccess` never called - broken |
| `CursorTemplate.tsx` | **NO** | `onSuccess` never called - broken |
| `ZaiTemplate.tsx` | Yes | None |
| `PhilosophyTemplate.tsx` | Yes (minimal) | None |
| `DefaultTemplate.tsx` | No | Different interface - not used |

**4 out of 10 phishing templates are broken (don't capture data).**

---

### Other Pages

| Page | Status | Issues |
|------|--------|--------|
| `OSINTPage.tsx` | Simulated | All results are fake/hardcoded |
| `DangerPage.tsx` | Simulated | All terminal output is canned |
| `HexPage.tsx` | Simulated | Build/test operations are fake |
| `ContactPage.tsx` | Broken | Submit button has no onClick handler |
| `CreditsPage.tsx` | Working | Contact buttons do nothing |
| `DocsPage.tsx` | Working | "READ_FULL_MANUAL" buttons do nothing |
| `AdminPage.tsx` | Partial | Analytics/API tabs show nothing |
| `NotFoundPage.tsx` | Working | None |

---

### Components

| Component | Issues |
|-----------|--------|
| `DataParticles.tsx` | Memory leak - `requestAnimationFrame` never cancelled |
| `BackgroundVideo.tsx` | Typo: `backgroud.webm` instead of `background` |
| `StatusFooter.tsx` | All status values are fake/hardcoded |
| `LoadingContext.tsx` | Loading is purely cosmetic/fake |
| `PhishingContext.tsx` | Generates fake IPs, no encryption |
| `BraveBrowserWrapper.tsx` | Inline CSS injected every render, tabs don't close |

---

## H-Dex Platform

### File: `H-dex Server/server.py` (845 lines)
**Purpose:** Python WebSocket server with SQLite database.

**Features:**
- Heartbeat mechanism (30s ping, 90s timeout)
- Log rotation (5 files x 5MB)
- HTTP `/health` endpoint
- Connection health tracking
- Graceful shutdown
- Audit logging

**Database Tables:**
- `devices` - Device registry
- `events` - Activity logs
- `harvested_records` - Captured data (passwords, wifi, cookies)
- `pending_tasks` - Queued commands for offline devices
- `payloads` - Hosted payload files

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| Medium | Default dashboard token `hdex_admin_2026` hardcoded |
| Low | Single SQLite connection - no thread safety |

---

### File: `H-Dex-Final-HF-Server/app.py` (911 lines)
**Purpose:** FastAPI + WebSocket server for Hugging Face deployment.

**Features:**
- FastAPI with uvicorn
- WebSocket device/dashboard communication
- Discord webhook notifications
- Telegram notifications
- SQLite database with 6 tables
- Payload registry
- Auto-tasking for offline devices

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| Medium | Bare `except: pass` blocks hide all errors |
| Low | No authentication on WebSocket connections |

---

### File: `hugging_face_server/server.py` (98 lines)
**Purpose:** Minimal WebSocket relay server.

**Features:**
- Device registration
- Dashboard registration
- Message routing
- Device list broadcasting

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| High | No authentication at all |
| Medium | Bare `except: pass` blocks |
| Low | Only one dashboard supported at a time |

---

### File: `client_template.py` (5937 lines)
**Purpose:** Headless Windows client (RAT).

**Features:**
- WebSocket connection with auto-reconnect
- Anti-VM detection
- Geofencing
- Startup persistence
- Stealth mode
- System info gathering
- File operations
- Process management
- Screenshot/screen capture
- Keylogger
- Clipboard monitoring
- Browser data extraction
- WiFi password harvesting
- Crypto wallet theft
- Discord token theft

**Configuration:**
```python
SERVER_URI = "wss://talhasss-hdex-ultra-server.hf.space/ws"
CLIENT_TAG = "HQ-ULTRA-NODE-01"
ADD_TO_STARTUP = "True"
STARTUP_KEY_NAME = "Windows Security Host"
```

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| High | `SERVER_URI` base64 encoded but easily decodable |
| Medium | `ENABLE_ANTI_VM` set to `False` by default |
| Medium | Configuration duplicated (defined twice) |

---

### File: `admin_dashboard.py` (3505 lines)
**Purpose:** Tkinter/customtkinter GUI dashboard.

**Features:**
- Multiple premium themes (OLED, Cyber Matrix, Deep Void, Crimson Apex)
- WebSocket connection to server
- Device management
- File browser
- Process manager
- Remote control
- Screenshot/webcam viewing
- Keylogger viewer
- Command execution
- Media playback

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| Medium | `matplotlib` imported at module level - slow startup |
| Low | Default server URL hardcoded |

---

### File: `H-Dex Bot/bot.py` (2732 lines)
**Purpose:** Discord bot for H-Dex control.

**Features:**
- Slash commands
- Device management
- Remote control via Discord
- File browser
- Process manager
- Rate limiting

**Bugs Found:**
| Severity | Bug |
|----------|-----|
| Medium | 15 second startup delay for API stability |
| Low | Bans stored in JSON file - not atomic |

---

## Server ↔ Website Matching

### A-Dex Server ↔ Website ADexPage

| Server Endpoint | Website Call | Match Status |
|-----------------|--------------|--------------|
| `GET /api/v1/devices` | `axios.get(/api/v1/devices)` | **MATCHED** |
| `GET /api/v1/devices/:id/commands/results` | `axios.get(/api/v1/devices/:id/commands/results)` | **MATCHED** |
| `GET /api/v1/devices/:id/events` | `axios.get(/api/v1/devices/:id/events)` | **MATCHED** |
| `POST /api/v1/commands` | `axios.post(/api/v1/commands)` | **MATCHED** |
| `GET /api/v1/capabilities` | Not called from website | **UNMATCHED** |
| `GET /api/v1/logs` | Not called from website | **UNMATCHED** |
| `GET /api/v1/intel` | Not called from website | **UNMATCHED** |

**Command Name Matching:**

| Website Button | Server Command | Android Handler | Status |
|---------------|----------------|-----------------|--------|
| Screenshot | `screenshot` | `handleScreenshot()` | **MATCHED** |
| Camera | `camera_snap` | `handleCameraSnap()` | **MATCHED** |
| Location | `location` | `handleLocation()` | **MATCHED** |
| Ring | `ring` | `handleRing()` (missing) | **MISSING** |
| Vibrate | `vibrate` | `handleVibrate()` (missing) | **MISSING** |
| Lock | `lock` | `handleLock()` | **MATCHED** |
| Shutdown | `shutdown` | `handleShutdown()` (missing) | **MISSING** |

**Missing Android Handlers for Website Commands:**
- `ring` - No handler in `CommandDispatcher.kt`
- `vibrate` - No handler in `CommandDispatcher.kt`
- `shutdown` - No handler in `CommandDispatcher.kt`
- `reboot` - No handler in `CommandDispatcher.kt`
- `send_sms` - No handler in `CommandDispatcher.kt`
- `dial` - No handler in `CommandDispatcher.kt`
- `open_url` - No handler in `CommandDispatcher.kt` (but `openlink` exists)
- `open_app` - No handler in `CommandDispatcher.kt` (but `open` exists)
- `getcontacts` - No handler in `CommandDispatcher.kt` (but `contactlookup` exists)
- `toast` - No handler in `CommandDispatcher.kt`
- `flash` - No handler in `CommandDispatcher.kt`

**Naming Mismatches:**
| Website/Server Name | Android Handler Name | Issue |
|--------------------|--------------------|-------|
| `camera_snap` | `handleCameraSnap()` | OK (internal) |
| `getcontacts` | `handleContactLookup()` | Different name |
| `send_sms` | `handleSmsDraft()` | Different name + different action |
| `open_url` | `handleOpenLink()` | Different name |
| `open_app` | `handleOpen()` | Different name |

---

### A-Dex Server ↔ Discord Bot

| Server Endpoint | Bot Call | Match Status |
|-----------------|----------|--------------|
| `POST /api/v1/commands` | `self.backend.post("/commands", body)` | **MATCHED** |
| `GET /api/v1/devices` | `self.backend.get("/devices")` | **MATCHED** |
| `GET /api/v1/devices/:id/events` | `self.backend.get(f"/devices/{id}/events")` | **MATCHED** |
| `GET /api/v1/capabilities` | `self.backend.get("/capabilities")` | **MATCHED** |
| `POST /api/v1/pairing/claim` | `self.backend.post("/pairing/claim", body)` | **MATCHED** |
| `POST /api/v1/channel-bindings` | `self.backend.post("/channel-bindings", body)` | **MATCHED** |
| `DELETE /api/v1/channel-bindings/:id` | `self.backend.delete(f"/channel-bindings/{id}")` | **MATCHED** |
| `POST /api/v1/admins` | `self.backend.post("/admins", body)` | **MATCHED** |
| `DELETE /api/v1/admins/:id` | `self.backend.delete(f"/admins/{id}")` | **MATCHED** |
| `POST /api/v1/config/auto-enroll` | `self.backend.post("/config/auto-enroll", body)` | **MATCHED** |
| `GET /api/v1/media/:id` | `self.backend.get_media(id)` | **MATCHED** |

**Bot Command Name Matching:**

| Slash Command | Server Command Payload | Android Handler | Status |
|---------------|----------------------|-----------------|--------|
| `/screenshot` | `screenshot` | `handleScreenshot()` | **MATCHED** |
| `/location` | `location` | `handleLocation()` | **MATCHED** |
| `/camerasnap` | `camera_snap` | `handleCameraSnap()` | **MATCHED** |
| `/getsms` | `getsms` | `handleGetSms()` | **MATCHED** |
| `/getcalllogs` | `getcalllogs` | `handleGetCallLogs()` | **MATCHED** |
| `/getpasswords` | `getpasswords` | `handleGetPasswords()` | **MATCHED** |
| `/lockapp` | `lockapp` | `handleLockApp()` | **MATCHED** |
| `/unlockapp` | `unlockapp` | `handleUnlockApp()` | **MATCHED** |

**Bug: `render_text()` doesn't exist:**
- `/files` command calls `view.render_text()` - crashes
- `/lockapp_picker` command calls `view.render_text()` - crashes
- Should be `view.render_embed()`

---

### Website ↔ H-Dex Server

| Website Page | H-Dex Server Endpoint | Match Status |
|-------------|----------------------|--------------|
| `HDexPage.tsx` WebSocket | `server.py` WebSocket | **MATCHED** (different protocol) |
| `FileManagerPage.tsx` `/fm/list` | `app.py` file manager routes | **MATCHED** |
| `FileManagerPage.tsx` `/fm/drive` | `app.py` drive listing | **MATCHED** |
| `FileManagerPage.tsx` `/fm/search` | `app.py` file search | **MATCHED** |
| `FileManagerPage.tsx` `/fm/download` | `app.py` file download | **MATCHED** |

**WebSocket Message Matching:**

| Website Sends | Server Handles | Match |
|--------------|----------------|-------|
| `register_dashboard` | `register_dashboard` | **MATCHED** |
| `command` | Route to device | **MATCHED** |

| Server Sends | Website Handles | Match |
|-------------|-----------------|-------|
| `device_list` | `setDevices()` | **MATCHED** |
| `screen_frame` | `setScreenFrame()` | **MATCHED** |
| `webcam_frame` | `setWebcamFrame()` | **MATCHED** |
| `process_list` | `setProcesses()` | **MATCHED** |
| `command_output` | Various handlers | **MATCHED** |
| `clipboard_content` | `setClipboard()` | **MATCHED** |
| `live_keylog` | `setKeylogLines()` | **MATCHED** |
| `keylog_dump` | `setKeylogDump()` | **MATCHED** |
| `dir_list` | `setDirListing()` | **MATCHED** |
| `sys_info` | `setSysInfo()` | **MATCHED** |
| `battery_status` | `setBatteryInfo()` | **MATCHED** |
| `network_info` | `setNetInfo()` | **MATCHED** |
| `heartbeat` | Connection check | **MATCHED** |

---

## Bug Report Summary

### Critical Bugs (Fix Immediately)

| # | File | Line | Bug |
|---|------|------|-----|
| 1 | `AuthContext.tsx` | - | Hardcoded admin credentials `hacker@gmail.com` / `admin123` |
| 2 | `firebase.ts` | - | Firebase API key exposed in source code |
| 3 | `main.py` (A-Dex Bot) | 937 | `view.render_text()` doesn't exist - `/files` crashes |
| 4 | `main.py` (A-Dex Bot) | 1854 | `view.render_text()` doesn't exist - `/lockapp_picker` crashes |

### High Severity Bugs

| # | File | Bug |
|---|------|-----|
| 5 | `auth.js` | Static token auth bypasses HMAC - replay vulnerability |
| 6 | `realtimeHub.js` | Bot WS auth uses `!==` instead of `safeCompare` |
| 7 | `api.js` | `GET /devices` for `hq-guild` returns ALL devices |
| 8 | `CommandDispatcher.kt` | `handleInstallApp()` - remote APK install without consent |
| 9 | `MainActivity.kt` | App auto-hides after setup - user can't uninstall |
| 10 | `client_template.py` | Server URI base64 encoded but easily decodable |
| 11 | `hugging_face_server/server.py` | No authentication at all |

### Medium Severity Bugs

| # | File | Bug |
|---|------|-----|
| 12 | `config.js` | `autoEnrollToken` no production warning |
| 13 | `db.js` | `ALTER TABLE` migration fragile - no versioning |
| 14 | `api.js` | `limit` param not validated - `NaN` to SQLite |
| 15 | `store.js` | `pruneMediaFiles` deletes file before DB row |
| 16 | `DeviceWebSocketManager.kt` | No recovery from degraded mode |
| 17 | `CommandDispatcher.kt` | `ImageReader` resource leak |
| 18 | `HDexPage.tsx` | `connectWS` in deps causes reconnection loops |
| 19 | `ADexPage.tsx` | Polling 3 endpoints every 8 seconds |
| 20 | `App.tsx` | `/p/:templateId` has no auth guard |
| 21 | `main.py` (A-Dex Bot) | Hardcoded `"Pakistani Guitar Store"` in errors |
| 22 | `command_parser.py` | snake_case/camelCase payload mismatch |
| 23 | `server.py` (H-Dex) | Default dashboard token hardcoded |
| 24 | `app.py` (H-Dex) | Bare `except: pass` blocks |

### Low Severity Bugs

| # | File | Bug |
|---|------|-----|
| 25 | `server.js` | Rate limiter `setInterval` no `unref()` |
| 26 | `server.js` | `requestId` not sent in response headers |
| 27 | `db.js` | Missing index on `command_results.command_id` |
| 28 | `mail.js` | Dead code - never used |
| 29 | `mail.js` | Creates new SMTP transporter per call |
| 30 | `random.js` | Modulo bias in `generatePairCode` |
| 31 | `realtimeHub.js` | No message size limit |
| 32 | `realtimeHub.js` | No heartbeat timeout |
| 33 | `store.js` | `completeCommand` calls `getCommandById` twice |
| 34 | `DataParticles.tsx` | Memory leak - rAF never cancelled |
| 35 | `BackgroundVideo.tsx` | Typo: `backgroud.webm` |
| 36 | `PhishingContext.tsx` | Fake IPs, no encryption |
| 37 | `LoadingContext.tsx` | Loading is fake |
| 38 | `StatusFooter.tsx` | Status values are fake |
| 39 | `contactpage.tsx` | Submit button has no handler |
| 40 | `DocsPage.tsx` | "READ_FULL_MANUAL" buttons do nothing |
| 41 | `CreditsPage.tsx` | Contact buttons do nothing |
| 42 | `AdminPage.tsx` | Analytics/API tabs show nothing |
| 43 | `main.py` (A-Dex Bot) | `_notify_user_ids` not persisted |
| 44 | `backend_client.py` | WS reconnect swallows errors |
| 45 | `config.py` | Default dev secrets could deploy |
| 46 | `CommandModels.kt` | `expiresAt` never checked |
| 47 | `BackendApiClient.kt` | No retry logic |

### Broken Features

| Feature | File | Issue |
|---------|------|-------|
| TwitterTemplate phishing | `TwitterTemplate.tsx` | `onSuccess` never called |
| SecurityTemplate phishing | `SecurityTemplate.tsx` | `onSuccess` never called |
| StartpageTemplate phishing | `StartpageTemplate.tsx` | `onSuccess` never called |
| CursorTemplate phishing | `CursorTemplate.tsx` | `onSuccess` never called |
| OSINT scanning | `OSINTPage.tsx` | All results fake/hardcoded |
| Danger terminal | `DangerPage.tsx` | All output canned |
| Hex build | `HexPage.tsx` | Build operations simulated |
| Contact form | `ContactPage.tsx` | Submit does nothing |
| Show password toggle | `GoogleLogin.tsx` | Doesn't toggle input type |
| BraveBrowser tabs | `BraveBrowserWrapper.tsx` | Tab close doesn't work |
| Window controls | `BraveBrowserWrapper.tsx` | Min/max/close don't work |

---

## Security Concerns

### Critical

1. **This is surveillance software** - The codebase implements keylogging, password sniffing, WhatsApp data exfiltration, silent photo capture, SMS/call log reading, clipboard monitoring, and remote APK installation.

2. **Hardcoded credentials** - Firebase admin account (`hacker@gmail.com`/`admin123`) and Firebase API key exposed in source code.

3. **No auth on phishing pages** - `/p/:templateId` accessible to anyone with the URL.

4. **Static token replay** - A-Dex bot auth uses static token without HMAC, allowing indefinite replay.

5. **WebSocket auth weakness** - Bot WS auth uses `!==` instead of constant-time comparison.

### High

6. **App hides itself** - Android app auto-hides after setup, making uninstallation difficult.

7. **Deceptive naming** - "System Update", "Pakistani Guitar Store", "System Integrity Verified" used throughout.

8. **Remote APK installation** - Can install arbitrary APKs without user consent.

9. **PIN bypass** - Remote PIN change/set possible.

10. **No input sanitization** - File paths vulnerable to `../` traversal.

### Medium

11. **No rate limiting on Discord bot HTTP requests**

12. **No message size limits on WebSocket**

13. **Fake data presented as real** - OSINT results, terminal output, status footer all show hardcoded data.

14. **No encryption** - Intel data stored as plaintext JSON in localStorage.

15. **Missing indexes** - Slow queries on large datasets.

---


*Analysis completed on: August 18, 2026*
*Total files analyzed: 60+*
*Total bugs found: 47*
*Broken features: 11*
