# Usa uma imagem oficial mínima e leve do Python baseada no sistema operacional Debian
FROM python:3.11-slim

# Instala ferramentas do sistema necessárias para compilar e rodar C++ e Java
# O comando rm -rf ao final limpa o cache de pacotes baixados e mantém a imagem Docker bem leve
RUN apt-get update && apt-get install -y \
    g++ \
    default-jdk \
    && rm -rf /var/lib/apt/lists/*

# Configura o diretório interno dentro do container onde o código do projeto vai rodar
WORKDIR /app

# Copia a lista de dependências Python (Flask) e as instala sem usar cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o restante do código-fonte e pastas locais para dentro do container Docker
COPY . .

# Roda a compilação de máquina (build) do motor C++ e Java já de forma nativa na imagem Docker
# Isso garante que eles já estejam prontos e otimizados antes mesmo da aplicação web ligar
RUN g++ -O3 calc.cpp -o calc
RUN javac Calc.java

# Expõe a porta 5000, indicando a rede onde o servidor web Flask irá escutar
EXPOSE 5000

# Princípio de Segurança (Menor Privilégio): cria um usuário normal para não rodar a aplicação web como Administrador/Root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Comando de inicialização final: quando o container docker iniciar de fato, ele liga o script do servidor
CMD ["python", "app.py"]
