#!/bin/bash

echo "🔧 CORREÇÃO AUTOMÁTICA - CONECTIVIDADE POSTGRESQL RDS"
echo "===================================================="

# Definir variáveis baseadas no erro mostrado
RDS_ENDPOINT="lacre-dev-db.c7ako26eotke.sa-east-1.rds.amazonaws.com"
# Extrair o identifier do endpoint (antes do primeiro ponto)
RDS_IDENTIFIER=$(echo $RDS_ENDPOINT | cut -d'.' -f1)

echo "🎯 RDS Identifier: $RDS_IDENTIFIER"
echo "🌐 RDS Endpoint: $RDS_ENDPOINT"

echo ""
echo "1️⃣ OBTENDO SECURITY GROUPS..."

# Obter security group do RDS
RDS_SG=$(aws rds describe-db-instances \
  --db-instance-identifier $RDS_IDENTIFIER \
  --region sa-east-1 \
  --query 'DBInstances[0].VpcSecurityGroups[0].VpcSecurityGroupId' \
  --output text)

echo "🔐 RDS Security Group: $RDS_SG"

# Obter security group do ECS
ECS_SG=$(aws ecs describe-services \
  --cluster lacrei-dev \
  --services lacrei-dev-service \
  --region sa-east-1 \
  --query 'services[0].networkConfiguration.awsvpcConfiguration.securityGroups[0]' \
  --output text)

echo "🔐 ECS Security Group: $ECS_SG"

echo ""
echo "2️⃣ VERIFICANDO REGRAS ATUAIS DO RDS..."
aws ec2 describe-security-groups \
  --group-ids $RDS_SG \
  --region sa-east-1 \
  --query 'SecurityGroups[0].IpPermissions[?FromPort==`5432`]' \
  --output table

echo ""
echo "3️⃣ ADICIONANDO REGRA DE ACESSO POSTGRESQL..."

# Tentar adicionar a regra (ignorar se já existe)
aws ec2 authorize-security-group-ingress \
  --group-id $RDS_SG \
  --protocol tcp \
  --port 5432 \
  --source-group $ECS_SG \
  --region sa-east-1 \
  2>/dev/null && echo "✅ Regra adicionada com sucesso!" || echo "⚠️  Regra pode já existir"

echo ""
echo "4️⃣ VERIFICANDO REGRAS APÓS MODIFICAÇÃO..."
aws ec2 describe-security-groups \
  --group-ids $RDS_SG \
  --region sa-east-1 \
  --query 'SecurityGroups[0].IpPermissions[?FromPort==`5432`]' \
  --output table

echo ""
echo "5️⃣ REINICIANDO SERVICE ECS PARA APLICAR MUDANÇAS..."
aws ecs update-service \
  --cluster lacrei-dev \
  --service lacrei-dev-service \
  --force-new-deployment \
  --region sa-east-1

echo ""
echo "✅ CORREÇÃO APLICADA!"
echo "==================="
echo "O ECS service será reiniciado com as novas regras de conectividade."
echo "Aguarde alguns minutos e verifique os logs novamente."

echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. Aguardar o deployment do ECS (2-3 minutos)"
echo "2. Verificar logs do container"
echo "3. Testar a aplicação"

echo ""
echo "📝 COMANDO PARA VERIFICAR LOGS:"
echo "aws logs tail /ecs/lacrei-dev --follow --region sa-east-1"
