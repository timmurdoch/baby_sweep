# Baby Sweep - Deployment Guide

A full-stack web application for running a baby pool/sweep where friends and family can guess baby details.

## 🎯 MVP Features (Phase 1)

✅ **Completed:**
- Password-protected access
- Guess submission form (gender, date, time, weight)
- Real-time weight conversion (lbs/oz ⟷ kg)
- View all guesses
- Mobile-responsive design
- 30-minute time blocks
- SQLite database
- RESTful API

## 📋 Tech Stack

- **Frontend:** React 18, Custom CSS
- **Backend:** Node.js, Express
- **Database:** SQLite (file-based, no separate DB server needed)
- **Deployment:** Docker or systemd service

## 🚀 Deployment Options

### Option 1: Docker Deployment (Recommended)

#### Prerequisites
- Docker and Docker Compose installed on your Proxmox LXC

#### Steps

1. **Transfer files to your server:**
```bash
# On your Proxmox LXC container
cd /opt
sudo git clone <your-repo> baby-sweep
# Or use scp to transfer the files
```

2. **Build and start the container:**
```bash
cd /opt/baby-sweep
sudo docker-compose up -d --build
```

3. **Check it's running:**
```bash
sudo docker-compose ps
sudo docker-compose logs -f
```

The application will be running on port 3001.

### Option 2: Direct Node.js Deployment

#### Prerequisites
- Node.js 18+ installed
- nginx installed

#### Steps

1. **Install dependencies and build frontend:**
```bash
cd /opt/baby-sweep/frontend
npm install
npm run build
```

2. **Install backend dependencies:**
```bash
cd /opt/baby-sweep/backend
npm install --production
```

3. **Initialize the database:**
```bash
cd /opt/baby-sweep/backend
node database.js
```

4. **Serve frontend from backend:**
```bash
# Copy built frontend to backend public folder
cp -r ../frontend/build ./public
```

5. **Create systemd service:**
```bash
sudo cp /opt/baby-sweep/baby-sweep.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable baby-sweep
sudo systemctl start baby-sweep
sudo systemctl status baby-sweep
```

## 🌐 Nginx Reverse Proxy Setup

1. **Copy nginx configuration:**
```bash
sudo cp /opt/baby-sweep/nginx.conf /etc/nginx/sites-available/babysweep
sudo ln -s /etc/nginx/sites-available/babysweep /etc/nginx/sites-enabled/
```

2. **Create SSL certificates directory (if not using Cloudflare):**
```bash
sudo mkdir -p /etc/nginx/ssl
```

3. **If using Cloudflare Origin Certificate:**
   - Go to Cloudflare Dashboard → SSL/TLS → Origin Server
   - Create Certificate
   - Save certificate as `/etc/nginx/ssl/cert.pem`
   - Save private key as `/etc/nginx/ssl/key.pem`

4. **Test and reload nginx:**
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## ☁️ Cloudflare Setup

1. **DNS Settings:**
   - Add an A record: `babysweep` → Your server IP
   - Enable proxy (orange cloud icon)

2. **SSL/TLS Settings:**
   - SSL/TLS encryption mode: Full (strict) if using Cloudflare Origin Certificate
   - Or Full if using self-signed certificate

3. **Security:**
   - Consider enabling "Under Attack Mode" if needed
   - Set up WAF rules if desired

## 🔐 Default Credentials

**Initial Access Password:** `babysweep2025`

⚠️ **IMPORTANT:** Change this immediately after deployment!

To change the password:
```bash
# Access the database
cd /opt/baby-sweep/backend
sqlite3 babysweep.db

# Update password
UPDATE settings SET value = 'your-new-password' WHERE key = 'app_password';
.exit
```

## 🎨 Configuration

Edit settings in the database:

```bash
cd /opt/baby-sweep/backend
sqlite3 babysweep.db

# View current settings
SELECT * FROM settings;

# Update due date
UPDATE settings SET value = '2025-12-25' WHERE key = 'due_date';

# Update welcome text
UPDATE settings SET value = 'Welcome to our baby pool!' WHERE key = 'welcome_text';

# Change time blocks (15, 30, or 60 minutes)
UPDATE settings SET value = '15' WHERE key = 'time_block_minutes';

# Change primary color
UPDATE settings SET value = '#ff6b9d' WHERE key = 'primary_color';

.exit
```

Restart the service after changes:
```bash
sudo systemctl restart baby-sweep
# Or with Docker:
sudo docker-compose restart
```

## 📊 Database Management

### Backup Database
```bash
cp /opt/baby-sweep/backend/babysweep.db /opt/baby-sweep/backend/babysweep.db.backup
```

### View All Guesses
```bash
cd /opt/baby-sweep/backend
sqlite3 babysweep.db
SELECT * FROM guesses ORDER BY created_at DESC;
.exit
```

### Export to CSV
```bash
cd /opt/baby-sweep/backend
sqlite3 babysweep.db
.headers on
.mode csv
.output guesses.csv
SELECT * FROM guesses;
.exit
```

## 🔧 Troubleshooting

### Check Application Logs

**Docker:**
```bash
sudo docker-compose logs -f
```

**Systemd:**
```bash
sudo journalctl -u baby-sweep -f
```

### Common Issues

1. **Port 3001 already in use:**
   ```bash
   sudo lsof -i :3001
   # Kill the process or change port in docker-compose.yml/.env
   ```

2. **Database locked error:**
   - Stop the application
   - Remove any `.db-journal` files
   - Restart the application

3. **CORS errors:**
   - Check that REACT_APP_API_URL in frontend matches your domain
   - Rebuild frontend if needed

## 🎯 Phase 2 Features (Coming Next)

- [ ] Full admin panel with authentication
- [ ] Configurable pricing tiers
- [ ] Entry rules management (unique vs duplicate guesses)
- [ ] Calendar visualization
- [ ] Export functionality
- [ ] Birth result entry + winner calculation
- [ ] Theme customization
- [ ] Multiple guesses per person tracking

## 📁 Project Structure

```
baby-sweep/
├── backend/
│   ├── server.js           # Express API server
│   ├── database.js         # Database initialization
│   ├── package.json        # Backend dependencies
│   └── babysweep.db        # SQLite database (created on first run)
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   ├── index.js        # React entry point
│   │   └── index.css       # Styles
│   ├── public/
│   │   └── index.html      # HTML template
│   └── package.json        # Frontend dependencies
├── Dockerfile              # Docker container definition
├── docker-compose.yml      # Docker Compose configuration
├── nginx.conf              # Nginx reverse proxy config
├── baby-sweep.service      # Systemd service file
└── README.md              # This file
```

## 🆘 Support

For issues or questions:
1. Check logs first (see Troubleshooting section)
2. Verify all services are running
3. Check Cloudflare dashboard for any issues
4. Review nginx configuration

## 📝 License

Private use only.
