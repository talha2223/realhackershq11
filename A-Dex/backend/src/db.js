const fs = require('fs');
const path = require('path');
const { DatabaseSync } = require('node:sqlite');
const { config } = require('./config');

let db;

const MIGRATIONS = [
  {
    version: 1,
    name: 'init',
    up() {
      const schemaPath = path.join(__dirname, '..', 'migrations', 'init.sql');
      const schema = fs.readFileSync(schemaPath, 'utf8');
      db.exec(schema);
    },
  },
  {
    version: 2,
    name: 'add_metadata_json',
    up() {
      db.exec('ALTER TABLE devices ADD COLUMN metadata_json TEXT;');
    },
  },
];

function initDb() {
  if (db) {
    return db;
  }

  // Open SQLite database in WAL mode for better concurrent read/write behavior.
  db = new DatabaseSync(config.dbPath);
  db.exec('PRAGMA journal_mode = WAL;');
  db.exec('PRAGMA foreign_keys = ON;');

  // Migration tracking table
  db.exec(`
    CREATE TABLE IF NOT EXISTS _migrations (
      version INTEGER PRIMARY KEY,
      name TEXT NOT NULL,
      applied_at INTEGER NOT NULL
    );
  `);

  // Apply pending migrations in order
  const applied = db.prepare('SELECT version FROM _migrations').all().map((r) => r.version);
  for (const migration of MIGRATIONS) {
    if (applied.includes(migration.version)) {
      continue;
    }
    db.exec('BEGIN TRANSACTION;');
    try {
      migration.up();
      db.prepare('INSERT INTO _migrations (version, name, applied_at) VALUES (?, ?, ?)')
        .run(migration.version, migration.name, Date.now());
      db.exec('COMMIT;');
    } catch (err) {
      db.exec('ROLLBACK;');
      console.error(`Migration ${migration.version} (${migration.name}) failed:`, err);
      throw err;
    }
  }

  return db;
}

function getDb() {
  if (!db) {
    return initDb();
  }
  return db;
}

module.exports = { initDb, getDb };
