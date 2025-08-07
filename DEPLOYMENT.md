# BeeMind Production Deployment Guide

This guide walks you through deploying BeeMind to your EC2 instance with the domain `beemind.dev`.

## 🚀 Quick Start

### Prerequisites
- ✅ Domain: `beemind.dev` (DNS configured)
- ✅ EC2 Instance: Running Ubuntu 20.04+ 
- ✅ GitHub Repository: `beemind-ai` created
- ✅ SSH Access: To your EC2 instance

### 1. Server Setup (Run on EC2)

```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@16.16.73.195

# Download and run server setup script
wget https://raw.githubusercontent.com/Zakarias-byte/beemind-ai/main/deployment/server-setup.sh
chmod +x server-setup.sh
./server-setup.sh

# Reboot to apply all changes
sudo reboot
```

### 2. Configure Environment

```bash
# SSH back into server after reboot
ssh -i your-key.pem ubuntu@16.16.73.195

# Navigate to deployment directory
cd /opt/beemind

# Edit environment configuration
nano deployment/.env

# Set these required variables:
# DB_PASSWORD=your_secure_password
# JWT_SECRET=your_jwt_secret
# REDIS_PASSWORD=your_redis_password
# NEXTAUTH_SECRET=your_nextauth_secret
# GRAFANA_PASSWORD=your_grafana_password
```

### 3. Deploy BeeMind

```bash
# Run deployment script
cd /opt/beemind
./deployment/deploy.sh
```

### 4. Verify Deployment

After deployment completes, verify all services:

```bash
# Check service status
docker-compose -f deployment/docker-compose.production.yml ps

# Test endpoints
curl -f https://beemind.dev
curl -f https://api.beemind.dev/health
curl -f https://mlflow.beemind.dev
```

## 🌐 Access URLs

- **Dashboard**: https://beemind.dev
- **API**: https://api.beemind.dev
- **API Docs**: https://api.beemind.dev/docs
- **MLFlow**: https://mlflow.beemind.dev
- **Monitoring**: https://monitoring.beemind.dev

## 🔐 Default Credentials

### BeeMind Dashboard
- **Username**: `admin`
- **Password**: `BeeMind2025!`

### Grafana Monitoring
- **Username**: `admin`
- **Password**: Check your `.env` file for `GRAFANA_PASSWORD`

## 📊 GitHub Actions CI/CD

### Setup Secrets

Add these secrets to your GitHub repository:

1. Go to: `Settings > Secrets and variables > Actions`
2. Add these repository secrets:

```
EC2_HOST=16.16.73.195
EC2_USER=ubuntu
EC2_SSH_KEY=<your-private-ssh-key-content>
```

### Automatic Deployment

Every push to `main` branch will:
1. Build Docker images
2. Push to GitHub Container Registry
3. Deploy to your EC2 instance
4. Run health checks

## 🛠️ Management Commands

### View Logs
```bash
# All services
docker-compose -f deployment/docker-compose.production.yml logs -f

# Specific service
docker-compose -f deployment/docker-compose.production.yml logs -f beemind-api
docker-compose -f deployment/docker-compose.production.yml logs -f beemind-dashboard
```

### Restart Services
```bash
# Restart all
docker-compose -f deployment/docker-compose.production.yml restart

# Restart specific service
docker-compose -f deployment/docker-compose.production.yml restart beemind-api
```

### Update Application
```bash
# Pull latest code
cd /opt/beemind
git pull origin main

# Rebuild and restart
docker-compose -f deployment/docker-compose.production.yml up -d --build
```

### Backup Data
```bash
# Manual backup
cd /opt/beemind
./backup.sh

# Automated backups run daily at 2 AM via cron
```

## 🔧 Troubleshooting

### SSL Certificate Issues
```bash
# Check certificate status
docker-compose -f deployment/docker-compose.production.yml logs certbot

# Manually renew certificates
docker-compose -f deployment/docker-compose.production.yml run --rm certbot renew
```

### DNS Issues
```bash
# Check DNS resolution
dig beemind.dev A
dig api.beemind.dev A

# Check from different DNS servers
dig @8.8.8.8 beemind.dev A
dig @1.1.1.1 beemind.dev A
```

### Service Health
```bash
# Check all container health
docker ps

# Check specific service logs
docker-compose -f deployment/docker-compose.production.yml logs beemind-api

# Check system resources
htop
df -h
```

### Database Issues
```bash
# Connect to PostgreSQL
docker-compose -f deployment/docker-compose.production.yml exec postgres psql -U beemind -d beemind

# Check database size
docker-compose -f deployment/docker-compose.production.yml exec postgres psql -U beemind -d beemind -c "SELECT pg_size_pretty(pg_database_size('beemind'));"
```

## 📈 Monitoring

### Prometheus Metrics
- **URL**: https://monitoring.beemind.dev/prometheus
- **Targets**: API, Dashboard, Database, Redis

### Grafana Dashboards
- **URL**: https://monitoring.beemind.dev
- **Default Dashboards**: System metrics, application metrics, logs

### Health Endpoints
- **API Health**: https://api.beemind.dev/health
- **Dashboard Health**: https://beemind.dev/api/health

## 🔒 Security

### Firewall Rules
```bash
# Check UFW status
sudo ufw status

# Allow additional ports if needed
sudo ufw allow 9090  # Prometheus
sudo ufw allow 3001  # Grafana
```

### SSL Configuration
- **Certificates**: Automatically managed by Let's Encrypt
- **Renewal**: Automatic via cron job
- **Security Headers**: Configured in Nginx

### Access Control
- **API Rate Limiting**: 100 requests/minute
- **Login Rate Limiting**: 5 attempts/minute
- **CORS**: Configured for beemind.dev domain

## 📦 Backup & Recovery

### Backup Strategy
- **Database**: Daily PostgreSQL dumps
- **Files**: Application data and logs
- **Retention**: 30 days
- **Location**: `/backups/beemind/`

### Recovery Process
```bash
# Restore from backup
cd /opt/beemind
./restore.sh /backups/beemind/YYYYMMDD_HHMMSS/
```

## 🚨 Emergency Procedures

### Complete Service Restart
```bash
cd /opt/beemind
docker-compose -f deployment/docker-compose.production.yml down
docker-compose -f deployment/docker-compose.production.yml up -d
```

### Rollback Deployment
```bash
# Rollback to previous version
cd /opt/beemind
git log --oneline -10  # Find previous commit
git checkout <previous-commit-hash>
docker-compose -f deployment/docker-compose.production.yml up -d --build
```

### Emergency Contacts
- **System Admin**: admin@beemind.dev
- **GitHub Issues**: https://github.com/Zakarias-byte/beemind-ai/issues

---

## 📞 Support

For deployment issues or questions:
1. Check this documentation
2. Review logs for error messages
3. Create GitHub issue with details
4. Contact system administrator

**🎉 Congratulations! BeeMind is now running in production at https://beemind.dev**
