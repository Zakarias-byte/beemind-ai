#!/bin/bash

# BeeMind Systemd Service Installation Script
# Ferdig systemd-servicefil - auto oppstart

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
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

# Install systemd service
install_service() {
    log_info "Installing BeeMind systemd service..."
    
    # Copy service file to systemd directory
    sudo cp /opt/beemind/deployment/beemind.service /etc/systemd/system/
    
    # Set correct permissions
    sudo chmod 644 /etc/systemd/system/beemind.service
    
    # Reload systemd daemon
    sudo systemctl daemon-reload
    
    log_success "BeeMind service installed"
}

# Enable and start service
enable_service() {
    log_info "Enabling BeeMind service for auto-start..."
    
    # Enable service (auto-start on boot)
    sudo systemctl enable beemind.service
    
    # Start service now
    sudo systemctl start beemind.service
    
    log_success "BeeMind service enabled and started"
}

# Check service status
check_service() {
    log_info "Checking BeeMind service status..."
    
    # Get service status
    if sudo systemctl is-active --quiet beemind.service; then
        log_success "BeeMind service is ACTIVE"
    else
        log_error "BeeMind service is NOT ACTIVE"
        sudo systemctl status beemind.service --no-pager
        return 1
    fi
    
    # Check if enabled for auto-start
    if sudo systemctl is-enabled --quiet beemind.service; then
        log_success "BeeMind service is ENABLED for auto-start"
    else
        log_warning "BeeMind service is NOT ENABLED for auto-start"
    fi
    
    # Show detailed status
    sudo systemctl status beemind.service --no-pager
}

# Create service management script
create_management_script() {
    log_info "Creating service management script..."
    
    cat > /opt/beemind/manage-service.sh << 'EOF'
#!/bin/bash
# BeeMind Service Management Script

case "$1" in
    start)
        echo "Starting BeeMind service..."
        sudo systemctl start beemind.service
        ;;
    stop)
        echo "Stopping BeeMind service..."
        sudo systemctl stop beemind.service
        ;;
    restart)
        echo "Restarting BeeMind service..."
        sudo systemctl restart beemind.service
        ;;
    reload)
        echo "Reloading BeeMind service..."
        sudo systemctl reload beemind.service
        ;;
    status)
        echo "BeeMind service status:"
        sudo systemctl status beemind.service --no-pager
        ;;
    logs)
        echo "BeeMind service logs:"
        sudo journalctl -u beemind.service -f
        ;;
    enable)
        echo "Enabling BeeMind service for auto-start..."
        sudo systemctl enable beemind.service
        ;;
    disable)
        echo "Disabling BeeMind service auto-start..."
        sudo systemctl disable beemind.service
        ;;
    health)
        echo "Checking BeeMind health..."
        curl -f https://beemind.dev/health || echo "Health check failed"
        curl -f https://api.beemind.dev/health || echo "API health check failed"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|reload|status|logs|enable|disable|health}"
        echo ""
        echo "Commands:"
        echo "  start    - Start BeeMind service"
        echo "  stop     - Stop BeeMind service"
        echo "  restart  - Restart BeeMind service"
        echo "  reload   - Reload BeeMind service"
        echo "  status   - Show service status"
        echo "  logs     - Show service logs (follow mode)"
        echo "  enable   - Enable auto-start on boot"
        echo "  disable  - Disable auto-start on boot"
        echo "  health   - Check application health"
        exit 1
        ;;
esac
EOF
    
    chmod +x /opt/beemind/manage-service.sh
    
    log_success "Service management script created: /opt/beemind/manage-service.sh"
}

# Setup log rotation for systemd logs
setup_log_rotation() {
    log_info "Setting up log rotation for BeeMind service..."
    
    # Configure journald for BeeMind service
    sudo mkdir -p /etc/systemd/journald.conf.d
    
    cat > /tmp/beemind-journald.conf << EOF
[Journal]
# BeeMind service log configuration
SystemMaxUse=100M
SystemKeepFree=1G
SystemMaxFileSize=10M
SystemMaxFiles=10
MaxRetentionSec=30day
EOF
    
    sudo mv /tmp/beemind-journald.conf /etc/systemd/journald.conf.d/beemind.conf
    
    # Restart journald to apply changes
    sudo systemctl restart systemd-journald
    
    log_success "Log rotation configured for BeeMind service"
}

# Main function
main() {
    log_info "🐧 Installing BeeMind systemd service for auto-start..."
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        log_error "Please do not run this script as root"
        exit 1
    fi
    
    # Check if service file exists
    if [ ! -f "/opt/beemind/deployment/beemind.service" ]; then
        log_error "Service file not found: /opt/beemind/deployment/beemind.service"
        exit 1
    fi
    
    # Install and configure service
    install_service
    enable_service
    create_management_script
    setup_log_rotation
    
    # Wait a moment for service to start
    sleep 10
    
    # Check service status
    check_service
    
    log_success "🎉 BeeMind systemd service installation completed!"
    echo ""
    echo "📋 Service Management:"
    echo "  Status:   sudo systemctl status beemind.service"
    echo "  Start:    sudo systemctl start beemind.service"
    echo "  Stop:     sudo systemctl stop beemind.service"
    echo "  Restart:  sudo systemctl restart beemind.service"
    echo "  Logs:     sudo journalctl -u beemind.service -f"
    echo ""
    echo "🔧 Quick Management:"
    echo "  /opt/beemind/manage-service.sh {start|stop|restart|status|logs|health}"
    echo ""
    echo "🚀 Auto-start: ENABLED (service will start automatically on boot)"
}

# Run main function
main "$@"
