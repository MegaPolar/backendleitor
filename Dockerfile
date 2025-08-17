
# Use uma imagem base Python oficial
FROM python:3.11-slim-bookworm

# Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instalar o Tesseract OCR e suas dependências
# Usamos apt-get aqui porque estamos construindo a imagem Docker, não no ambiente de build do Render diretamente
RUN apt-get update && \
    apt-get install -y tesseract-ocr libtesseract-dev libleptonica-dev libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

# Copiar o arquivo de requisitos e instalar as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código da aplicação
COPY . .

# Expor a porta que a aplicação Flask irá rodar
EXPOSE 5000

# Comando para iniciar a aplicação Flask
CMD ["python", "src/main.py"]


