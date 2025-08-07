#!/bin/bash

# BeeMind EC2 Server Setup Script
# Run this script on your EC2 instance to prepare for deployment

set -e

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

# Update system
update_system() {
    log_info "Updating system packages..."
    sudo apt update && sudo apt upgrade -y
    log_success "System updated"
}

# Install Docker
install_docker() {
    log_info "Installing Docker..."
    
    # Remove old versions
    sudo apt-get remove -y docker docker-engine docker.io containerd runc || true
    
    # Install dependencies
    sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Add Docker's official GPG key
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Set up repository
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    # Start and enable Docker
    sudo systemctl start docker
    sudo systemctl enable docker
    
    log_success "Docker installed successfully"
}

# Install Docker Compose
install_docker_compose() {
    log_info "Installing Docker Compose..."
    
    # Download latest version
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # Make executable
    sudo chmod +x /usr/local/bin/docker-compose
    
    # Create symlink
    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    log_success "Docker Compose installed: $(docker-compose --version)"
}

# Install additional tools
install_tools() {
    log_info "Installing additional tools..."
    
    sudo apt-get install -y \
        git \
        curl \
        wget \
        unzip \
        htop \
        nginx-utils \
        openssl \
        jq \
        tree
    
    log_success "Additional tools installed"
}

# Setup firewall
setup_firewall() {
    log_info "Configuring firewall..."
    
    # Enable UFW
    sudo ufw --force enable
    
    # Allow SSH
    sudo ufw allow ssh
    sudo ufw allow 22
    
    # Allow HTTP and HTTPS
    sudo ufw allow 80
    sudo ufw allow 443
    
    # Allow specific ports for development (optional)
    sudo ufw allow 3000  # Next.js dev
    sudo ufw allow 8000  # FastAPI
    
    # Show status
    sudo ufw status
    
    log_success "Firewall configured"
}

# Create deployment directory
setup_deployment_dir() {
    log_info "Setting up deployment directory..."
    
    # Create directory
    sudo mkdir -p /opt/beemind
    sudo chown -R $USER:$USER /opt/beemind
    
    # Create subdirectories
    mkdir -p /opt/beemind/{data,logs,ssl,backups}
    
    log_success "Deployment directory created: /opt/beemind"
}

# Clone repository
clone_repository() {
    log_info "Cloning BeeMind repository..."
    
    cd /opt/beemind
    
    # Clone repository (you'll need to update this URL)
    git clone https://github.com/Zakarias-byte/beemind-ai.git .
    
    # Set up git for future pulls
    git config pull.rebase false
    
    log_success "Repository cloned successfully"
}

# Setup environment file
setup_environment() {
    log_info "Setting up environment configuration..."
    
    cd /opt/beemind
    
    # Copy example environment file
    cp deployment/.env.example deployment/.env
    
    log_warning "Please edit /opt/beemind/deployment/.env with your configuration"
    log_info "Required variables to set:"
    echo "  - DB_PASSWORD"
    echo "  - JWT_SECRET" 
    echo "  - REDIS_PASSWORD"
    echo "  - NEXTAUTH_SECRET"
    echo "  - GRAFANA_PASSWORD"
    
    log_success "Environment template created"
}

# Setup SSL directory
setup_ssl() {
    log_info "Setting up SSL directory..."
    
    cd /opt/beemind
    mkdir -p deployment/ssl
    chmod 755 deployment/ssl
    
    log_success "SSL directory ready for Let's Encrypt"
}

# Setup systemd service for auto-start
setup_systemd() {
    log_info "Setting up systemd service..."
    
    sudo tee /etc/systemd/system/beemind.service > /dev/null <<EOF
[Unit]
Description=BeeMind AI Platform
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/beemind
ExecStart=/usr/local/bin/docker-compose -f deployment/docker-compose.production.yml up -d
ExecStop=/usr/local/bin/docker-compose -f deployment/docker-compose.production.yml down
TimeoutStartSec=0
User=$USER
Group=$USER

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable beemind.service
    
    log_success "BeeMind systemd service created and enabled"
}

# Setup log rotation
setup_logrotate() {
    log_info "Setting up log rotation..."
    
    sudo tee /etc/logrotate.d/beemind > /dev/null <<EOF
/opt/beemind/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF
    
    log_success "Log rotation configured"
}

# Setup backup cron job
setup_backup_cron() {
    log_info "Setting up backup cron job..."
    
    # Create backup script
    cat > /opt/beemind/backup.sh << 'EOF'
#!/bin/bash
cd /opt/beemind
./deployment/backup.sh
EOF
    
    chmod +x /opt/beemind/backup.sh
    
    # Add to crontab (daily at 2 AM)
    (crontab -l 2>/dev/null; echo "0 2 * * * /opt/beemind/backup.sh") | crontab -
    
    log_success "Backup cron job configured (daily at 2 AM)"
}

# Main setup function
main() {
    log_info "🚀 Starting BeeMind EC2 server setup..."
    
    update_system
    install_docker
    install_docker_compose
    install_tools
    setup_firewall
    setup_deployment_dir
    clone_repository
    setup_environment
    setup_ssl
    setup_systemd
    setup_logrotate
    setup_backup_cron
    
    log_success "🎉 Server setup completed!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Edit /opt/beemind/deployment/.env with your configuration"
    echo "2. Run: cd /opt/beemind && ./deployment/deploy.sh"
    echo "3. Your BeeMind platform will be available at https://beemind.dev"
    echo ""
    log_warning "Please reboot the server to ensure all changes take effect:"
    echo "sudo reboot"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    log_error "Please do not run this script as root"
    exit 1
fi

# Run main function
main "$@"
