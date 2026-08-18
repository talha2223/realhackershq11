# Phases — Development Roadmap

## Phase 1 — Security Hardening ✅

**Status:** Complete

### A-Dex Backend
- [x] Fix timing-safe comparison for bot static token (`auth.js`)
- [x] Add `safeCompare()` utility using `crypto.timingSafeEqual`
- [x] Remove IDOR in `requireGuildAdmin` — document trust boundary
- [x] Add `validatedGuildId` / `validatedDiscordUserId` to request object
- [x] Add CORS restrictions via `CORS_ORIGINS` env var
- [x] Re-enable Helmet security headers (except frameguard for HF iframe)
- [x] Remove weak default secrets (`dev-secret-change-me`) — fail in production
- [x] Add `requireSecret()` helper with ephemeral fallback in dev only
- [x] Add guild-scoping to `GET /devices/:id/events`
- [x] Add guild-scoping to `GET /devices/:id/commands/results`
- [x] Add guild-scoping to `GET /media/:mediaId`
- [x] Fix `GET /devices` owner bypass — remove `hq-guild` spoofing
- [x] Add per-IP rate limiter on `POST /pairing/code` (10 req/min)
- [x] Add global rate limiter (120 req/min per IP)
- [x] Add request ID middleware for tracing
- [x] Add `isDeviceInGuild()` store method for ownership checks
- [x] Cap pagination limits on intel/logs/commands endpoints
- [x] Switch from `morgan('tiny')` to `morgan('combined')` with health endpoint skip
- [x] Add 404 handler for unmatched routes

## Phase 2 — H-Dex Security Fixes

**Status:** Pending

- [ ] Add auth to `/fm/list`, `/fm/search`, `/fm/download` endpoints (CRITICAL)
- [ ] Add auth to `/dl/{payload_name}` endpoint (CRITICAL)
- [ ] Move dashboard token from query parameter to Authorization header
- [ ] Add constant-time token comparison (`hmac.compare_digest`)
- [ ] Remove hardcoded password `nela001` from H-Dex bot
- [ ] Add device registration authentication
- [ ] Add rate limiting to all HTTP endpoints
- [ ] Add input sanitization for filesystem paths in file manager
- [ ] Enable SSL certificate verification in H-Dex bot

## Phase 3 — Website Security Fixes

**Status:** Pending

- [ ] Remove hardcoded admin credentials fallback from `AuthContext.tsx`
- [ ] Require `VITE_HQ_ADMIN_EMAIL` and `VITE_HQ_ADMIN_PASSWORD` env vars
- [ ] Move Firebase config to environment variables
- [ ] Add session timeout and auto-logout
- [ ] Add CSRF protection

## Phase 4 — Auth & Authorization Hardening

**Status:** Pending

- [ ] Add device token expiry and rotation mechanism
- [ ] Implement token blacklist for revocation
- [ ] Add per-guild rate limiting
- [ ] Add brute-force protection on Discord bot commands
- [ ] Add IP-based device tracking for anomaly detection

## Phase 5 — Open-Claw Security

**Status:** Pending

- [ ] Add API key authentication to `/api/ask`
- [ ] Add rate limiting on AI inference calls
- [ ] Add input validation and prompt injection protection

## Phase 6 — Testing & CI

**Status:** Pending

- [ ] Write integration tests for all API endpoints
- [ ] Add security regression tests for fixed vulnerabilities
- [ ] Set up GitHub Actions CI pipeline
- [ ] Add lint and typecheck to CI

## Phase 7 — Documentation & Deployment

**Status:** Pending

- [x] Create PRD.md
- [x] Create Architecture.md
- [x] Create Rules.md
- [x] Create Phases.md
- [x] Create Design.md
- [x] Create Memory.md
- [ ] Add API documentation (OpenAPI/Swagger)
- [ ] Document deployment steps for each component
- [ ] Add security policy and responsible disclosure guidelines
