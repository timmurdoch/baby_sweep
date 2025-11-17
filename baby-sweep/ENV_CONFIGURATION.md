# Environment Configuration Guide

This guide explains all environment variables available in the Baby Sweep application and how to configure them.

## Quick Start

1. **Backend Configuration:**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your preferred values
   ```

2. **Frontend Configuration:**
   ```bash
   cd frontend
   cp .env.example .env
   # Edit .env with your preferred values
   npm run build  # Rebuild after changes
   ```

---

## Backend Environment Variables

Location: `backend/.env`

### Server Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `3001` | Port number for the backend server |
| `NODE_ENV` | `production` | Node environment (`production` or `development`) |

### Application Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_PASSWORD` | `babysweep2025` | Password for accessing the admin panel and viewing all guesses |
| `DUE_DATE` | `2025-12-31` | Baby's due date in YYYY-MM-DD format. Users cannot guess beyond this date. |
| `WELCOME_TEXT` | Welcome message | Custom welcome message displayed on the main form |

### Time Block Settings

| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `TIME_BLOCK_MINUTES` | `30` | `15`, `30`, `60` | Time interval in minutes for available time slots |
| `MAX_BLOCK_SELECTION_MINUTES` | `60` | Any positive integer | Maximum duration in minutes that users can select for block guesses |

**Examples for MAX_BLOCK_SELECTION_MINUTES:**
- `60` = 1 hour maximum (2 slots of 30 min each)
- `120` = 2 hours maximum (4 slots of 30 min each)
- `180` = 3 hours maximum (6 slots of 30 min each)

### Gender Options

| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `INCLUDE_SURPRISE_GENDER` | `true` | `true`, `false` | Whether to include the "Surprise" option alongside "Boy" and "Girl" |

### Other Settings

| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `ALLOW_DUPLICATES` | `true` | `true`, `false` | Allow multiple guesses for the same date/time combination |
| `PRIMARY_COLOR` | `#3b82f6` | Any hex color | Primary theme color for the UI |

---

## Frontend Environment Variables

Location: `frontend/.env`

**Important:** All React environment variables MUST be prefixed with `REACT_APP_`

### API Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `REACT_APP_API_URL` | empty | Backend API URL. Leave empty for relative URLs (production). Use `http://localhost:3001` for development. |

### UI Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `REACT_APP_INCLUDE_SURPRISE_GENDER` | `true` | Show/hide "Surprise" gender option. Should match backend setting. |
| `REACT_APP_TIME_BLOCK_MINUTES` | `30` | Time interval for calendar slots. Should match backend setting. |
| `REACT_APP_MAX_BLOCK_SELECTION_MINUTES` | `60` | Maximum block selection duration. Should match backend setting. |

---

## Configuration Examples

### Example 1: 15-Minute Intervals, 1-Hour Maximum

**Backend (.env):**
```env
TIME_BLOCK_MINUTES=15
MAX_BLOCK_SELECTION_MINUTES=60
```

**Frontend (.env):**
```env
REACT_APP_TIME_BLOCK_MINUTES=15
REACT_APP_MAX_BLOCK_SELECTION_MINUTES=60
```

**Result:** Users can select time in 15-minute increments (e.g., 2:00 PM, 2:15 PM, 2:30 PM, 2:45 PM) up to a maximum of 4 consecutive slots (1 hour total).

### Example 2: 30-Minute Intervals, 2-Hour Maximum

**Backend (.env):**
```env
TIME_BLOCK_MINUTES=30
MAX_BLOCK_SELECTION_MINUTES=120
```

**Frontend (.env):**
```env
REACT_APP_TIME_BLOCK_MINUTES=30
REACT_APP_MAX_BLOCK_SELECTION_MINUTES=120
```

**Result:** Users can select time in 30-minute increments (e.g., 2:00 PM, 2:30 PM, 3:00 PM) up to a maximum of 4 consecutive slots (2 hours total).

### Example 3: Boy/Girl Only (No Surprise Option)

**Backend (.env):**
```env
INCLUDE_SURPRISE_GENDER=false
```

**Frontend (.env):**
```env
REACT_APP_INCLUDE_SURPRISE_GENDER=false
```

**Result:** Gender selection will only show "Boy" and "Girl" options.

### Example 4: Custom Due Date and Password

**Backend (.env):**
```env
APP_PASSWORD=mySecurePassword2025
DUE_DATE=2025-06-15
```

**Result:** Admin panel requires the custom password, and guesses are limited to June 15, 2025.

---

## Important Notes

### Frontend Environment Variables

1. **Build Time vs Runtime:** React environment variables are embedded at **build time**, not runtime. You must rebuild the frontend after changing any `REACT_APP_` variables:
   ```bash
   cd frontend
   npm run build
   ```

2. **Consistency:** Ensure `TIME_BLOCK_MINUTES`, `MAX_BLOCK_SELECTION_MINUTES`, and `INCLUDE_SURPRISE_GENDER` match between frontend and backend configurations.

3. **Prefix Required:** All React environment variables MUST start with `REACT_APP_` or they will be ignored.

### Backend Environment Variables

1. **Database Initialization:** Environment variables are used to set default values in the database during initialization. If you change them after the database is created, you'll need to either:
   - Delete `backend/babysweep.db` and restart (all data will be lost)
   - Or manually update the settings table in the database

2. **Password Security:** For production deployments, use a strong password and keep the `.env` file secure. Never commit `.env` files to version control.

### Docker Deployment

If using Docker, you can pass environment variables in `docker-compose.yml`:

```yaml
services:
  baby-sweep:
    environment:
      - APP_PASSWORD=mySecurePassword
      - DUE_DATE=2025-06-15
      - TIME_BLOCK_MINUTES=30
      - MAX_BLOCK_SELECTION_MINUTES=120
      - INCLUDE_SURPRISE_GENDER=true
```

---

## Troubleshooting

### Changes Not Appearing

**Problem:** Changed frontend `.env` but nothing changed in the application.

**Solution:** Remember to rebuild the frontend after changing `REACT_APP_` variables:
```bash
cd frontend
npm run build
```

### Mismatched Settings

**Problem:** Calendar shows different time intervals than the form.

**Solution:** Ensure `TIME_BLOCK_MINUTES` matches in both backend and frontend `.env` files.

### Surprise Option Still Showing

**Problem:** Set `INCLUDE_SURPRISE_GENDER=false` but "Surprise" option still appears.

**Solution:**
1. Ensure both backend and frontend `.env` files have `INCLUDE_SURPRISE_GENDER=false`
2. Rebuild the frontend: `npm run build`
3. Restart the backend server

### Password Not Working

**Problem:** Changed `APP_PASSWORD` but old password still works.

**Solution:** The password is stored in the database during initialization. Either:
1. Delete `backend/babysweep.db` and restart (loses all data)
2. Or update the database directly using an SQLite client

---

## Additional Configuration

### Custom Welcome Message

You can customize the welcome text with line breaks:

```env
WELCOME_TEXT=Welcome to our Baby Sweep!\n\nGuess when our little one will arrive and win prizes!\n\nGood luck!
```

### Custom Theme Color

Change the primary color to match your preferences:

```env
PRIMARY_COLOR=#ec4899  # Pink theme
PRIMARY_COLOR=#10b981  # Green theme
PRIMARY_COLOR=#8b5cf6  # Purple theme
```

---

## Support

For issues or questions:
- Check the `.env.example` files for reference
- Ensure all variables are spelled correctly
- Verify that frontend variables have the `REACT_APP_` prefix
- Remember to rebuild the frontend after changes
