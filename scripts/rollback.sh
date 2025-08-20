#!/bin/bash

echo "🔄 ROLLBACK MANUAL"
echo "=================="

echo "📋 Listando versões disponíveis..."
aws ecs list-task-definitions \
    --family-prefix desafio-lacrei-production \
    --status ACTIVE \
    --query 'taskDefinitionArns[-5:]' \
    --output table

echo ""
read -p "Digite o número da revisão para rollback (ex: 10): " revision

if [[ -z "$revision" ]]; then
    echo "❌ Revisão não informada."
    exit 1
fi

TASK_DEF="desafio-lacrei-production:$revision"

echo "🔄 Executando rollback para $TASK_DEF..."
aws ecs update-service \
    --cluster desafio-lacrei-production \
    --service desafio-lacrei-production-service \
    --task-definition $TASK_DEF

echo "⏳ Monitorando rollback..."
aws ecs wait services-stable \
    --cluster desafio-lacrei-production \
    --services desafio-lacrei-production-service

echo "✅ Rollback concluído!"

# Verificar status
aws ecs describe-services \
    --cluster desafio-lacrei-production \
    --services desafio-lacrei-production-service \
    --query 'services[0].{TaskDefinition:taskDefinition,RunningCount:runningCount,DesiredCount:desiredCount}'
