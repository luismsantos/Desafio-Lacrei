# 🛠️ Scripts de Deploy e Operações

Este diretório contém scripts essenciais para operação da aplicação em produção.

## 📋 Scripts Disponíveis

### 🐳 **Produção/Pipeline**
- **`entrypoint.sh`** - Script de entrada do Docker (ESSENCIAL - não remover)
  - Executa migrações e inicia Gunicorn
  - Usado no Dockerfile como ENTRYPOINT

### 🚀 **Deploy e Infraestrutura**
- **`setup-aws-infrastructure.sh`** - Configuração inicial da infraestrutura AWS
  - Cria VPC, subnets, security groups, ECS cluster
- **`setup-postgres-production.sh`** - Setup do banco PostgreSQL RDS
  - Cria instância RDS e configura parâmetros SSM

### 🚨 **Operações de Emergência**
- **`emergency-deploy.sh`** - Deploy de emergência
  - Para serviço, faz build e deploy rápido
- **`emergency-stop.sh`** - Parar serviço em emergência
  - Para o serviço ECS imediatamente
- **`rollback.sh`** - Rollback para versão anterior
  - Reverte para task definition anterior

### 🔍 **Diagnóstico e Debug**
- **`diagnose-simple.sh`** - Diagnóstico básico da infraestrutura AWS
  - Verifica RDS, ECS, conectividade
- **`diagnose-postgresql.sh`** - Diagnóstico específico do PostgreSQL
  - Debug de conectividade e configuração

## 🚀 Como Usar

### Setup Inicial:
```bash
# 1. Configurar infraestrutura
./scripts/setup-aws-infrastructure.sh

# 2. Configurar banco de dados
./scripts/setup-postgres-production.sh
```

### Operações:
```bash
# Diagnóstico rápido
./scripts/diagnose-simple.sh

# Deploy de emergência
./scripts/emergency-deploy.sh

# Rollback
./scripts/rollback.sh
```

## ⚠️ Importante

- **`entrypoint.sh`** é crítico para o funcionamento - NÃO REMOVER
- Scripts de emergência devem ser usados com cuidado em produção
- Sempre teste em ambiente de staging primeiro