#!/bin/bash

# Script para configurar a infraestrutura AWS básica para o Desafio Lacrei
# Execute este script depois de configurar suas credenciais AWS

set -e

# Variáveis - ajuste conforme necessário
REGION=${AWS_REGION:-us-east-1}
CLUSTER_NAME="desafio-lacrei-production"
SERVICE_NAME="desafio-lacrei-production-service"
VPC_NAME="desafio-lacrei-vpc"
ECR_REPO="desafio-lacrei"

echo "🚀 Configurando infraestrutura AWS para Desafio Lacrei..."
echo "Região: $REGION"

# 1. Criar repositório ECR se não existir
echo "📦 Verificando repositório ECR..."
if ! aws ecr describe-repositories --repository-names $ECR_REPO --region $REGION >/dev/null 2>&1; then
    echo "Criando repositório ECR: $ECR_REPO"
    aws ecr create-repository \
        --repository-name $ECR_REPO \
        --region $REGION \
        --image-scanning-configuration scanOnPush=true
else
    echo "Repositório ECR já existe: $ECR_REPO"
fi

# 2. Criar VPC e recursos de rede
echo "🌐 Verificando VPC..."
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=$VPC_NAME" --query 'Vpcs[0].VpcId' --output text --region $REGION)

if [ "$VPC_ID" = "None" ] || [ -z "$VPC_ID" ]; then
    echo "Criando VPC..."
    VPC_ID=$(aws ec2 create-vpc \
        --cidr-block 10.0.0.0/16 \
        --region $REGION \
        --query 'Vpc.VpcId' \
        --output text)
    
    # Tag da VPC
    aws ec2 create-tags \
        --resources $VPC_ID \
        --tags Key=Name,Value=$VPC_NAME \
        --region $REGION
    
    # Habilitar DNS
    aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames --region $REGION
    aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-support --region $REGION
    
    # Criar Internet Gateway
    IGW_ID=$(aws ec2 create-internet-gateway --region $REGION --query 'InternetGateway.InternetGatewayId' --output text)
    aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID --region $REGION
    aws ec2 create-tags --resources $IGW_ID --tags Key=Name,Value="${VPC_NAME}-igw" --region $REGION
    
    # Criar subnets públicas
    SUBNET_1=$(aws ec2 create-subnet \
        --vpc-id $VPC_ID \
        --cidr-block 10.0.1.0/24 \
        --availability-zone ${REGION}a \
        --region $REGION \
        --query 'Subnet.SubnetId' \
        --output text)
    
    SUBNET_2=$(aws ec2 create-subnet \
        --vpc-id $VPC_ID \
        --cidr-block 10.0.2.0/24 \
        --availability-zone ${REGION}b \
        --region $REGION \
        --query 'Subnet.SubnetId' \
        --output text)
    
    # Tags das subnets
    aws ec2 create-tags --resources $SUBNET_1 --tags Key=Name,Value="${VPC_NAME}-subnet-1" --region $REGION
    aws ec2 create-tags --resources $SUBNET_2 --tags Key=Name,Value="${VPC_NAME}-subnet-2" --region $REGION
    
    # Habilitar IP público automático
    aws ec2 modify-subnet-attribute --subnet-id $SUBNET_1 --map-public-ip-on-launch --region $REGION
    aws ec2 modify-subnet-attribute --subnet-id $SUBNET_2 --map-public-ip-on-launch --region $REGION
    
    # Criar route table
    ROUTE_TABLE_ID=$(aws ec2 create-route-table --vpc-id $VPC_ID --region $REGION --query 'RouteTable.RouteTableId' --output text)
    aws ec2 create-tags --resources $ROUTE_TABLE_ID --tags Key=Name,Value="${VPC_NAME}-public-rt" --region $REGION
    
    # Adicionar rota para internet gateway
    aws ec2 create-route --route-table-id $ROUTE_TABLE_ID --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID --region $REGION
    
    # Associar subnets à route table
    aws ec2 associate-route-table --subnet-id $SUBNET_1 --route-table-id $ROUTE_TABLE_ID --region $REGION
    aws ec2 associate-route-table --subnet-id $SUBNET_2 --route-table-id $ROUTE_TABLE_ID --region $REGION
    
else
    echo "VPC já existe: $VPC_ID"
    # Obter IDs das subnets existentes
    SUBNET_1=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" "Name=tag:Name,Values=${VPC_NAME}-subnet-1" --query 'Subnets[0].SubnetId' --output text --region $REGION)
    SUBNET_2=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" "Name=tag:Name,Values=${VPC_NAME}-subnet-2" --query 'Subnets[0].SubnetId' --output text --region $REGION)
fi

# 3. Criar Security Group
echo "🔒 Verificando Security Group..."
SG_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=desafio-lacrei-sg" "Name=vpc-id,Values=$VPC_ID" \
    --query 'SecurityGroups[0].GroupId' \
    --output text \
    --region $REGION)

if [ "$SG_ID" = "None" ] || [ -z "$SG_ID" ]; then
    echo "Criando Security Group..."
    SG_ID=$(aws ec2 create-security-group \
        --group-name desafio-lacrei-sg \
        --description "Security Group para Desafio Lacrei" \
        --vpc-id $VPC_ID \
        --region $REGION \
        --query 'GroupId' \
        --output text)
    
    # Regras de entrada
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 8000 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 443 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0 \
        --region $REGION
else
    echo "Security Group já existe: $SG_ID"
fi

# 4. Criar cluster ECS
echo "🐳 Verificando cluster ECS..."
if ! aws ecs describe-clusters --clusters $CLUSTER_NAME --region $REGION >/dev/null 2>&1; then
    echo "Criando cluster ECS: $CLUSTER_NAME"
    aws ecs create-cluster \
        --cluster-name $CLUSTER_NAME \
        --capacity-providers FARGATE \
        --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1 \
        --region $REGION
else
    echo "Cluster ECS já existe: $CLUSTER_NAME"
fi

# 5. Criar CloudWatch Log Groups
echo "📊 Criando Log Groups..."
aws logs create-log-group --log-group-name "/ecs/desafio-lacrei-production" --region $REGION 2>/dev/null || echo "Log group principal já existe"
aws logs create-log-group --log-group-name "/ecs/desafio-lacrei-production-migrate" --region $REGION 2>/dev/null || echo "Log group migração já existe"

# 6. Criar parâmetros SSM (apenas estrutura - você deve definir os valores)
echo "🔐 Verificando parâmetros SSM..."
aws ssm put-parameter \
    --name "/desafio-lacrei/production/database-url" \
    --value "postgresql://user:password@host:5432/database" \
    --type "SecureString" \
    --description "URL do banco de dados PostgreSQL" \
    --region $REGION \
    --overwrite 2>/dev/null || echo "Parâmetro DATABASE_URL já existe"

aws ssm put-parameter \
    --name "/desafio-lacrei/production/secret-key" \
    --value "CHANGE-THIS-SECRET-KEY-IN-PRODUCTION" \
    --type "SecureString" \
    --description "Django Secret Key" \
    --region $REGION \
    --overwrite 2>/dev/null || echo "Parâmetro SECRET_KEY já existe"

# 7. Imprimir informações importantes
echo ""
echo "✅ Configuração concluída!"
echo ""
echo "📋 Informações para configurar no GitHub Secrets:"
echo "AWS_REGION=$REGION"
echo "AWS_SUBNET_1=$SUBNET_1"
echo "AWS_SUBNET_2=$SUBNET_2"
echo "AWS_SECURITY_GROUP=$SG_ID"
echo ""
echo "⚠️  IMPORTANTE:"
echo "1. Configure a URL do banco de dados:"
echo "   aws ssm put-parameter --name '/desafio-lacrei/production/database-url' --value 'sua-url-aqui' --type SecureString --overwrite"
echo ""
echo "2. Configure uma SECRET_KEY segura:"
echo "   aws ssm put-parameter --name '/desafio-lacrei/production/secret-key' --value 'sua-secret-key-aqui' --type SecureString --overwrite"
echo ""
echo "3. ECR Repository URI: $(aws ecr describe-repositories --repository-names $ECR_REPO --query 'repositories[0].repositoryUri' --output text --region $REGION)"
