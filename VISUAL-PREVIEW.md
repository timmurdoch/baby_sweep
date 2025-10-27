# 🍼 Baby Sweep - Visual Preview

## What Your Application Looks Like

### 🔐 Login Screen

```
╔════════════════════════════════════════╗
║                                        ║
║        🍼 Baby Sweep                   ║
║     Guess our baby's details!          ║
║                                        ║
╠════════════════════════════════════════╣
║                                        ║
║      Enter Password                    ║
║                                        ║
║   Password: [________________]         ║
║                                        ║
║   [   Access Baby Sweep   ]            ║
║                                        ║
╚════════════════════════════════════════╝
```

**Features:**
- Clean, centered design
- Gradient blue/purple header
- Simple password field
- Full-width button

---

### 📝 Main Application - Make a Guess Tab

```
╔════════════════════════════════════════════════════════╗
║                                                        ║
║              🍼 Baby Sweep                             ║
║    Welcome to our Baby Sweep! Guess the gender,       ║
║    birth date, time, and weight of our little one.    ║
║                                                        ║
╠════════════════════════════════════════════════════════╣
║                                                        ║
║  [Make a Guess]  All Guesses (5)                      ║
║                                                        ║
╠════════════════════════════════════════════════════════╣
║                                                        ║
║  Submit Your Guess                                     ║
║                                                        ║
║  Your Name *          │  Email (optional)             ║
║  [John Smith____]     │  [john@email.com_]            ║
║                                                        ║
║  Gender *                                              ║
║  ○ Boy 👶  ○ Girl 👶  ○ Surprise! 🎉                  ║
║                                                        ║
║  Birth Date *         │  Birth Time *                 ║
║  [2025-12-25____]     │  [3:30 PM▼]                  ║
║                                                        ║
║  Birth Weight *                                        ║
║  ○ Pounds & Ounces  ○ Kilograms                       ║
║                                                        ║
║  ┌─────────────────────────────────┐                  ║
║  │ [7_] lbs  [8_] oz  ≈ 3.40 kg   │                  ║
║  └─────────────────────────────────┘                  ║
║                                                        ║
║  [      Submit Guess ($10)      ]                     ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
```

**Features:**
- Two-column layout (desktop) / stacked (mobile)
- Real-time weight conversion
- Radio button selection for gender and weight unit
- Dropdown for time selection (30-min intervals)
- Date picker with validation
- Clear visual hierarchy

---

### 👥 All Guesses Tab

```
╔════════════════════════════════════════════════════════╗
║                                                        ║
║              🍼 Baby Sweep                             ║
║    Welcome to our Baby Sweep! Guess the gender,       ║
║    birth date, time, and weight of our little one.    ║
║                                                        ║
╠════════════════════════════════════════════════════════╣
║                                                        ║
║  Make a Guess  [All Guesses (5)]                      ║
║                                                        ║
╠════════════════════════════════════════════════════════╣
║                                                        ║
║  ┌─────────────────────┐  ┌─────────────────────┐    ║
║  │ Sarah Johnson       │  │ Mike Chen           │    ║
║  │                     │  │                     │    ║
║  │ Gender:  👶 Girl    │  │ Gender:  👶 Boy     │    ║
║  │ Date:    Dec 25     │  │ Date:    Dec 24     │    ║
║  │ Time:    3:30 PM    │  │ Time:    11:00 AM   │    ║
║  │ Weight:  7 lbs 8 oz │  │ Weight:  8 lbs 2 oz │    ║
║  │         (3.40 kg)   │  │         (3.69 kg)   │    ║
║  └─────────────────────┘  └─────────────────────┘    ║
║                                                        ║
║  ┌─────────────────────┐  ┌─────────────────────┐    ║
║  │ Emma Williams       │  │ David Lee           │    ║
║  │                     │  │                     │    ║
║  │ Gender: 🎉 Surprise │  │ Gender:  👶 Boy     │    ║
║  │ Date:    Dec 26     │  │ Date:    Dec 23     │    ║
║  │ Time:    6:45 PM    │  │ Time:    2:15 AM    │    ║
║  │ Weight:  7 lbs 12oz │  │ Weight:  8 lbs 0 oz │    ║
║  │         (3.52 kg)   │  │         (3.63 kg)   │    ║
║  └─────────────────────┘  └─────────────────────┘    ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
```

**Features:**
- Grid layout (2 columns on desktop, 1 on mobile)
- Card-based design for each guess
- Color-coded gender badges (blue/pink/yellow)
- Clean typography and spacing
- Shows both weight systems
- Most recent guesses first

---

## 🎨 Design System

### Colors

**Primary Gradient:**
- Blue: #3b82f6
- Purple: #8b5cf6
- Used in header and buttons

**Gender Colors:**
- Boy: Light blue (#dbeafe) with dark blue text
- Girl: Light pink (#fce7f3) with dark pink text
- Surprise: Light yellow (#fef3c7) with brown text

**UI Colors:**
- Background: #f9fafb (light gray)
- Cards: #ffffff (white)
- Borders: #e5e7eb (light gray)
- Text: #111827 (dark gray)
- Secondary text: #6b7280 (medium gray)

### Typography

- **Headers:** 2rem (32px) on desktop, 1.5rem (24px) on mobile
- **Body:** 1rem (16px)
- **Labels:** 0.875rem (14px)
- **Font:** System fonts (San Francisco, Segoe UI, Roboto, etc.)

### Spacing

- Cards: 1.5rem (24px) padding
- Grid gap: 1rem (16px)
- Form fields: 1rem (16px) margin-bottom
- Container max-width: 1200px

---

## 📱 Mobile Experience

### Portrait (iPhone)

```
┌─────────────────────┐
│  🍼 Baby Sweep      │
│  Guess our baby's   │
│  details!           │
├─────────────────────┤
│                     │
│ [Make a Guess]      │
│ All Guesses (5)     │
│                     │
├─────────────────────┤
│                     │
│ Submit Your Guess   │
│                     │
│ Your Name *         │
│ [John Smith___]     │
│                     │
│ Email (optional)    │
│ [john@email.com]    │
│                     │
│ Gender *            │
│ ○ Boy 👶           │
│ ○ Girl 👶          │
│ ○ Surprise! 🎉     │
│                     │
│ Birth Date *        │
│ [2025-12-25___]     │
│                     │
│ Birth Time *        │
│ [3:30 PM▼]         │
│                     │
│ Birth Weight *      │
│ ○ Pounds & Ounces  │
│ ○ Kilograms        │
│                     │
│ [7] lbs [8] oz     │
│ ≈ 3.40 kg          │
│                     │
│ [Submit Guess]     │
│                     │
└─────────────────────┘
```

**Mobile Features:**
- Single column layout
- Touch-friendly form inputs
- Large tap targets (44px minimum)
- Optimized font sizes
- Proper viewport scaling

---

## 🖥️ Desktop Experience

**Wide Screen (1200px+):**
- Two-column form layout
- Two-column guess grid
- Maximum width container (1200px)
- Generous spacing and padding
- Easy to read and navigate

**Features:**
- Hover effects on buttons
- Focus states on inputs
- Smooth transitions
- Professional appearance

---

## 🎯 User Flow

1. **User arrives** → Login screen with password
2. **Enters password** → Authenticated, taken to main app
3. **Sees two tabs:**
   - Make a Guess (default)
   - All Guesses
4. **Fills out form:**
   - Name (required)
   - Email (optional)
   - Gender selection
   - Date picker
   - Time dropdown
   - Weight with unit selection
5. **Submits guess** → Success message → Auto-switch to All Guesses tab
6. **Views all guesses** → Grid of cards showing everyone's guesses
7. **Can make multiple guesses** → Switch back to form tab

---

## ✨ Polish & Details

- **Smooth animations** on tab switches
- **Real-time validation** with error messages
- **Success feedback** when guess submitted
- **Loading states** when fetching data
- **Empty states** with call-to-action
- **Responsive images** and icons
- **Accessible forms** with proper labels
- **Keyboard navigation** support

---

## 🔄 Interactive Features

### Weight Conversion
- Type in pounds/ounces → Automatically shows kg
- Type in kg → Automatically shows lbs/oz
- Instant conversion as you type

### Form Validation
- Required field indicators (*)
- Error messages in red
- Success messages in green
- Disabled submit until valid

### Session Management
- Password saved in localStorage
- Stays logged in on refresh
- 24-hour session expiry
- Secure token-based auth

---

This is what your family and friends will see when they visit babysweep.timmurdoch.com.au!

The design is clean, professional, fun, and easy to use on any device.
