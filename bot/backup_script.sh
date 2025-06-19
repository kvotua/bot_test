#!/bin/sh

BACKUP_DIR="/backups"
PG_HOST="localhost"  
PG_USER="$POSTGRES_USER"
PG_PASSWORD="$POSTGRES_PASSWORD"
PG_DATABASE="$POSTGRES_DB"

mkdir -p "$BACKUP_DIR"
CURRENT_DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_FILE="$BACKUP_DIR/${PG_DATABASE}_${CURRENT_DATE}.sql.gz"

echo "$(date) - Starting backup of $PG_DATABASE database..."

until pg_isready -h "$PG_HOST" -U "$PG_USER" -d "$PG_DATABASE"; do
  echo "$(date) - Waiting for PostgreSQL..."
  sleep 2
done

PGPASSWORD="$PG_PASSWORD" pg_dump \
  -h "$PG_HOST" \
  -U "$PG_USER" \
  -d "$PG_DATABASE" \
  | gzip > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "$(date) - Backup successfully created: $BACKUP_FILE"
    
    find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete
    exit 0
else
    echo "$(date) - Backup failed!"
    rm -f "$BACKUP_FILE"
    exit 1
fi