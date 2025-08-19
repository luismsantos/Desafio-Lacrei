#!/bin/bash

# Script de entrada para produção
set -e

echo "🚀 Starting Django application..."

# Aguardar banco de dados estar disponível (se necessário)
echo "⏳ Waiting for database to be ready..."
python manage.py check --database default

# Coletar arquivos estáticos
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear --verbosity 2

# Executar migrações
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# Inicializar aplicação
echo "✅ Starting application server..."
exec "$@"
