# Multi-stage build para otimizar imagem
FROM python:3.11-slim AS builder

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN pip install poetry==1.8.3

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

# Instalar dependências de runtime e curl para healthcheck
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry para desenvolvimento
RUN pip install poetry==1.8.3

# Configurar Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Criar usuário não-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Criar ambiente virtual fora do diretório de trabalho para evitar conflito com volume mount
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv ${VIRTUAL_ENV}
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Dar ownership do virtual env para appuser
RUN chown -R appuser:appuser ${VIRTUAL_ENV}

# Criar diretórios necessários com permissões corretas ANTES de mudar para appuser
RUN mkdir -p /var/log/django staticfiles && \
    chmod 777 /var/log/django && \
    chown -R appuser:appuser /var/log/django

# Definir diretório de trabalho
WORKDIR /app

# Copiar código da aplicação
COPY --chown=appuser:appuser . .

# Garantir que o entrypoint.sh tenha permissões de execução
RUN chmod +x entrypoint.sh

# Coletar arquivos estáticos como root antes de mudar para appuser
RUN python manage.py collectstatic --noinput

# Ajustar permissões dos arquivos estáticos para appuser
RUN chown -R appuser:appuser staticfiles

# Mudar para usuário não-root
USER appuser

# Expor porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Usar entrypoint script que funciona tanto para desenvolvimento quanto produção
ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--timeout", "120", "--keepalive", "5", "--max-requests", "1000", "--max-requests-jitter", "100", "--preload", "--worker-class", "gthread", "core.wsgi:application"]
