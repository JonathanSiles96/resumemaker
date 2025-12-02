# Tech Stack Summary - Free Resume Maker

## 🛠️ Technology Stack

### Backend
```
Language:    Python 3.8+
Framework:   Flask 3.1.2
CORS:        Flask-CORS 6.0.1
PDF:         ReportLab 4.4.4
AI:          DeepSeek API (via OpenAI SDK 1.55.3)
Config:      python-dotenv 1.0.1
Storage:     JSON files
Port:        5000
```

### Frontend
```
HTML:        HTML5 (semantic markup)
CSS:         CSS3 (responsive, no framework)
JavaScript:  Vanilla JS (no React/Vue/Angular)
Build:       None needed (static files)
Port:        8080 (development)
```

### Infrastructure
```
Web Server:  Nginx (production)
Process:     PM2 (process manager)
SSL:         Let's Encrypt (free)
Storage:     File-based (JSON + PDF)
```

## 📦 Project Structure

```
resume_maker/
├── backend/
│   ├── app.py                 # Main Flask app
│   ├── services/              # Business logic
│   │   ├── ai_content_generator.py
│   │   ├── ats_matcher.py
│   │   ├── content_generator.py
│   │   ├── data_service.py
│   │   └── pdf_generator.py
│   ├── data/
│   │   └── user_data.json     # Saved data
│   └── output/                # Generated PDFs
├── frontend/
│   ├── index.html            # Main page
│   ├── app.js                # Frontend logic
│   ├── styles.css            # Styling
│   ├── robots.txt            # SEO
│   └── sitemap.xml           # SEO
├── docs/                     # Documentation
└── requirements.txt          # Python dependencies
```

## 🚀 Quick Deployment Summary

### Hostinger VPS (Recommended)

**1. What You Need:**
- Hostinger VPS account ($4-8/month)
- Domain: freeresumemake.com
- DeepSeek API key (free tier available)

**2. Basic Steps:**
```bash
# 1. Connect to VPS
ssh root@YOUR_VPS_IP

# 2. Install Python & Nginx
apt update && apt install python3 python3-pip nginx -y

# 3. Upload project files
# (via Git, SCP, or FileZilla)

# 4. Install dependencies
cd /var/www/freeresumemake/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configure Nginx (reverse proxy)
# 6. Get SSL certificate (certbot)
# 7. Start with PM2
```

**3. Time Required:**
- Setup: 1-2 hours
- SSL: 15 minutes
- Testing: 30 minutes

## ⚠️ Important Notes

### Hosting Requirements
❌ **Shared Hosting** - Won't work (PHP only)  
✅ **VPS Hosting** - Perfect (full control)  
✅ **Cloud Hosting** - Works (managed)

### Why Not Shared Hosting?
- Needs Python runtime
- Needs custom web server (Flask)
- Needs process management
- Shared hosting = PHP only

### Hostinger VPS Plans
- **KVM 1**: 1 CPU, 4GB RAM - $4.99/mo (sufficient)
- **KVM 2**: 2 CPU, 8GB RAM - $6.99/mo (better)
- **KVM 4**: 4 CPU, 16GB RAM - $12.99/mo (overkill)

**Recommended**: KVM 1 or KVM 2

## 💰 Cost Breakdown

| Item | Cost | Notes |
|------|------|-------|
| VPS Hosting | $5-7/mo | Hostinger VPS |
| Domain | $0 | Already owned |
| SSL Certificate | $0 | Let's Encrypt free |
| DeepSeek API | ~$1-5/mo | Pay per use |
| **Total** | **~$6-12/mo** | Very affordable |

## 🔑 Key Features of This Stack

### Advantages
✅ **Simple**: No complex build process  
✅ **Fast**: Vanilla JS = no framework overhead  
✅ **Cheap**: Minimal hosting requirements  
✅ **Scalable**: Easy to add features  
✅ **Portable**: Runs anywhere Python works  
✅ **SEO-Ready**: Server-rendered HTML  

### Trade-offs
⚠️ Needs VPS (not shared hosting)  
⚠️ Manual deployments (no auto CI/CD)  
⚠️ File-based storage (consider DB later)  

## 📝 Environment Variables Needed

Create `backend/.env`:
```env
DEEPSEEK_API_KEY=your_key_here
FLASK_ENV=production
FLASK_DEBUG=False
```

## 🔧 Development vs Production

### Development (Your Local Machine)
```bash
# Terminal 1: Backend
cd backend
python app.py
# Runs on http://localhost:5000

# Terminal 2: Frontend
cd frontend
python -m http.server 8080
# Runs on http://localhost:8080
```

### Production (Hostinger VPS)
```bash
# Backend: PM2 (process manager)
pm2 start app.py --interpreter python3

# Frontend: Nginx (web server)
# Serves static files
# Proxies /api/ to Flask backend
```

## 📊 Performance Specs

### Expected Performance
- **Page Load**: < 2 seconds
- **Resume Generation**: 30-35 seconds (AI processing)
- **Concurrent Users**: 10-20 (on basic VPS)
- **Monthly Resumes**: Unlimited (API costs apply)

### Optimization Tips
1. Use Gunicorn for production (4 workers)
2. Enable Nginx caching
3. Compress static assets
4. Monitor API usage

## 🔐 Security Features

✅ HTTPS (SSL certificate)  
✅ CORS configured properly  
✅ Environment variables (.env)  
✅ Firewall (UFW)  
✅ Regular updates  
✅ Secure headers (Nginx)  

## 📖 Full Deployment Guide

See: **DEPLOYMENT_GUIDE_HOSTINGER.md**

Complete step-by-step instructions for:
- Initial server setup
- Python environment
- Nginx configuration
- SSL certificate
- Process management
- DNS configuration
- Troubleshooting
- Maintenance

## 🆘 Quick Help

### Backend Won't Start?
```bash
# Check logs
pm2 logs

# Check Python
python3 --version

# Check dependencies
pip list
```

### Frontend Can't Reach Backend?
```bash
# Check Nginx
nginx -t
systemctl status nginx

# Check backend is running
curl http://localhost:5000/api/health
```

### SSL Issues?
```bash
# Renew certificate
certbot renew

# Check status
certbot certificates
```

## 📞 Support Links

- **Hostinger VPS**: https://www.hostinger.com/vps-hosting
- **Flask Docs**: https://flask.palletsprojects.com
- **DeepSeek API**: https://platform.deepseek.com
- **Let's Encrypt**: https://letsencrypt.org

---

## TL;DR

**Tech Stack**: Python Flask + Vanilla JavaScript  
**Hosting**: Hostinger VPS ($5-7/mo)  
**Domain**: freeresumemake.com  
**SSL**: Free (Let's Encrypt)  
**Deployment**: 1-2 hours with guide  
**Guide**: See DEPLOYMENT_GUIDE_HOSTINGER.md  

**Ready to deploy!** 🚀

---

**Last Updated**: November 18, 2025

