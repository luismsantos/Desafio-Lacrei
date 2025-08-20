#!/bin/bash

# Script para corrigir conectividade PostgreSQL entre ECS e RDS
set -e

REGION="sa-east-1"
RDS_IDENTIFIER="lacre-dev-db"

echo "🔍 Diagnosticando conectividade PostgreSQL RDS..."

# 1. Verificar se a instância RDS existe e está acessível
echo "📊 Verificando RDS instance..."
RDS_STATUS=$(aws rds describe-db-instances --db-instance-identifier lacrei-dev-db --region sa-east-1 --query 'DBInstances[0].DBInstanceStatus' --output text 2>/dev/null)

if [ "$RDS_STATUS" != "available" ]; then
    echo "❌ RDS instance lacrei-dev-db não encontrada!"
    echo "💡 Verifique se o nome está correto e se está na região sa-east-1"
    exit 1

echo "✅ RDS encontrado:"
echo "$RDS_INFO" | jq '.'

# 2. Obter VPC do RDS
RDS_VPC=$(echo "$RDS_INFO" | jq -r '.VpcId')
RDS_SG=$(echo "$RDS_INFO" | jq -r '.SecurityGroups')

echo ""
echo "📊 RDS está na VPC: $RDS_VPC"
echo "📊 RDS Security Group: $RDS_SG"

# 3. Verificar se o ECS está na mesma VPC
echo ""
echo "🚀 Verificando ECS service..."

ECS_SERVICE_INFO=$(aws ecs describe-services \
    --cluster "desafio-lacrei-production" \
    --services "desafio-lacrei-app" \
    --region $REGION \
    --query 'services[0].networkConfiguration.awsvpcConfiguration.{subnets:subnets,securityGroups:securityGroups}' \
    --output json 2>/dev/null || echo '{}')

if [ "$ECS_SERVICE_INFO" = "{}" ]; then
    echo "❌ ECS service não encontrado!"
    echo "💡 Verifique se o cluster e service existem"
    exit 1
fi

ECS_SUBNETS=$(echo "$ECS_SERVICE_INFO" | jq -r '.subnets[]' | head -1)
ECS_SG=$(echo "$ECS_SERVICE_INFO" | jq -r '.securityGroups[]' | head -1)

echo "✅ ECS configurado:"
echo "   Subnet: $ECS_SUBNETS"
echo "   Security Group: $ECS_SG"

# 4. Verificar VPC das subnets do ECS
ECS_VPC=$(aws ec2 describe-subnets \
    --subnet-ids $ECS_SUBNETS \
    --region $REGION \
    --query 'Subnets[0].VpcId' \
    --output text)

echo "📊 ECS está na VPC: $ECS_VPC"

# 5. Verificar se estão na mesma VPC
if [ "$RDS_VPC" != "$ECS_VPC" ]; then
    echo ""
    echo "❌ PROBLEMA: ECS e RDS estão em VPCs diferentes!"
    echo "   ECS VPC: $ECS_VPC"
    echo "   RDS VPC: $RDS_VPC"
    echo ""
    echo "💡 SOLUÇÕES:"
    echo "   1. Mover ECS para a mesma VPC do RDS"
    echo "   2. Criar VPC Peering"
    echo "   3. Recriar RDS na VPC do ECS"
    exit 1
fi

echo "✅ ECS e RDS estão na mesma VPC!"

# 6. Adicionar regra de entrada no Security Group do RDS
echo ""
echo "🔒 Configurando Security Group do RDS..."

aws ec2 authorize-security-group-ingress \
    --group-id $RDS_SG \
    --protocol tcp \
    --port 5432 \
    --source-group $ECS_SG \
    --region $REGION || echo "⚠️ Regra pode já existir"

echo "✅ Regra adicionada: permitir ECS ($ECS_SG) → RDS ($RDS_SG) porta 5432"

# 7. Verificar regras aplicadas
echo ""
echo "🔍 Verificando regras do Security Group RDS:"
aws ec2 describe-security-groups \
    --group-ids $RDS_SG \
    --region $REGION \
    --query 'SecurityGroups[0].IpPermissions[?FromPort==`5432`]' \
    --output table

echo ""
echo "✅ CONECTIVIDADE CONFIGURADA!"
echo ""
echo "🎯 Próximos passos:"
echo "   1. Aguarde 2-3 minutos para propagação das regras"
echo "   2. Force um novo deployment do ECS:"
echo "      aws ecs update-service --cluster desafio-lacrei-production --service desafio-lacrei-app --force-new-deployment --region $REGION"
echo "   3. Monitore os logs do container"
