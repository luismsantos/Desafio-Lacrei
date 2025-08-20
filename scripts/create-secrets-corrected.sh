#!/bin/bash

echo "🔐 Criando secrets AWS para PostgreSQL..."

# Criar secret para DATABASE_URL
DATABASE_URL="postgresql://lacrei_user:sua_senha_aqui@lacre-dev-db.c7ako26eotke.sa-east-1.rds.amazonaws.com:5432/lacrei_db"

echo "Criando secret DATABASE_URL..."
aws secretsmanager create-secret \
  --name "lacrei/database/url" \
  --description "Database URL for Lacrei application" \
  --secret-string "$DATABASE_URL" \
  --region sa-east-1

# Criar secret para SECRET_KEY
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

echo "Criando secret SECRET_KEY..."
aws secretsmanager create-secret \
  --name "lacrei/django/secret-key" \
  --description "Django secret key for Lacrei application" \
  --secret-string "$SECRET_KEY" \
  --region sa-east-1

echo "✅ Secrets criados com sucesso!"
echo ""
echo "📋 Para atualizar a DATABASE_URL com suas credenciais reais:"
echo "aws secretsmanager update-secret --secret-id lacrei/database/url --secret-string 'postgresql://USERNAME:PASSWORD@lacre-dev-db.c7ako26eotke.sa-east-1.rds.amazonaws.com:5432/DBNAME' --region sa-east-1"
