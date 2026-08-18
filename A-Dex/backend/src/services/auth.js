const crypto = require('crypto');
const { computeBotSignature } = require('../utils/signature');

// Constant-time string comparison to prevent timing attacks on token brute-force.
function safeCompare(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string') {
    return false;
  }
  const bufA = Buffer.from(a, 'utf8');
  const bufB = Buffer.from(b, 'utf8');
  if (bufA.length !== bufB.length) {
    // Still do the comparison to avoid leaking length info.
    crypto.timingSafeEqual(bufA, Buffer.alloc(bufA.length));
    return false;
  }
  return crypto.timingSafeEqual(bufA, bufB);
}

// Bot auth uses signed requests with timestamp to prevent replay.
function createBotAuthMiddleware(config) {
  return function botAuth(req, res, next) {
    const botToken = req.header('x-adex-bot-token');
    if (botToken && config.botWsToken && safeCompare(botToken, config.botWsToken)) {
      return next();
    }

    const signature = req.header('x-adex-signature');
    const timestamp = req.header('x-adex-timestamp');

    if (!signature || !timestamp) {
      return res.status(401).json({ error: 'BOT_AUTH_HEADERS_MISSING' });
    }

    const ts = Number(timestamp);
    if (!Number.isFinite(ts)) {
      return res.status(401).json({ error: 'BOT_AUTH_TIMESTAMP_INVALID' });
    }

    const ageMs = Math.abs(Date.now() - ts);
    if (ageMs > 5 * 60 * 1000) {
      return res.status(401).json({ error: 'BOT_AUTH_TIMESTAMP_EXPIRED' });
    }

    const expected = computeBotSignature(config.botHmacSecret, timestamp, req.rawBody || '');
    const expectedBuffer = Buffer.from(expected);
    const signatureBuffer = Buffer.from(signature);

    if (expectedBuffer.length !== signatureBuffer.length || !crypto.timingSafeEqual(expectedBuffer, signatureBuffer)) {
      return res.status(401).json({ error: 'BOT_AUTH_SIGNATURE_INVALID' });
    }

    return next();
  };
}

// Device auth is a bearer token tied to a concrete device id.
function createDeviceAuthMiddleware(store) {
  return function deviceAuth(req, res, next) {
    const deviceId = req.header('x-device-id');
    const authorization = req.header('authorization') || '';
    const token = authorization.startsWith('Bearer ') ? authorization.slice('Bearer '.length) : null;

    if (!deviceId || !token) {
      return res.status(401).json({ error: 'DEVICE_AUTH_HEADERS_MISSING' });
    }

    if (!store.validateDeviceToken(deviceId, token)) {
      return res.status(401).json({ error: 'DEVICE_AUTH_INVALID' });
    }

    req.deviceId = deviceId;
    return next();
  };
}

// Guild admin check. The caller must provide guildId and discordUserId in the
// request body. The botAuth middleware above already verified that the request
// comes from a trusted bot, so we trust the bot's claimed identity.
// SECURITY: These values MUST come from the bot (server-side), never from a
// client-side user directly. The bot is responsible for passing the correct
// identity of the Discord user who invoked the command.
function requireGuildAdmin(store) {
  return function guildAdmin(req, res, next) {
    const guildId = req.body.guildId || req.query.guildId;
    const discordUserId = req.body.discordUserId || req.query.discordUserId || req.body.actorUserId || req.query.actorUserId;

    if (!guildId || !discordUserId) {
      return res.status(400).json({ error: 'GUILD_OR_USER_MISSING' });
    }

    if (!store.ensureGuildAdmin(guildId, discordUserId)) {
      return res.status(403).json({ error: 'DISCORD_USER_NOT_AUTHORIZED' });
    }

    // Attach validated values so downstream handlers never re-read from raw body.
    req.validatedGuildId = guildId;
    req.validatedDiscordUserId = discordUserId;

    return next();
  };
}

module.exports = {
  createBotAuthMiddleware,
  createDeviceAuthMiddleware,
  requireGuildAdmin,
};
