# 🚀 BeeMind Deployment Guide for beemind.dev

## 📋 Overview

This guide will help you deploy BeeMind to your AWS EC2 instance and make it available at `beemind.dev`.

### Prerequisites
- AWS EC2 instance running Ubuntu 24.04 LTS
- SSH access with key pair `cybersecurity-key`
- Domain `beemind.dev` configured with DNS
- Git repository access

---

## 🎯 Step 1: Connect to Your Server

```bash
# Connect to your EC2 instance
ssh -i ~/.ssh/cybersecurity-key ubuntu@16.16.73.195
```

---

## 🔧 Step 2: Server Setup

Run the server setup script:

```bash
# Download and run the setup script
curl -fsSL https://raw.githubusercontent.com/yourusername/beemind/main/deployment/server-setup.sh | bash
```

**What this script does:**
- Updates system packages
- Installs Python 3.11, Node.js 18, Docker, Redis, PostgreSQL
- Configures firewall (UFW)
- Sets up Nginx with reverse proxy
- Creates systemd services
- Prepares deployment directory

---

## 📦 Step 3: Clone Repository

```bash
# Navigate to application directory
cd /opt/beemind

# Clone your repository (replace with your actual repo URL)
git clone https://github.com/yourusername/beemind.git .

# Or if you want to copy files from your local machine:
# (Run this from your local machine)
scp -i ~/.ssh/cybersecurity-key -r . ubuntu@16.16.73.195:/opt/beemind/
```

---

## 🐍 Step 4: Python Environment Setup

```bash
cd /opt/beemind

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install additional dependencies for production
pip install gunicorn uvicorn[standard]
```

---

## 📱 Step 5: Dashboard Setup

```bash
cd /opt/beemind/dashboard

# Install Node.js dependencies
npm install

# Build for production
npm run build

# Verify build
ls -la dist/
```

---

## ⚙️ Step 6: Environment Configuration

Create environment file:

```bash
cd /opt/beemind

# Create environment file
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
SECRET_KEY=your-super-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Performance
MAX_CONCURRENT_CONNECTIONS=1000
ENABLE_GPU_ACCELERATION=false
EOF
```

---

## 🔒 Step 7: SSL Certificate Setup

```bash
# Install SSL certificate with Let's Encrypt
sudo certbot --nginx -d beemind.dev -d www.beemind.dev

# Test SSL renewal
sudo certbot renew --dry-run
```

---

## 🚀 Step 8: Start Services

```bash
cd /opt/beemind

# Start backend service
sudo systemctl start beemind-backend
sudo systemctl enable beemind-backend

# Start dashboard service
sudo systemctl start beemind-dashboard
sudo systemctl enable beemind-dashboard

# Check service status
sudo systemctl status beemind-backend
sudo systemctl status beemind-dashboard
```

---

## ✅ Step 9: Verify Deployment

### Test API Endpoints:
```bash
# Test main API
curl https://beemind.dev/health

# Test dashboard API
curl https://beemind.dev/api/dashboard/status

# Test WebSocket (using wscat if installed)
wscat -c wss://beemind.dev/ws
```

### Test Dashboard:
- Open `https://beemind.dev/dashboard` in your browser
- Verify all components load correctly
- Test WebSocket connections
- Check real-time data updates

---

## 🔄 Step 10: Automated Deployment

Use the deployment script for future updates:

```bash
cd /opt/beemind

# Run deployment script
./deploy.sh
```

---

## 📊 Monitoring & Maintenance

### Check Logs:
```bash
# Backend logs
sudo journalctl -u beemind-backend -f

# Dashboard logs
sudo journalctl -u beemind-dashboard -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### System Status:
```bash
# Check all services
sudo systemctl status beemind-backend beemind-dashboard nginx redis-server postgresql

# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
htop
```

### Backup Database:
```bash
# Create backup
pg_dump -U beemind beemind > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
psql -U beemind beemind < backup_file.sql
```

---

## 🚨 Troubleshooting

### Common Issues:

1. **Service won't start:**
   ```bash
   sudo systemctl status beemind-backend
   sudo journalctl -u beemind-backend -n 50
   ```

2. **Port already in use:**
   ```bash
   sudo netstat -tlnp | grep :8000
   sudo netstat -tlnp | grep :8001
   ```

3. **Permission issues:**
   ```bash
   sudo chown -R ubuntu:ubuntu /opt/beemind
   sudo chmod +x /opt/beemind/deploy.sh
   ```

4. **SSL certificate issues:**
   ```bash
   sudo certbot certificates
   sudo certbot renew
   ```

5. **Database connection issues:**
   ```bash
   sudo -u postgres psql -c "\l"
   sudo -u postgres psql -c "SELECT * FROM pg_user;"
   ```

---

## 📈 Performance Optimization

### Nginx Optimization:
```bash
# Edit Nginx configuration
sudo nano /etc/nginx/nginx.conf

# Add to http block:
client_max_body_size 100M;
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
```

### Python Optimization:
```bash
# Use Gunicorn for production
pip install gunicorn

# Update systemd service to use Gunicorn
sudo nano /etc/systemd/system/beemind-backend.service
```

---

## 🔄 Update Process

For future updates:

1. **Pull latest code:**
   ```bash
   cd /opt/beemind
   git pull origin main
   ```

2. **Update dependencies:**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Rebuild dashboard:**
   ```bash
   cd dashboard
   npm install
   npm run build
   ```

4. **Restart services:**
   ```bash
   sudo systemctl restart beemind-backend
   sudo systemctl restart beemind-dashboard
   ```

---

## 🎉 Success!

Your BeeMind platform should now be available at:
- **Main API**: https://beemind.dev
- **Dashboard**: https://beemind.dev/dashboard
- **API Documentation**: https://beemind.dev/docs

### Final Checklist:
- ✅ Server setup completed
- ✅ Repository cloned
- ✅ Python environment configured
- ✅ Dashboard built
- ✅ SSL certificate installed
- ✅ Services running
- ✅ All endpoints responding
- ✅ Dashboard accessible

---

**BeeMind is now live at beemind.dev! 🐝🧠**
