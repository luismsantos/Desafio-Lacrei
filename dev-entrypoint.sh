#!/bin/bash
set -e

echo "🚀 Starting development server..."

# Activate virtual environment
source /opt/venv/bin/activate

# Create database directory
mkdir -p /tmp/db  # nosec B108

# Check if we need to run migrations
echo "📊 Checking database status..."
python manage.py migrate --check --verbosity=0 >/dev/null 2>&1 || {
    echo "🔄 Running database migrations..."
    python manage.py migrate
}

# Create superuser if it doesn't exist (for development)
echo "👤 Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Created superuser: admin/admin123')
else:
    print('✅ Superuser already exists')
" 2>/dev/null || echo "⚠️  Could not check/create superuser"

echo "🌟 Starting Django development server on 0.0.0.0:8000..."
exec python manage.py runserver 0.0.0.0:8000
