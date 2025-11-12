# Baby Sweep - Phase 2 Features Roadmap

## 🎯 MVP (Phase 1) - COMPLETED ✅

- [x] Password-protected access
- [x] Guess submission form (gender, date, time, weight)
- [x] Real-time weight conversion (lbs/oz ⟷ kg)
- [x] View all guesses in grid layout
- [x] Mobile-responsive design
- [x] 30-minute time blocks (configurable in DB)
- [x] SQLite database with guesses and settings
- [x] RESTful API
- [x] Docker deployment option
- [x] Nginx reverse proxy configuration

## 🚀 Phase 2 Features - TO BE IMPLEMENTED

### 1. Admin Panel 🔐
**Priority: HIGH**

Features:
- Separate admin login with different password
- Dashboard with statistics:
  - Total guesses
  - Total amount collected
  - Most popular dates/times
  - Gender distribution
- Settings management UI:
  - Change due date
  - Edit welcome text
  - Toggle time block intervals (15/30/60 minutes)
  - Enable/disable duplicate guesses
  - Configure pricing tiers
  - Customize color scheme
- User management:
  - View all participants
  - Edit/delete guesses
  - Export data

Implementation Notes:
- Add admin_password to settings table
- Create AdminPanel component in React
- Add admin routes to backend API
- Implement admin authentication middleware

### 2. Calendar Visualization 📅
**Priority: HIGH**

Features:
- Interactive calendar showing all guess dates
- Heat map showing popular dates
- Click on date to see all guesses for that day
- Visual indicators for:
  - Number of guesses per date
  - Most popular time slots
  - Gender distribution per date

Implementation Notes:
- Install date picker library (react-calendar or similar)
- Create CalendarView component
- Add API endpoint for guess aggregation by date
- Implement date filtering in frontend

### 3. Configurable Pricing Tiers 💰
**Priority: MEDIUM**

Features:
- Multiple pricing tiers:
  - Example: $10 for 1 guess, $40 for 5, $70 for 10
  - Admin can set custom tier structure
- Track amount paid per guess
- Payment tracking (not processing - just recording)
- Total collected summary

Implementation Notes:
- Create pricing_tiers table
- Add tier selection in guess form
- Update guess submission to track pricing tier used
- Add pricing configuration in admin panel

### 4. Entry Rules Management ⚙️
**Priority: MEDIUM**

Features:
- Toggle to allow/disallow duplicate combinations
- Validation on submission:
  - Check if exact combination exists
  - Show similar guesses to user
  - Option to proceed anyway or modify
- "Reserved" indicator on taken combinations

Implementation Notes:
- Add uniqueness check in API
- Create combination validation function
- Update frontend to show availability
- Add visual feedback for taken combinations

### 5. Enhanced Export Functionality 📊
**Priority: MEDIUM**

Features:
- Export formats:
  - CSV
  - Excel
  - PDF report
- Customizable export fields
- Include statistics in export
- Email export option

Implementation Notes:
- Install export libraries (xlsx, pdfkit)
- Create export endpoints
- Add export buttons in admin panel
- Generate formatted reports

### 6. Birth Results & Winner Calculation 🏆
**Priority: HIGH**

Features:
- Admin form to enter actual birth details:
  - Gender
  - Date
  - Time
  - Weight
- Automatic winner calculation:
  - Exact match wins
  - Closest match if no exact winner
  - Multiple winner handling
- Winner announcement:
  - Display on site
  - Highlight winning guess(es)
  - Show leaderboard of closest guesses
- Scoring system:
  - Points for each correct field
  - Weighted scoring (date more important than time, etc.)

Implementation Notes:
- Create birth_results table
- Add winner calculation algorithm
- Create results display component
- Add confetti or celebration animation for winners

### 7. Theme Customization 🎨
**Priority: LOW**

Features:
- Preset color themes:
  - Boy (blues)
  - Girl (pinks)
  - Neutral (yellows/greens)
  - Custom
- Customizable:
  - Primary color
  - Secondary color
  - Background
  - Font family
- Real-time preview in admin panel

Implementation Notes:
- Create theme configuration in settings
- Add CSS variables for dynamic theming
- Create theme switcher in admin panel
- Add theme preview component

### 8. Multiple Guesses Per Person 👥
**Priority: MEDIUM**

Features:
- Track multiple guesses from same person
- Show user's previous guesses
- "My Guesses" view
- Email notifications for their guesses
- Prevent duplicate submissions from same email

Implementation Notes:
- Add email validation
- Create user profile/history view
- Add "view my guesses" feature
- Implement email-based filtering

### 9. Email Notifications 📧
**Priority: LOW**

Features:
- Send confirmation email when guess submitted
- Notify participants when baby arrives
- Winner announcement email
- Admin notification for new guesses

Implementation Notes:
- Integrate email service (SendGrid, Mailgun, or SMTP)
- Create email templates
- Add email configuration to settings
- Implement email queue for reliability

### 10. Social Sharing 📱
**Priority: LOW**

Features:
- Share button to invite others
- Generate unique referral links
- Show who invited whom
- Social media preview cards

Implementation Notes:
- Add Open Graph meta tags
- Create shareable link generator
- Add social sharing buttons
- Track referrals (optional)

### 11. Mobile App (Future) 📱
**Priority: VERY LOW**

Features:
- Native iOS/Android apps
- Push notifications
- Offline support
- Camera integration for sharing baby photos

Implementation Notes:
- Use React Native or Flutter
- Share API with web version
- Implement push notification service

## 📅 Suggested Implementation Order

**Sprint 1 (Week 1):**
1. Admin Panel (basic)
2. Birth Results & Winner Calculation
3. Enhanced Export (CSV/Excel)

**Sprint 2 (Week 2):**
4. Calendar Visualization
5. Configurable Pricing Tiers
6. Entry Rules Management

**Sprint 3 (Week 3):**
7. Multiple Guesses Per Person
8. Theme Customization
9. Admin Panel (advanced features)

**Future Enhancements:**
10. Email Notifications
11. Social Sharing
12. Mobile App

## 🛠️ Development Setup for Phase 2

When you're ready to start Phase 2:

1. Create a new branch:
```bash
git checkout -b feature/admin-panel
```

2. Install additional dependencies:
```bash
# Backend
cd backend
npm install --save xlsx pdfkit nodemailer

# Frontend
cd ../frontend
npm install --save react-calendar chart.js react-chartjs-2
```

3. Run database migrations (add new tables):
```sql
-- Add to database.js or create migration script
CREATE TABLE IF NOT EXISTS pricing_tiers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  num_guesses INTEGER NOT NULL,
  price REAL NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS birth_results (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  gender TEXT,
  birth_date TEXT,
  birth_time TEXT,
  weight_lbs INTEGER,
  weight_oz INTEGER,
  weight_kg REAL,
  announced_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 💡 Feature Request?

Have ideas for additional features? Add them to this document!

Some ideas from brainstorming:
- Photo upload when baby arrives
- Guess the baby name (separate pool)
- Baby milestone predictions
- Virtual baby shower integration
- Gift registry integration
- Video message submission
- Live countdown to due date
- Weather prediction for birth day
- Astrological sign display
