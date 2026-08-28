# ====================================================================================
# CONFIGURAÇÃO DA IMAGEM DOCKER (Dockerfile)
# 
# Objetivo do Arquivo:
# 1. Criar um ambiente autocontido (container) com tudo que a aplicação precisa para rodar.
# 2. Instalar os compiladores de C++ (g++) e Java (JDK).
# 3. Pré-compilar os motores C++ e Java durante a construção (Build) da imagem.
# 4. Configurar a execução segura sem privilégios de administrador (non-root user).
# ====================================================================================

# 1. IMAGEM BASE: Usa uma imagem oficial mínima e otimizada do Python 3.11 sobre o Debian Linux
FROM python:3.11-slim

# 2. INSTALAÇÃO DE DEPENDÊNCIAS DO SISTEMA:
# - g++: Compilador de C++ para gerar o executável nativo.
# - default-jdk: Kit de Desenvolvimento Java para compilar (.java -> .class) e rodar a JVM.
# - rm -rf /var/lib/apt/lists/*: Limpa os arquivos temporários da instalação para deixar a imagem leve.
RUN apt-get update && apt-get install -y \
    g++ \
    default-jdk \
    && rm -rf /var/lib/apt/lists/*

# 3. DIRETÓRIO DE TRABALHO: Define /app como a pasta raiz dentro do container
WORKDIR /app

# 4. INSTALAÇÃO DE DEPENDÊNCIAS PYTHON:
# Copia o requirements.txt e instala o Flask sem armazenar cache desnecessário
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. CÓPIA DO CÓDIGO-FONTE: Copia todos os arquivos do projeto para dentro do container
COPY . .

# 6. COMPILAÇÃO NATIVA DOS MOTORES:
# - C++: Compilado com a flag de otimização máxima (-O3) gerando o binário executável 'calc'
# - Java: Compilado pelo javac gerando o bytecode executável 'Calc.class'
RUN g++ -O3 calc.cpp -o calc
RUN javac Calc.java

# 7. EXPOSIÇÃO DE PORTA DE REDE:
# Avisa ao Docker que o servidor Flask estará ouvindo na porta 5000
EXPOSE 5000

# 8. BOAS PRÁTICAS DE SEGURANÇA (Princípio do Menor Privilégio):
# Cria um usuário padrão de sistema chamado 'appuser' sem poderes de Administrador/Root
# Isso impede que invasores ganhem controle do sistema caso o servidor web seja atacado
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# 9. COMANDO DE ENTRADA (ENTRYPOINT):
# Quando o container Docker é ligado, ele executa automaticamente o servidor Python Flask
CMD ["python", "app.py"]
