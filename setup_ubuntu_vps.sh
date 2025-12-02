#!/bin/bash
###############################################################################
# Resume Maker - Quick Ubuntu VPS Setup Script
# This script sets up everything needed for production on Ubuntu VPS
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_warning "This script should be run as root for system package installation"
   print_warning "Continuing without sudo - some steps may fail"
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_DIR="$SCRIPT_DIR"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"

print_step "Resume Maker - Ubuntu VPS Setup"
echo "Application directory: $APP_DIR"

# Get API key from user
echo ""
read -p "Enter your DeepSeek API Key: " DEEPSEEK_API_KEY
if [ -z "$DEEPSEEK_API_KEY" ]; then
    print_error "API key is required"
    exit 1
fi

read -p "Enter your domain (or press Enter to skip): " DOMAIN
if [ -z "$DOMAIN" ]; then
    DOMAIN=$(hostname -I | awk '{print $1}')
    print_warning "Using IP address: $DOMAIN"
fi

# 1. Install system packages
print_step "1/7 - Installing System Packages"
if command -v apt &> /dev/null; then
    sudo apt update -y || apt update -y || true
    sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential nginx curl || \
    apt install -y python3 python3-pip python3-venv python3-dev build-essential nginx curl || true
    print_success "System packages installed"
else
    print_warning "apt not found, skipping system package installation"
fi

# 2. Install Node.js and PM2
print_step "2/7 - Installing Node.js and PM2"
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash - || curl -fsSL https://deb.nodesource.com/setup_18.x | bash - || true
    sudo apt install -y nodejs || apt install -y nodejs || true
fi
if command -v npm &> /dev/null; then
    sudo npm install -g pm2 || npm install -g pm2 || true
    print_success "PM2 installed"
else
    print_warning "npm not found, PM2 not installed"
fi

# 3. Setup Python virtual environment
print_step "3/7 - Setting Up Python Environment"
cd "$BACKEND_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r "$APP_DIR/requirements.txt"
print_success "Python environment configured"

# 4. Create .env file
print_step "4/7 - Creating Environment Configuration"
cat > "$BACKEND_DIR/.env" << EOF
# DeepSeek API Configuration
DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_APP=app.py

# Server Configuration
HOST=0.0.0.0
PORT=5000

# Domain
DOMAIN=$DOMAIN
EOF
chmod 600 "$BACKEND_DIR/.env"
print_success "Environment file created"

# 5. Create necessary directories
print_step "5/7 - Creating Directories"
mkdir -p "$BACKEND_DIR/output"
mkdir -p "$BACKEND_DIR/data"
mkdir -p "$APP_DIR/logs"
chmod -R 755 "$BACKEND_DIR/output"
chmod -R 755 "$BACKEND_DIR/data"
print_success "Directories created"

# 6. Configure Nginx (if available)
print_step "6/7 - Configuring Nginx"
if command -v nginx &> /dev/null; then
    NGINX_CONF="/etc/nginx/sites-available/resumemaker"
    
    sudo tee "$NGINX_CONF" > /dev/null << 'NGINXCONF'
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
    
    root FRONTEND_PATH;
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
}
NGINXCONF

    # Replace placeholders
    sudo sed -i "s|FRONTEND_PATH|$FRONTEND_DIR|g" "$NGINX_CONF"
    sudo sed -i "s|server_name _;|server_name $DOMAIN;|g" "$NGINX_CONF"
    
    # Enable site
    sudo ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
    
    # Test and reload
    sudo nginx -t && sudo systemctl reload nginx
    print_success "Nginx configured"
else
    print_warning "Nginx not found, skipping configuration"
fi

# 7. Start application with PM2
print_step "7/7 - Starting Application"
cd "$APP_DIR"

# Stop existing instance if any
pm2 delete resumemaker 2>/dev/null || true

# Update ecosystem config with correct paths
cat > "$APP_DIR/ecosystem.config.js" << EOF
module.exports = {
  apps: [{
    name: 'resumemaker',
    cwd: '$BACKEND_DIR',
    script: 'venv/bin/gunicorn',
    args: '-w 4 -b 127.0.0.1:5000 --timeout 300 --access-logfile - --error-logfile - app:app',
    interpreter: 'none',
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      FLASK_ENV: 'production',
      FLASK_DEBUG: 'False'
    },
    error_file: '$APP_DIR/logs/error.log',
    out_file: '$APP_DIR/logs/access.log',
    time: true
  }]
};
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup systemd -u $(whoami) --hp $HOME 2>/dev/null || true

print_success "Application started"

# Test
sleep 3
if curl -s http://localhost:5000/api/health | grep -q "healthy"; then
    print_success "Backend is running correctly!"
else
    print_warning "Backend might not be responding. Check: pm2 logs resumemaker"
fi

# Final message
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║           🎉  SETUP COMPLETED SUCCESSFULLY!  🎉            ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📍 Access your application:${NC}"
echo -e "   ${BLUE}http://$DOMAIN${NC}"
echo ""
echo -e "${YELLOW}🛠️  Useful Commands:${NC}"
echo -e "   View status:     ${BLUE}pm2 status${NC}"
echo -e "   View logs:       ${BLUE}pm2 logs resumemaker${NC}"
echo -e "   Restart app:     ${BLUE}pm2 restart resumemaker${NC}"
echo -e "   Stop app:        ${BLUE}pm2 stop resumemaker${NC}"
echo ""
echo -e "${YELLOW}📁 Important Files:${NC}"
echo -e "   .env file:       ${BLUE}$BACKEND_DIR/.env${NC}"
echo -e "   Logs:            ${BLUE}$APP_DIR/logs/${NC}"
echo ""

