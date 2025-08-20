#!/bin/bash

# Script para corrigir permissões do IAM para ECS acessar Secrets Manager
set -e

ACCOUNT_ID="038462749081"
REGION="sa-east-1"

echo "🔧 Configurando permissões IAM para ECS acessar Secrets Manager..."

# 1. Criar policy para acesso aos secrets
echo "📋 Criando policy para acesso aos secrets..."

POLICY_JSON='{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret"
            ],
            "Resource": [
                "arn:aws:secretsmanager:sa-east-1:038462749081:secret:desafio-lacrei/database-url-*",
                "arn:aws:secretsmanager:sa-east-1:038462749081:secret:desafio-lacrei/secret-key-*"
            ]
        }
    ]
}'

# Criar policy se não existir
aws iam create-policy \
    --policy-name DesafioLacreiSecretsManagerAccess \
    --policy-document "$POLICY_JSON" \
    --description "Policy para ECS acessar secrets do Desafio Lacrei" \
    --region $REGION || echo "Policy já existe ou houve erro na criação"

# 2. Anexar policy à role ecsTaskExecutionRole
echo "🔗 Anexando policy à role ecsTaskExecutionRole..."

aws iam attach-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/DesafioLacreiSecretsManagerAccess" \
    --region $REGION || echo "Policy já anexada ou houve erro"

# 3. Verificar se as permissões foram aplicadas
echo "✅ Verificando permissões aplicadas..."

aws iam list-attached-role-policies \
    --role-name ecsTaskExecutionRole \
    --region $REGION

echo ""
echo "🎯 Permissões configuradas! A role ecsTaskExecutionRole agora pode acessar:"
echo "   - arn:aws:secretsmanager:sa-east-1:038462749081:secret:desafio-lacrei/database-url-*"
echo "   - arn:aws:secretsmanager:sa-east-1:038462749081:secret:desafio-lacrei/secret-key-*"
echo ""
echo "⚠️  Aguarde alguns minutos para que as permissões sejam propagadas antes de redeployar a aplicação."
