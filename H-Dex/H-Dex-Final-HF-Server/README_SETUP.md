# 🚀 H-Dex Ultimate Server for Hugging Face (2026)

This server is specifically designed to run on Hugging Face Spaces free tier. It is optimized for high traffic, low latency, and 24/7 reliability.

## 📋 Features
- **High Concurrency**: Built on `FastAPI` and `uvicorn` with `uvloop` for maximum speed.
- **Auto-Health Check**: Includes a built-in monitoring page at the root URL.
- **Persistent Heartbeats**: Configured to stay awake as long as 1 client is active.
- **Encryption Ready**: Supports `wss://` out of the box.

## 🛠️ Step-by-Step Setup
1.  **Create a New Space**:
    - Go to [Hugging Face Spaces](https://huggingface.co/spaces).
    - Click **"Create new Space"**.
    - **Space Name**: Give it a name (e.g., `my-hdex-hub`).
    - **SDK**: Select **"Docker"**.
    - **Template**: Select **"Blank"**.
    - **Visibility**: Public (recommended for ease) or Private.

2.  **Upload the Files**:
    - Upload all files from the `H-Dex-Final-HF-Server` folder:
        - `app.py`
        - `Dockerfile`
        - `requirements.txt`

3.  **Set Secret Token (Recommended)**:
    - Go to your Space **Settings** -> **Variables and secrets**.
    - Add a new **Secret**.
    - **Name**: `DASHBOARD_TOKEN`
    - **Value**: Your preferred admin password (default is `hdex_admin_2026`).

4.  **Connect Your Client**:
    - Your server URL will look like: `wss://yourname-spacename.hf.space/ws`
    - (e.g., `wss://john-my-hdex-hub.hf.space/ws`)

## 🖥️ Monitoring
Open your Space link in a browser (the normal `https://...` link). You will see a professional dashboard showing:
- Real-time Client Count
- RAM & CPU Usage
- Server Uptime
