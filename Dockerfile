FROM python:3.9-slim-buster

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && \
    apt-get install -y default-mysql-client && \
    rm -rf /var/lib/apt/lists/*

# Instala dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos da aplicação (incluindo 'migrations' agora)
COPY . .

# REMOVA A LINHA ABAIXO:
# VOLUME /app/migrations

CMD ["flask", "run", "--host=0.0.0.0"]