# Memory — AI Context & Progress Tracker

## Project State

**Last updated:** Phase 1 complete (security hardening)

## What Was Done (Phase 1)

### Security Fixes — A-Dex Backend

| Fix | File | What Changed |
|-----|------|-------------|
| Timing-safe bot token | `auth.js` | Added `safeCompare()` using `crypto.timingSafeEqual` for static token check |
| IDOR in guild admin | `auth.js` | Added `validatedGuildId`/`validatedDiscordUserId` on request; documented trust boundary |
| CORS restrictions | `server.js` | Added `CORS_ORIGINS` env var; no-origin-allowed mode when not configured |
| Helmet re-enabled | `server.js` | Enabled all headers except frameguard (HF iframe) and CSP (too restrictive for HF) |
| Secret validation | `config.js` | `requireSecret()` fails in production, generates ephemeral value in dev with warning |
| IDOR device events | `api.js` | Added guild admin check + `isDeviceInGuild()` verification |
| IDOR device results | `api.js` | Same guild-scoping as events endpoint |
| IDOR media download | `api.js` | Added guild admin check + command ownership chain verification |
| Owner bypass fix | `api.js` | Removed `hq-guild` spoofing; only `ownerDiscordUserId` gets all devices |
| Pairing rate limit | `api.js` | 10 requests per minute per IP on `POST /pairing/code` |
| Global rate limit | `server.js` | 120 requests per minute per IP across all endpoints |
| Request ID tracking | `server.js` | UUID assigned to every request for tracing in logs/errors |
| Pagination caps | `api.js` | Intel: 200, logs: 500, commands: 200 max |
| Store helper | `store.js` | Added `isDeviceInGuild()` method for device-guild membership checks |

### Code Quality — A-Dex Backend

| Improvement | File |
|------------|------|
| 404 handler for unmatched routes | `server.js` |
| `morgan('combined')` with health skip | `server.js` |
| Structured error logging with request ID | `server.js` |

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Keep SQLite | No migration overhead, single-file deployment, WAL mode handles concurrency |
| No JWT | Static tokens + HMAC is simpler and sufficient for this architecture |
| Timing-safe comparison everywhere | Prevents side-channel attacks on token brute-force |
| Guild-scoping on device endpoints | Prevents cross-guild data leakage (IDOR) |
| Rate limiting in-process | Single-server deployment; Redis would be overkill |
| No token expiry on device tokens | Devices are long-lived; rotation on re-registration is sufficient |

## Known Remaining Issues

| Issue | Severity | Component |
|-------|----------|-----------|
| H-Dex file manager has no auth | CRITICAL | H-Dex HF Server |
| H-Dex `/dl` has no auth | CRITICAL | H-Dex HF Server |
| Dashboard token in query params | CRITICAL | H-Dex HF Server |
| Hardcoded password `nela001` | CRITICAL | H-Dex Bot |
| SSL verification disabled | HIGH | H-Dex Bot |
| Website hardcoded admin creds | CRITICAL | Website AuthContext |
| Open-Claw has no auth | HIGH | Open-Claw |

## File Locations Quick Reference

| What | Path |
|------|------|
| A-Dex auth middleware | `A-Dex/backend/src/services/auth.js` |
| A-Dex API routes | `A-Dex/backend/src/routes/api.js` |
| A-Dex data layer | `A-Dex/backend/src/services/store.js` |
| A-Dex WebSocket hub | `A-Dex/backend/src/services/realtimeHub.js` |
| A-Dex config | `A-Dex/backend/src/config.js` |
| A-Dex server entry | `A-Dex/backend/src/server.js` |
| A-Dex DB schema | `A-Dex/backend/migrations/init.sql` |
| H-Dex HF server | `H-Dex/H-Dex-Final-HF-Server/app.py` |
| H-Dex standalone | `H-Dex/H-dex Server/server.py` |
| H-Dex bot | `H-Dex/H-Dex Bot/bot.py` |
| Website auth | `website/src/components/AuthContext.tsx` |
| Website firebase | `website/src/firebase.ts` |

## Tech Stack Summary

- **A-Dex Backend:** Node.js 22 + Express 4 + SQLite (WAL) + WebSocket
- **A-Dex Bot:** discord.js (Node) / discord.py (Python)
- **A-Dex Android:** Kotlin + OkHttp + Room
- **H-Dex Server:** Python 3.11 + FastAPI + SQLite + websockets
- **H-Dex Bot:** discord.py + websockets
- **Open-Claw:** Python + FastAPI + HuggingFace InferenceClient
- **Website:** React 19 + TypeScript + Vite 8 + Firebase Auth + Leaflet
