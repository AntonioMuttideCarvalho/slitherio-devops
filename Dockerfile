# Imagem base do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências primeiro (otimiza o cache do Docker)
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o resto do projeto para dentro do container
COPY . .

# Expõe a porta que o Flask vai usar
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["python", "app.py"]