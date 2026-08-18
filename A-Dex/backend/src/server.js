const http = require('http');
const crypto = require('crypto');
const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const morgan = require('morgan');
const { config } = require('./config');
const { initDb } = require('./db');
const { createStore } = require('./services/store');
const { RealtimeHub } = require('./services/realtimeHub');
const { createBotAuthMiddleware, createDeviceAuthMiddleware, requireGuildAdmin } = require('./services/auth');
const { createApiRouter } = require('./routes/api');

// ---------------------------------------------------------------------------
// In-memory rate limiter: { ip -> [timestamp, ...] }
// Simple sliding window counter per IP. Resets on restart which is acceptable
// for a single-server deployment.
// ---------------------------------------------------------------------------
const RATE_LIMIT_WINDOW_MS = 60_000;
const RATE_LIMIT_MAX_REQUESTS = 120;
const rateLimitMap = new Map();

function rateLimiter(req, res, next) {
  const ip = req.ip || req.socket.remoteAddress || 'unknown';
  const now = Date.now();
  const timestamps = rateLimitMap.get(ip) || [];
  const recent = timestamps.filter((t) => now - t < RATE_LIMIT_WINDOW_MS);
  if (recent.length >= RATE_LIMIT_MAX_REQUESTS) {
    res.setHeader('Retry-After', Math.ceil(RATE_LIMIT_WINDOW_MS / 1000));
    return res.status(429).json({ error: 'RATE_LIMITED' });
  }
  recent.push(now);
  rateLimitMap.set(ip, recent);
  return next();
}

// Periodically prune stale entries so the map does not grow unbounded.
const pruneTimer = setInterval(() => {
  const now = Date.now();
  for (const [ip, timestamps] of rateLimitMap) {
    const recent = timestamps.filter((t) => now - t < RATE_LIMIT_WINDOW_MS);
    if (recent.length === 0) {
      rateLimitMap.delete(ip);
    } else {
      rateLimitMap.set(ip, recent);
    }
  }
}, RATE_LIMIT_WINDOW_MS * 2);
pruneTimer.unref();

function createApp() {
  const db = initDb();
  const store = createStore(db, config);

  const app = express();

  // Assign a unique request ID to every request for tracing.
  app.use((req, res, next) => {
    req.requestId = crypto.randomUUID();
    res.setHeader('X-Request-Id', req.requestId);
    next();
  });

  // Preserve raw JSON payload for HMAC verification before parsing mutates shape.
  app.use(express.json({
    limit: '2mb',
    verify: (req, _res, buf) => {
      req.rawBody = buf.toString('utf8');
    },
  }));

  // CORS: restrict to known origins in production, allow all in dev.
  const allowedOrigins = (process.env.CORS_ORIGINS || '')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);
  app.use(cors({
    origin: allowedOrigins.length > 0 ? (origin, cb) => {
      if (!origin || allowedOrigins.includes(origin)) {
        cb(null, true);
      } else {
        cb(new Error('CORS_NOT_ALLOWED'));
      }
    } : undefined,
    credentials: true,
    maxAge: 86400,
  }));

  // Security headers via Helmet.
  // Hugging Face loads the Space in an iframe so frameguard must stay off,
  // but all other protections are enabled.
  app.use(helmet({
    contentSecurityPolicy: false,
    frameguard: false,
    crossOriginEmbedderPolicy: false,
  }));

  app.use(morgan('combined', {
    skip: (req) => req.url === '/health' || req.url === '/api/v1/health',
  }));

  // Global rate limiter.
  app.use(rateLimiter);

  const server = http.createServer(app);
  const hub = new RealtimeHub(server, { store, config });

  const botAuth = createBotAuthMiddleware(config);
  const deviceAuth = createDeviceAuthMiddleware(store);
  const guildAdminAuth = requireGuildAdmin(store);

  app.use('/api/v1', createApiRouter({ store, hub, config, botAuth, deviceAuth, guildAdminAuth }));

  // Root route is useful for container platforms that probe the service URL.
  app.get('/', (_req, res) => {
    res.json({
      service: 'A-Dex backend',
      health: '/api/v1/health',
      ws: '/ws',
      ts: Date.now(),
    });
  });

  // 404 handler for unmatched routes.
  app.use((_req, res) => {
    res.status(404).json({ error: 'NOT_FOUND' });
  });

  // Last-resort error handler keeps response shape consistent.
  app.use((err, req, res, _next) => {
    // eslint-disable-next-line no-console
    console.error(`[${req.requestId || 'no-id'}] Unhandled error:`, err);
    res.status(500).json({ error: 'INTERNAL_SERVER_ERROR', requestId: req.requestId });
  });

  return { app, server, hub };
}

if (require.main === module) {
  const { server } = createApp();
  server.listen(config.port, config.host, () => {
    // eslint-disable-next-line no-console
    console.log(`A-Dex backend listening on ${config.host}:${config.port}`);
  });
}

module.exports = { createApp };
