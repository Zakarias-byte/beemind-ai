#!/bin/bash

# BeeMind Production Deployment Script
# This script deploys BeeMind to production environment with SSL and monitoring

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="beemind.dev"
EMAIL="admin@beemind.dev"
COMPOSE_FILE="docker-compose.production.yml"

# Functions
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

check_requirements() {
    log_info "Checking deployment requirements..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        log_error ".env file not found. Please create it with required environment variables."
        exit 1
    fi
    
    log_success "All requirements satisfied"
}

setup_environment() {
    log_info "Setting up deployment environment..."
    
    # Create necessary directories
    mkdir -p data/beemind
    mkdir -p logs
    mkdir -p ssl
    mkdir -p monitoring/grafana/provisioning
    mkdir -p init-scripts
    
    # Set proper permissions
    chmod 755 data/beemind
    chmod 755 logs
    chmod 755 ssl
    
    log_success "Environment setup complete"
}

generate_secrets() {
    log_info "Generating secure secrets..."
    
    # Check if .env already has secrets
    if grep -q "JWT_SECRET=" .env && grep -q "DB_PASSWORD=" .env; then
        log_info "Secrets already exist in .env file"
        return
    fi
    
    # Generate random secrets
    JWT_SECRET=$(openssl rand -base64 32)
    DB_PASSWORD=$(openssl rand -base64 16)
    REDIS_PASSWORD=$(openssl rand -base64 16)
    NEXTAUTH_SECRET=$(openssl rand -base64 32)
    GRAFANA_PASSWORD=$(openssl rand -base64 12)
    
    # Append to .env if not exists
    echo "" >> .env
    echo "# Generated secrets" >> .env
    echo "JWT_SECRET=${JWT_SECRET}" >> .env
    echo "DB_PASSWORD=${DB_PASSWORD}" >> .env
    echo "REDIS_PASSWORD=${REDIS_PASSWORD}" >> .env
    echo "NEXTAUTH_SECRET=${NEXTAUTH_SECRET}" >> .env
    echo "GRAFANA_PASSWORD=${GRAFANA_PASSWORD}" >> .env
    
    log_success "Secrets generated and saved to .env"
    log_warning "Please save these credentials securely!"
}

setup_ssl() {
    log_info "Setting up SSL certificates..."
    
    # Check if certificates already exist
    if [ -f "ssl/live/${DOMAIN}/fullchain.pem" ]; then
        log_info "SSL certificates already exist"
        return
    fi
    
    # Create temporary nginx config for certificate generation
    cat > nginx/conf.d/temp.conf << EOF
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN} api.${DOMAIN};
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}
EOF
    
    # Start nginx for certificate generation
    docker-compose -f ${COMPOSE_FILE} up -d nginx
    
    # Wait for nginx to start
    sleep 10
    
    # Generate SSL certificates
    docker-compose -f ${COMPOSE_FILE} run --rm certbot
    
    # Remove temporary config
    rm nginx/conf.d/temp.conf
    
    log_success "SSL certificates generated"
}

build_images() {
    log_info "Building Docker images..."
    
    # Build BeeMind API
    docker build -t beemind-api:latest ..
    
    # Build Dashboard (create production Dockerfile if not exists)
    if [ ! -f "../admin-dashboard/Dockerfile.production" ]; then
        cat > ../admin-dashboard/Dockerfile.production << EOF
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
ENV PORT 3000
CMD ["node", "server.js"]
EOF
    fi
    
    docker build -t beemind-dashboard:latest -f ../admin-dashboard/Dockerfile.production ../admin-dashboard
    
    log_success "Docker images built successfully"
}

create_monitoring_config() {
    log_info "Creating monitoring configuration..."
    
    # Prometheus configuration
    cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'beemind-api'
    static_configs:
      - targets: ['beemind-api:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'beemind-dashboard'
    static_configs:
      - targets: ['beemind-dashboard:3000']
    metrics_path: '/api/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
EOF
    
    # Create MLFlow requirements
    cat > mlflow-requirements.txt << EOF
mlflow==2.8.1
psycopg2-binary==2.9.7
boto3==1.29.7
EOF
    
    log_success "Monitoring configuration created"
}

deploy_services() {
    log_info "Deploying BeeMind services..."
    
    # Pull latest images
    docker-compose -f ${COMPOSE_FILE} pull
    
    # Start all services
    docker-compose -f ${COMPOSE_FILE} up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 30
    
    # Check service health
    for service in beemind-api beemind-dashboard postgres redis; do
        if docker-compose -f ${COMPOSE_FILE} ps ${service} | grep -q "Up (healthy)"; then
            log_success "${service} is healthy"
        else
            log_warning "${service} health check pending..."
        fi
    done
    
    log_success "BeeMind services deployed successfully"
}

setup_database() {
    log_info "Setting up database..."
    
    # Wait for PostgreSQL to be ready
    docker-compose -f ${COMPOSE_FILE} exec -T postgres pg_isready -U beemind -d beemind
    
    # Create MLFlow database
    docker-compose -f ${COMPOSE_FILE} exec -T postgres psql -U beemind -d beemind -c "CREATE DATABASE mlflow;"
    
    # Run database migrations (if any)
    # docker-compose -f ${COMPOSE_FILE} exec beemind-api python -m alembic upgrade head
    
    log_success "Database setup complete"
}

create_backup_script() {
    log_info "Creating backup script..."
    
    cat > backup.sh << 'EOF'
#!/bin/bash
# BeeMind Backup Script

BACKUP_DIR="/backups/beemind/$(date +%Y%m%d_%H%M%S)"
mkdir -p ${BACKUP_DIR}

# Backup PostgreSQL
docker-compose -f docker-compose.production.yml exec -T postgres pg_dump -U beemind beemind > ${BACKUP_DIR}/beemind_db.sql
docker-compose -f docker-compose.production.yml exec -T postgres pg_dump -U beemind mlflow > ${BACKUP_DIR}/mlflow_db.sql

# Backup data volumes
docker run --rm -v beemind_postgres_data:/data -v ${BACKUP_DIR}:/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .
docker run --rm -v beemind_redis_data:/data -v ${BACKUP_DIR}:/backup alpine tar czf /backup/redis_data.tar.gz -C /data .
docker run --rm -v beemind_mlflow_artifacts:/data -v ${BACKUP_DIR}:/backup alpine tar czf /backup/mlflow_artifacts.tar.gz -C /data .

# Backup application data
tar czf ${BACKUP_DIR}/app_data.tar.gz data/ logs/

echo "Backup completed: ${BACKUP_DIR}"
EOF
    
    chmod +x backup.sh
    log_success "Backup script created"
}

print_deployment_info() {
    log_success "🎉 BeeMind deployment completed successfully!"
    echo ""
    echo "🌐 Access URLs:"
    echo "   Dashboard: https://${DOMAIN}"
    echo "   API:       https://api.${DOMAIN}"
    echo "   Docs:      https://api.${DOMAIN}/docs"
    echo "   Monitoring: https://monitoring.${DOMAIN}"
    echo ""
    echo "📊 Default Credentials:"
    echo "   Admin: admin / BeeMind2025!"
    echo "   Grafana: admin / $(grep GRAFANA_PASSWORD .env | cut -d'=' -f2)"
    echo ""
    echo "🔧 Management Commands:"
    echo "   View logs:    docker-compose -f ${COMPOSE_FILE} logs -f [service]"
    echo "   Restart:      docker-compose -f ${COMPOSE_FILE} restart [service]"
    echo "   Stop:         docker-compose -f ${COMPOSE_FILE} down"
    echo "   Backup:       ./backup.sh"
    echo ""
    echo "📁 Important Files:"
    echo "   Environment:  .env"
    echo "   SSL Certs:    ssl/"
    echo "   App Data:     data/"
    echo "   Logs:         logs/"
    echo ""
    log_warning "Please change default passwords after first login!"
}

# Main deployment flow
main() {
    log_info "🚀 Starting BeeMind production deployment..."
    
    check_requirements
    setup_environment
    generate_secrets
    create_monitoring_config
    build_images
    setup_ssl
    deploy_services
    setup_database
    create_backup_script
    
    print_deployment_info
}

# Run main function
main "$@"
