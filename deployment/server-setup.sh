#!/bin/bash

# BeeMind Server Setup Script for AWS EC2 Ubuntu 24.04
# This script prepares the server for BeeMind deployment

set -e  # Exit on any error

echo "🚀 Starting BeeMind Server Setup..."
echo "=================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo "🔧 Installing essential packages..."
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
    python3-certbot-nginx

# Install Python 3.11 and pip
echo "🐍 Installing Python 3.11..."
sudo apt install -y python3.11 python3.11-pip python3.11-venv python3.11-dev

# Install Node.js 18.x
echo "📦 Installing Node.js 18.x..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER

# Install Redis
echo "🔴 Installing Redis..."
sudo apt install -y redis-server

# Install PostgreSQL
echo "🐘 Installing PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib

# Configure PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE beemind;"
sudo -u postgres psql -c "CREATE USER beemind WITH PASSWORD 'beemind_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE beemind TO beemind;"

# Configure Redis
echo "🔴 Configuring Redis..."
sudo sed -i 's/bind 127.0.0.1/bind 0.0.0.0/' /etc/redis/redis.conf
sudo systemctl enable redis-server
sudo systemctl restart redis-server

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/beemind
sudo chown $USER:$USER /opt/beemind

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000
sudo ufw allow 8001
sudo ufw --force enable

# Create systemd service files
echo "⚙️ Creating systemd service files..."

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

# Reload systemd
sudo systemctl daemon-reload

# Create Nginx configuration
echo "🌐 Creating Nginx configuration..."
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

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/beemind.dev /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Start Nginx
sudo systemctl enable nginx
sudo systemctl restart nginx

# Create deployment script
echo "📝 Creating deployment script..."
tee /opt/beemind/deploy.sh > /dev/null <<EOF
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

chmod +x /opt/beemind/deploy.sh

echo "✅ Server setup completed!"
echo "=================================="
echo "Next steps:"
echo "1. Clone BeeMind repository to /opt/beemind"
echo "2. Set up Python virtual environment"
echo "3. Install Python dependencies"
echo "4. Build dashboard"
echo "5. Configure SSL with Let's Encrypt"
echo "6. Start services"
echo ""
echo "Run: cd /opt/beemind && ./deploy.sh"
