const express = require('express');
const cors = require('cors');
const Database = require('better-sqlite3');
const path = require('path');
const crypto = require('crypto');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3001;

// Initialize database
const db = new Database(path.join(__dirname, 'babysweep.db'));

// Middleware
app.use(cors());
app.use(express.json());

// Serve static files from React build
app.use(express.static(path.join(__dirname, 'public')));

// Helper function to generate session token
function generateSessionToken() {
  return crypto.randomBytes(32).toString('hex');
}

// Helper function to verify session
function verifySession(token) {
  const session = db.prepare('SELECT * FROM sessions WHERE session_token = ? AND expires_at > datetime("now")').get(token);
  return !!session;
}

// Helper function to convert lbs/oz to kg
function lbsOzToKg(lbs, oz) {
  const totalPounds = lbs + (oz / 16);
  return Math.round(totalPounds * 0.453592 * 100) / 100;
}

// Helper function to convert kg to lbs/oz
function kgToLbsOz(kg) {
  const totalPounds = kg / 0.453592;
  const lbs = Math.floor(totalPounds);
  const oz = Math.round((totalPounds - lbs) * 16);
  return { lbs, oz };
}

// ==================== AUTH ROUTES ====================

// Login endpoint
app.post('/api/auth/login', (req, res) => {
  const { password } = req.body;
  
  const appPassword = db.prepare('SELECT value FROM settings WHERE key = ?').get('app_password');
  
  if (password === appPassword.value) {
    const sessionToken = generateSessionToken();
    const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(); // 24 hours
    
    db.prepare('INSERT INTO sessions (session_token, expires_at) VALUES (?, ?)').run(sessionToken, expiresAt);
    
    res.json({ success: true, token: sessionToken });
  } else {
    res.status(401).json({ success: false, message: 'Invalid password' });
  }
});

// Verify session endpoint
app.post('/api/auth/verify', (req, res) => {
  const { token } = req.body;
  
  if (verifySession(token)) {
    res.json({ valid: true });
  } else {
    res.json({ valid: false });
  }
});

// ==================== SETTINGS ROUTES ====================

// Get settings
app.get('/api/settings', (req, res) => {
  const settings = {};
  const rows = db.prepare('SELECT key, value FROM settings').all();
  
  rows.forEach(row => {
    settings[row.key] = row.value;
  });
  
  res.json(settings);
});

// Get welcome text (public)
app.get('/api/settings/welcome', (req, res) => {
  const welcomeText = db.prepare('SELECT value FROM settings WHERE key = ?').get('welcome_text');
  res.json({ text: welcomeText ? welcomeText.value : '' });
});

// ==================== GUESS ROUTES ====================

// Submit a guess
app.post('/api/guesses', (req, res) => {
  const { token, name, email, gender, birthDate, birthTime, timeBlocks, weightLbs, weightOz, weightKg } = req.body;

  // Verify session
  if (!verifySession(token)) {
    return res.status(401).json({ success: false, message: 'Invalid session' });
  }

  // Determine if this is a block guess or single guess
  const isBlockGuess = timeBlocks && Array.isArray(timeBlocks) && timeBlocks.length > 0;
  const finalBirthTime = isBlockGuess ? timeBlocks[0] : birthTime; // Use first time block or single time

  // Validate required fields
  if (!name || !gender || !birthDate || (!birthTime && !isBlockGuess)) {
    return res.status(400).json({ success: false, message: 'Missing required fields' });
  }

  // Calculate weight in both systems
  let finalWeightKg, finalWeightLbs, finalWeightOz;

  if (weightKg !== undefined && weightKg !== null) {
    finalWeightKg = parseFloat(weightKg);
    const converted = kgToLbsOz(finalWeightKg);
    finalWeightLbs = converted.lbs;
    finalWeightOz = converted.oz;
  } else {
    finalWeightLbs = parseInt(weightLbs);
    finalWeightOz = parseInt(weightOz);
    finalWeightKg = lbsOzToKg(finalWeightLbs, finalWeightOz);
  }

  try {
    const stmt = db.prepare(`
      INSERT INTO guesses (name, email, gender, birth_date, birth_time, weight_lbs, weight_oz, weight_kg, is_block_guess, time_blocks)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    const result = stmt.run(
      name,
      email || null,
      gender,
      birthDate,
      finalBirthTime,
      finalWeightLbs,
      finalWeightOz,
      finalWeightKg,
      isBlockGuess ? 1 : 0,
      isBlockGuess ? JSON.stringify(timeBlocks) : null
    );

    res.json({ success: true, id: result.lastInsertRowid });
  } catch (error) {
    console.error('Error inserting guess:', error);
    res.status(500).json({ success: false, message: 'Failed to save guess' });
  }
});

// Get all guesses
app.get('/api/guesses', (req, res) => {
  const { token } = req.query;
  
  // Verify session
  if (!verifySession(token)) {
    return res.status(401).json({ success: false, message: 'Invalid session' });
  }
  
  try {
    const guesses = db.prepare('SELECT * FROM guesses ORDER BY created_at DESC').all();
    res.json(guesses);
  } catch (error) {
    console.error('Error fetching guesses:', error);
    res.status(500).json({ success: false, message: 'Failed to fetch guesses' });
  }
});

// Get guesses by date (for calendar view)
app.get('/api/guesses/by-date', (req, res) => {
  const { token } = req.query;

  // Verify session
  if (!verifySession(token)) {
    return res.status(401).json({ success: false, message: 'Invalid session' });
  }

  try {
    const guesses = db.prepare('SELECT birth_date, COUNT(*) as count FROM guesses GROUP BY birth_date').all();

    const dateMap = {};
    guesses.forEach(g => {
      dateMap[g.birth_date] = g.count;
    });

    res.json(dateMap);
  } catch (error) {
    console.error('Error fetching guesses by date:', error);
    res.status(500).json({ success: false, message: 'Failed to fetch guesses' });
  }
});

// Get guesses formatted for calendar display
app.get('/api/guesses/calendar', (req, res) => {
  const { token } = req.query;

  // Verify session
  if (!verifySession(token)) {
    return res.status(401).json({ success: false, message: 'Invalid session' });
  }

  try {
    const guesses = db.prepare('SELECT * FROM guesses ORDER BY birth_date, birth_time').all();

    // Transform guesses into calendar events
    const events = [];
    guesses.forEach(guess => {
      if (guess.is_block_guess && guess.time_blocks) {
        // For block guesses, create an event for each time block
        const timeBlocks = JSON.parse(guess.time_blocks);
        timeBlocks.forEach(time => {
          events.push({
            id: `${guess.id}-${time}`,
            guessId: guess.id,
            title: `${guess.name} - ${guess.gender}`,
            start: new Date(`${guess.birth_date}T${time}`),
            end: new Date(`${guess.birth_date}T${time}`),
            resource: guess
          });
        });
      } else {
        // For single guesses, create one event
        events.push({
          id: guess.id,
          guessId: guess.id,
          title: `${guess.name} - ${guess.gender}`,
          start: new Date(`${guess.birth_date}T${guess.birth_time}`),
          end: new Date(`${guess.birth_date}T${guess.birth_time}`),
          resource: guess
        });
      }
    });

    res.json(events);
  } catch (error) {
    console.error('Error fetching calendar guesses:', error);
    res.status(500).json({ success: false, message: 'Failed to fetch calendar guesses' });
  }
});

// ==================== UTILITY ROUTES ====================

// Weight conversion endpoint
app.post('/api/convert/weight', (req, res) => {
  const { lbs, oz, kg } = req.body;
  
  if (kg !== undefined && kg !== null) {
    const converted = kgToLbsOz(parseFloat(kg));
    res.json({ lbs: converted.lbs, oz: converted.oz });
  } else if (lbs !== undefined && oz !== undefined) {
    const convertedKg = lbsOzToKg(parseInt(lbs), parseInt(oz));
    res.json({ kg: convertedKg });
  } else {
    res.status(400).json({ error: 'Invalid input' });
  }
});

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Serve React app for all other routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start server
app.listen(PORT, () => {
  console.log(`Baby Sweep API running on port ${PORT}`);
});
