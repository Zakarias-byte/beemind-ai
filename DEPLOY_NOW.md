# 🚀 BeeMind Deployment Guide - DEPLOY NOW!

Alt er klart for deployment! Følg disse stegene for å få BeeMind live på https://beemind.dev

## 📋 Pre-deployment Checklist ✅

- ✅ DNS: beemind.dev peker til 16.16.73.195
- ✅ EC2: Ubuntu server klar
- ✅ GitHub: Repository opprettet
- ✅ Kode: Alle filer committed lokalt
- ✅ Infrastructure: nginx + SSL + Docker Compose + systemd + CORS

## 🔥 STEP 1: Push til GitHub

```bash
# I Windows PowerShell (c:/Users/zchib/beemind/)
git push -u origin main
```

**Hvis du får authentication error:**
```bash
# Set up GitHub credentials
git config --global user.name "Zakarias-byte"
git config --global user.email "your-email@example.com"

# Use GitHub token or SSH key for authentication
git remote set-url origin https://ghp_YOUR_TOKEN@github.com/Zakarias-byte/beemind-ai.git
git push -u origin main
```

## 🔥 STEP 2: SSH til EC2 og Setup Server

```bash
# SSH til din EC2 (erstatt med din private key path)
ssh -i "your-key.pem" ubuntu@16.16.73.195

# Download og kjør server setup
wget https://raw.githubusercontent.com/Zakarias-byte/beemind-ai/main/deployment/server-setup.sh
chmod +x server-setup.sh
./server-setup.sh

# Reboot server
sudo reboot
```

## 🔥 STEP 3: SSH tilbake og Deploy

```bash
# SSH tilbake etter reboot
ssh -i "your-key.pem" ubuntu@16.16.73.195

# Naviger til deployment directory
cd /opt/beemind

# Konfigurer environment variabler
cp deployment/.env.example deployment/.env
nano deployment/.env
```

**Sett disse verdiene i .env:**
```bash
# Required secrets (generer sterke passord)
DB_PASSWORD=your_secure_db_password_123
JWT_SECRET=your_jwt_secret_key_456
REDIS_PASSWORD=your_redis_password_789
NEXTAUTH_SECRET=your_nextauth_secret_abc
GRAFANA_PASSWORD=your_grafana_password_def

# Domain configuration
DOMAIN=beemind.dev
EMAIL=admin@beemind.dev
ENVIRONMENT=production
```

## 🔥 STEP 4: Deploy BeeMind

```bash
# Kjør deployment script
./deployment/deploy.sh

# Install systemd service for auto-start
./deployment/install-systemd.sh
```

## 🔥 STEP 5: Verify Deployment

```bash
# Check service status
./manage-service.sh status

# Test endpoints
curl -f https://beemind.dev/health
curl -f https://api.beemind.dev/health
curl -f https://mlflow.beemind.dev

# Check logs if needed
./manage-service.sh logs
```

## 🌐 Access URLs After Deployment

- **🏠 Dashboard**: https://beemind.dev
- **🔧 API**: https://api.beemind.dev
- **📚 API Docs**: https://api.beemind.dev/docs
- **📊 MLFlow**: https://mlflow.beemind.dev
- **📈 Monitoring**: https://monitoring.beemind.dev

## 🔐 Default Login Credentials

### BeeMind Dashboard
- **Username**: `admin`
- **Password**: `BeeMind2025!`

### Grafana Monitoring
- **Username**: `admin`
- **Password**: (check your .env file for GRAFANA_PASSWORD)

## 🛠️ Troubleshooting Commands

```bash
# If deployment fails, check logs
docker-compose -f deployment/docker-compose.production.yml logs

# Restart services
./manage-service.sh restart

# Check SSL certificates
openssl s_client -connect beemind.dev:443 -servername beemind.dev

# Check DNS resolution
dig beemind.dev A
```

## 🚨 Emergency Commands

```bash
# Complete restart
cd /opt/beemind
docker-compose -f deployment/docker-compose.production.yml down
docker-compose -f deployment/docker-compose.production.yml up -d

# Check system resources
htop
df -h
docker ps
```

---

## 🎯 Expected Timeline

1. **Push to GitHub**: 2 minutes
2. **Server Setup**: 10-15 minutes (includes reboot)
3. **Configuration**: 5 minutes
4. **Deployment**: 10-15 minutes (includes SSL certificates)
5. **Verification**: 2 minutes

**Total: ~30-40 minutes** 🕐

---

## ✅ Success Indicators

When deployment is successful, you should see:

1. ✅ All Docker containers running
2. ✅ SSL certificates generated
3. ✅ HTTPS endpoints responding
4. ✅ Dashboard accessible at https://beemind.dev
5. ✅ API responding at https://api.beemind.dev/health

---

## 🆘 Need Help?

If you encounter issues:

1. **Check logs**: `./manage-service.sh logs`
2. **Verify DNS**: `dig beemind.dev A`
3. **Check SSL**: `openssl s_client -connect beemind.dev:443`
4. **System status**: `htop` and `docker ps`

---

# 🚀 Ready to Deploy? Let's Go!

Copy and paste the commands above step by step. BeeMind will be live in ~30 minutes! 🎉
