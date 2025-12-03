# Baby Sweep - Project Recreation Prompt

## Project Overview

Create a full-stack web application called "Baby Sweep" - a digital baby pool platform where friends and family can submit guesses about a baby's birth details (gender, date, time, and weight). The application should be simple enough for non-technical users while being production-ready and fully self-contained.

## Technology Stack Requirements

### Frontend
- React 18.2.0
- Custom CSS (no CSS frameworks like Bootstrap or Tailwind)
- React Big Calendar for calendar visualization
- Moment.js for date/time handling
- Mobile-first responsive design

### Backend
- Node.js 18+ with Express 4.18
- SQLite database using better-sqlite3 (no external database server)
- bcrypt for password hashing
- Session-based authentication with 24-hour tokens
- CORS enabled for frontend communication
- dotenv for environment configuration

### Deployment
- Docker support with multi-stage builds
- Docker Compose for orchestration
- Alternative systemd service configuration
- Nginx reverse proxy configuration
- Designed to run on minimal hardware (512MB RAM)

## Core Features (Phase 1 - MVP)

### 1. Authentication System
- Single password for all users (no individual accounts needed)
- POST /api/auth/login endpoint - accepts password, returns session token
- POST /api/auth/verify endpoint - validates session tokens
- Session tokens valid for 24 hours
- Tokens stored in localStorage for persistence
- All guess-related endpoints require valid authentication

### 2. Guess Submission Form
Users should be able to submit guesses with the following fields:
- **Name** (required, text input)
- **Email** (required, email input)
- **Gender** (required, radio buttons: Boy, Girl, Surprise)
  - Configurable to hide "Surprise" option via environment variable
- **Birth Date** (required, date picker)
  - Should not allow dates past the configured due date
- **Birth Time** (required, dropdown in configurable intervals)
  - Support 15, 30, or 60-minute time blocks
  - Generate time options dynamically based on TIME_BLOCK_MINUTES setting
- **Weight** (required, dual input system):
  - Imperial: Pounds (number) and Ounces (0-15)
  - Metric: Kilograms (decimal)
  - Real-time bidirectional conversion between units
  - Both values stored in database

### 3. Block Guess Feature
- Allow users to select multiple consecutive time slots for a single guess
- Calendar integration: clicking time slots in calendar view selects them for the form
- Visual feedback showing selected time range
- Configurable maximum block duration (default: 1 hour)
- Store block selections as JSON array in database
- Higher cost for block guesses (future pricing feature)

### 4. Weight Conversion API
- POST /api/convert/weight endpoint
- Accept either imperial (lbs, oz) or metric (kg)
- Return both formats in response
- Conversion logic:
  - kg = (lbs × 453.592 + oz × 28.3495) / 1000
  - lbs = floor(kg × 1000 / 453.592)
  - oz = round((kg × 1000 % 453.592) / 28.3495)

### 5. View All Guesses
Display all submitted guesses in a responsive card grid:
- Show name, email, gender (color-coded badge)
- Display birth date and time
- Show weight in both imperial and metric
- Show submission timestamp
- Color coding:
  - Blue for Boy
  - Pink for Girl
  - Purple for Surprise
- Indicate if it's a block guess with time range

### 6. Calendar Visualization
Interactive calendar using react-big-calendar:
- Show all guesses as colored events on calendar
- Color-code by gender (blue/pink/purple)
- Support month, week, and day views
- **Interactive Mode**:
  - Click empty time slots to select for block guesses
  - Visual selection feedback
  - Selected times populate the form
  - Support clicking and dragging for range selection
- **View Mode**:
  - Click existing guess events to show full details in modal
  - Modal displays all guess information
  - Close button to dismiss
- Display guess name and time on calendar events
- Handle multiple guesses in same time slot (stacking/overlap)

### 7. Navigation
Three main views with navigation tabs:
- "Make a Guess" - Submission form with calendar at bottom
- "Calendar View" - Full interactive calendar
- "All Guesses" - Card grid of all submissions
- Highlight active tab
- Mobile-friendly navigation (collapsible on small screens)

## Database Schema

Create SQLite database with three tables:

### settings table
```sql
- id: INTEGER PRIMARY KEY AUTOINCREMENT
- key: TEXT UNIQUE NOT NULL
- value: TEXT
```

Default settings to create:
- app_password: hashed password for access
- due_date: maximum allowable guess date
- welcome_text: greeting message for login page
- time_block_minutes: interval for time selections (15, 30, or 60)
- max_block_selection_minutes: maximum duration for block guesses
- include_surprise_gender: boolean (1 or 0)
- allow_duplicates: boolean for duplicate date/time combos
- primary_color: theme color hex code

### guesses table
```sql
- id: INTEGER PRIMARY KEY AUTOINCREMENT
- name: TEXT NOT NULL
- email: TEXT NOT NULL
- gender: TEXT NOT NULL (Boy, Girl, or Surprise)
- birth_date: TEXT NOT NULL (YYYY-MM-DD format)
- birth_time: TEXT NOT NULL (HH:MM format)
- weight_lbs: INTEGER
- weight_oz: INTEGER
- weight_kg: REAL
- amount_paid: REAL DEFAULT 0
- is_block_guess: INTEGER DEFAULT 0 (boolean)
- time_blocks: TEXT (JSON array of time strings)
- created_at: TEXT DEFAULT CURRENT_TIMESTAMP
```

### sessions table
```sql
- id: INTEGER PRIMARY KEY AUTOINCREMENT
- session_token: TEXT UNIQUE NOT NULL
- created_at: TEXT DEFAULT CURRENT_TIMESTAMP
- expires_at: TEXT NOT NULL
```

## API Endpoints Specification

### Authentication Routes
- **POST /api/auth/login**
  - Body: { password: string }
  - Validates against hashed app_password in settings
  - Generates random session token (crypto.randomBytes)
  - Stores session with 24-hour expiration
  - Returns: { token: string }
  - Status: 200 on success, 401 on invalid password

- **POST /api/auth/verify**
  - Body: { token: string }
  - Checks if token exists and not expired
  - Returns: { valid: boolean }
  - Status: 200 always (boolean in response)

### Settings Routes
- **GET /api/settings**
  - Requires authentication (check Authorization header)
  - Returns all settings as key-value object
  - Status: 200 on success, 401 if not authenticated

- **GET /api/settings/welcome**
  - Public endpoint (no auth required)
  - Returns just the welcome_text value
  - Status: 200

### Guess Routes
- **POST /api/guesses**
  - Requires authentication
  - Body: { name, email, gender, birth_date, birth_time, weight_lbs, weight_oz, weight_kg, is_block_guess, time_blocks }
  - Validate all required fields
  - Check birth_date <= due_date
  - If allow_duplicates=false, check for existing guess with same date/time
  - Insert into database
  - Returns: { id: number, message: string }
  - Status: 201 on success, 400 on validation error, 409 on duplicate

- **GET /api/guesses**
  - Requires authentication
  - Returns array of all guesses
  - Order by created_at DESC
  - Status: 200

- **GET /api/guesses/by-date**
  - Requires authentication
  - Aggregates guesses by birth_date
  - Returns: { [date]: { total: number, boy: number, girl: number, surprise: number } }
  - Status: 200

- **GET /api/guesses/calendar**
  - Requires authentication
  - Formats guesses for react-big-calendar
  - For block guesses, creates separate event for each time slot
  - Returns array of: { id, title, start, end, gender, guessData }
  - Status: 200

### Utility Routes
- **POST /api/convert/weight**
  - Body: { lbs?, oz?, kg? }
  - Converts between imperial and metric
  - Returns: { lbs, oz, kg }
  - Status: 200

- **GET /api/health**
  - Simple health check
  - Returns: { status: 'ok', timestamp: ISO_string }
  - Status: 200

## Configuration System

### Backend Environment Variables (.env)
```
PORT=3001
APP_PASSWORD=babysweep2025
DUE_DATE=2025-12-31
TIME_BLOCK_MINUTES=30
MAX_BLOCK_SELECTION_MINUTES=60
INCLUDE_SURPRISE_GENDER=true
ALLOW_DUPLICATES=false
PRIMARY_COLOR=#4A90E2
WELCOME_TEXT=Welcome to our Baby Sweep! Make your guess about when our little one will arrive.
```

### Frontend Environment Variables (.env)
All variables must be prefixed with REACT_APP_:
```
REACT_APP_API_URL=http://localhost:3001
REACT_APP_DUE_DATE=2025-12-31
REACT_APP_TIME_BLOCK_MINUTES=30
REACT_APP_MAX_BLOCK_SELECTION_MINUTES=60
REACT_APP_INCLUDE_SURPRISE_GENDER=true
REACT_APP_PRIMARY_COLOR=#4A90E2
```

Provide .env.example files for both frontend and backend with these defaults.

## UI/UX Requirements

### Design Principles
- Clean, modern aesthetic with subtle gradients
- Accessible color contrasts (WCAG AA compliant)
- Clear visual hierarchy
- Consistent spacing and padding
- Mobile-first responsive design

### Color Scheme
- Primary: Configurable (default #4A90E2 - soft blue)
- Boy: Blue badges/calendar events
- Girl: Pink badges/calendar events
- Surprise: Purple badges/calendar events
- Background: Light gradient (white to very light blue/pink)
- Cards: White with subtle shadow
- Buttons: Primary color with hover states

### Responsive Breakpoints
- Mobile: < 768px
  - Single column layout
  - Stacked form fields
  - Collapsible navigation
  - Smaller calendar views
- Tablet: 768px - 1024px
  - Two column guess grid
  - Full calendar visibility
- Desktop: > 1024px
  - Three column guess grid
  - Optimal calendar size
  - Spacious form layout

### Form Validation
- Real-time validation feedback
- Red borders on invalid fields
- Error messages below fields
- Disable submit until valid
- Success message after submission
- Clear form after successful submit

### Calendar Features
- Default to month view
- Toolbar with view options (month/week/day)
- Navigation arrows for previous/next
- Today button to return to current date
- Event tooltips on hover (desktop)
- Touch-friendly event selection (mobile)

### Loading States
- Loading spinner during API calls
- Disabled buttons during submission
- Graceful error handling with user-friendly messages

## Project Structure

```
baby-sweep/
├── backend/
│   ├── server.js              # Main Express server
│   ├── database.js            # SQLite initialization
│   ├── package.json
│   ├── .env.example
│   └── .gitignore
│
├── frontend/
│   ├── public/
│   │   └── index.html         # HTML template
│   ├── src/
│   │   ├── App.js             # Main component
│   │   ├── CalendarView.js    # Calendar component
│   │   ├── index.js           # React entry point
│   │   ├── index.css          # All styling
│   │   └── reportWebVitals.js
│   ├── package.json
│   ├── .env.example
│   └── .gitignore
│
├── Dockerfile                  # Multi-stage build
├── docker-compose.yml          # Container orchestration
├── nginx.conf                  # Reverse proxy config
├── baby-sweep.service          # Systemd service
├── .gitignore
└── README.md
```

## Component Architecture

### App.js (Main Component)
State to manage:
- isAuthenticated: boolean
- sessionToken: string
- currentView: 'form' | 'calendar' | 'all-guesses'
- formData: object with all form fields
- guesses: array
- settings: object
- selectedTimeSlots: array for block guesses
- showModal: boolean
- selectedGuess: object for modal display

Functions needed:
- handleLogin(password)
- handleLogout()
- verifySession()
- fetchSettings()
- fetchGuesses()
- handleFormChange(field, value)
- handleWeightChange(type, value) with conversion
- handleSubmit()
- handleCalendarSlotClick(slot)
- handleGuessEventClick(guess)
- switchView(view)

Effects:
- On mount: verify session, fetch settings/guesses
- On weight change: trigger conversion
- Store token in localStorage

### CalendarView.js
Props:
- guesses: array
- onSlotSelect: function (optional - for interactive mode)
- onEventClick: function
- selectedSlots: array (optional)
- readOnly: boolean

Features:
- Configure react-big-calendar with moment localizer
- Custom event styling based on gender
- Slot selection logic for block guesses
- Event component with guess details
- Multiple view support

### Styling (index.css)
Include styles for:
- Global resets and fonts
- Container and layout classes
- Navigation tabs
- Form controls and validation states
- Guess cards with gender badges
- Calendar customization
- Modal overlay and content
- Buttons and interactive elements
- Loading states
- Responsive media queries

## Docker Configuration

### Dockerfile (Multi-stage Build)
Stage 1 - Frontend Build:
- Use node:18-alpine
- Copy frontend files
- npm install
- npm run build
- Output to /app/frontend/build

Stage 2 - Production:
- Use node:18-alpine
- Copy backend files
- Copy frontend build from stage 1
- npm install --production
- Expose port 3001
- Run node server.js

### docker-compose.yml
- Service: baby-sweep
- Build from Dockerfile
- Port mapping: 3001:3001
- Volume: ./data:/app/backend/data (database persistence)
- Environment variables from .env file
- Restart policy: unless-stopped

### nginx.conf
- Upstream to localhost:3001
- Location / : proxy to backend
- WebSocket support headers
- Gzip compression
- Security headers

## Systemd Service (Alternative Deployment)

baby-sweep.service:
- Run as specific user
- WorkingDirectory: /path/to/backend
- ExecStart: node server.js
- Restart on failure
- Environment file support

## Documentation Requirements

Create the following documentation files:

### README.md
- Project overview and purpose
- Technology stack
- Quick start guide
- Development setup
- Deployment options (Docker vs systemd)
- Environment variable reference
- API documentation summary

### QUICKSTART.md
- 5-minute setup instructions
- Prerequisites check
- Clone and configure steps
- Docker deployment (recommended)
- Access instructions
- First login steps

### DEPLOYMENT-CHECKLIST.md
- Pre-deployment verification
- Configuration checklist
- Build verification
- Database initialization
- Security checklist (change default password!)
- SSL setup with Cloudflare
- Testing checklist
- Monitoring setup

### ENV_CONFIGURATION.md
- Detailed explanation of each environment variable
- Impact of changing settings
- Common configurations
- Troubleshooting config issues

### TROUBLESHOOTING.md
- Common issues and solutions
- Database connection problems
- CORS errors
- Build failures
- Port conflicts
- Session/authentication issues
- Calendar display problems

### VISUAL-PREVIEW.md
- Text-based mockups of UI layout
- Component descriptions
- Color scheme reference
- Responsive behavior notes

## Implementation Priorities

### Phase 1 (MVP - Current Scope)
1. Basic authentication system
2. Guess submission form with all fields
3. Weight conversion functionality
4. View all guesses in card layout
5. Basic calendar visualization
6. Block guess support
7. Mobile responsive design
8. Docker deployment
9. Complete documentation

### Phase 2 (Future Enhancements - Document but Don't Implement)
Create PHASE2.md with roadmap:
- Admin panel with separate authentication
- Dashboard with statistics and charts
- Winner calculation algorithm
- Pricing tiers and payment tracking
- Enhanced exports (CSV, Excel, PDF)
- Email notifications
- Theme customization UI
- Multiple guesses per person
- Social sharing features

Create admin-panel.jsx as a template/mockup but don't integrate it yet.

## Testing Requirements

### Manual Testing Checklist
- Authentication flow (login, session persistence, logout)
- Form submission with all field combinations
- Weight conversion accuracy
- Duplicate guess prevention (when enabled)
- Block guess creation and display
- Calendar interaction (clicking slots and events)
- View switching
- Mobile responsiveness
- Cross-browser compatibility (Chrome, Firefox, Safari)
- Database persistence after restart

### Edge Cases to Handle
- Password with special characters
- Past due date selection attempt
- Invalid weight values (negative, too large)
- Network errors during submission
- Expired session handling
- Empty database state
- Overlapping calendar events
- Very long names or emails
- Timezone considerations

## Security Considerations

- Hash password using bcrypt with salt rounds = 10
- Use crypto.randomBytes for session tokens (minimum 32 bytes)
- Validate all user inputs server-side
- Sanitize database inputs (use parameterized queries)
- Set secure CORS policy (don't use * in production)
- Implement rate limiting on login endpoint (future enhancement)
- Regular session cleanup (delete expired sessions)
- Don't expose sensitive errors to client
- Secure session tokens in localStorage (consider httpOnly cookies as enhancement)

## Performance Optimization

- Minimize database queries (cache settings)
- Use indexes on frequently queried fields (session_token, created_at)
- Lazy load guess images if added in future
- Debounce weight conversion API calls
- Implement pagination for large guess lists (future)
- Optimize calendar rendering for many events
- Gzip compression on nginx
- CDN for static assets (Cloudflare)

## Accessibility Requirements

- Semantic HTML elements
- Proper ARIA labels on form fields
- Keyboard navigation support
- Focus indicators on interactive elements
- Sufficient color contrast (4.5:1 minimum)
- Screen reader friendly error messages
- Alt text for any images
- Responsive text sizing

## Success Criteria

The project is complete when:
1. User can log in with password
2. User can submit a guess with all fields
3. Weight converts automatically between units
4. All guesses display in card grid
5. Calendar shows all guesses color-coded by gender
6. Block guesses can be created by clicking calendar
7. Clicking guess events shows details in modal
8. Works on mobile, tablet, and desktop
9. Deploys successfully via Docker
10. Database persists between restarts
11. All documentation is complete and accurate
12. Session authentication works reliably
13. Configuration via environment variables works

## Final Notes

- Prioritize simplicity over complexity
- Make it family-friendly and easy to use
- No user accounts needed - single password keeps it simple
- Self-contained deployment (no external services)
- Comprehensive documentation for non-technical users
- Clean, maintainable code with comments
- Graceful error handling throughout
- Consider future Phase 2 features in architecture but don't implement yet
