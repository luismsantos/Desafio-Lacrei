#!/bin/bash

# Script de entrada para produção
set -e

echo "🚀 Starting Django application..."

# Aguardar banco de dados estar disponível (se necessário)
echo "⏳ Waiting for database to be ready..."
python manage.py check --database default

# Executar migrações
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# Inicializar aplicação
echo "✅ Starting application server..."
exec "$@"
