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

# Verificar se há argumentos passados, senão usar comando padrão
if [ $# -eq 0 ]; then
    echo "✅ Starting application server with default Gunicorn settings..."
    exec gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 120 --max-requests 1000 --preload core.wsgi:application
else
    echo "✅ Starting application server with custom command: $@"
    exec "$@"
fi
