#!/bin/bash
set -e

# Load environment variables
source .env

# Configuration
BACKUP_DIR="/app/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="backup_${TIMESTAMP}.sql.gz"
MEDIA_BACKUP="media_${TIMESTAMP}.tar.gz"

# Create backup directory
mkdir -p ${BACKUP_DIR}

echo "Starting backup process..."

# Database backup
echo "Backing up database..."
PGPASSWORD=${DB_PASSWORD} pg_dump \
    -h ${DB_HOST} \
    -p ${DB_PORT} \
    -U ${DB_USER} \
    -d ${DB_NAME} \
    --verbose \
    --clean \
    --no-owner \
    --no-privileges | gzip > ${BACKUP_DIR}/${BACKUP_FILE}

# Media files backup
echo "Backing up media files..."
tar -czf ${BACKUP_DIR}/${MEDIA_BACKUP} -C /app media/

# Upload to cloud storage (optional)
if [ ! -z "$AWS_S3_BUCKET" ]; then
    echo "Uploading to S3..."
    aws s3 cp ${BACKUP_DIR}/${BACKUP_FILE} s3://${AWS_S3_BUCKET}/backups/
    aws s3 cp ${BACKUP_DIR}/${MEDIA_BACKUP} s3://${AWS_S3_BUCKET}/backups/
fi

# Cleanup old backups
echo "Cleaning up old backups..."
find ${BACKUP_DIR} -name "backup_*.sql.gz" -mtime +${BACKUP_RETENTION_DAYS} -delete
find ${BACKUP_DIR} -name "media_*.tar.gz" -mtime +${BACKUP_RETENTION_DAYS} -delete

echo "Backup completed successfully!"
echo "Database backup: ${BACKUP_FILE}"
echo "Media backup: ${MEDIA_BACKUP}"