#!/bin/bash

# BeeMind Quick Deployment Script
# Run this script on your EC2 instance to deploy BeeMind

set -e

echo "🚀 BeeMind Quick Deployment Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    log_error "Please do not run this script as root"
    exit 1
fi

# Step 1: Update system
log_info "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Step 2: Install dependencies
log_info "Installing dependencies..."
sudo apt install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    htop \
    nginx \
    ufw \
    certbot \
    python3-certbot-nginx \
    python3.11 \
    python3.11-pip \
    python3.11-venv \
    python3.11-dev \
    redis-server \
    postgresql \
    postgresql-contrib

# Step 3: Install Node.js
log_info "Installing Node.js 18.x..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Step 4: Install Docker
log_info "Installing Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker $USER

# Step 5: Configure PostgreSQL
log_info "Configuring PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE beemind;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE USER beemind WITH PASSWORD 'beemind_password';" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE beemind TO beemind;" 2>/dev/null || true

# Step 6: Configure Redis
log_info "Configuring Redis..."
sudo sed -i 's/bind 127.0.0.1/bind 0.0.0.0/' /etc/redis/redis.conf
sudo systemctl enable redis-server
sudo systemctl restart redis-server

# Step 7: Create application directory
log_info "Creating application directory..."
sudo mkdir -p /opt/beemind
sudo chown $USER:$USER /opt/beemind

# Step 8: Configure firewall
log_info "Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000
sudo ufw allow 8001
sudo ufw --force enable

# Step 9: Create systemd services
log_info "Creating systemd services..."

# BeeMind Backend Service
sudo tee /etc/systemd/system/beemind-backend.service > /dev/null <<EOF
[Unit]
Description=BeeMind Backend API
After=network.target postgresql.service redis-server.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/beemind
Environment=PATH=/opt/beemind/venv/bin
ExecStart=/opt/beemind/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# BeeMind Dashboard Service
sudo tee /etc/systemd/system/beemind-dashboard.service > /dev/null <<EOF
[Unit]
Description=BeeMind Dashboard WebSocket
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/beemind
Environment=PATH=/opt/beemind/venv/bin
ExecStart=/opt/beemind/venv/bin/python dashboard_websocket.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload

# Step 10: Create Nginx configuration
log_info "Creating Nginx configuration..."
sudo tee /etc/nginx/sites-available/beemind.dev > /dev/null <<EOF
server {
    listen 80;
    server_name beemind.dev www.beemind.dev;

    # Main API
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Dashboard WebSocket
    location /ws {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Dashboard API
    location /api/dashboard {
        proxy_pass http://localhost:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Dashboard Frontend
    location /dashboard {
        alias /opt/beemind/dashboard/dist;
        try_files \$uri \$uri/ /dashboard/index.html;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000;
        access_log off;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/beemind.dev /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and start Nginx
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx

# Step 11: Clone or copy BeeMind code
log_info "Setting up BeeMind code..."

cd /opt/beemind

# Check if code already exists
if [ ! -f "main.py" ]; then
    log_warning "BeeMind code not found. Please copy your code to /opt/beemind"
    log_info "You can either:"
    log_info "1. Clone from git: git clone https://github.com/yourusername/beemind.git ."
    log_info "2. Copy from local machine: scp -r . ubuntu@16.16.73.195:/opt/beemind/"
    log_info "3. Upload files manually"
    read -p "Press Enter after you've copied the code..."
fi

# Step 12: Set up Python environment
log_info "Setting up Python environment..."
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Step 13: Set up dashboard
log_info "Setting up dashboard..."
cd dashboard
npm install
npm run build
cd ..

# Step 14: Create environment file
log_info "Creating environment configuration..."
cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://beemind:beemind_password@localhost/beemind
REDIS_URL=redis://localhost:6379

# Dashboard Configuration
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8001
WEBSOCKET_PATH=/ws
CORS_ORIGINS=https://beemind.dev,https://www.beemind.dev

# Production Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false

# Security
SECRET_KEY=beemind-production-secret-key-$(date +%s)
JWT_SECRET=beemind-jwt-secret-$(date +%s)

# Performance
MAX_CONCURRENT_CONNECTIONS=1000
ENABLE_GPU_ACCELERATION=false
EOF

# Step 15: Start services
log_info "Starting services..."
sudo systemctl start beemind-backend
sudo systemctl enable beemind-backend
sudo systemctl start beemind-dashboard
sudo systemctl enable beemind-dashboard

# Step 16: Set up SSL (optional)
log_info "Setting up SSL certificate..."
read -p "Do you want to set up SSL certificate with Let's Encrypt? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo certbot --nginx -d beemind.dev -d www.beemind.dev --non-interactive --agree-tos --email admin@beemind.dev
fi

# Step 17: Create deployment script
log_info "Creating deployment script..."
cat > deploy.sh << 'EOF'
#!/bin/bash

echo "🚀 Deploying BeeMind..."

# Stop services
sudo systemctl stop beemind-backend
sudo systemctl stop beemind-dashboard

# Update code
cd /opt/beemind
git pull origin main

# Update Python dependencies
source venv/bin/activate
pip install -r requirements.txt

# Build dashboard
cd dashboard
npm install
npm run build
cd ..

# Start services
sudo systemctl start beemind-backend
sudo systemctl start beemind-dashboard

echo "✅ Deployment completed!"
EOF

chmod +x deploy.sh

# Step 18: Final verification
log_info "Verifying deployment..."

# Check services
if sudo systemctl is-active --quiet beemind-backend; then
    log_success "Backend service is running"
else
    log_error "Backend service failed to start"
fi

if sudo systemctl is-active --quiet beemind-dashboard; then
    log_success "Dashboard service is running"
else
    log_error "Dashboard service failed to start"
fi

if sudo systemctl is-active --quiet nginx; then
    log_success "Nginx is running"
else
    log_error "Nginx failed to start"
fi

# Test endpoints
log_info "Testing endpoints..."
if curl -s http://localhost:8000/health > /dev/null; then
    log_success "Backend API is responding"
else
    log_warning "Backend API is not responding"
fi

if curl -s http://localhost:8001/api/dashboard/status > /dev/null; then
    log_success "Dashboard API is responding"
else
    log_warning "Dashboard API is not responding"
fi

log_success "🎉 BeeMind deployment completed!"
echo ""
echo "📋 Your BeeMind platform should now be available at:"
echo "   🌐 Main API: http://beemind.dev"
echo "   📊 Dashboard: http://beemind.dev/dashboard"
echo ""
echo "🔧 To update in the future, run:"
echo "   cd /opt/beemind && ./deploy.sh"
echo ""
echo "📊 To check logs:"
echo "   sudo journalctl -u beemind-backend -f"
echo "   sudo journalctl -u beemind-dashboard -f"
echo ""
log_warning "Please reboot the server to ensure all changes take effect:"
echo "sudo reboot"
