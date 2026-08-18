const path = require('path');
const fs = require('fs');
const dotenv = require('dotenv');

// Load environment variables from backend/.env when present.
dotenv.config();

const baseDir = process.cwd();
const dataDir = path.join(baseDir, 'data');
const dbPath = process.env.DB_PATH ? path.resolve(baseDir, process.env.DB_PATH) : path.join(dataDir, 'adex.db');
const mediaDir = process.env.MEDIA_DIR ? path.resolve(baseDir, process.env.MEDIA_DIR) : path.join(dataDir, 'media');

// Ensure runtime directories exist before server startup.
fs.mkdirSync(path.dirname(dbPath), { recursive: true });
fs.mkdirSync(mediaDir, { recursive: true });

// ---------------------------------------------------------------------------
// Secret validation: in production the two critical secrets MUST be provided
// via environment variables. In development we generate random ephemeral
// values so the server can start without manual config, but we log a warning
// so the operator knows they need to set them before deploying.
// ---------------------------------------------------------------------------
function requireSecret(envName, fallbackPrefix) {
  const value = process.env[envName];
  if (value && value !== '' && !value.startsWith(fallbackPrefix)) {
    return value;
  }
  // Only fall back in non-production environments.
  if (process.env.NODE_ENV === 'production') {
    console.error(`FATAL: Environment variable ${envName} is required in production.`);
    process.exit(1);
  }
  const generated = `${fallbackPrefix}-${require('crypto').randomBytes(16).toString('hex')}`;
  console.warn(`WARNING: ${envName} not set — using ephemeral value. Set this before deploying.`);
  return generated;
}

const config = {
  host: process.env.HOST || '0.0.0.0',
  port: Number(process.env.PORT || 8080),
  dbPath,
  mediaDir,
  botHmacSecret: requireSecret('BOT_HMAC_SECRET', 'ephemeral-hmac'),
  botWsToken: requireSecret('BOT_WS_TOKEN', 'ephemeral-ws'),
  ownerDiscordUserId: process.env.OWNER_DISCORD_USER_ID || '',
  autoEnrollToken: process.env.AUTO_ENROLL_TOKEN || '',
  autoEnrollGuildId: process.env.AUTO_ENROLL_GUILD_ID || '',
  autoEnrollChannelId: process.env.AUTO_ENROLL_CHANNEL_ID || '',
  autoEnrollBindChannel: String(process.env.AUTO_ENROLL_BIND_CHANNEL || 'false').toLowerCase() === 'true',
  pairCodeTtlSeconds: Number(process.env.PAIR_CODE_TTL_SECONDS || 300),
  commandTimeoutSeconds: Number(process.env.COMMAND_TIMEOUT_SECONDS || 90),
  mediaRetentionHours: Number(process.env.MEDIA_RETENTION_HOURS || 24),
  maxUploadBytes: Number(process.env.MAX_UPLOAD_BYTES || 10 * 1024 * 1024),
  backendVersion: process.env.BACKEND_VERSION || '1.0.0',
  backendBuildTs: process.env.BACKEND_BUILD_TS || String(Date.now()),
};

if (process.env.NODE_ENV === 'production' && !config.autoEnrollToken) {
  console.warn('WARNING: AUTO_ENROLL_TOKEN is not set — auto-enrollment will be disabled.');
}

module.exports = { config };
