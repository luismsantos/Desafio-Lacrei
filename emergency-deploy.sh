#!/bin/bash

# Script de deploy de emergência
set -e

echo "🚨 EMERGENCY DEPLOY - Fixing ECS service"

# 1. Parar o serviço atual
echo "⏹️ Stopping current service..."
aws ecs update-service \
  --cluster desafio-lacrei-production \
  --service desafio-lacrei-production-service \
  --desired-count 0

echo "⏳ Waiting for service to stop..."
aws ecs wait services-stable \
  --cluster desafio-lacrei-production \
  --services desafio-lacrei-production-service

# 2. Build nova imagem sem health check
echo "🔨 Building emergency image..."
docker build -t emergency-lacrei .

# 3. Tag e push para registry
echo "📤 Pushing emergency image..."
IMAGE_TAG="emergency-$(date +%s)"
docker tag emergency-lacrei ghcr.io/luismsantos/desafio-lacrei:$IMAGE_TAG
docker push ghcr.io/luismsantos/desafio-lacrei:$IMAGE_TAG

# 4. Criar nova task definition sem health check
echo "📋 Creating emergency task definition..."
TASK_DEF=$(cat <<EOF
{
  "family": "desafio-lacrei-production",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "desafio-lacrei-app",
      "image": "ghcr.io/luismsantos/desafio-lacrei:$IMAGE_TAG",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DEBUG",
          "value": "False"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/desafio-lacrei-production",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "emergency"
        }
      }
    }
  ]
}
EOF
)

aws ecs register-task-definition --cli-input-json "$TASK_DEF"

# 5. Restart service
echo "🚀 Restarting service with emergency task definition..."
aws ecs update-service \
  --cluster desafio-lacrei-production \
  --service desafio-lacrei-production-service \
  --desired-count 1 \
  --task-definition desafio-lacrei-production

echo "✅ Emergency deploy completed!"
echo "🔍 Monitor at: https://console.aws.amazon.com/ecs/home?region=us-east-1#/clusters/desafio-lacrei-production/services"
