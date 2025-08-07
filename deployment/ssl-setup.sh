#!/bin/bash

# BeeMind SSL Certificate Setup Script
# Ferdig certbot-kommando for beemind.dev

set -e

# Colors
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

# Configuration
DOMAIN="beemind.dev"
EMAIL="admin@beemind.dev"
WEBROOT="/var/www/html"

# Create webroot directory
setup_webroot() {
    log_info "Setting up webroot for certificate validation..."
    sudo mkdir -p ${WEBROOT}
    sudo chown -R www-data:www-data ${WEBROOT}
    sudo chmod -R 755 ${WEBROOT}
    log_success "Webroot configured: ${WEBROOT}"
}

# Generate SSL certificates using certbot
generate_certificates() {
    log_info "Generating SSL certificates for ${DOMAIN}..."
    
    # Install certbot if not present
    if ! command -v certbot &> /dev/null; then
        log_info "Installing certbot..."
        sudo apt update
        sudo apt install -y certbot python3-certbot-nginx
    fi
    
    # Generate certificates for all subdomains
    sudo certbot certonly \
        --webroot \
        --webroot-path=${WEBROOT} \
        --email ${EMAIL} \
        --agree-tos \
        --no-eff-email \
        --expand \
        -d ${DOMAIN} \
        -d www.${DOMAIN} \
        -d api.${DOMAIN} \
        -d mlflow.${DOMAIN} \
        -d monitoring.${DOMAIN}
    
    log_success "SSL certificates generated successfully!"
}

# Setup automatic renewal
setup_renewal() {
    log_info "Setting up automatic certificate renewal..."
    
    # Create renewal script
    cat > /opt/beemind/ssl-renew.sh << 'EOF'
#!/bin/bash
# SSL Certificate Renewal Script

# Renew certificates
certbot renew --quiet

# Reload nginx in docker
docker-compose -f /opt/beemind/deployment/docker-compose.production.yml exec nginx nginx -s reload

# Log renewal
echo "$(date): SSL certificates renewed" >> /opt/beemind/logs/ssl-renewal.log
EOF
    
    chmod +x /opt/beemind/ssl-renew.sh
    
    # Add to crontab (twice daily)
    (crontab -l 2>/dev/null; echo "0 0,12 * * * /opt/beemind/ssl-renew.sh") | crontab -
    
    log_success "Automatic renewal configured (twice daily)"
}

# Test certificate
test_certificate() {
    log_info "Testing SSL certificate..."
    
    # Test certificate validity
    echo | openssl s_client -servername ${DOMAIN} -connect ${DOMAIN}:443 2>/dev/null | openssl x509 -noout -dates
    
    # Test HTTPS connectivity
    curl -I https://${DOMAIN} || log_warning "HTTPS test failed - check nginx configuration"
    
    log_success "SSL certificate test completed"
}

# Docker certbot command (alternative method)
docker_certbot() {
    log_info "Using Docker certbot method..."
    
    # Run certbot in Docker container
    docker run -it --rm \
        -v /opt/beemind/ssl:/etc/letsencrypt \
        -v ${WEBROOT}:/var/www/html \
        certbot/certbot certonly \
        --webroot \
        --webroot-path=/var/www/html \
        --email ${EMAIL} \
        --agree-tos \
        --no-eff-email \
        --expand \
        -d ${DOMAIN} \
        -d www.${DOMAIN} \
        -d api.${DOMAIN} \
        -d mlflow.${DOMAIN} \
        -d monitoring.${DOMAIN}
    
    log_success "Docker certbot completed"
}

# Main function
main() {
    log_info "🔐 Starting SSL certificate setup for ${DOMAIN}..."
    
    # Check if running in Docker environment
    if [ -f "/.dockerenv" ]; then
        log_info "Docker environment detected, using Docker certbot method"
        docker_certbot
    else
        log_info "Host environment detected, using native certbot"
        setup_webroot
        generate_certificates
        setup_renewal
        test_certificate
    fi
    
    log_success "🎉 SSL setup completed!"
    echo ""
    echo "📋 Certificate locations:"
    echo "  Certificates: /etc/letsencrypt/live/${DOMAIN}/"
    echo "  Private key:  /etc/letsencrypt/live/${DOMAIN}/privkey.pem"
    echo "  Full chain:   /etc/letsencrypt/live/${DOMAIN}/fullchain.pem"
    echo ""
    echo "🔄 Automatic renewal: Configured (twice daily via cron)"
}

# Run main function
main "$@"
