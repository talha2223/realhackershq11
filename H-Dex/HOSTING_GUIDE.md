# 🚀 Hosting H-DEX Server on Railway (Best Method)

Railway is excellent for hosting Python WebSockets because it supports long-lived connections.

## Option 1: Quick Deploy via GitHub (Recommended)
1. **Push your code** to a GitHub repository (private or public).
2. Sign up at [Railway.app](https://railway.app/).
3. Click **New Project** -> **Deploy from GitHub**.
4. Select your repository.
5. Railway will automatically detect the `Procfile` and `requirements.txt` I have included in the root folder.
6. **Done!** Your server will be online.

## Option 2: Railway CLI
1. Install [Railway CLI](https://docs.railway.app/guides/cli).
2. Open terminal in this folder.
3. Run `railway login`.
4. Run `railway init`.
5. Run `railway up`.

## ⚙️ Configuration
In Railway Project Settings -> **Variables**, add:
- `DASHBOARD_TOKEN`: `hdex_admin_2026` (Or your custom token)

*Note: The server automatically listens on the `PORT` provided by Railway.*

## 🌐 Connecting your Dashboard & Clients
Once deployed, Railway provides a public domain (e.g., `web-production-xxxx.up.railway.app`).

**Use this URL in your internal settings:**
- **Protocol**: Use `wss://` (Secure WebSocket) instead of `ws://`.
- **Example**: `wss://web-production-xxxx.up.railway.app`

### 1. In Admin Dashboard:
Go to **Settings** -> **Server Configuration** -> **Server URL**.
Enter: `wss://your-railway-url.app`

### 2. In Client Builder:
When building a new client, enter the same `wss://` URL.
