# H-Dex Transparent PC Monitor (Pro)

A Python-based system monitor client that connects to the Real Hackers HQ Command Center.

## 🔥 New Features
- **Advanced Telemetry:** Reports CPU, RAM, Disk Usage, Battery Status, and Uptime.
- **Stealth & Persistence:** Caches `deviceToken` to avoid re-pairing after restart.
- **Remote Commands:** 
  - `shell`: Run invisible shell commands and get output back.
  - `screenshot`: Capture the remote machine's screen invisibly.
  - `clipboard`: Read or write to the PC's clipboard.
  - `lock`: Instantly lock the workstation.
  - `open_url`: Open a link in the default browser.
  - `message`: Display a native Windows alert popup.
  - `ls`/`dir`: Browse computer files.
  - `shutdown`: Trigger remote shutdown.

## 🛠️ Setup

1.  **Install Python 3.8+**
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run with Python (Console mode):**
    ```bash
    python client.py
    ```
    **Run Hidden (Stealth mode - Windows):**
    ```bash
    pythonw client.py
    ```
    *(To stop it in stealth mode, kill it via Task Manager)*

## How it works
1.  **Handshake:** The client connects to `/api/v1/pairing/code` to get a `deviceToken`.
2.  **Persistence:** The token is saved to `.device_token` locally so it stays paired.
3.  **Telemetry:** Collects stats using `psutil` and streams them over WSS.
4.  **Commands:** Listens to WebSocket messages and hooks into OS-level APIs (`ctypes`, `subprocess`, `mss`) to execute commands securely.