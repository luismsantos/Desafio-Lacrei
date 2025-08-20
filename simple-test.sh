#!/bin/bash
# simple-test.sh - Teste simples do container

echo "🧪 Testando container de forma simples..."

echo "1. Testando se o container executa echo:"
docker run --rm lacrei-fixed echo "✅ Container executa comandos"

echo "2. Testando Python no container:"
docker run --rm lacrei-fixed python --version

echo "3. Testando Django manage.py:"
docker run --rm \
  -e DEBUG=True \
  -e SECRET_KEY=test-key-123 \
  -e DATABASE_URL=sqlite:///db.sqlite3 \
  -e ALLOWED_HOSTS=localhost,127.0.0.1 \
  -e USE_FILE_LOGGING=False \
  lacrei-fixed \
  python manage.py --version

echo "4. Testando check do Django:"
docker run --rm \
  -e DEBUG=True \
  -e SECRET_KEY=test-key-123 \
  -e DATABASE_URL=sqlite:///db.sqlite3 \
  -e ALLOWED_HOSTS=localhost,127.0.0.1 \
  -e USE_FILE_LOGGING=False \
  lacrei-fixed \
  python manage.py check --deploy

echo "✅ Testes concluídos"
