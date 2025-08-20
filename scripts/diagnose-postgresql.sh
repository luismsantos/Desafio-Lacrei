#!/bin/bash

echo "🔍 Diagnosticando conectividade PostgreSQL RDS..."
echo "================================================="

# 1. Verificar se a instância RDS existe e está acessível
echo "📊 Verificando RDS instance..."
RDS_STATUS=$(aws rds describe-db-instances --db-instance-identifier lacrei-dev-db --region sa-east-1 --query 'DBInstances[0].DBInstanceStatus' --output text 2>/dev/null)

if [ "$RDS_STATUS" != "available" ]; then
    echo "❌ RDS instance lacrei-dev-db não está disponível. Status: $RDS_STATUS"
    echo "💡 Aguardando a instância ficar disponível..."
fi

echo "✅ RDS Status: $RDS_STATUS"

# 2. Obter informações detalhadas da instância RDS
echo "📋 Obtendo detalhes da instância RDS..."
RDS_INFO=$(aws rds describe-db-instances --db-instance-identifier lacrei-dev-db --region sa-east-1)
RDS_ENDPOINT=$(echo "$RDS_INFO" | jq -r '.DBInstances[0].Endpoint.Address')
RDS_PORT=$(echo "$RDS_INFO" | jq -r '.DBInstances[0].Endpoint.Port')
RDS_VPC_ID=$(echo "$RDS_INFO" | jq -r '.DBInstances[0].DBSubnetGroup.VpcId')
RDS_SUBNETS=$(echo "$RDS_INFO" | jq -r '.DBInstances[0].DBSubnetGroup.Subnets[].SubnetIdentifier' | tr '\n' ' ')
RDS_SECURITY_GROUPS=$(echo "$RDS_INFO" | jq -r '.DBInstances[0].VpcSecurityGroups[].VpcSecurityGroupId' | tr '\n' ' ')

echo "🌐 RDS Endpoint: $RDS_ENDPOINT"
echo "🔌 Porta: $RDS_PORT"
echo "🏢 VPC ID: $RDS_VPC_ID"
echo "🔐 Security Groups: $RDS_SECURITY_GROUPS"
echo "📍 Subnets: $RDS_SUBNETS"

# 3. Verificar cluster ECS
echo ""
echo "📱 Verificando cluster ECS..."
ECS_CLUSTER_INFO=$(aws ecs describe-clusters --clusters lacrei-dev --region sa-east-1)
ECS_CLUSTER_STATUS=$(echo "$ECS_CLUSTER_INFO" | jq -r '.clusters[0].status')
echo "✅ ECS Cluster Status: $ECS_CLUSTER_STATUS"

# 4. Verificar service ECS
echo ""
echo "🚀 Verificando service ECS..."
ECS_SERVICE_INFO=$(aws ecs describe-services --cluster lacrei-dev --services lacrei-dev-service --region sa-east-1)
ECS_SERVICE_STATUS=$(echo "$ECS_SERVICE_INFO" | jq -r '.services[0].status')
ECS_TASK_DEFINITION=$(echo "$ECS_SERVICE_INFO" | jq -r '.services[0].taskDefinition')

echo "✅ Service Status: $ECS_SERVICE_STATUS"
echo "📋 Task Definition: $ECS_TASK_DEFINITION"

# 5. Verificar configuração de rede do service
echo ""
echo "🌐 Verificando configuração de rede do ECS..."
ECS_NETWORK_CONFIG=$(echo "$ECS_SERVICE_INFO" | jq -r '.services[0].networkConfiguration')
ECS_SUBNETS=$(echo "$ECS_NETWORK_CONFIG" | jq -r '.awsvpcConfiguration.subnets[]' | tr '\n' ' ')
ECS_SECURITY_GROUPS=$(echo "$ECS_NETWORK_CONFIG" | jq -r '.awsvpcConfiguration.securityGroups[]' | tr '\n' ' ')
ECS_PUBLIC_IP=$(echo "$ECS_NETWORK_CONFIG" | jq -r '.awsvpcConfiguration.assignPublicIp')

echo "📍 ECS Subnets: $ECS_SUBNETS"
echo "🔐 ECS Security Groups: $ECS_SECURITY_GROUPS"
echo "🌍 Public IP: $ECS_PUBLIC_IP"

# 6. Comparar VPCs
echo ""
echo "🔍 Análise de conectividade..."
if [ "$RDS_VPC_ID" = "$(aws ec2 describe-subnets --subnet-ids $ECS_SUBNETS --region sa-east-1 --query 'Subnets[0].VpcId' --output text)" ]; then
    echo "✅ RDS e ECS estão na mesma VPC: $RDS_VPC_ID"
else
    echo "❌ RDS e ECS estão em VPCs diferentes!"
    echo "RDS VPC: $RDS_VPC_ID"
    echo "ECS VPC: $(aws ec2 describe-subnets --subnet-ids $ECS_SUBNETS --region sa-east-1 --query 'Subnets[0].VpcId' --output text)"
fi

# 7. Verificar regras de security group
echo ""
echo "🔐 Verificando regras de security group do RDS..."
for sg in $RDS_SECURITY_GROUPS; do
    echo "Security Group: $sg"
    aws ec2 describe-security-groups --group-ids $sg --region sa-east-1 --query 'SecurityGroups[0].IpPermissions[?FromPort==`5432`]' --output table
done

# 8. Testar resolução DNS
echo ""
echo "🌐 Testando resolução DNS do endpoint RDS..."
echo "Endpoint: $RDS_ENDPOINT"
if nslookup "$RDS_ENDPOINT" >/dev/null 2>&1; then
    echo "✅ DNS resolução funcionando"
    echo "IP: $(nslookup "$RDS_ENDPOINT" | grep -A1 "Name:" | tail -1 | awk '{print $2}')"
else
    echo "❌ Falha na resolução DNS"
fi

# 9. Sugestões de correção
echo ""
echo "💡 Sugestões de correção:"
echo "================================"
echo "1. Verificar se os security groups permitem tráfego PostgreSQL (porta 5432)"
echo "2. Confirmar se RDS e ECS estão na mesma VPC"
echo "3. Verificar se as subnets do ECS têm rota para as subnets do RDS"
echo "4. Confirmar se o RDS está em subnets privadas acessíveis ao ECS"

echo ""
echo "🔧 Para permitir acesso PostgreSQL, execute:"
echo "aws ec2 authorize-security-group-ingress --group-id $RDS_SECURITY_GROUPS --protocol tcp --port 5432 --source-group $ECS_SECURITY_GROUPS --region sa-east-1"
