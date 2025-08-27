#!/bin/bash

echo "🔍 Diagnosticando conectividade PostgreSQL RDS..."
echo "================================================="

# 1. Verificar instância RDS
echo "📊 Verificando instância RDS..."
aws rds describe-db-instances --db-instance-identifier lacrei-dev-db --region us-east-1 --output table

echo ""
echo "🌐 Obtendo endpoint RDS..."
RDS_ENDPOINT=$(aws rds describe-db-instances --db-instance-identifier lacrei-dev-db --region us-east-1 --query 'DBInstances[0].Endpoint.Address' --output text)
echo "Endpoint: $RDS_ENDPOINT"

echo ""
echo "🔐 Obtendo Security Groups do RDS..."
aws rds describe-db-instances --db-instance-identifier lacrei-dev-db --region us-east-1 --query 'DBInstances[0].VpcSecurityGroups[*].VpcSecurityGroupId' --output table

RDS_SG=$(aws rds describe-db-instances --db-instance-identifier lacrei-dev-db --region us-east-1 --query 'DBInstances[0].VpcSecurityGroups[0].VpcSecurityGroupId' --output text)
echo "RDS Security Group: $RDS_SG"

echo ""
echo "🏢 Obtendo VPC do RDS..."
RDS_VPC=$(aws rds describe-db-instances --db-instance-identifier lacrei-dev-db --region us-east-1 --query 'DBInstances[0].DBSubnetGroup.VpcId' --output text)
echo "RDS VPC: $RDS_VPC"

echo ""
echo "🚀 Verificando service ECS..."
aws ecs describe-services --cluster lacrei-dev --services lacrei-dev-service --region us-east-1 --query 'services[0].networkConfiguration.awsvpcConfiguration' --output table

ECS_SG=$(aws ecs describe-services --cluster lacrei-dev --services lacrei-dev-service --region us-east-1 --query 'services[0].networkConfiguration.awsvpcConfiguration.securityGroups[0]' --output text)
echo "ECS Security Group: $ECS_SG"

ECS_SUBNET=$(aws ecs describe-services --cluster lacrei-dev --services lacrei-dev-service --region us-east-1 --query 'services[0].networkConfiguration.awsvpcConfiguration.subnets[0]' --output text)
echo "ECS Subnet: $ECS_SUBNET"

echo ""
echo "🏢 Obtendo VPC do ECS..."
ECS_VPC=$(aws ec2 describe-subnets --subnet-ids $ECS_SUBNET --region us-east-1 --query 'Subnets[0].VpcId' --output text)
echo "ECS VPC: $ECS_VPC"

echo ""
echo "🔍 Comparando VPCs..."
if [ "$RDS_VPC" = "$ECS_VPC" ]; then
    echo "✅ RDS e ECS estão na mesma VPC: $RDS_VPC"
else
    echo "❌ RDS e ECS estão em VPCs diferentes!"
    echo "   RDS VPC: $RDS_VPC"
    echo "   ECS VPC: $ECS_VPC"
fi

echo ""
echo "🔐 Verificando regras do Security Group do RDS..."
echo "Security Group: $RDS_SG"
aws ec2 describe-security-groups --group-ids $RDS_SG --region us-east-1 --query 'SecurityGroups[0].IpPermissions' --output table

echo ""
echo "🌐 Testando resolução DNS..."
if nslookup "$RDS_ENDPOINT" >/dev/null 2>&1; then
    echo "✅ DNS resolução funcionando para $RDS_ENDPOINT"
else
    echo "❌ Falha na resolução DNS para $RDS_ENDPOINT"
fi

echo ""
echo "💡 DIAGNÓSTICO COMPLETO"
echo "======================="
echo "RDS Endpoint: $RDS_ENDPOINT"
echo "RDS Security Group: $RDS_SG"
echo "RDS VPC: $RDS_VPC"
echo "ECS Security Group: $ECS_SG"
echo "ECS VPC: $ECS_VPC"

echo ""
echo "🔧 Para corrigir conectividade, execute:"
echo "aws ec2 authorize-security-group-ingress \\"
echo "  --group-id $RDS_SG \\"
echo "  --protocol tcp \\"
echo "  --port 5432 \\"
echo "  --source-group $ECS_SG \\"
echo "  --region us-east-1"
