#!/bin/bash
set -e

echo "🚀 Starting ApeX Barbershop API..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
while ! pg_isready -h "${POSTGRES_HOST:-localhost}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER:-postgres}" -q; do
    sleep 1
done
echo "✅ Database is ready!"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis..."
while ! redis-cli -h "${REDIS_HOST:-localhost}" -p "${REDIS_PORT:-6379}" ping > /dev/null 2>&1; do
    sleep 1
done
echo "✅ Redis is ready!"

# Run database migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# Create trigram extension for PostgreSQL (if not exists)
echo "🔧 Setting up PostgreSQL extensions..."
python manage.py shell -c "
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm;')
    print('✅ pg_trgm extension enabled')
" 2>/dev/null || true

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create superuser if it doesn't exist
echo "👤 Checking for superuser..."
python manage.py shell -c "
from apps.users.models import User
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        email='${DJANGO_SUPERUSER_EMAIL:-admin@apexbarbershop.com}',
        password='${DJANGO_SUPERUSER_PASSWORD:-admin123}',
        first_name='Admin'
    )
    print('✅ Superuser created')
else:
    print('ℹ️ Superuser already exists')
"

echo "🎉 Setup complete! Starting server..."

# Execute the main command
exec "$@"
