# Desafio Lacrei - API REST

API REST desenvolvida em Django REST Framework para gerenciamento de profissionais e consultas.

## 🚀 Funcionalidades

- **Autenticação JWT**: Sistema completo de autenticação com tokens JWT
- **Gerenciamento de Profissionais**: CRUD completo para profissionais de saúde
- **Sistema de Consultas**: Agendamento e gerenciamento de consultas
- **Documentação Swagger**: API totalmente documentada com Swagger/OpenAPI
- **Testes Automatizados**: Cobertura completa de testes

## 🛠️ Tecnologias Utilizadas

- Python 3.11+
- Django 5.2.5
- Django REST Framework
- JWT Authentication
- PostgreSQL
- Docker & Docker Compose
- Poetry (Gerenciamento de dependências)

## 📦 Por que Poetry?

Este projeto usa **Poetry** como gerenciador de dependências porque:

- **Resolução de dependências**: Evita conflitos entre bibliotecas
- **Ambientes virtuais**: Criação automática e isolada
- **Lock file**: Garante versões consistentes entre diferentes máquinas
- **Facilidade**: Comandos simples e intuitivos
- **Padrão moderno**: Ferramenta recomendada pela comunidade Python

## 📋 Pré-requisitos

- Python 3.11 ou superior
- Poetry (gerenciador de dependências)
- Docker
- Git

## 🔧 Instalação e Configuração

### 1. Clone o repositório

```bash
git clone https://github.com/luismsantos/Desafio-Lacrei.git
cd Desafio-Lacrei
```

### 2. Configure as variáveis de ambiente

Copie o arquivo de exemplo e configure suas variáveis:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# Configurações do Django
SECRET_KEY=sua-chave-secreta-super-segura-aqui
DEBUG=True

# Configurações do Banco de Dados PostgreSQL
DATABASE_URL=postgres://usuario:senha@localhost:5432/lacrei_db

# Configurações opcionais
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Instale o Poetry (se não tiver)

```bash
# No Linux/macOS
curl -sSL https://install.python-poetry.org | python3 -

# No Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### 4. Instale as dependências

```bash
poetry install
```

### 5. Configure o banco de dados

#### Usando Docker 

```bash
docker-compose up -d db
```

### 6. Execute as migrações

```bash
poetry run python manage.py migrate
```

### 7. Crie um superusuário (opcional)

```bash
poetry run python manage.py createsuperuser
```

### 8. Execute os testes

```bash
poetry run python manage.py test
```

### 9. Inicie o servidor de desenvolvimento

```bash
poetry run python manage.py runserver
```

## 🐳 Executando com Docker

Para executar toda a aplicação com Docker:

```bash
docker-compose up
```

A aplicação estará disponível em: `http://localhost:8000`

## 📚 Documentação da API

### Swagger UI
Acesse a documentação interativa em: `http://localhost:8000/swagger/`

## 🔐 Autenticação

A API utiliza JWT (JSON Web Tokens) para autenticação. 

### Como usar no Swagger:

1. Faça login em `/auth/entrar/`
2. Copie o token de acesso retornado
3. No Swagger, clique no botão "Authorize"
4. Digite: `Bearer seu_token_aqui`
5. Agora você pode acessar os endpoints protegidos

### Endpoints de autenticação:

- `POST /auth/registrar/` - Registro de novo usuário
- `POST /auth/entrar/` - Login (retorna tokens)
- `GET /auth/perfil/` - Perfil do usuário logado
- `POST /auth/sair/` - Logout (blacklist do token)

## 🧪 Testes

Execute todos os testes:

```bash
poetry run python manage.py test
```

Execute testes de um app específico:

```bash
poetry run python manage.py test authentication
poetry run python manage.py test profissionais
poetry run python manage.py test consultas


## 📁 Estrutura do Projeto

```
Desafio-Lacrei/
├── authentication/          # App de autenticação JWT
├── consultas/              # App de gerenciamento de consultas
├── profissionais/          # App de gerenciamento de profissionais
├── core/                   # Configurações do Django
├── docker-compose.yml      # Configuração do Docker
├── Dockerfile             # Container da aplicação
├── manage.py              # Script de gerenciamento do Django
├── pyproject.toml         # Configuração do Poetry
└── README.md              # Este arquivo
```
