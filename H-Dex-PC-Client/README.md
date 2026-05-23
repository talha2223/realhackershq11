# H-Dex Transparent PC Monitor

A Python-based system monitor client that connects to the Real Hackers HQ Command Center.

## Features
- **Real-time Telemetry:** Reports CPU and RAM usage every 5 seconds.
- **Remote Commands:** Supports `message`, `beep`, and `info` commands from the web dashboard.
- **Transparent & Removable:** Logs all actions to the console and can be stopped with `Ctrl+C`.

## Setup

1.  **Install Python 3.8+**
2.  **Install Dependencies:**
    ```bash
    pip install psutil requests websockets
    ```
3.  **Configure:**
    Open `client.py` and ensure `BASE_URL` and `WS_URL` point to your Hugging Face Space.
4.  **Run:**
    ```bash
    python client.py
    ```

## How it works
1.  **Handshake:** The client sends a POST request to `/api/v1/pairing/code` to register and get a `deviceToken`.
2.  **Command Channel:** It opens a WebSocket connection to `/ws` and identifies itself using `device.hello`.
3.  **Telemetry:** It uses `psutil` to collect system stats and sends them via `device.event`.
4.  **Commands:** It listens for `server.command` messages and sends back `device.result` after execution.

## Removal
Simply close the terminal or press `Ctrl+C`. No files are modified outside of this directory.

#sealth spyware like adex
need imprvent init
fix it