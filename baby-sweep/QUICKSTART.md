# Baby Sweep - Quick Start Guide

## 🚀 Fastest Way to Deploy (5 minutes)

### Step 1: Prepare Your LXC Container

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install nginx
sudo apt install -y nginx

# Optional: Install Docker if you prefer Docker deployment
# curl -fsSL https://get.docker.com | sh
```

### Step 2: Upload & Setup Application

```bash
# Create directory
sudo mkdir -p /opt/baby-sweep
cd /opt/baby-sweep

# Upload your files here (via scp, git, or other method)
# Then:

# Build frontend
cd frontend
npm install
npm run build

# Setup backend
cd ../backend
npm install --production
node database.js
cp -r ../frontend/build ./public

# Start the application (test run)
node server.js
```

You should see: "Baby Sweep API running on port 3001"

### Step 3: Setup as Service

```bash
# Create service file
sudo cp /opt/baby-sweep/baby-sweep.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable baby-sweep
sudo systemctl start baby-sweep

# Check status
sudo systemctl status baby-sweep
```

### Step 4: Configure Nginx

```bash
# Copy nginx config
sudo cp /opt/baby-sweep/nginx.conf /etc/nginx/sites-available/babysweep
sudo ln -s /etc/nginx/sites-available/babysweep /etc/nginx/sites-enabled/

# Setup SSL certificates (Cloudflare Origin Certificate)
sudo mkdir -p /etc/nginx/ssl
# Upload your Cloudflare cert.pem and key.pem to /etc/nginx/ssl/

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### Step 5: Cloudflare DNS

1. Go to your Cloudflare dashboard
2. Add DNS record:
   - Type: A
   - Name: babysweep
   - IPv4: Your server IP
   - Proxy status: Proxied (orange cloud)
3. SSL/TLS mode: Full (strict)

### Step 6: Test!

Visit: https://babysweep.timmurdoch.com.au

Default password: `babysweep2025`

**IMPORTANT:** Change the password immediately:

```bash
cd /opt/baby-sweep/backend
sqlite3 babysweep.db
UPDATE settings SET value = 'your-secure-password' WHERE key = 'app_password';
.exit
sudo systemctl restart baby-sweep
```

## ✅ You're Done!

Your baby sweep is now live and accessible at babysweep.timmurdoch.com.au

## 🎯 What You Can Do Now

1. **Make a test guess** - Try submitting a guess to make sure everything works
2. **Customize settings** - Change due date, welcome text, time blocks (see README.md)
3. **Share with family** - Give them the URL and password
4. **Monitor guesses** - Check the "All Guesses" tab

## 🔍 Quick Troubleshooting

**App won't start?**
```bash
sudo journalctl -u baby-sweep -n 50
```

**Can't access the site?**
```bash
sudo systemctl status nginx
sudo systemctl status baby-sweep
```

**Need to reset everything?**
```bash
cd /opt/baby-sweep/backend
rm babysweep.db
node database.js
sudo systemctl restart baby-sweep
```

## 📊 View Your Data

```bash
cd /opt/baby-sweep/backend
sqlite3 babysweep.db "SELECT name, gender, birth_date, birth_time FROM guesses;"
```

That's it! You're ready to start collecting guesses! 🎉
