#!/bin/bash

echo "🚨 CORREÇÃO IMEDIATA - Task Definition Limpa"
echo "============================================="

echo "📋 1. Pare o serviço atual:"
echo "aws ecs update-service --cluster desafio-lacrei-production --service desafio-lacrei-production-service --desired-count 0"
echo ""

echo "⏳ 2. Aguarde o serviço parar:"
echo "aws ecs wait services-stable --cluster desafio-lacrei-production --services desafio-lacrei-production-service"
echo ""

echo "📝 3. Registre nova task definition (sem entrypoint):"
echo "aws ecs register-task-definition --cli-input-json file://fix-task-definition.json"
echo ""

echo "🚀 4. Reinicie o serviço:"
echo "aws ecs update-service --cluster desafio-lacrei-production --service desafio-lacrei-production-service --desired-count 1 --task-definition desafio-lacrei-production"
echo ""

echo "✅ 5. Monitore o deployment:"
echo "aws ecs describe-services --cluster desafio-lacrei-production --services desafio-lacrei-production-service"
echo ""

echo "🔍 ANTES DE EXECUTAR:"
echo "1. Substitua YOUR_ACCOUNT_ID em fix-task-definition.json pelo seu Account ID da AWS"
echo "2. Atualize os ARNs dos secrets se necessário"
echo "3. Certifique-se de ter as credenciais AWS configuradas"
echo ""

echo "📊 CAUSA DO PROBLEMA:"
echo "A task definition ainda referencia './entrypoint.sh' que foi removido do Dockerfile"
echo "Esta nova task definition usa apenas o CMD do Dockerfile (sem entrypoint)"
