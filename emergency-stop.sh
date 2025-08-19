#!/bin/bash

echo "🚨 EMERGÊNCIA - Parando serviço ECS"
echo "=================================="

read -p "Tem certeza que deseja parar o serviço? (y/N): " confirm
if [[ $confirm != [yY] ]]; then
    echo "Operação cancelada."
    exit 0
fi

echo "⏹️ Parando serviço..."
aws ecs update-service \
    --cluster desafio-lacrei-production \
    --service desafio-lacrei-production-service \
    --desired-count 0

echo "⏳ Aguardando parada completa..."
aws ecs wait services-stable \
    --cluster desafio-lacrei-production \
    --services desafio-lacrei-production-service

echo "✅ Serviço parado com sucesso!"
echo "Para reativar: aws ecs update-service --cluster desafio-lacrei-production --service desafio-lacrei-production-service --desired-count 1"
