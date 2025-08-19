# Dockerfile otimizado para builds mais rápidos
FROM python:3.11-slim

# Instalar dependências do sistema em uma única layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Criar usuário não-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements.txt primeiro para cache de layer
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY --chown=appuser:appuser . .

# Criar diretórios e coletar static files
RUN mkdir -p staticfiles \
    && python manage.py collectstatic --noinput \
    && chown -R appuser:appuser staticfiles /app

# Mudar para usuário não-root
USER appuser

# Expor porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Comando inline sem entrypoint para simplificar
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 30 core.wsgi:application"]
