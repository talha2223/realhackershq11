# H-Dex ULTRA v3.0 - Changelog

## [v3.1 HOTFIX] - 2026-01-17
### 🐛 Bug Fixes
- **Geolocation**: Fixed IP location retrieval with multiple API fallbacks (ip-api.com, ipapi.co).
- **WiFi Extraction**: Rewrote password extraction logic using robust regex patterns.
- **Wallpaper**: Fixed base64 wallpaper setting not working from Dashboard and Discord Bot.
- **Crazy Mouse**: Fixed async/sync threading issue causing the feature to fail.
- **WebSocket Frame Size**: Increased max frame size to 10MB across all components to prevent "message too big" errors.
- **Builder**: Fixed missing `build_client` function and Unicode encoding issues.
- **Connection Stability**: Fixed server concurrency bug ("Set changed size") and implemented STABLE client IDs based on MAC/Hostname to prevent "Target Not Found" errors.
- **Control Features**: Fixed `send_msg` (Message Box), `monitor_off`/`on`, and `open_cd`.
- **System Info**: Fixed missing `send_system_info` implementation on client side.

### 🚀 New Features
- **Device Info Logging**: Server now saves comprehensive device information to text files in `device_logs/` folder when clients connect.
- **Enhanced Registration**: Client now sends comprehensive system info on connect:
  - Username, Hostname, Architecture, Processor
  - RAM (Total/Available), CPU Cores, Disk Space
  - Local IP, MAC Address
  - Geo-location (Country, City, Region, ISP, Timezone)
- **Discord Bot New Commands**:
  - `/wallpaper <url>` - Download and set wallpaper via URL
  - `/virus` - Trigger scary virus prank effect
  - `/fakebsod` - Display fake Blue Screen of Death
  - `/matrix` - Display Matrix screen effect
  - `/hangup` - CPU stress/hang system
  - `/selfdestruct` - Remove client and all traces
  - `/disabledefender` / `/enabledefender` - Toggle Windows Defender
  - `/realbsod` - Trigger actual BSOD (dangerous)
  - `/emptyrecycle` - Empty recycle bin
  - `/hideicons` / `/showicons` - Toggle desktop icons
  - `/broadcast <cmd>` - Send command to ALL devices
- **Client Functions**: Added `toggle_defender`, `toggle_usb`, `toggle_wifi`, `minimize_all`, `spam_open_url`, `crazy_mouse`, `start_input_blocking`, `stop_input_blocking`.

### 🛠 Improvements
- **Builder**: Professional build logging with progress indicators and status reporting.
- **Server**: Added psutil dependency for memory monitoring.
- **Bot**: Added requests dependency, 15+ new slash commands, increased WebSocket frame size.
- **Code Cleanup**: Removed duplicate handlers, consolidated redundant functions.


---

## [v3.0 ULTRA] - 2026-01-16
### 🚀 New Features
#### **Dashboard**
- **Professional UI**: Complete redesign with Indigo/Slate theme, glassmorphism, and responsive layout.
- **Script Editor**: Create, save, and execute PowerShell/Batch/Python scripts on multiple devices.
- **Macro Recorder**: Record dashboard actions and replay them as automated macros.
- **Advanced Control**:
  - **Multi-select**: Control multiple devices simultaneously.
  - **Device Groups**: Organize devices into logical groups.
  - **Export Data**: Export device list to CSV/JSON.
  - **Bandwidth Monitor**: Real-time network upload/download speed graphs.
- **Tools**:
  - Remote Desktop (Screen Share) with quality controls.
  - Webcam & Microphone live streaming.
  - File Manager (Upload/Download/Execute).
  - Registry & Service Manager.
  - Process Manager with Kill capability.
  - Keystroke Injection & Keylogger Manager.

#### **Client (Silent Agent)**
- **Stealth & Security**:
  - **Geofencing**: Self-destruct if outside allowed countries.
  - **Anti-VM**: Detects VirtualBox/VMware and terminates.
  - **Stealth Mode**: Hides tracks (files/processes).
- **Surveillance**:
  - **Network Scanner**: Scan local subnet for open ports.
  - **Browser Data**: Extract History and Saved Passwords (Chrome/Edge/Firefox).
  - **WiFi**: Extract saved WiFi profiles and passwords.
  - **Location**: IP-based geolocation tracking.
- **System Control**:
  - Input Blocking (Mouse/Keyboard).
  - Blue Screen (BSOD) trigger.
  - Text-to-Speech & Audio Playback.
  - Wallpaper changer.

#### **Server**
- **Persistence**: SQLite database for device inventory and audit logs.
- **Reliability**: Heartbeat mechanism, auto-reconnect logic, and connection health monitoring.
- **Monitoring**: HTTP `/health` and `/metrics` endpoints.

#### **Discord Bot**
- **Interactive GUI**: Rich Embeds, Paginated Lists, and Interactive Buttons.
- **40+ Commands**: Comprehensive control via Discord slash commands.
- **Security**: Role-based permissions and channel locking.

### 🛠 Improvements
- **Performance**: Optimized WebSocket message handling for lower latency.
- **Stability**: Robust error handling and automatic recovery for all components.
- **Documentation**: Comprehensive HTML manual with search and dark mode.

---
## [v2.0] - Legacy
- Basic remote shell.
- Simple file transfer.
## [v3.5]
   - 65 New Premium Themes
   - 