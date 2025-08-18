                                                                                        #!/bin/bash

# Script para configurar PostgreSQL RDS na produção
# Este script deve ser executado uma vez para configurar o banco PostgreSQL na AWS

set -e

echo "🐘 Configurando PostgreSQL para produção no AWS RDS..."

# Verificar se AWS CLI está configurado
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "❌ AWS CLI não está configurado. Configure com 'aws configure'"
    exit 1
fi

# Parâmetros do RDS PostgreSQL
DB_INSTANCE_IDENTIFIER="desafio-lacrei-postgres"
DB_NAME="lacrei_production"
DB_USERNAME="lacrei_user"
DB_PASSWORD=$(openssl rand -base64 32 | head -c 24)  # Gerar senha aleatória
DB_INSTANCE_CLASS="db.t3.micro"  # Instância pequena para desenvolvimento
REGION=${AWS_DEFAULT_REGION:-us-east-1}

echo "📋 Configurações do RDS:"
echo "   - Instance ID: $DB_INSTANCE_IDENTIFIER"
echo "   - Database Name: $DB_NAME"
echo "   - Username: $DB_USERNAME"
echo "   - Instance Class: $DB_INSTANCE_CLASS"
echo "   - Region: $REGION"

# Verificar se a instância RDS já existe
if aws rds describe-db-instances --db-instance-identifier "$DB_INSTANCE_IDENTIFIER" >/dev/null 2>&1; then
    echo "✅ Instância RDS já existe: $DB_INSTANCE_IDENTIFIER"
    
    # Obter endpoint da instância existente
    DB_ENDPOINT=$(aws rds describe-db-instances \
        --db-instance-identifier "$DB_INSTANCE_IDENTIFIER" \
        --query 'DBInstances[0].Endpoint.Address' \
        --output text)
    
    echo "📍 Endpoint: $DB_ENDPOINT"
    
    # Usar senha existente ou solicitar ao usuário
    read -s -p "Digite a senha do banco de dados existente: " EXISTING_PASSWORD
    echo
    DB_PASSWORD="$EXISTING_PASSWORD"
else
    echo "🚀 Criando nova instância RDS PostgreSQL..."
    
    # Criar instância RDS
    aws rds create-db-instance \
        --db-instance-identifier "$DB_INSTANCE_IDENTIFIER" \
        --db-instance-class "$DB_INSTANCE_CLASS" \
        --engine postgres \
        --engine-version 15.8 \
        --master-username "$DB_USERNAME" \
        --master-user-password "$DB_PASSWORD" \
        --db-name "$DB_NAME" \
        --allocated-storage 20 \
        --storage-type gp2 \
        --vpc-security-group-ids default \
        --backup-retention-period 7 \
        --storage-encrypted \
        --publicly-accessible
    
    echo "⏳ Aguardando RDS ficar disponível (isso pode levar alguns minutos)..."
    
    aws rds wait db-instance-available --db-instance-identifier "$DB_INSTANCE_IDENTIFIER"
    
    # Obter endpoint da nova instância
    DB_ENDPOINT=$(aws rds describe-db-instances \
        --db-instance-identifier "$DB_INSTANCE_IDENTIFIER" \
        --query 'DBInstances[0].Endpoint.Address' \
        --output text)
    
    echo "✅ RDS PostgreSQL criado com sucesso!"
    echo "📍 Endpoint: $DB_ENDPOINT"
    echo "🔐 Senha gerada: $DB_PASSWORD"
fi

# Montar DATABASE_URL
DATABASE_URL="postgres://${DB_USERNAME}:${DB_PASSWORD}@${DB_ENDPOINT}:5432/${DB_NAME}"

echo "🔧 Configurando parâmetro SSM para produção..."

# Salvar DATABASE_URL no Parameter Store
aws ssm put-parameter \
    --name "/desafio-lacrei/production/database-url" \
    --value "$DATABASE_URL" \
    --type SecureString \
    --overwrite \
    --description "PostgreSQL RDS database URL for production"

echo "✅ Parâmetro DATABASE_URL configurado no SSM Parameter Store"

# Verificar conectividade (opcional)
echo "🧪 Testando conectividade com o banco..."
if command -v psql >/dev/null 2>&1; then
    echo "Testando conexão PostgreSQL..."
    if timeout 10 psql "$DATABASE_URL" -c "SELECT version();" >/dev/null 2>&1; then
        echo "✅ Conexão com PostgreSQL bem-sucedida!"
    else
        echo "⚠️  Não foi possível conectar ao banco (pode ser problema de segurança/firewall)"
    fi
else
    echo "ℹ️  psql não encontrado, pulando teste de conectividade"
fi

echo ""
echo "🎉 Configuração concluída!"
echo "📋 Resumo:"
echo "   - RDS Instance: $DB_INSTANCE_IDENTIFIER"
echo "   - Endpoint: $DB_ENDPOINT"
echo "   - Database: $DB_NAME"
echo "   - Username: $DB_USERNAME"
echo "   - SSM Parameter: /desafio-lacrei/production/database-url"
echo ""
echo "🚀 Agora você pode fazer deploy da aplicação que usará PostgreSQL!"
echo ""
echo "⚠️  IMPORTANTE: Salve estas informações em local seguro:"
echo "   Database Password: $DB_PASSWORD"
echo "   Connection String: $DATABASE_URL"
