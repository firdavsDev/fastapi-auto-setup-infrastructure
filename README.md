# 🚀 Pet Project - Resilient FastAPI Infrastructure

A production-ready FastAPI application with automated backup, failover, and high availability features across multiple servers.

## 🏗️ Architecture Overview

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Primary Server    │    │   Backup Server     │    │   Database Server   │
│   (Cloud Provider)  │    │   (Local/Office)    │    │   (Dedicated)       │
│                     │    │                     │    │                     │
│ ┌─────────────────┐ │    │ ┌─────────────────┐ │    │ ┌─────────────────┐ │
│ │   FastAPI App   │ │    │ │   FastAPI App   │ │    │ │   PostgreSQL    │ │
│ │   (Active)      │ │    │ │   (Standby)     │ │    │ │   (Primary)     │ │
│ └─────────────────┘ │    │ └─────────────────┘ │    │ └─────────────────┘ │
│                     │    │                     │    │                     │
│ ┌─────────────────┐ │    │ ┌─────────────────┐ │    │ ┌─────────────────┐ │
│ │   Health Check  │ │    │ │   Monitoring    │ │    │ │   Backup Agent  │ │
│ │   DNS Manager   │ │    │ │   Auto-Deploy   │ │    │ │   (Weekly)      │ │
│ └─────────────────┘ │    │ └─────────────────┘ │    │ └─────────────────┘ │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## ✨ Features

- **🔄 Automatic Failover**: 10-minute detection and recovery
- **💾 Automated Backups**: Weekly database + media backups
- **🌐 DNS Management**: Automatic domain switching
- **🐳 Docker Integration**: Complete containerization
- **📊 Health Monitoring**: Real-time server health checks
- **🔒 SSL/TLS Support**: HTTPS with Let's Encrypt
- **📈 Metrics & Alerts**: Prometheus + Grafana monitoring
- **🎯 Zero Downtime**: Seamless failover process

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.11+
- **Database**: PostgreSQL 15+
- **Containerization**: Docker, Docker Compose
- **Reverse Proxy**: Nginx
- **Monitoring**: Prometheus, Grafana
- **DNS**: Cloudflare API
- **Storage**: Local + S3 (optional)

## 📋 Prerequisites

- 3 Linux servers (Ubuntu 20.04+ recommended)
- Domain name with API access (Cloudflare recommended)
- PostgreSQL 15+
- Docker & Docker Compose
- SSL certificates (Let's Encrypt)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone git@github.com:firdavsDev/auto-setup-infrastructure.git
cd auto-setup-infrastructure

# Copy and configure environment
cp .env.example .env
nano .env  # Edit with your configurations
```

### 2. Configure Environment Variables

```bash
# Database Configuration
DB_HOST=your-db-server-ip
DB_PORT=5432
DB_NAME=pet_project
DB_USER=pet_user
DB_PASSWORD=your-secure-password

# Server Configuration
SERVER_NAME=primary
PRIMARY_SERVER_IP=your-primary-server-ip
BACKUP_SERVER_IP=your-backup-server-ip

# Domain Configuration
DOMAIN_NAME=yourdomain.com
CLOUDFLARE_API_KEY=your-cloudflare-api-key
CLOUDFLARE_EMAIL=your-email@example.com
CLOUDFLARE_ZONE_ID=your-zone-id
```

### 3. Deploy to Servers

```bash
# Setup Primary Server
./deploy/setup_server.sh

# Setup Backup Server
scp -r . root@backup-server:/app/
ssh root@backup-server "cd /app && ./deploy/setup_server.sh"

# Setup Database Server
ssh root@db-server "
  apt-get update && apt-get install -y postgresql postgresql-contrib
  sudo -u postgres createdb pet_project
  sudo -u postgres createuser pet_user
  sudo -u postgres psql -c \"ALTER USER pet_user WITH PASSWORD 'your-password';\"
  sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE pet_project TO pet_user;\"
"
```

### 4. Start Services

```bash
# Start on primary server
docker-compose up -d

# Verify health
curl http://yourdomain.com/health
```

## 📁 Project Structure

```
pet-project/
├── app/                    # FastAPI application
│   ├── __init__.py
│   ├── main.py            # Main application file
│   ├── database.py        # Database configuration
│   ├── models.py          # SQLAlchemy models
│   └── routers/           # API routes
├── scripts/               # Automation scripts
│   ├── backup.sh          # Database backup script
│   ├── restore.sh         # Database restore script
│   ├── health_check.py    # Health monitoring
│   └── failover.py        # Failover automation
├── docker/                # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
├── monitoring/            # Monitoring setup
│   ├── prometheus.yml
│   └── grafana/
├── deploy/                # Deployment scripts
│   ├── deploy.sh
│   └── setup_server.sh
├── media/                 # Uploaded files
├── backups/               # Backup storage
├── .env                   # Environment variables
└── requirements.txt       # Python dependencies
```

## 🔧 Configuration

### Database Configuration

The application uses PostgreSQL with connection pooling and automatic reconnection. Configure your database settings in `.env`:

```env
DATABASE_URL=postgresql://pet_user:password@db-server:5432/pet_project
```

### Backup Configuration

Automated backups run weekly (configurable) and include:
- Database dumps (compressed with gzip)
- Media files (tar.gz archives)
- Retention policy (30 days default)

### Health Check Configuration

Health checks run every minute and monitor:
- Database connectivity
- Application response time
- Server resource usage
- SSL certificate validity

## 🚨 Failover Process

When primary server fails:

1. **Detection** (60 seconds): Health checks fail
2. **Verification** (5 minutes): Multiple failed checks
3. **Backup Activation** (2 minutes): Start backup server
4. **Data Restoration** (2 minutes): Restore latest backup
5. **DNS Update** (1 minute): Switch domain to backup
6. **Verification** (30 seconds): Confirm backup is healthy

**Total failover time: ~10 minutes**

## 📊 Monitoring

### Endpoints

- **Health Check**: `GET /health`
- **Metrics**: `GET /metrics`
- **Status**: `GET /`

### Grafana Dashboards

Access monitoring at: `http://yourdomain.com:3000`

Default credentials:
- Username: `admin`
- Password: `admin`

### Prometheus Alerts

Common alerts configured:
- Server down (5 minutes)
- High CPU usage (>80%)
- Low disk space (<10%)
- Database connection errors

## 🔒 Security

### SSL/TLS Configuration

```bash
# Generate SSL certificates
certbot certonly --standalone -d yourdomain.com

# Auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

### Firewall Rules

```bash
# Allow necessary ports
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw allow 5432  # PostgreSQL (database server only)
ufw enable
```

## 🧪 Testing

### Manual Testing

```bash
# Test primary server
curl -f http://yourdomain.com/health

# Test backup server
curl -f http://backup-server-ip:8000/health

# Test database connection
docker-compose exec app python -c "
from app.database import engine
try:
    engine.execute('SELECT 1')
    print('Database connection: OK')
except Exception as e:
    print(f'Database connection failed: {e}')
"
```

### Simulate Failover

```bash
# Stop primary server
ssh root@primary-server "docker-compose down"

# Monitor logs
tail -f /var/log/health_check.log

# Verify backup takes over (wait 10 minutes)
curl -f http://yourdomain.com/health
```

### Load Testing

```bash
# Install Apache Bench
apt-get install apache2-utils

# Run load test
ab -n 1000 -c 10 http://yourdomain.com/

# Monitor metrics
docker-compose exec app python -c "
import psutil
print(f'CPU: {psutil.cpu_percent()}%')
print(f'Memory: {psutil.virtual_memory().percent}%')
"
```

## 🚀 Deployment

### Manual Deployment

```bash
# Update code
git pull origin main

# Deploy changes
./deploy/deploy.sh

# Check deployment
curl -f http://yourdomain.com/health
```

### CI/CD Pipeline

Example GitHub Actions workflow:

```yaml
name: Deploy to Production
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        run: |
          ssh root@${{ secrets.SERVER_IP }} "
            cd /app &&
            git pull origin main &&
            ./deploy/deploy.sh
          "
```

## 🔍 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check database status
docker-compose exec db pg_isready

# Check logs
docker-compose logs db
```

**Backup Restore Failed**
```bash
# Check backup files
ls -la backups/

# Manual restore
./scripts/restore.sh
```

**Health Check Fails**
```bash
# Check application logs
docker-compose logs app

# Check nginx logs
docker-compose logs nginx
```

**DNS Not Updating**
```bash
# Check Cloudflare credentials
curl -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer $CLOUDFLARE_API_KEY"

# Manual DNS update
python3 scripts/failover.py
```

### Log Locations

- Application logs: `/var/log/pet-project/app.log`
- Health check logs: `/var/log/pet-project/health_check.log`
- Backup logs: `/var/log/pet-project/backup.log`
- Nginx logs: `/var/log/nginx/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI team for the excellent framework
- Docker team for containerization
- PostgreSQL team for the robust database
- Cloudflare for DNS management
- Nginx for reverse proxy capabilities

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Web: https://davronbekdev.uz

---

**Made with ❤️ for reliable, scalable web applications by [DavronbekDev](https://github.com/firdavsdev)**
