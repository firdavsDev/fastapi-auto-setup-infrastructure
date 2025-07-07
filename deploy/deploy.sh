#!/bin/bash
set -e

echo "Deploying application..."

# Pull latest code
git pull origin main

# Build and deploy
docker-compose build
docker-compose up -d

# Run database migrations
docker-compose exec app alembic upgrade head

# Test health endpoint
sleep 10
curl -f http://localhost:8000/health

echo "Deployment completed successfully!"