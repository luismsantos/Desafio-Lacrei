#!/bin/bash
# test-container.sh - Script para testar o container localmente

echo "🧪 Testando container com configurações otimizadas..."

# Para o container se estiver rodando
docker stop $(docker ps -q --filter ancestor=lacrei-fixed) 2>/dev/null || true

# Executa o container em modo de teste
echo "🚀 Iniciando container..."
docker run --rm -p 8080:8000 \
  -e DEBUG=True \
  -e SECRET_KEY=test-key-for-container-testing \
  -e DATABASE_URL=sqlite:///db.sqlite3 \
  -e ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0 \
  --name lacrei-test \
  lacrei-fixed &

CONTAINER_PID=$!

# Espera o container inicializar
echo "⏳ Aguardando inicialização..."
sleep 10

# Testa endpoints
echo "🩺 Testando health check..."
curl -f http://localhost:8080/health/ || echo "❌ Health check falhou"

echo "🔐 Testando readiness check..."
curl -f http://localhost:8080/ready/ || echo "❌ Readiness check falhou"

echo "📋 Testando API root..."
curl -f http://localhost:8080/ || echo "❌ API root falhou"

# Para o container
echo "🛑 Parando container de teste..."
docker stop lacrei-test 2>/dev/null || kill $CONTAINER_PID 2>/dev/null

echo "✅ Teste finalizado!"
