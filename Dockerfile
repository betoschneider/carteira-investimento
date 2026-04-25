FROM python:3.12-slim

# Instalar uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Configurar diretório de trabalho
WORKDIR /app

# Copiar arquivos de configuração
COPY pyproject.toml uv.lock ./

# Instalar dependências
RUN uv sync --frozen --no-install-project --no-dev

# Copiar código fonte
COPY . .

# Expor porta
EXPOSE 8501

# Comando para executar
CMD ["uv", "run", "streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]