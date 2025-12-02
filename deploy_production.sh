#!/bin/bash
###############################################################################
# Resume Maker - Complete Production Deployment Script
# This script sets up everything needed for production deployment
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
APP_DIR="/var/www/resumemaker"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"

# Helper functions
print_step() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
fi

print_step "🚀 Resume Maker - Production Deployment"
echo "This script will:"
echo "  1. Install all system requirements"
echo "  2. Set up Python environment"
echo "  3. Configure Nginx reverse proxy"
echo "  4. Set up PM2 process manager"
echo "  5. Configure security settings"
echo ""
read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Get configuration from user
print_step "📋 Configuration"
read -p "Enter your DeepSeek API Key: " DEEPSEEK_API_KEY
read -p "Enter your domain (or press Enter to use IP): " DOMAIN
read -p "Do you want to set up SSL with Let's Encrypt? (y/n): " -n 1 -r SETUP_SSL
echo

if [ -z "$DOMAIN" ]; then
    DOMAIN=$(hostname -I | awk '{print $1}')
    SETUP_SSL="n"
fi

# Generate secret key
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))' 2>/dev/null || openssl rand -hex 32)

print_step "1/10 - Updating System Packages"
apt update && apt upgrade -y
print_success "System updated"

print_step "2/10 - Installing System Requirements"
apt install -y curl wget git vim ufw htop build-essential
apt install -y python3 python3-pip python3-venv python3-dev
apt install -y nginx
apt install -y libssl-dev libffi-dev
print_success "System packages installed"

print_step "3/10 - Installing Node.js and PM2"
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
fi
npm install -g pm2
print_success "Node.js and PM2 installed"

print_step "4/10 - Setting Up Python Virtual Environment"
cd $BACKEND_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r $APP_DIR/requirements.txt
pip install gunicorn
deactivate
print_success "Python environment configured"

print_step "5/10 - Creating Environment Configuration"
cat > $BACKEND_DIR/.env << EOF
# DeepSeek API Configuration
DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_APP=app.py

# Application Settings
SECRET_KEY=$SECRET_KEY

# Domain
DOMAIN=$DOMAIN

# Server Configuration
HOST=0.0.0.0
PORT=5000
EOF
chmod 600 $BACKEND_DIR/.env
print_success "Environment file created"

print_step "6/10 - Creating Application Directories"
mkdir -p $BACKEND_DIR/output
mkdir -p $BACKEND_DIR/data
mkdir -p /var/log/resumemaker
chmod -R 755 $APP_DIR
chmod -R 777 $BACKEND_DIR/output
chmod -R 777 $BACKEND_DIR/data
print_success "Directories created"

print_step "7/10 - Configuring PM2 Process Manager"
cat > $APP_DIR/ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'resumemaker',
    cwd: '$BACKEND_DIR',
    script: 'venv/bin/gunicorn',
    args: '-w 4 -b 127.0.0.1:5000 --timeout 300 app:app',
    interpreter: 'none',
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      FLASK_ENV: 'production'
    },
    error_file: '/var/log/resumemaker/error.log',
    out_file: '/var/log/resumemaker/access.log',
    time: true
  }]
};
EOF

# Stop PM2 if running
pm2 delete resumemaker 2>/dev/null || true

# Start application
cd $APP_DIR
pm2 start ecosystem.config.js
pm2 save
pm2 startup systemd -u root --hp /root

print_success "PM2 configured and application started"

print_step "8/10 - Updating Frontend API Configuration"
if grep -q "localhost:5000" "$FRONTEND_DIR/app.js"; then
    sed -i "s|const API_BASE_URL = 'http://localhost:5000/api';|const API_BASE_URL = '/api';|g" $FRONTEND_DIR/app.js
    print_success "Frontend API URL updated"
else
    print_warning "Frontend API URL already configured or not found"
fi

print_step "9/10 - Configuring Nginx"
cat > /etc/nginx/sites-available/resumemaker << 'NGINXCONF'
# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=resume_limit:10m rate=2r/s;

upstream resumemaker_backend {
    server 127.0.0.1:5000 fail_timeout=0;
}

server {
    listen 80;
    listen [::]:80;
    server_name _;
    
    root /var/www/resumemaker/frontend;
    index index.html;
    
    client_max_body_size 10M;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript;
    
    # Frontend
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "public, max-age=3600";
    }
    
    # Backend API
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        
        proxy_pass http://resumemaker_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    # Resume generation (stricter rate limit)
    location /api/generate-resume {
        limit_req zone=resume_limit burst=3 nodelay;
        
        proxy_pass http://resumemaker_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    # Static files caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # Security
    location ~ /\. {
        deny all;
    }
    
    # Logs
    access_log /var/log/nginx/resumemaker_access.log;
    error_log /var/log/nginx/resumemaker_error.log;
}
NGINXCONF

# Update server_name with actual domain
sed -i "s|server_name _;|server_name $DOMAIN;|g" /etc/nginx/sites-available/resumemaker

# Enable site
ln -sf /etc/nginx/sites-available/resumemaker /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and restart
nginx -t
systemctl restart nginx
systemctl enable nginx

print_success "Nginx configured"

print_step "10/10 - Configuring Firewall"
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
print_success "Firewall configured"

# Optional SSL setup
if [[ $SETUP_SSL =~ ^[Yy]$ ]]; then
    print_step "Setting Up SSL Certificate"
    apt install -y certbot python3-certbot-nginx
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN --redirect
    print_success "SSL certificate installed"
fi

# Set up backup script
print_step "Setting Up Automated Backups"
mkdir -p /backup/resumemaker
cat > /usr/local/bin/backup-resumemaker.sh << 'BACKUPSCRIPT'
#!/bin/bash
BACKUP_DIR="/backup/resumemaker"
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf "$BACKUP_DIR/backup_$DATE.tar.gz" \
    --exclude='backend/venv' \
    --exclude='backend/__pycache__' \
    --exclude='backend/output/*.pdf' \
    /var/www/resumemaker
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +7 -delete
BACKUPSCRIPT
chmod +x /usr/local/bin/backup-resumemaker.sh
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-resumemaker.sh") | crontab -
print_success "Backup script created (runs daily at 2 AM)"

# Test application
print_step "Testing Application"
sleep 3
if curl -s http://localhost:5000/api/health | grep -q "healthy"; then
    print_success "Backend is running correctly"
else
    print_warning "Backend might not be responding. Check logs with: pm2 logs resumemaker"
fi

# Print completion message
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║           🎉  DEPLOYMENT COMPLETED SUCCESSFULLY!  🎉       ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📍 Access your application:${NC}"
if [[ $SETUP_SSL =~ ^[Yy]$ ]]; then
    echo -e "   ${BLUE}https://$DOMAIN${NC}"
else
    echo -e "   ${BLUE}http://$DOMAIN${NC}"
fi
echo ""
echo -e "${YELLOW}🛠️  Useful Commands:${NC}"
echo -e "   View status:     ${BLUE}pm2 status${NC}"
echo -e "   View logs:       ${BLUE}pm2 logs resumemaker${NC}"
echo -e "   Restart app:     ${BLUE}pm2 restart resumemaker${NC}"
echo -e "   Monitor app:     ${BLUE}pm2 monit${NC}"
echo -e "   Restart Nginx:   ${BLUE}systemctl restart nginx${NC}"
echo ""
echo -e "${YELLOW}📊 Check Application Status:${NC}"
echo -e "   Backend health:  ${BLUE}curl http://localhost:5000/api/health${NC}"
echo -e "   PM2 status:      ${BLUE}pm2 status${NC}"
echo -e "   Nginx status:    ${BLUE}systemctl status nginx${NC}"
echo ""
echo -e "${YELLOW}📁 Important Paths:${NC}"
echo -e "   Application:     ${BLUE}$APP_DIR${NC}"
echo -e "   Backend:         ${BLUE}$BACKEND_DIR${NC}"
echo -e "   Frontend:        ${BLUE}$FRONTEND_DIR${NC}"
echo -e "   Logs:            ${BLUE}/var/log/resumemaker/${NC}"
echo -e "   Backups:         ${BLUE}/backup/resumemaker/${NC}"
echo ""
echo -e "${GREEN}✅ Your Resume Maker is now live and ready to use!${NC}"
echo ""

