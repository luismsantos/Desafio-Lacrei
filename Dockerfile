# Imagem base com Python 3.11 slim
FROM python:3.13-slim

# Instalar dependências do sistema para compilação e PostgreSQL client
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instala Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Adiciona Poetry ao PATH
ENV PATH="/root/.local/bin:$PATH"

# Copia arquivos de dependências para instalar pacotes
COPY pyproject.toml poetry.lock ./

# Instala dependências via Poetry
RUN poetry install --no-root --without dev

# Copia o código fonte para o container
COPY . .

# Expõe a porta padrão do Django para desenvolvimento
EXPOSE 8000

# Comando para rodar o servidor Django (pode ser modificado)
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
