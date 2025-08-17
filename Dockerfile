# Multi-stage build para otimizar imagem
FROM python:3.11-slim AS builder

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN pip install poetry==1.6.1

# Configurar Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Copiar arquivos de dependência
WORKDIR /app
COPY pyproject.toml poetry.lock ./

# Instalar dependências e exportar requirements
RUN poetry export -f requirements.txt --output requirements.txt --without dev && \
    rm -rf $POETRY_CACHE_DIR

# Imagem final
FROM python:3.11-slim AS runtime

# Instalar apenas dependências de runtime
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Criar ambiente virtual e instalar dependências
ENV VIRTUAL_ENV=/app/.venv
RUN python -m venv ${VIRTUAL_ENV}
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Definir diretório de trabalho
WORKDIR /app

# Copiar código da aplicação
COPY --chown=appuser:appuser . .

# Criar diretório para logs
RUN mkdir -p /var/log/django && chown appuser:appuser /var/log/django

# Mudar para usuário não-root
USER appuser

# Expor porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Comando padrão
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
