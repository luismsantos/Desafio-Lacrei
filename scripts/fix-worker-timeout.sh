#!/bin/bash

echo "🚨 CORREÇÃO IMEDIATA ECS - Worker Timeout Fix"
echo "============================================="

CLUSTER="desafio-lacrei-production"
SERVICE="desafio-lacrei-production-service"

echo "🔧 1. Parando todas as tasks com problema..."
aws ecs update-service \
    --cluster $CLUSTER \
    --service $SERVICE \
    --desired-count 0

echo "⏳ Aguardando parada completa..."
aws ecs wait services-stable \
    --cluster $CLUSTER \
    --services $SERVICE

echo "🔄 2. Forçando nova task definition com configurações otimizadas..."

# Criar task definition temporária com configurações robustas
cat > /tmp/fix-task-definition.json << EOF
{
  "family": "desafio-lacrei-production",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "desafio-lacrei-app",
      "image": "ghcr.io/luismsantos/desafio-lacrei:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/aws/ecs/desafio-lacrei-production",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "/desafio-lacrei/production/database-url"
        },
        {
          "name": "SECRET_KEY",
          "valueFrom": "/desafio-lacrei/production/secret-key"
        }
      ],
      "environment": [
        {
          "name": "DEBUG",
          "value": "False"
        },
        {
          "name": "ALLOWED_HOSTS",
          "value": "*"
        }
      ],
      "healthCheck": {
        "command": [
          "CMD-SHELL",
          "curl -f http://localhost:8000/health/ || exit 1"
        ],
        "interval": 30,
        "timeout": 10,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
EOF

echo "📝 3. Registrando nova task definition..."
aws ecs register-task-definition --cli-input-json file:///tmp/fix-task-definition.json

echo "🚀 4. Reiniciando serviço com configurações otimizadas..."
aws ecs update-service \
    --cluster $CLUSTER \
    --service $SERVICE \
    --desired-count 1 \
    --task-definition desafio-lacrei-production

echo "⏳ 5. Monitorando nova inicialização..."
echo "Aguardando estabilização (pode levar alguns minutos)..."

# Monitor por 10 minutos
for i in {1..20}; do
    echo "Tentativa $i/20..."
    
    STATUS=$(aws ecs describe-services \
        --cluster $CLUSTER \
        --services $SERVICE \
        --query 'services[0].{Running:runningCount,Desired:desiredCount}' \
        --output text)
    
    echo "Status: $STATUS"
    
    if [[ "$STATUS" == "1	1" ]]; then
        echo "✅ Serviço estabilizado!"
        break
    fi
    
    sleep 30
done

echo -e "\n📊 Status Final:"
aws ecs describe-services \
    --cluster $CLUSTER \
    --services $SERVICE \
    --query 'services[0].{TaskDefinition:taskDefinition,RunningCount:runningCount,DesiredCount:desiredCount}' \
    --output table

echo -e "\n🔍 Para monitorar logs:"
echo "aws logs tail /aws/ecs/desafio-lacrei-production --follow"

# Cleanup
rm -f /tmp/fix-task-definition.json
