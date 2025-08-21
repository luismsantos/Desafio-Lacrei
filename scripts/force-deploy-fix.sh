#!/bin/bash

echo "🚀 DEPLOY FORÇADO - Correção Gunicorn Parameters"
echo "============================================="

# Fazer commit das mudanças
echo "📝 Fazendo commit das correções..."
git add .
git commit -m "fix: correct Gunicorn keep-alive parameter syntax" || echo "Nada para commit"

# Push para disparar o pipeline
echo "📤 Enviando para GitHub..."
git push origin main

echo ""
echo "✅ Pipeline disparado!"
echo ""
echo "📋 O GitHub Actions vai:"
echo "   1. Build da nova imagem Docker com o entrypoint corrigido"
echo "   2. Push para o ECR"
echo "   3. Deploy automático no ECS"
echo ""
echo "⏱️  Aguarde 3-5 minutos para o deployment completo"
echo ""
echo "📊 Monitorar:"
echo "   • GitHub: https://github.com/luismsantos/Desafio-Lacrei/actions"
echo "   • Logs ECS: aws logs tail /ecs/desafio-lacrei-production --follow --region sa-east-1"
