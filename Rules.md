# Rules — AI Boundaries & Guidelines

## Libraries to Use

| Component | Approved Libraries |
|-----------|-------------------|
| A-Dex Backend | express, helmet, cors, morgan, multer, ws, zod, nodemailer, dotenv, node:sqlite |
| A-Dex Bot | discord.js, axios, ws |
| H-Dex Server | FastAPI, uvicorn, websockets, sqlite3, psutil |
| H-Dex Bot | discord.py, websockets, requests |
| Website | React, Vite, TypeScript, firebase/auth, react-router-dom, leaflet, framer-motion, axios |
| Open-Claw | FastAPI, huggingface_hub |

## Libraries to Avoid

- **No ORMs** (Prisma, Sequelize, SQLAlchemy) — use raw SQL with parameterized queries
- **No MongoDB/PostgreSQL** — SQLite is the standard for all servers
- **No Next.js** — the website is a plain Vite SPA
- **No heavy UI frameworks** (Material UI, Ant Design) — keep the cyberpunk aesthetic with custom CSS
- **No JWT libraries** — the project uses static tokens, HMAC signatures, and Firebase Auth
- **No bcrypt/argon2** — device auth uses random tokens, not password hashing (except H-Dex admin dashboard)

## Security Rules (Mandatory)

1. **Never hardcode secrets** in source code. All secrets must come from environment variables.
2. **Always validate input** with Zod (Node) or manual checks (Python) before processing.
3. **Use timing-safe comparison** for all token/secret checks (`crypto.timingSafeEqual` or `hmac.compare_digest`).
4. **Parameterized SQL only** — never concatenate user input into SQL strings.
5. **No CORS wildcard** in production — restrict to known origins via `CORS_ORIGINS` env var.
6. **Rate limit** all unauthenticated endpoints.
7. **Audit log** every mutation (create, update, delete) with actor attribution.
8. **Set max limits** on pagination — never allow `LIMIT 999999`.
9. **Sanitize filenames** — strip non-alphanumeric characters from user-provided filenames.
10. **Expire sensitive tokens** — pairing codes (5 min), commands (90s), media (24h).

## Error Handling Rules

- All API errors return `{ error: 'ERROR_CODE' }` — no stack traces in production.
- Use consistent HTTP status codes: 400 (bad input), 401 (auth required), 403 (forbidden), 404 (not found), 429 (rate limited), 500 (server error).
- Log full error details server-side; return sanitized messages to clients.
- Never expose internal paths, database schema, or stack traces in error responses.

## Code Style Rules

| Component | Convention |
|-----------|-----------|
| A-Dex Backend | CommonJS (`require`), 2-space indent, semicolons, `camelCase` variables |
| A-Dex Bot (JS) | CommonJS, discord.js patterns |
| H-Dex Server | Python 3.11+, snake_case, async/await |
| Website | TypeScript, functional components, hooks, 2-space indent |
| SQL | UPPERCASE keywords, snake_case columns, parameterized queries |

## What the AI Should Do

- Follow existing code patterns — look at neighboring files before writing new code.
- Use the existing `store.js` pattern for database access (centralized SQL in store functions).
- Add Zod validation schemas for every new API endpoint.
- Add audit logging for every new mutation endpoint.
- Run lint/typecheck commands after making changes.
- Check `package.json` / `requirements.txt` before adding new dependencies.

## What the AI Should NOT Do

- Do not refactor working code without an explicit request.
- Do not add unnecessary comments — code should be self-documenting.
- Do not commit secrets, tokens, or API keys.
- Do not change the database schema without discussing the migration strategy.
- Do not add new dependencies unless absolutely necessary and already in the ecosystem.
- Do not suppress TypeScript errors with `@ts-ignore` — fix the root cause.
- Do not use `any` type in TypeScript — use proper typing.
