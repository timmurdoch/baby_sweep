const Database = require('better-sqlite3');
const path = require('path');
require('dotenv').config();

function initializeDatabase() {
  const db = new Database(path.join(__dirname, 'babysweep.db'));
  
  // Create settings table
  db.exec(`
    CREATE TABLE IF NOT EXISTS settings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      key TEXT UNIQUE NOT NULL,
      value TEXT NOT NULL
    )
  `);
  
  // Create guesses table
  db.exec(`
    CREATE TABLE IF NOT EXISTS guesses (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT,
      gender TEXT NOT NULL,
      birth_date TEXT NOT NULL,
      birth_time TEXT NOT NULL,
      weight_lbs INTEGER NOT NULL,
      weight_oz INTEGER NOT NULL,
      weight_kg REAL NOT NULL,
      amount_paid REAL DEFAULT 10.0,
      is_block_guess INTEGER DEFAULT 0,
      time_blocks TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  // Add columns for block guesses if they don't exist (for existing databases)
  try {
    db.exec(`ALTER TABLE guesses ADD COLUMN is_block_guess INTEGER DEFAULT 0`);
  } catch (err) {
    // Column already exists, ignore error
  }

  try {
    db.exec(`ALTER TABLE guesses ADD COLUMN time_blocks TEXT`);
  } catch (err) {
    // Column already exists, ignore error
  }
  
  // Create sessions table for authentication
  db.exec(`
    CREATE TABLE IF NOT EXISTS sessions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_token TEXT UNIQUE NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      expires_at DATETIME NOT NULL
    )
  `);
  
  // Insert default settings if they don't exist
  const insertSetting = db.prepare('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)');

  insertSetting.run('app_password', process.env.APP_PASSWORD || 'babysweep2025');
  insertSetting.run('due_date', process.env.DUE_DATE || '2025-12-31');
  insertSetting.run('welcome_text', process.env.WELCOME_TEXT || 'Welcome to our Baby Sweep! Guess the gender, birth date, time, and weight of our little one.');
  insertSetting.run('time_block_minutes', process.env.TIME_BLOCK_MINUTES || '30');
  insertSetting.run('max_block_selection_minutes', process.env.MAX_BLOCK_SELECTION_MINUTES || '60');
  insertSetting.run('include_surprise_gender', process.env.INCLUDE_SURPRISE_GENDER || 'true');
  insertSetting.run('allow_duplicates', process.env.ALLOW_DUPLICATES || 'true');
  insertSetting.run('primary_color', process.env.PRIMARY_COLOR || '#3b82f6');
  
  console.log('Database initialized successfully!');
  db.close();
}

module.exports = initializeDatabase;

if (require.main === module) {
  initializeDatabase();
}
