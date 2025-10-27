# 🔧 Baby Sweep - Troubleshooting Guide

Quick solutions to common problems you might encounter.

---

## 🚨 Application Won't Start

### Symptom
Service fails to start or immediately stops.

### Solutions

**Check service status:**
```bash
sudo systemctl status baby-sweep
```

**View detailed logs:**
```bash
sudo journalctl -u baby-sweep -n 100 --no-pager
```

**Common causes:**

1. **Port 3001 already in use:**
   ```bash
   sudo lsof -i :3001
   # Kill the process:
   sudo kill -9 [PID]
   # Or change port in .env file
   ```

2. **Missing dependencies:**
   ```bash
   cd /opt/baby-sweep/backend
   npm install --production
   ```

3. **Database permission issues:**
   ```bash
   sudo chown -R www-data:www-data /opt/baby-sweep/backend
   ```

4. **Missing frontend build:**
   ```bash
   cd /opt/baby-sweep/frontend
   npm run build
   cd ../backend
   cp -r ../frontend/build ./public
   ```

---

## 🌐 Website Not Accessible

### Symptom
Can't reach babysweep.timmurdoch.com.au

### Solutions

**Check nginx:**
```bash
sudo systemctl status nginx
sudo nginx -t
```

**Check DNS propagation:**
```bash
nslookup babysweep.timmurdoch.com.au
# or
dig babysweep.timmurdoch.com.au
```

**Verify Cloudflare:**
- Login to Cloudflare dashboard
- Check DNS record exists and is proxied (orange cloud)
- Verify SSL/TLS mode is "Full (strict)"

**Test locally:**
```bash
curl http://localhost:3001
# Should return HTML
```

**Check firewall:**
```bash
sudo ufw status
# Ensure ports 80 and 443 are allowed
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

---

## 🔐 Can't Login / Invalid Password

### Symptom
Login fails even with correct password.

### Solutions

**Verify password in database:**
```bash
cd /opt/baby-sweep/backend
sqlite3 babysweep.db
SELECT value FROM settings WHERE key = 'app_password';
.exit
```

**Reset to default password:**
```bash
sqlite3 babysweep.db
UPDATE settings SET value = 'babysweep2025' WHERE key = 'app_password';
.exit
sudo systemctl restart baby-sweep
```

**Check browser console:**
- Press F12 in browser
- Go to Console tab
- Look for error messages
- Check Network tab for failed API calls

**Clear browser data:**
- Clear cache and cookies
- Try incognito/private mode
- Try different browser

**Verify API is responding:**
```bash
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"password":"babysweep2025"}'
# Should return success with token
```

---

## 💾 Database Issues

### Symptom
"Database is locked" or data not saving.

### Solutions

**Database locked:**
```bash
cd /opt/baby-sweep/backend
# Stop the service
sudo systemctl stop baby-sweep

# Remove journal file
rm -f babysweep.db-journal
rm -f babysweep.db-wal
rm -f babysweep.db-shm

# Restart service
sudo systemctl start baby-sweep
```

**Check database integrity:**
```bash
sqlite3 babysweep.db
PRAGMA integrity_check;
.exit
```

**Verify tables exist:**
```bash
sqlite3 babysweep.db
.tables
# Should show: guesses, sessions, settings
.exit
```

**Recreate database if corrupted:**
```bash
# Backup first!
cp babysweep.db babysweep.db.corrupted

# Reinitialize
rm babysweep.db
node database.js

# Restore password
sqlite3 babysweep.db
UPDATE settings SET value = 'your-password' WHERE key = 'app_password';
.exit
```

---

## 📝 Guesses Not Displaying

### Symptom
Submitted guesses don't show up in "All Guesses" tab.

### Solutions

**Check database directly:**
```bash
cd /opt/baby-sweep/backend
sqlite3 babysweep.db
SELECT * FROM guesses;
.exit
```

**Check API endpoint:**
```bash
# Get a valid token first by logging in, then:
curl "http://localhost:3001/api/guesses?token=YOUR_TOKEN_HERE"
```

**Review application logs:**
```bash
sudo journalctl -u baby-sweep -n 50 -f
# Keep this running and submit a guess
# Watch for errors
```

**Check browser console:**
- F12 → Console tab
- Submit a guess
- Look for errors

**Clear localStorage:**
```javascript
// In browser console (F12):
localStorage.clear();
location.reload();
// Then login again
```

---

## ⚖️ Weight Conversion Not Working

### Symptom
Weight doesn't convert between lbs/oz and kg.

### Solutions

**Test conversion API:**
```bash
curl -X POST http://localhost:3001/api/convert/weight \
  -H "Content-Type: application/json" \
  -d '{"lbs":7,"oz":8}'
# Should return kg value

curl -X POST http://localhost:3001/api/convert/weight \
  -H "Content-Type: application/json" \
  -d '{"kg":3.4}'
# Should return lbs and oz
```

**Check browser console:**
- Watch Network tab when typing weight
- Look for failed API calls

**Known issue - Rapid typing:**
- Conversion happens on blur (when you click away)
- Or every time you type
- This is normal behavior

---

## 🔒 SSL / HTTPS Errors

### Symptom
SSL warnings, "Not Secure", or HTTPS not working.

### Solutions

**Verify Cloudflare SSL mode:**
- Dashboard → SSL/TLS → Overview
- Should be: "Full (strict)"
- If using self-signed cert, use "Full"

**Check certificate files:**
```bash
ls -la /etc/nginx/ssl/
# Should show cert.pem and key.pem
# Permissions should be 600 or 400

sudo chmod 600 /etc/nginx/ssl/*.pem
```

**Test nginx SSL configuration:**
```bash
sudo nginx -t
sudo systemctl reload nginx
```

**Check nginx error log:**
```bash
sudo tail -f /var/log/nginx/error.log
```

**Test SSL online:**
Visit: https://www.ssllabs.com/ssltest/
Enter: babysweep.timmurdoch.com.au

**Regenerate Cloudflare Origin Certificate:**
1. Cloudflare Dashboard → SSL/TLS → Origin Server
2. Create new certificate
3. Replace cert.pem and key.pem
4. Reload nginx

---

## 📱 Mobile Issues

### Symptom
Doesn't work well on mobile devices.

### Solutions

**Check viewport meta tag:**
Should be in index.html:
```html
<meta name="viewport" content="width=device-width, initial-scale=1" />
```

**Test responsive design:**
- Desktop browser → F12 → Toggle device toolbar
- Test different screen sizes
- Check if layout adapts

**Common mobile issues:**
- Text too small → Check CSS font sizes
- Buttons too small → Should be min 44px
- Horizontal scrolling → Check max-width and overflow

**Check mobile logs:**
- Some browsers have remote debugging
- Safari: Develop menu → Device
- Chrome: chrome://inspect

---

## 🐌 Performance Issues

### Symptom
Slow loading, lag, or timeouts.

### Solutions

**Check server resources:**
```bash
# CPU and memory
top
# or
htop

# Disk space
df -h

# If low on disk space:
sudo apt clean
sudo journalctl --vacuum-time=7d
```

**Check database size:**
```bash
ls -lh /opt/baby-sweep/backend/babysweep.db
# Should be under 1MB for normal use
```

**Optimize database:**
```bash
sqlite3 babysweep.db
VACUUM;
ANALYZE;
.exit
```

**Review nginx logs:**
```bash
sudo tail -f /var/log/nginx/access.log
# Watch request times
```

**Check for slow queries:**
```bash
sudo journalctl -u baby-sweep -n 100 | grep -i "slow\|timeout"
```

---

## 🔄 Session/Login Issues

### Symptom
Keeps logging out or session expires too quickly.

### Solutions

**Check session expiry:**
Sessions expire after 24 hours by default.

**Clean up old sessions:**
```bash
sqlite3 babysweep.db
DELETE FROM sessions WHERE expires_at < datetime('now');
.exit
```

**Check localStorage:**
```javascript
// Browser console (F12):
console.log(localStorage.getItem('babysweep_token'));
// Should show a long hex string
```

**Browser privacy settings:**
- Some browsers block localStorage
- Check browser privacy settings
- Try different browser

---

## 🗑️ Need to Start Fresh?

### Complete Reset (Nuclear Option)

**⚠️ WARNING: This deletes ALL data!**

```bash
# Stop the service
sudo systemctl stop baby-sweep

# Backup current database (just in case)
cd /opt/baby-sweep/backend
cp babysweep.db babysweep.db.backup-$(date +%Y%m%d)

# Delete database
rm babysweep.db

# Reinitialize
node database.js

# Set your password
sqlite3 babysweep.db
UPDATE settings SET value = 'your-new-password' WHERE key = 'app_password';
UPDATE settings SET value = '2025-12-25' WHERE key = 'due_date';
UPDATE settings SET value = 'Welcome to our Baby Sweep!' WHERE key = 'welcome_text';
.exit

# Restart service
sudo systemctl start baby-sweep

# Verify it's working
sudo systemctl status baby-sweep
```

---

## 📞 Getting More Help

### Gather Information

When asking for help, provide:

1. **Error messages:**
```bash
sudo journalctl -u baby-sweep -n 100 --no-pager > ~/baby-sweep-logs.txt
```

2. **System information:**
```bash
uname -a
node --version
nginx -v
```

3. **What you were doing when the error occurred**

4. **What you've already tried**

### Useful Commands

**View all services status:**
```bash
sudo systemctl status baby-sweep nginx
```

**Follow logs in real-time:**
```bash
# Terminal 1: Application logs
sudo journalctl -u baby-sweep -f

# Terminal 2: Nginx logs
sudo tail -f /var/log/nginx/error.log

# Terminal 3: Test the application
```

**Check entire system health:**
```bash
sudo systemctl status
top
df -h
free -h
```

---

## 🎯 Prevention Tips

### Regular Maintenance

**Weekly:**
```bash
# Backup database
cp /opt/baby-sweep/backend/babysweep.db ~/backups/babysweep-$(date +%Y%m%d).db

# Check logs for errors
sudo journalctl -u baby-sweep --since "1 week ago" | grep -i error

# Update system
sudo apt update && sudo apt upgrade -y
```

**Monthly:**
```bash
# Check disk space
df -h

# Vacuum database
cd /opt/baby-sweep/backend
sqlite3 babysweep.db "VACUUM; ANALYZE;"

# Review and clean old session tokens
sqlite3 babysweep.db "DELETE FROM sessions WHERE expires_at < datetime('now', '-30 days');"
```

### Monitoring

Set up simple monitoring:

**Create health check script:**
```bash
#!/bin/bash
# /opt/baby-sweep/health-check.sh

URL="https://babysweep.timmurdoch.com.au"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $URL)

if [ $STATUS -ne 200 ]; then
    echo "ALERT: Baby Sweep is down! Status: $STATUS"
    # Send email, notification, etc.
fi
```

**Run via cron every 5 minutes:**
```bash
*/5 * * * * /opt/baby-sweep/health-check.sh
```

---

## ✅ Quick Diagnostic Checklist

Run through these quickly when troubleshooting:

- [ ] Is the service running? `sudo systemctl status baby-sweep`
- [ ] Is nginx running? `sudo systemctl status nginx`
- [ ] Any errors in logs? `sudo journalctl -u baby-sweep -n 20`
- [ ] Can curl localhost? `curl http://localhost:3001/api/health`
- [ ] Is DNS resolving? `nslookup babysweep.timmurdoch.com.au`
- [ ] Is SSL valid? Check browser lock icon
- [ ] Any disk space issues? `df -h`
- [ ] Any firewall blocks? `sudo ufw status`

---

**Remember:** Most issues can be solved by:
1. Checking logs
2. Restarting the service
3. Clearing browser cache
4. Verifying configuration

When in doubt, check the logs first! 📋
