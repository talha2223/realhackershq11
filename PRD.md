# PRD — Real Hackers HQ

## Project Overview

Real Hackers HQ is a multi-platform remote administration and security testing framework consisting of three core components: **A-Dex** (Android), **H-Dex** (Windows), and a central **Website** dashboard. The system allows authorized security operators to manage, monitor, and interact with remote devices through Discord bots, WebSocket connections, and a web interface.

## Target Users

- Security researchers conducting authorized penetration tests
- Red team operators managing multi-device engagements
- System administrators performing remote device management
- Educational institutions teaching cybersecurity concepts

## Sub-Projects

### A-Dex (Android Remote Administration)

| Feature | Description |
|---------|-------------|
| Device Pairing | QR-code / code-based pairing with HMAC-signed device registration |
| 84+ Remote Commands | screenshot, location, SMS, call logs, contacts, files, camera, audio, app management, clipboard, WhatsApp, passwords |
| Discord Bot Control | Full command suite via Discord slash commands with embed-based UI |
| WebSocket Real-time | Persistent device connection with heartbeat, command queuing, and media upload |
| Guild Multi-tenancy | Discord guild-based device isolation with admin roles |
| Audit Logging | Every command, pairing, and admin action logged with timestamps |
| Media Pipeline | Upload screenshots/audio/video to server with auto-cleanup |
| Auto-enrollment | Token-based automatic device enrollment into guilds |

### H-Dex (Windows Remote Administration)

| Feature | Description |
|---------|-------------|
| Device Management | Register, monitor, ban/unban, tag, and organize devices |
| Data Harvesting | Browser passwords, cookies, Discord tokens, Telegram sessions, crypto wallets, WiFi keys, SSH keys, RDP credentials |
| Keylogger | Start/stop/dump keylog with date-range queries and batch sync |
| File Manager | Browse, search, and download files from remote devices |
| Live Monitoring | Clipboard, webcam snapshots, screen streaming, window tracking |
| Prank Suite | BSOD, matrix effect, mouse chaos, sound effects, input blocking |
| Advanced Tools | UAC bypass, USB spreading, Defender management, self-destruct |
| Discord Bot | Full control panel via Discord with category-based navigation |
| AI Agent (Open-Claw) | Llama-3/Mistral-powered natural language command generation |
| Pending Task Queue | Commands queued for offline devices, auto-executed on reconnect |

### Website (HQ Dashboard)

| Feature | Description |
|---------|-------------|
| Firebase Authentication | Email/password auth with persistent sessions |
| HQ Dashboard | Central control panel for A-Dex and H-Dex |
| Phishing Templates | Simulated login page templates for social engineering tests |
| Device Map | Leaflet-based geographic device visualization |
| Animated UI | Framer Motion transitions, CRT effects, glassmorphism |

## Security Requirements

| Requirement | Implementation |
|-------------|---------------|
| Authentication | HMAC-SHA256 signed requests with timestamp replay protection |
| Device Auth | 256-bit random bearer tokens with ownership verification |
| Authorization | Discord guild-based admin roles with owner override |
| Input Validation | Zod schemas on all API endpoints |
| Audit Trail | Immutable log of all mutations with actor attribution |
| Rate Limiting | Per-IP sliding window on sensitive endpoints |
| Timing Safety | Constant-time comparison for all secret/token checks |
| CORS | Origin-restricted in production |
| Security Headers | Helmet.js with CSP, HSTS, XSS protection |

## Deployment Targets

| Component | Platform | Port |
|-----------|----------|------|
| A-Dex Backend | Docker / HuggingFace Spaces | 8080 |
| A-Dex Discord Bot | Any Node.js host | N/A |
| H-Dex HF Server | HuggingFace Spaces | 7860 |
| H-Dex Standalone | Self-hosted VPS | 8765 |
| Open-Claw AI | HuggingFace Spaces | 7860 |
| Website | Firebase Hosting | 443 |

## Non-Goals

- Multi-user role system (current model: owner + guild admins only)
- Database migrations framework (SQLite schema is stable)
- GraphQL API (REST + WebSocket is sufficient)
- Mobile web app (separate native apps handle mobile)
