#!/bin/bash
set -e

echo "Setting up server..."

# Update system
apt-get update && apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install additional tools
apt-get install -y curl wget git postgresql-client awscli

# Create application directory
mkdir -p /app
cd /app

# Clone repository (replace with your repo)
git clone https://github.com/yourusername/pet-project.git .

# Copy environment file
cp .env.example .env

# Generate SSL certificates (Let's Encrypt)
apt-get install -y certbot
certbot certonly --standalone -d yourdomain.com

# Setup cron jobs
echo "0 2 * * 0 /app/scripts/backup.sh" | crontab -
echo "*/1 * * * * /app/scripts/health_check.py" | crontab -

# Start services
docker-compose up -d

echo "Server setup completed!"