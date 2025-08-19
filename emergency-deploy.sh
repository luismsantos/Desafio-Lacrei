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

# 4. Criar nova task definition sem health check e sem entrypoint
echo "📋 Creating emergency task definition..."

# Obter ARNs atuais das roles
EXECUTION_ROLE=$(aws ecs describe-task-definition --task-definition desafio-lacrei-production --query 'taskDefinition.executionRoleArn' --output text 2>/dev/null || echo "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/ecsTaskExecutionRole")
TASK_ROLE=$(aws ecs describe-task-definition --task-definition desafio-lacrei-production --query 'taskDefinition.taskRoleArn' --output text 2>/dev/null || echo "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/ecsTaskRole")

echo "Using Execution Role: $EXECUTION_ROLE"
echo "Using Task Role: $TASK_ROLE"

TASK_DEF=$(cat <<EOF
{
  "family": "desafio-lacrei-production",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "$EXECUTION_ROLE",
  "taskRoleArn": "$TASK_ROLE",
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
        },
        {
          "name": "DJANGO_SETTINGS_MODULE",
          "value": "core.settings_production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:$(aws sts get-caller-identity --query Account --output text):secret:desafio-lacrei/database-url"
        },
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:$(aws sts get-caller-identity --query Account --output text):secret:desafio-lacrei/secret-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/desafio-lacrei-production",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "emergency"
        }
      },
      "essential": true,
      "user": "appuser"
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
