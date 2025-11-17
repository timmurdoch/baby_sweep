import React, { useState, useEffect } from 'react';
import './index.css';
import CalendarView from './CalendarView';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001';

// Configuration from environment variables
const INCLUDE_SURPRISE_GENDER = process.env.REACT_APP_INCLUDE_SURPRISE_GENDER === 'true';
const TIME_BLOCK_MINUTES = parseInt(process.env.REACT_APP_TIME_BLOCK_MINUTES) || 30;
const MAX_BLOCK_SELECTION_MINUTES = parseInt(process.env.REACT_APP_MAX_BLOCK_SELECTION_MINUTES) || 60;

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [sessionToken, setSessionToken] = useState('');
  const [currentView, setCurrentView] = useState('form'); // 'form', 'calendar', or 'guesses'
  const [settings, setSettings] = useState({});
  const [guesses, setGuesses] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    gender: 'boy',
    birthDate: '',
    birthTime: '',
    weightUnit: 'lbs', // 'lbs' or 'kg'
    weightLbs: '',
    weightOz: '',
    weightKg: '',
    timeBlocks: [] // For block guesses from calendar
  });
  const [formError, setFormError] = useState('');
  const [formSuccess, setFormSuccess] = useState('');

  // Check for existing session on load
  useEffect(() => {
    const savedToken = localStorage.getItem('babysweep_token');
    if (savedToken) {
      verifySession(savedToken);
    }
  }, []);

  // Load settings when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      loadSettings();
      loadGuesses();
    }
  }, [isAuthenticated]);

  const verifySession = async (token) => {
    try {
      const response = await fetch(`${API_URL}/api/auth/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token })
      });
      const data = await response.json();
      
      if (data.valid) {
        setSessionToken(token);
        setIsAuthenticated(true);
      } else {
        localStorage.removeItem('babysweep_token');
      }
    } catch (err) {
      console.error('Session verification failed:', err);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setSessionToken(data.token);
        localStorage.setItem('babysweep_token', data.token);
        setIsAuthenticated(true);
      } else {
        setError('Invalid password. Please try again.');
      }
    } catch (err) {
      setError('Connection error. Please try again.');
      console.error('Login error:', err);
    }
  };

  const loadSettings = async () => {
    try {
      const response = await fetch(`${API_URL}/api/settings`);
      const data = await response.json();
      setSettings(data);
    } catch (err) {
      console.error('Failed to load settings:', err);
    }
  };

  const loadGuesses = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/guesses?token=${sessionToken}`);
      const data = await response.json();
      setGuesses(data);
    } catch (err) {
      console.error('Failed to load guesses:', err);
    }
    setLoading(false);
  };

  const generateTimeOptions = () => {
    const options = [];
    const intervalMinutes = parseInt(settings.time_block_minutes) || TIME_BLOCK_MINUTES;

    for (let hour = 0; hour < 24; hour++) {
      for (let minute = 0; minute < 60; minute += intervalMinutes) {
        const timeStr = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
        const displayTime = new Date(`2000-01-01T${timeStr}`).toLocaleTimeString('en-US', {
          hour: 'numeric',
          minute: '2-digit',
          hour12: true
        });
        options.push({ value: timeStr, label: displayTime });
      }
    }

    return options;
  };

  const handleFormChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setFormError('');
  };

  const convertWeight = async () => {
    try {
      let body = {};
      if (formData.weightUnit === 'lbs') {
        body = { lbs: parseInt(formData.weightLbs), oz: parseInt(formData.weightOz) };
      } else {
        body = { kg: parseFloat(formData.weightKg) };
      }
      
      const response = await fetch(`${API_URL}/api/convert/weight`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      
      const data = await response.json();
      
      if (formData.weightUnit === 'lbs') {
        setFormData(prev => ({ ...prev, weightKg: data.kg.toString() }));
      } else {
        setFormData(prev => ({ ...prev, weightLbs: data.lbs.toString(), weightOz: data.oz.toString() }));
      }
    } catch (err) {
      console.error('Weight conversion error:', err);
    }
  };

  useEffect(() => {
    if (formData.weightUnit === 'lbs' && formData.weightLbs && formData.weightOz) {
      convertWeight();
    } else if (formData.weightUnit === 'kg' && formData.weightKg) {
      convertWeight();
    }
  }, [formData.weightLbs, formData.weightOz, formData.weightKg]);

  // Handle calendar time slot selection
  const handleCalendarSelection = (selection) => {
    setFormData(prev => ({
      ...prev,
      birthDate: selection.date,
      birthTime: selection.times[0], // Set first time as default
      timeBlocks: selection.isBlock ? selection.times : []
    }));
    setCurrentView('form'); // Switch to form to complete the guess
  };

  const handleSubmitGuess = async (e) => {
    e.preventDefault();
    setFormError('');
    setFormSuccess('');
    
    // Validation
    if (!formData.name || !formData.birthDate || !formData.birthTime) {
      setFormError('Please fill in all required fields');
      return;
    }
    
    if (formData.weightUnit === 'lbs' && (!formData.weightLbs || !formData.weightOz)) {
      setFormError('Please enter weight in pounds and ounces');
      return;
    }
    
    if (formData.weightUnit === 'kg' && !formData.weightKg) {
      setFormError('Please enter weight in kilograms');
      return;
    }
    
    try {
      const payload = {
        token: sessionToken,
        name: formData.name,
        email: formData.email,
        gender: formData.gender,
        birthDate: formData.birthDate,
        birthTime: formData.birthTime
      };

      // Add time blocks if this is a block guess
      if (formData.timeBlocks && formData.timeBlocks.length > 0) {
        payload.timeBlocks = formData.timeBlocks;
      }

      if (formData.weightUnit === 'lbs') {
        payload.weightLbs = parseInt(formData.weightLbs);
        payload.weightOz = parseInt(formData.weightOz);
      } else {
        payload.weightKg = parseFloat(formData.weightKg);
      }
      
      const response = await fetch(`${API_URL}/api/guesses`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      const data = await response.json();
      
      if (data.success) {
        setFormSuccess('Your guess has been submitted successfully!');
        // Reset form
        setFormData({
          name: '',
          email: '',
          gender: 'boy',
          birthDate: '',
          birthTime: '',
          weightUnit: 'lbs',
          weightLbs: '',
          weightOz: '',
          weightKg: '',
          timeBlocks: []
        });
        // Reload guesses
        loadGuesses();
        // Switch to guesses view after a delay
        setTimeout(() => {
          setCurrentView('guesses');
          setFormSuccess('');
        }, 2000);
      } else {
        setFormError(data.message || 'Failed to submit guess');
      }
    } catch (err) {
      setFormError('Connection error. Please try again.');
      console.error('Submit guess error:', err);
    }
  };

  const formatWeight = (lbs, oz, kg) => {
    return `${lbs} lbs ${oz} oz (${kg} kg)`;
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { 
      weekday: 'short', 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const formatTime = (timeStr) => {
    const [hours, minutes] = timeStr.split(':');
    const date = new Date();
    date.setHours(parseInt(hours), parseInt(minutes));
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
  };

  // Login Screen
  if (!isAuthenticated) {
    return (
      <div className="container">
        <div className="header">
          <h1>🍼 Baby Sweep</h1>
          <p>Guess our baby's details!</p>
        </div>
        
        <div className="card" style={{ maxWidth: '400px', margin: '0 auto' }}>
          <h2 style={{ marginBottom: '1.5rem', textAlign: 'center' }}>Enter Password</h2>
          <form onSubmit={handleLogin}>
            <div className="input-group">
              <label className="label">Password</label>
              <input
                type="password"
                className="input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter access password"
              />
            </div>
            {error && <div className="error">{error}</div>}
            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }}>
              Access Baby Sweep
            </button>
          </form>
        </div>
      </div>
    );
  }

  // Main App
  return (
    <div className="container">
      <div className="header">
        <h1>🍼 Baby Sweep</h1>
        <p>{settings.welcome_text || 'Guess our baby\'s details!'}</p>
      </div>

      <div className="tabs">
        <button
          className={`tab ${currentView === 'form' ? 'active' : ''}`}
          onClick={() => setCurrentView('form')}
        >
          Make a Guess
        </button>
        <button
          className={`tab ${currentView === 'calendar' ? 'active' : ''}`}
          onClick={() => setCurrentView('calendar')}
        >
          📅 Calendar
        </button>
        <button
          className={`tab ${currentView === 'guesses' ? 'active' : ''}`}
          onClick={() => setCurrentView('guesses')}
        >
          All Guesses ({guesses.length})
        </button>
      </div>

      {currentView === 'form' && (
        <div className="card">
          <h2 style={{ marginBottom: '1.5rem' }}>Submit Your Guess</h2>
          <form onSubmit={handleSubmitGuess}>
            <div className="grid grid-2">
              <div className="input-group">
                <label className="label">Your Name *</label>
                <input
                  type="text"
                  className="input"
                  value={formData.name}
                  onChange={(e) => handleFormChange('name', e.target.value)}
                  placeholder="Enter your name"
                  required
                />
              </div>

              <div className="input-group">
                <label className="label">Email (optional)</label>
                <input
                  type="email"
                  className="input"
                  value={formData.email}
                  onChange={(e) => handleFormChange('email', e.target.value)}
                  placeholder="your@email.com"
                />
              </div>
            </div>

            <div className="input-group">
              <label className="label">Gender *</label>
              <div className="radio-group">
                <div className="radio-option">
                  <input
                    type="radio"
                    id="boy"
                    name="gender"
                    value="boy"
                    checked={formData.gender === 'boy'}
                    onChange={(e) => handleFormChange('gender', e.target.value)}
                  />
                  <label htmlFor="boy">Boy 👶</label>
                </div>
                <div className="radio-option">
                  <input
                    type="radio"
                    id="girl"
                    name="gender"
                    value="girl"
                    checked={formData.gender === 'girl'}
                    onChange={(e) => handleFormChange('gender', e.target.value)}
                  />
                  <label htmlFor="girl">Girl 👶</label>
                </div>
                {INCLUDE_SURPRISE_GENDER && (
                  <div className="radio-option">
                    <input
                      type="radio"
                      id="surprise"
                      name="gender"
                      value="surprise"
                      checked={formData.gender === 'surprise'}
                      onChange={(e) => handleFormChange('gender', e.target.value)}
                    />
                    <label htmlFor="surprise">Surprise! 🎉</label>
                  </div>
                )}
              </div>
            </div>

            <div className="grid grid-2">
              <div className="input-group">
                <label className="label">Birth Date *</label>
                <input
                  type="date"
                  className="input"
                  value={formData.birthDate}
                  onChange={(e) => handleFormChange('birthDate', e.target.value)}
                  min={new Date().toISOString().split('T')[0]}
                  max={settings.due_date || '2026-12-31'}
                  required
                />
              </div>

              <div className="input-group">
                <label className="label">Birth Time *</label>
                {formData.timeBlocks && formData.timeBlocks.length > 1 ? (
                  <div className="time-blocks-display">
                    <div className="info-box">
                      <strong>Block Guess:</strong> {formData.timeBlocks.length} time slots selected
                      <div style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}>
                        {formData.timeBlocks.map(time => formatTime(time)).join(', ')}
                      </div>
                      <button
                        type="button"
                        className="btn btn-secondary"
                        style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}
                        onClick={() => setFormData(prev => ({ ...prev, timeBlocks: [], birthTime: '' }))}
                      >
                        Clear Block Selection
                      </button>
                    </div>
                  </div>
                ) : (
                  <select
                    className="select"
                    value={formData.birthTime}
                    onChange={(e) => handleFormChange('birthTime', e.target.value)}
                    required
                  >
                    <option value="">Select time</option>
                    {generateTimeOptions().map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                )}
              </div>
            </div>

            {formData.timeBlocks && formData.timeBlocks.length > 1 && (
              <div className="info-box" style={{ marginBottom: '1rem' }}>
                <p><strong>💡 Tip:</strong> You've selected multiple time slots from the calendar. This creates a "block guess" covering {formData.timeBlocks.length} consecutive times.</p>
              </div>
            )}

            <div className="input-group">
              <label className="label">Birth Weight *</label>
              <div className="radio-group" style={{ marginBottom: '1rem' }}>
                <div className="radio-option">
                  <input
                    type="radio"
                    id="lbs"
                    name="weightUnit"
                    value="lbs"
                    checked={formData.weightUnit === 'lbs'}
                    onChange={(e) => handleFormChange('weightUnit', e.target.value)}
                  />
                  <label htmlFor="lbs">Pounds & Ounces</label>
                </div>
                <div className="radio-option">
                  <input
                    type="radio"
                    id="kg"
                    name="weightUnit"
                    value="kg"
                    checked={formData.weightUnit === 'kg'}
                    onChange={(e) => handleFormChange('weightUnit', e.target.value)}
                  />
                  <label htmlFor="kg">Kilograms</label>
                </div>
              </div>

              {formData.weightUnit === 'lbs' ? (
                <div className="weight-converter">
                  <div className="weight-converter-row">
                    <input
                      type="number"
                      className="weight-input-small"
                      value={formData.weightLbs}
                      onChange={(e) => handleFormChange('weightLbs', e.target.value)}
                      placeholder="lbs"
                      min="0"
                      max="20"
                      required
                    />
                    <span>lbs</span>
                    <input
                      type="number"
                      className="weight-input-small"
                      value={formData.weightOz}
                      onChange={(e) => handleFormChange('weightOz', e.target.value)}
                      placeholder="oz"
                      min="0"
                      max="15"
                      required
                    />
                    <span>oz</span>
                    {formData.weightKg && (
                      <span style={{ marginLeft: '1rem', color: '#6b7280' }}>
                        ≈ {formData.weightKg} kg
                      </span>
                    )}
                  </div>
                </div>
              ) : (
                <div className="weight-converter">
                  <div className="weight-converter-row">
                    <input
                      type="number"
                      step="0.01"
                      className="weight-input-small"
                      value={formData.weightKg}
                      onChange={(e) => handleFormChange('weightKg', e.target.value)}
                      placeholder="kg"
                      min="0"
                      max="10"
                      required
                    />
                    <span>kg</span>
                    {formData.weightLbs && (
                      <span style={{ marginLeft: '1rem', color: '#6b7280' }}>
                        ≈ {formData.weightLbs} lbs {formData.weightOz} oz
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>

            {formError && <div className="error">{formError}</div>}
            {formSuccess && <div className="success">{formSuccess}</div>}

            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1.5rem' }}>
              Submit Guess ($10)
            </button>
          </form>
        </div>
      )}

      {currentView === 'calendar' && (
        <CalendarView
          sessionToken={sessionToken}
          settings={settings}
          onSelectTimeSlots={handleCalendarSelection}
          maxBlockSelectionMinutes={MAX_BLOCK_SELECTION_MINUTES}
        />
      )}

      {currentView === 'guesses' && (
        <div>
          {loading ? (
            <div className="loading">Loading guesses...</div>
          ) : guesses.length === 0 ? (
            <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
              <p style={{ fontSize: '1.125rem', color: '#6b7280' }}>
                No guesses yet! Be the first to make a guess.
              </p>
              <button 
                className="btn btn-primary" 
                style={{ marginTop: '1rem' }}
                onClick={() => setCurrentView('form')}
              >
                Make a Guess
              </button>
            </div>
          ) : (
            <div className="grid grid-2">
              {guesses.map(guess => (
                <div key={guess.id} className="guess-card">
                  <h3>{guess.name}</h3>
                  <div className="guess-detail">
                    <span className="guess-label">Gender:</span>
                    <span className={`badge badge-${guess.gender}`}>
                      {guess.gender === 'boy' ? '👶 Boy' : guess.gender === 'girl' ? '👶 Girl' : '🎉 Surprise'}
                    </span>
                  </div>
                  <div className="guess-detail">
                    <span className="guess-label">Date:</span>
                    <span className="guess-value">{formatDate(guess.birth_date)}</span>
                  </div>
                  <div className="guess-detail">
                    <span className="guess-label">Time:</span>
                    <span className="guess-value">
                      {guess.is_block_guess && guess.time_blocks ? (
                        <div>
                          <strong>Block Guess ({JSON.parse(guess.time_blocks).length} slots):</strong>
                          <div style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>
                            {JSON.parse(guess.time_blocks).map(time => formatTime(time)).join(', ')}
                          </div>
                        </div>
                      ) : (
                        formatTime(guess.birth_time)
                      )}
                    </span>
                  </div>
                  <div className="guess-detail">
                    <span className="guess-label">Weight:</span>
                    <span className="guess-value">{formatWeight(guess.weight_lbs, guess.weight_oz, guess.weight_kg)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
