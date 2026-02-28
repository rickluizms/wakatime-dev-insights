FROM python:3.11-slim

# Instala dependências do sistema necessárias para o psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala o uv para gerenciamento de dependências rápido
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copia os arquivos de dependências
COPY pyproject.toml uv.lock ./

# Instala as dependências
RUN uv sync --frozen

# Copia o restante do código
COPY . .

# Variáveis de ambiente padrão
ENV PYTHONUNBUFFERED=1
ENV RUN_SCHEDULED=true

# O ponto de entrada padrão será o orchestrator
CMD ["uv", "run", "python", "main.py"]
