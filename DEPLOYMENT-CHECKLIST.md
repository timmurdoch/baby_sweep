# 🍼 Baby Sweep - Deployment Checklist

Use this checklist to ensure a smooth deployment of your Baby Sweep application.

## 📋 Pre-Deployment Checklist

### Server Preparation
- [ ] Proxmox LXC container created and running
- [ ] Ubuntu/Debian OS installed (recommended: Ubuntu 24.04 LTS)
- [ ] Container has internet access
- [ ] Container can be accessed via SSH
- [ ] Root or sudo access available

### Software Requirements
- [ ] Node.js 18+ installed (`node --version`)
- [ ] npm installed (`npm --version`)
- [ ] nginx installed (`nginx -v`)
- [ ] Git installed (optional, for version control)
- [ ] Docker installed (if using Docker deployment)

### Domain & DNS
- [ ] Domain registered and active (timmurdoch.com.au)
- [ ] Access to Cloudflare dashboard
- [ ] A record ready to create (babysweep → server IP)

### Cloudflare SSL
- [ ] Cloudflare Origin Certificate generated
- [ ] Certificate (.pem) file downloaded
- [ ] Private key (.pem) file downloaded

---

## 🚀 Deployment Steps Checklist

### Step 1: Upload Application
- [ ] Extract baby-sweep.tar.gz on server
- [ ] Files located in /opt/baby-sweep
- [ ] Correct permissions set (`sudo chown -R www-data:www-data /opt/baby-sweep`)

### Step 2: Build Frontend
- [ ] Navigate to frontend directory
- [ ] Run `npm install`
- [ ] Run `npm run build`
- [ ] Build folder created successfully
- [ ] No build errors

### Step 3: Setup Backend
- [ ] Navigate to backend directory
- [ ] Run `npm install --production`
- [ ] Run `node database.js` to initialize database
- [ ] Copy frontend build: `cp -r ../frontend/build ./public`
- [ ] Test run: `node server.js` (should see "Baby Sweep API running on port 3001")

### Step 4: Create System Service
- [ ] Copy service file: `sudo cp baby-sweep.service /etc/systemd/system/`
- [ ] Reload systemd: `sudo systemctl daemon-reload`
- [ ] Enable service: `sudo systemctl enable baby-sweep`
- [ ] Start service: `sudo systemctl start baby-sweep`
- [ ] Check status: `sudo systemctl status baby-sweep` (should show "active (running)")

### Step 5: Configure Nginx
- [ ] Copy nginx config to sites-available
- [ ] Create symbolic link to sites-enabled
- [ ] Create SSL directory: `sudo mkdir -p /etc/nginx/ssl`
- [ ] Upload Cloudflare certificate to `/etc/nginx/ssl/cert.pem`
- [ ] Upload Cloudflare private key to `/etc/nginx/ssl/key.pem`
- [ ] Set permissions: `sudo chmod 600 /etc/nginx/ssl/*.pem`
- [ ] Test nginx config: `sudo nginx -t` (should show "successful")
- [ ] Reload nginx: `sudo systemctl reload nginx`

### Step 6: Cloudflare Configuration
- [ ] Login to Cloudflare dashboard
- [ ] Select your domain (timmurdoch.com.au)
- [ ] Add DNS A record:
  - Name: babysweep
  - IPv4: [Your server IP]
  - Proxy status: Proxied (orange cloud)
  - TTL: Auto
- [ ] Go to SSL/TLS settings
- [ ] Set encryption mode: Full (strict)
- [ ] Enable "Always Use HTTPS"
- [ ] Enable "Automatic HTTPS Rewrites"

### Step 7: Firewall Configuration
- [ ] Open port 80: `sudo ufw allow 80/tcp`
- [ ] Open port 443: `sudo ufw allow 443/tcp`
- [ ] Enable firewall: `sudo ufw enable`
- [ ] Check status: `sudo ufw status`

---

## ✅ Post-Deployment Verification

### Connectivity Tests
- [ ] Can access via HTTP: http://babysweep.timmurdoch.com.au
- [ ] Auto-redirects to HTTPS
- [ ] HTTPS works: https://babysweep.timmurdoch.com.au
- [ ] No SSL certificate warnings
- [ ] Page loads within 2 seconds

### Application Tests
- [ ] Login page displays correctly
- [ ] Can login with default password (babysweep2025)
- [ ] After login, main page loads
- [ ] Can switch between tabs (Make a Guess / All Guesses)
- [ ] Form displays all fields correctly
- [ ] Can submit a test guess
- [ ] Test guess appears in "All Guesses" tab
- [ ] Weight conversion works (try both lbs/oz and kg)
- [ ] Mobile view works (test on phone)
- [ ] Tablet view works

### Mobile Testing
- [ ] Open on iPhone/Android
- [ ] Page is responsive
- [ ] Form is usable
- [ ] Can submit guess from mobile
- [ ] Text is readable
- [ ] Buttons are tappable

### Backend Tests
- [ ] Check logs: `sudo journalctl -u baby-sweep -n 50`
- [ ] No errors in logs
- [ ] API endpoints respond correctly
- [ ] Database is being updated
- [ ] Sessions work correctly

### Database Verification
- [ ] Database file exists: `/opt/baby-sweep/backend/babysweep.db`
- [ ] Can query database: `sqlite3 babysweep.db "SELECT * FROM guesses;"`
- [ ] Test guess appears in database
- [ ] Settings table has correct values

---

## 🔒 Security Checklist

### Immediate Security Tasks
- [ ] Change default password from `babysweep2025`
  ```bash
  cd /opt/baby-sweep/backend
  sqlite3 babysweep.db
  UPDATE settings SET value = 'your-secure-password-here' WHERE key = 'app_password';
  .exit
  sudo systemctl restart baby-sweep
  ```
- [ ] Verify new password works
- [ ] Document new password securely

### Ongoing Security
- [ ] Keep system updated: `sudo apt update && sudo apt upgrade`
- [ ] Monitor logs regularly
- [ ] Backup database weekly
- [ ] Review access logs
- [ ] Update Node.js dependencies monthly

---

## 📝 Configuration Checklist

### Customize Settings
- [ ] Update due date in database
  ```sql
  UPDATE settings SET value = 'YYYY-MM-DD' WHERE key = 'due_date';
  ```
- [ ] Customize welcome text
  ```sql
  UPDATE settings SET value = 'Your welcome message' WHERE key = 'welcome_text';
  ```
- [ ] Adjust time blocks if needed (15, 30, or 60 minutes)
  ```sql
  UPDATE settings SET value = '30' WHERE key = 'time_block_minutes';
  ```
- [ ] Restart service after changes: `sudo systemctl restart baby-sweep`

### Optional Configuration
- [ ] Change primary color (hex code)
- [ ] Set up automatic database backups
- [ ] Configure log rotation
- [ ] Set up monitoring/alerts

---

## 💾 Backup Checklist

### Initial Backup
- [ ] Backup database: `cp babysweep.db babysweep.db.backup`
- [ ] Backup entire application: `tar -czf baby-sweep-backup.tar.gz /opt/baby-sweep`
- [ ] Store backup off-server (local computer, cloud storage)

### Ongoing Backups
- [ ] Set up weekly cron job for database backup
- [ ] Test restore process
- [ ] Keep 3-4 backup versions
- [ ] Document backup location

---

## 🎯 Go-Live Checklist

### Final Checks Before Sharing
- [ ] Application fully tested
- [ ] Password changed from default
- [ ] Due date set correctly
- [ ] Welcome message customized
- [ ] All guesses display properly
- [ ] Mobile version works
- [ ] HTTPS working with no errors
- [ ] Database backed up

### Communication
- [ ] Prepare announcement message
- [ ] Include URL: https://babysweep.timmurdoch.com.au
- [ ] Include password (communicate securely!)
- [ ] Explain how it works
- [ ] Set expectations (when baby arrives, results, etc.)
- [ ] Send to family & friends!

---

## 📊 Monitoring Checklist

### Daily (First Week)
- [ ] Check application is running
- [ ] Review any error logs
- [ ] Verify new guesses are being saved
- [ ] Check Cloudflare analytics

### Weekly
- [ ] Review all guesses
- [ ] Backup database
- [ ] Check disk space
- [ ] Review system updates
- [ ] Check SSL certificate validity

### Monthly
- [ ] Update Node.js packages if needed
- [ ] Review and optimize database
- [ ] Check security advisories
- [ ] Review Cloudflare settings

---

## 🐛 Troubleshooting Checklist

If something goes wrong, check these in order:

### Application Not Loading
- [ ] Is the service running? `sudo systemctl status baby-sweep`
- [ ] Check logs: `sudo journalctl -u baby-sweep -n 50`
- [ ] Is nginx running? `sudo systemctl status nginx`
- [ ] Test nginx config: `sudo nginx -t`
- [ ] Check port 3001: `sudo netstat -tlnp | grep 3001`

### Can't Login
- [ ] Verify password in database
- [ ] Check browser console for errors (F12)
- [ ] Clear browser cache and cookies
- [ ] Try incognito/private mode
- [ ] Check API is responding: `curl http://localhost:3001/api/health`

### Guesses Not Saving
- [ ] Check database permissions
- [ ] Check disk space: `df -h`
- [ ] Review application logs
- [ ] Test database manually with sqlite3
- [ ] Check session token is valid

### SSL/HTTPS Issues
- [ ] Verify Cloudflare SSL mode (Full strict)
- [ ] Check certificate files exist in /etc/nginx/ssl/
- [ ] Check certificate permissions (600)
- [ ] Review nginx error log: `sudo tail -f /var/log/nginx/error.log`
- [ ] Test SSL: https://www.ssllabs.com/ssltest/

---

## ✨ Success Criteria

Your deployment is successful when:

- ✅ Website loads at https://babysweep.timmurdoch.com.au
- ✅ Login works with your custom password
- ✅ Can submit guesses successfully
- ✅ All guesses display correctly
- ✅ Weight conversion works
- ✅ Mobile version is fully functional
- ✅ No errors in logs
- ✅ Database is being updated
- ✅ HTTPS is secure with no warnings
- ✅ Family and friends can access it

---

## 🎉 Post-Launch Tasks

After successful deployment:

- [ ] Share the URL and password with family
- [ ] Make a test guess yourself
- [ ] Ask a friend to test it
- [ ] Monitor the first few submissions
- [ ] Backup database after first guesses
- [ ] Enjoy the excitement!
- [ ] Plan for Phase 2 features

---

## 📞 Need Help?

Refer to:
- **README.md** - Full documentation
- **QUICKSTART.md** - Step-by-step guide
- **VISUAL-PREVIEW.md** - See what it should look like

Check logs for specific errors and troubleshoot systematically using the checklist above.

---

**Remember:** Test thoroughly before sharing with family and friends!

**Most Important:** Change the default password before going live!

Good luck with your deployment! 🍼👶
