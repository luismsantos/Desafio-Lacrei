#!/bin/bash

# Script de entrada para produção
set -e

echo "🚀 Starting Django application..."

# Aguardar banco de dados estar disponível (com timeout rápido)
echo "⏳ Checking database connection..."
timeout 30 python manage.py check --database default || echo "⚠️ DB check timeout, proceeding anyway"

# Executar migrações (skip se falhar rapidamente)
echo "🗄️ Running database migrations..."
timeout 60 python manage.py migrate --noinput || echo "⚠️ Migration timeout, proceeding anyway"

# Inicializar aplicação
echo "✅ Starting application server..."
exec "$@"
