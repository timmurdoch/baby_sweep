const Database = require('better-sqlite3');
const path = require('path');

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
  
  insertSetting.run('app_password', 'babysweep2025');
  insertSetting.run('due_date', '2025-12-31');
  insertSetting.run('welcome_text', 'Welcome to our Baby Sweep! Guess the gender, birth date, time, and weight of our little one.');
  insertSetting.run('time_block_minutes', '30');
  insertSetting.run('allow_duplicates', 'true');
  insertSetting.run('primary_color', '#3b82f6');
  
  console.log('Database initialized successfully!');
  db.close();
}

module.exports = initializeDatabase;

if (require.main === module) {
  initializeDatabase();
}
