# 🏥 Lacrei Saúde - API de Consultas Médicas

**🚀 [Acesse a API em Produção](http://54.207.65.222:8000/swagger/)**

## 🎯 Sobre o Projeto

Plataforma desenvolvida para o **Desafio Lacrei Saúde** que permite:

- 👩‍⚕️ Cadastro de profissionais com **nome social**
- 📅 Agendamento e gerenciamento de consultas
- 🔐 Autenticação JWT segura
- 📊 API RESTful documentada com Swagger

## 🛠 Tecnologias

**Backend:**
- Django 5.2.5 + Django REST Framework 3.16.1
- PostgreSQL 17.5 + psycopg2-binary 2.9.10
- SimpleJWT 5.5.1 (autenticação)
- WhiteNoise 6.9.0 (arquivos estáticos)
- drf-yasg 1.21.10 (documentação Swagger)

**DevOps:**
- Docker + Docker Compose
- Gunicorn 23.0.0 (WSGI server)
- Poetry (gerenciamento de dependências)

**Qualidade:**
- pytest + Black + Flake8 + Bandit

## 🏗 Estrutura do Projeto

```
authentication/    # Sistema de login/registro JWT
profissionais/     # CRUD de profissionais (com nome social)
consultas/         # CRUD de consultas médicas
core/              # Configurações Django + health checks
```

**Modelos principais:**
- `Profissional`: nome, nome_social, especialidade, email, telefone
- `Consulta`: profissional, paciente_nome, data_hora, observacoes

## ⚙️ Como Executar

### Com Docker (Recomendado)

```bash
git clone https://github.com/luismsantos/Desafio-Lacrei.git
cd Desafio-Lacrei
docker-compose up --build
```

**🎉 Acesse:** `http://localhost:8000/swagger/`

### Variáveis de Ambiente
```bash
DATABASE_URL=postgres://user:password@host:port/database
SECRET_KEY=sua-chave-secreta
DEBUG=False
```

## 🚀 API Endpoints

**Produção:** `http://54.207.65.222:8000` | **Local:** `http://localhost:8000`  
**� Documentação:** `/swagger/`

### Principais Rotas

**Autenticação (`/api/auth/`):**
- `POST /registrar/` - Registrar usuário
- `POST /entrar/` - Login (retorna JWT)
- `GET /perfil/` - Dados do usuário

**Profissionais (`/api/profissionais/`):**
- `GET /` - Listar profissionais
- `POST /` - Criar profissional  
- `GET /{id}/` - Detalhes
- `PUT /{id}/` - Atualizar

**Consultas (`/api/consultas/`):**
- `GET /` - Listar consultas
- `POST /` - Agendar consulta
- `GET /{id}/` - Detalhes
- `PUT /{id}/` - Atualizar

### Exemplo de Uso

```bash
# Login
curl -X POST http://54.207.65.222:8000/api/auth/entrar/ \
  -d '{"username": "usuario", "password": "senha"}'

# Criar profissional
curl -X POST http://54.207.65.222:8000/api/profissionais/ \
  -H "Authorization: Bearer SEU_JWT_TOKEN" \
  -d '{"nome": "Dr. João", "nome_social": "João", "especialidade": "Cardiologia"}'
```

## 🚀 Deploy

**🌩️ AWS:** Aplicação deployada em [http://54.207.65.222:8000/swagger/](http://54.207.65.222:8000/swagger/)

**Infraestrutura:**
- EC2 Ubuntu 22.04 + PostgreSQL RDS
- Docker multi-stage build otimizado
- Pipeline CI/CD automatizado
- Health checks (`/health/`, `/ready/`)

## 🧪 Testes

```bash
# Com Docker
docker-compose exec web pytest --cov=.

# Local
poetry run pytest
```

## 💳 Integração com Asaas (Gateway de Pagamento)

### Arquitetura Proposta

```python
# Modelo de Pagamento
class Pagamento(models.Model):
    consulta = models.OneToOneField(Consulta, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago'),
        ('CANCELADO', 'Cancelado')
    ])
    asaas_payment_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Implementação com Asaas API

**Endpoint de Pagamento:**
```bash
POST /api/consultas/{id}/pagamento/
{
  "valor": 150.00,
  "metodo": "PIX",  
  "customer": {
    "nome": "Paciente Nome",
    "email": "paciente@email.com",
    "cpf": "12345678901"
  }
}
```

**Webhook Asaas:**
```bash
POST /webhooks/asaas/
# Recebe notificações de pagamento aprovado/rejeitado
# Atualiza status da consulta automaticamente
```

### Fluxo de Pagamento

1. **Agendamento** → Consulta criada (status: PENDENTE)
2. **Gerar Cobrança** → Integração com Asaas API
3. **Pagamento** → Cliente paga via PIX/Boleto/Cartão
4. **Confirmação** → Webhook atualiza consulta (status: CONFIRMADA)
5. **Atendimento** → Consulta liberada para o profissional

### 🔧 Exemplo de Uso da API

**Variáveis de Ambiente (Postman):**
```json
{
  "base_url": "http://54.207.65.222:8000",
  "jwt_token": "{{access_token}}"
}
```

**Headers Padrão:**
```json
{
  "Authorization": "Bearer {{jwt_token}}",
  "Content-Type": "application/json"
}
```

## ✨ Funcionalidades

- ✅ **Autenticação JWT** completa
- ✅ **CRUD de Profissionais** com nome social (inclusividade LGBTQIA+)
- ✅ **Sistema de Consultas** médicas
- ✅ **Gateway de Pagamento** (Asaas integração)
- ✅ **Deploy em produção** na AWS
- ✅ **Pipeline CI/CD** automatizado
- ✅ **Testes automatizados**

## 🔒 Segurança

### Checklist de Segurança

**✅ Configurações Obrigatórias:**
- **TLS/HTTPS:** Sempre usar HTTPS em produção
- **HSTS:** Header `Strict-Transport-Security` configurado
- **JWT:** Tokens com expiração de 15min (access) e 7 dias (refresh)
- **Secrets:** Rotação mensal de `SECRET_KEY` e credenciais DB
- **Senhas:** Mínimo 8 caracteres, Django PBKDF2 por padrão

### Configuração por Ambiente

```bash
# .env.development
DEBUG=True
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ALLOWED_HOSTS=localhost,127.0.0.1

# .env.production  
DEBUG=False
CORS_ALLOWED_ORIGINS=https://lacrei.com.br
ALLOWED_HOSTS=54.207.65.222,lacrei.com.br
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

### Rate Limiting

Configurado para rotas sensíveis:
- **Login:** 5 tentativas/minuto
- **Listagem:** 100 requests/minuto
- **Criação:** 10 requests/minuto

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'login': '5/min'
    }
}
```

## 📊 Monitoramento e Logs

### Logs de Aplicação

**Local de Armazenamento:**
```bash
# ECS/CloudWatch
/aws/ecs/desafio-lacrei-production

# Logs locais
/var/log/django/application.log
/var/log/django/error.log
```

**Como Visualizar:**

```bash
# CloudWatch (AWS)
aws logs tail /aws/ecs/desafio-lacrei-production --follow

# ECS Container Logs
aws ecs describe-tasks --cluster desafio-lacrei-production --tasks TASK_ID
aws logs get-log-events --log-group-name /aws/ecs/desafio-lacrei-production
```

### Health Checks

```bash
# Verificar saúde da aplicação
curl https://54.207.65.222:8000/health/

# Verificar readiness (ECS)
curl https://54.207.65.222:8000/ready/
```

## 🔄 Deploy e Rollback

### Visualizar Deploy

```bash
# Status do serviço ECS
aws ecs describe-services \
  --cluster desafio-lacrei-production \
  --services desafio-lacrei-production-service

# Logs de deploy
aws logs filter-log-events \
  --log-group-name /aws/ecs/desafio-lacrei-production \
  --start-time 1600000000000
```

### Rollback Manual

**1. Identificar versão anterior:**
```bash
aws ecs list-task-definitions \
  --family-prefix desafio-lacrei-production \
  --status ACTIVE
```

**2. Executar rollback:**
```bash
aws ecs update-service \
  --cluster desafio-lacrei-production \
  --service desafio-lacrei-production-service \
  --task-definition desafio-lacrei-production:REVISION_ANTERIOR
```

**3. Monitorar rollback:**
```bash
aws ecs wait services-stable \
  --cluster desafio-lacrei-production \
  --services desafio-lacrei-production-service
```

### Scripts de Emergência

```bash
# Parar serviço
./emergency-stop.sh

# Deploy de emergência  
./emergency-deploy.sh

# Restaurar último backup
./restore-backup.sh
```

## 🛡️ Configurações de Segurança Avançadas

### JWT Configuration

```python
# settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

### CORS Policy

```python
# Produção - Restritivo
CORS_ALLOWED_ORIGINS = [
    "https://lacrei.com.br",
    "https://app.lacrei.com.br",
]

# Desenvolvimento - Permissivo
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

### Headers de Segurança

```python
# settings.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 ano
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
```
