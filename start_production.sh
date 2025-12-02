#!/bin/bash
###############################################################################
# Resume Maker - Production Startup Script for Ubuntu VPS
# Run this after deploying the code to start the application
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
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

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"

print_step "Resume Maker - Production Startup"
echo "Script directory: $SCRIPT_DIR"
echo "Backend directory: $BACKEND_DIR"

# Check if .env file exists
if [ ! -f "$BACKEND_DIR/.env" ]; then
    print_warning ".env file not found. Creating template..."
    cat > "$BACKEND_DIR/.env" << 'EOF'
# DeepSeek API Configuration
DEEPSEEK_API_KEY=your_api_key_here

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_APP=app.py

# Server Configuration
HOST=0.0.0.0
PORT=5000
EOF
    print_warning "Please edit $BACKEND_DIR/.env and add your DEEPSEEK_API_KEY"
    print_error "Cannot start without API key. Exiting."
    exit 1
fi

# Check for API key
if grep -q "your_api_key_here" "$BACKEND_DIR/.env"; then
    print_error "Please update DEEPSEEK_API_KEY in $BACKEND_DIR/.env"
    exit 1
fi

print_success ".env file found"

# Create necessary directories
print_step "Creating directories"
mkdir -p "$BACKEND_DIR/data"
mkdir -p "$BACKEND_DIR/output"
chmod -R 755 "$BACKEND_DIR/data"
chmod -R 755 "$BACKEND_DIR/output"
print_success "Directories created"

# Check for virtual environment
print_step "Checking Python environment"
if [ ! -d "$BACKEND_DIR/venv" ]; then
    print_warning "Virtual environment not found. Creating..."
    cd "$BACKEND_DIR"
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate venv and install dependencies
cd "$BACKEND_DIR"
source venv/bin/activate
print_success "Virtual environment activated"

print_step "Installing dependencies"
pip install --upgrade pip -q
pip install -r "$SCRIPT_DIR/requirements.txt" -q
print_success "Dependencies installed"

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    print_error "gunicorn not found. Installing..."
    pip install gunicorn
fi
print_success "gunicorn is available"

# Test the API health endpoint
print_step "Starting application"

# Check if port 5000 is already in use
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_warning "Port 5000 is already in use. Killing existing process..."
    fuser -k 5000/tcp 2>/dev/null || true
    sleep 2
fi

# Export environment variables
export FLASK_ENV=production
export FLASK_DEBUG=False

# Start with gunicorn
echo ""
echo -e "${GREEN}Starting Resume Maker with gunicorn...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

# Run gunicorn with optimized settings for production
# -w 4: 4 worker processes
# -b 0.0.0.0:5000: bind to all interfaces on port 5000
# --timeout 300: allow 5 minutes for AI generation
# --access-logfile -: log to stdout
# --error-logfile -: log errors to stderr
gunicorn \
    -w 4 \
    -b 0.0.0.0:5000 \
    --timeout 300 \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance \
    app:app

