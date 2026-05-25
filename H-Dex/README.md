# H-Dex ULTRA v3.0

![Version](https://img.shields.io/badge/version-3.0_ULTRA-indigo?style=for-the-badge) ![Status](https://img.shields.io/badge/status-ACTIVE-success?style=for-the-badge) ![License](https://img.shields.io/badge/license-EDUCATIONAL-orange?style=for-the-badge)

**H-Dex ULTRA** is a state-of-the-art Remote Administration Tool (PRO) designed for professional system administration and monitoring. Featuring a stunning glassmorphism dashboard, a powerful Python-based server, and a silent, feature-rich client agent.

---

## 🚀 Key Features

### 🖥️ Professional Dashboard
- **Modern UI**: Beautiful Indigo/Slate theme with responsive design and glass effects.
- **Real-time Monitoring**: Live CPU, RAM, and *new* **Bandwidth Monitoring**.
- **Device Management**: Grouping, Filtering, Multi-select, and Export (CSV/JSON).
- **Advanced Tools**: Script Editor, Macro Recorder, and Builder.

### 🕵️ Silent Client (Agent)
- **Stealth Mode**: Hides tracks, files, and processes.
- **Security**: **Geofencing** and **Anti-VM** protection to prevent unauthorized analysis.
- **Surveillance**:
  - Live Screen, Webcam, and Audio streaming.
  - Browser Data Extraction (Passwords, History).
  - WiFi Profile Extractor.
  - Network & Port Scanner.
  - Location Tracking.
- **Control**:
  - File Manager (Upload/Download/Execute).
  - Remote Shell & Registry Editor.
  - Process & Service Manager.
  - Input Blocking & BSOD Trigger.

### 🤖 Discord Bot Integration
- Control your fleet directly from Discord.
- 40+ Slash Commands.
- Interactive GUI with buttons and menus.
- Role-based security.

### ⚙️ Server Core
- **Reliable**: Heartbeat monitoring and auto-reconnection.
- **Persistent**: SQLite database storage for devices and audit logs.
- **Scalable**: Handles multiple concurrent connections efficiently.

---

## 📦 Installation & Setup

### 1. Requirements
- Python 3.8+
- Windows OS (Client/Dashboard)
- Hosting environment (Server)

### 2. Quick Start
#### Server
```bash
cd "H-dex Server"
pip install -r requirements.txt
python server.py
# Server runs on port 8765
```

#### Dashboard
```bash
pip install -r requirements.txt
python admin_dashboard.py
# Login with default password/token if prompted
```

#### Bot
```bash
# Configure token in bot.py or config.json
python bot.py
```

### 3. Building a Client
1. Open the **Dashboard**.
2. Navigate to the **Builder** tab.
3. Enter your Server URI (e.g., `wss://your-server.com`).
4. Set a Client Tag and Icon.
5. Click **Build Executable**.

---

## 📚 Documentation
- [User Manual (HTML)](Use%20H-DEX.html) - Comprehensive interactive guide.
- [Changelog](CHANGELOG.md) - View latest updates in v3.0.
- [Security Policy](SECURITY.md) - Security features and best practices.

---

## ⚠️ Legal Disclaimer
**H-Dex is for EDUCATIONAL PURPOSES and AUTHORIZED ADMINISTRATION ONLY.**
The developer assumes **NO LIABILITY** for any misuse of this software. You are responsible for complying with all local, state, and federal laws. **Do not install this software on systems you do not own or have explicit permission to monitor.**

---
*Created by the H-Dex Team*