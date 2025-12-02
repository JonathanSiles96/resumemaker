# Hostinger Deployment Guide - Free Resume Maker

## Project Tech Stack

### Backend
- **Framework**: Flask 3.1.2 (Python)
- **CORS**: Flask-CORS 6.0.1
- **PDF Generation**: ReportLab 4.4.4
- **AI Integration**: OpenAI SDK 1.55.3 (using DeepSeek API)
- **Environment**: python-dotenv 1.0.1
- **Language**: Python 3.8+

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Responsive design
- **JavaScript**: Vanilla JS (no framework)
- **No Build Process**: Static files only

### Data Storage
- **JSON files**: Simple file-based storage
- **Output**: PDF files in backend/output directory

### APIs Used
- **DeepSeek API**: AI content generation
- **Port**: Backend runs on 5000, Frontend on 8080

---

## Hostinger Deployment Options

### ⚠️ Important Note
This project requires **Python backend** support. Hostinger offers:

1. **✅ VPS Hosting** (Recommended) - Full Python support
2. **✅ Cloud Hosting** (Alternative) - Managed with Python
3. **❌ Shared Hosting** (Not suitable) - PHP only, no Python

**Recommended**: **VPS Hosting** for full control and Python support

---

## Option 1: VPS Hosting (Recommended)

### Step 1: Get Hostinger VPS

1. Go to Hostinger VPS: https://www.hostinger.com/vps-hosting
2. Choose a plan (KVM 1 or higher recommended)
3. Purchase and note your:
   - VPS IP address
   - Root password
   - SSH access details

### Step 2: Initial Server Setup

#### 2.1 Connect via SSH
```bash
# On Windows (use PowerShell or PuTTY)
ssh root@YOUR_VPS_IP

# On Mac/Linux
ssh root@YOUR_VPS_IP
```

#### 2.2 Update System
```bash
apt update && apt upgrade -y
```

#### 2.3 Install Python and Dependencies
```bash
# Install Python 3.10+
apt install python3 python3-pip python3-venv -y

# Install Nginx (web server)
apt install nginx -y

# Install system dependencies for ReportLab
apt install python3-dev build-essential -y
```

#### 2.4 Install Node.js (for process management)
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install nodejs -y
npm install -g pm2
```

### Step 3: Upload Project Files

#### 3.1 Create Project Directory
```bash
mkdir -p /var/www/freeresumemake
cd /var/www/freeresumemake
```

#### 3.2 Upload Files (Choose One Method)

**Method A: Git (Recommended)**
```bash
# If your project is on GitHub
git clone https://github.com/yourusername/resume_maker.git .
```

**Method B: SCP/SFTP**
```bash
# From your local machine
scp -r D:\work\resume_maker/* root@YOUR_VPS_IP:/var/www/freeresumemake/
```

**Method C: FileZilla (GUI)**
- Download FileZilla: https://filezilla-project.org
- Connect to: YOUR_VPS_IP, Port 22, root user
- Upload entire project to `/var/www/freeresumemake/`

### Step 4: Backend Setup

#### 4.1 Create Virtual Environment
```bash
cd /var/www/freeresumemake/backend
python3 -m venv venv
source venv/bin/activate
```

#### 4.2 Install Python Dependencies
```bash
pip install -r ../requirements.txt
```

#### 4.3 Create Environment File
```bash
nano .env
```

Add this content:
```env
# DeepSeek API Key
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Domain
DOMAIN=freeresumemake.com
```

Save: `Ctrl+O`, Enter, `Ctrl+X`

#### 4.4 Test Backend
```bash
python app.py
```

Should see:
```
🤖 AI-POWERED RESUME GENERATOR
✓ DeepSeek AI integration enabled
```

Press `Ctrl+C` to stop.

### Step 5: Configure PM2 (Process Manager)

#### 5.1 Create PM2 Configuration
```bash
cd /var/www/freeresumemake
nano ecosystem.config.js
```

Add:
```javascript
module.exports = {
  apps: [{
    name: 'resume-maker-backend',
    cwd: '/var/www/freeresumemake/backend',
    script: 'venv/bin/python',
    args: 'app.py',
    interpreter: 'none',
    env: {
      FLASK_ENV: 'production'
    },
    error_file: '/var/log/resume-maker-error.log',
    out_file: '/var/log/resume-maker-out.log',
    time: true
  }]
};
```

#### 5.2 Start Backend with PM2
```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

#### 5.3 Check Status
```bash
pm2 status
pm2 logs resume-maker-backend
```

### Step 6: Configure Nginx

#### 6.1 Create Nginx Configuration
```bash
nano /etc/nginx/sites-available/freeresumemake.com
```

Add:
```nginx
# HTTP - Redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name freeresumemake.com www.freeresumemake.com;
    
    # Redirect all HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS - Main site
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name freeresumemake.com www.freeresumemake.com;

    # SSL certificates (will be configured with Certbot)
    ssl_certificate /etc/letsencrypt/live/freeresumemake.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/freeresumemake.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    # Frontend (static files)
    root /var/www/freeresumemake/frontend;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # Frontend files
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "public, max-age=3600";
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }

    # Static assets caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

#### 6.2 Enable Site
```bash
ln -s /etc/nginx/sites-available/freeresumemake.com /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Step 7: SSL Certificate (HTTPS)

#### 7.1 Install Certbot
```bash
apt install certbot python3-certbot-nginx -y
```

#### 7.2 Get SSL Certificate
```bash
certbot --nginx -d freeresumemake.com -d www.freeresumemake.com
```

Follow prompts:
- Enter email
- Agree to terms
- Choose redirect (option 2)

#### 7.3 Test Auto-Renewal
```bash
certbot renew --dry-run
```

### Step 8: Update Frontend API URL

#### 8.1 Edit app.js
```bash
nano /var/www/freeresumemake/frontend/app.js
```

Change line 2:
```javascript
// From:
const API_BASE_URL = 'http://localhost:5000/api';

// To:
const API_BASE_URL = '/api';  // Use relative URL
```

Save and exit.

### Step 9: Set Correct Permissions

```bash
# Set ownership
chown -R www-data:www-data /var/www/freeresumemake

# Set permissions
chmod -R 755 /var/www/freeresumemake
chmod -R 777 /var/www/freeresumemake/backend/output
chmod -R 777 /var/www/freeresumemake/backend/data
```

### Step 10: Configure Firewall

```bash
# Allow SSH, HTTP, HTTPS
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### Step 11: DNS Configuration

1. Go to your domain registrar (where you bought freeresumemake.com)
2. Update DNS records:

```
Type    Name    Value           TTL
A       @       YOUR_VPS_IP     3600
A       www     YOUR_VPS_IP     3600
```

3. Wait 1-24 hours for DNS propagation

### Step 12: Final Testing

#### 12.1 Test Backend
```bash
curl http://localhost:5000/api/health
```

Should return:
```json
{"status": "healthy"}
```

#### 12.2 Test Frontend
Visit: https://freeresumemake.com

#### 12.3 Test Resume Generation
1. Paste a job description
2. Fill in personal info
3. Generate resume
4. Download PDF

---

## Post-Deployment Maintenance

### Monitor Backend
```bash
pm2 status
pm2 logs resume-maker-backend
```

### Restart Backend
```bash
pm2 restart resume-maker-backend
```

### View Logs
```bash
# Backend logs
tail -f /var/log/resume-maker-out.log
tail -f /var/log/resume-maker-error.log

# Nginx logs
tail -f /var/nginx/access.log
tail -f /var/nginx/error.log
```

### Update Application
```bash
cd /var/www/freeresumemake
git pull origin main  # If using Git
pm2 restart resume-maker-backend
```

---

## Option 2: Cloud Hosting (Alternative)

Hostinger Cloud Hosting is similar to VPS but managed. Follow same steps but:
- Use Hostinger's control panel for initial setup
- Python environment may be pre-configured
- Use their deployment tools

---

## Troubleshooting

### Backend Not Starting
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check dependencies
cd /var/www/freeresumemake/backend
source venv/bin/activate
pip list

# Check logs
pm2 logs resume-maker-backend
```

### 502 Bad Gateway
```bash
# Backend not running
pm2 status
pm2 restart resume-maker-backend

# Check Nginx
nginx -t
systemctl status nginx
```

### API Key Issues
```bash
# Verify .env file
cat /var/www/freeresumemake/backend/.env

# Test API key
cd /var/www/freeresumemake/backend
source venv/bin/activate
python check_api.py
```

### Permission Denied
```bash
# Fix permissions
chown -R www-data:www-data /var/www/freeresumemake
chmod -R 755 /var/www/freeresumemake
chmod -R 777 /var/www/freeresumemake/backend/output
```

### SSL Certificate Issues
```bash
# Renew certificate
certbot renew

# Test configuration
certbot certificates
```

---

## Performance Optimization

### 1. Enable Caching
Already configured in Nginx config above.

### 2. Optimize Python
```bash
# Use production WSGI server
pip install gunicorn

# Update PM2 config
pm2 delete resume-maker-backend
```

Edit ecosystem.config.js:
```javascript
script: 'venv/bin/gunicorn',
args: '-w 4 -b 127.0.0.1:5000 app:app',
```

```bash
pm2 start ecosystem.config.js
```

### 3. Monitor Resources
```bash
# Check memory
free -h

# Check disk
df -h

# Check CPU
top
```

---

## Security Checklist

- [x] SSL certificate installed (HTTPS)
- [x] Firewall configured (UFW)
- [x] SSH key authentication (recommended)
- [x] Regular updates: `apt update && apt upgrade`
- [x] Strong passwords
- [x] PM2 process monitoring
- [x] Log monitoring
- [x] Backup data directory
- [x] Environment variables secured (.env)

---

## Backup Strategy

### Manual Backup
```bash
# Backup entire application
tar -czf backup-$(date +%Y%m%d).tar.gz /var/www/freeresumemake

# Backup data only
tar -czf data-backup-$(date +%Y%m%d).tar.gz /var/www/freeresumemake/backend/data
```

### Automated Backup (Daily)
```bash
# Create backup script
nano /root/backup.sh
```

Add:
```bash
#!/bin/bash
BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d)
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/resume-maker-$DATE.tar.gz /var/www/freeresumemake
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete  # Keep 7 days
```

```bash
chmod +x /root/backup.sh
crontab -e
```

Add line:
```
0 2 * * * /root/backup.sh
```

---

## Cost Estimate (Hostinger VPS)

- **VPS Hosting**: $4-8/month
- **Domain**: $10-15/year (if not owned)
- **SSL**: Free (Let's Encrypt)
- **DeepSeek API**: ~$0.14 per 1M tokens (very cheap)

**Total**: ~$5-10/month

---

## Quick Reference

### Important Paths
- Application: `/var/www/freeresumemake`
- Backend: `/var/www/freeresumemake/backend`
- Frontend: `/var/www/freeresumemake/frontend`
- Logs: `/var/log/resume-maker-*.log`
- Nginx Config: `/etc/nginx/sites-available/freeresumemake.com`

### Important Commands
```bash
# Backend
pm2 status
pm2 restart resume-maker-backend
pm2 logs resume-maker-backend

# Nginx
nginx -t
systemctl restart nginx

# SSL
certbot renew
certbot certificates

# Updates
cd /var/www/freeresumemake
git pull
pm2 restart resume-maker-backend
```

---

## Support Resources

- **Hostinger VPS Docs**: https://support.hostinger.com/en/collections/1742634-vps
- **Flask Deployment**: https://flask.palletsprojects.com/en/latest/deploying/
- **Nginx Docs**: https://nginx.org/en/docs/
- **PM2 Docs**: https://pm2.keymetrics.io/docs/usage/quick-start/
- **Let's Encrypt**: https://letsencrypt.org/getting-started/

---

## Summary

✅ **Tech Stack**: Python Flask + Vanilla JavaScript  
✅ **Recommended**: Hostinger VPS Hosting  
✅ **SSL**: Free with Let's Encrypt  
✅ **Cost**: ~$5-10/month  
✅ **Deployment Time**: 1-2 hours  

**Status**: Ready to deploy with this guide!

---

**Last Updated**: November 18, 2025  
**Domain**: freeresumemake.com  
**Guide Version**: 1.0

