# 🐳 Guia de Desenvolvimento com Docker e Hot-Reload

Para facilitar a engenharia de software no seu dia a dia, configuramos uma estrutura de desenvolvimento com **Docker Compose**. 

Normalmente, no Docker clássico (`docker build` e `docker run`), a imagem é estática e fechada. Qualquer linha de código que você mudar (como editar o `app.py` ou o HTML), exigiria reconstruir a imagem do zero, o que toma tempo.

Com o **Docker Compose + Volumes**, nós criamos um túnel entre a pasta real da sua máquina (onde está o seu VS Code) e a pasta virtual do container Linux. 

### 🚀 As Vantagens que você ganha com essa função:
1. **Hot-Reload de Python e HTML:** Se você editar os arquivos `app.py`, `index.html` ou `style.css` e apertar `Ctrl+S` (Salvar), o site atualizará em tempo real. Você só precisará dar F5 no navegador para ver a mudança.
2. **Recompilação Automática:** Se você fizer modificações pesadas na lógica do C++ (`calc.cpp`) ou Java (`Calc.java`), você só precisa reiniciar o container, e ele fará o trabalho árduo de compilar os binários sozinho antes de ligar o Flask.

---

### 💻 Como Utilizar (Passo a Passo)

Abra o seu terminal na pasta raiz do projeto.

#### 1. Iniciar o projeto em Modo de Desenvolvimento (Live)
```bash
docker-compose up
```
Esse comando vai subir o sistema espelhando os arquivos.
Se não quiser que ele trave a sua tela do terminal, adicione a flag `-d` (Modo Detached):
```bash
docker-compose up -d
```

#### 2. Reiniciar para aplicar mudanças de C++ ou Java
Como o C++ e o Java não são interpretados na hora (eles são compilados em binários pesados), se você modificar algo neles, apenas rode o comando abaixo para recompilá-los automaticamente:
```bash
docker-compose restart
```

#### 3. Derrubar o Ambiente (Desligar tudo)
Quando acabar de estudar e quiser desligar os serviços e liberar memória:
```bash
docker-compose down
```

### ⚙️ Como funciona a Mágica por baixo dos panos?
Se você observar o arquivo `docker-compose.yml`, notará três segredos:
- `volumes: - .:/app`: Espelha a pasta local no container.
- `FLASK_DEBUG=1`: Liga a flag de desenvolvimento do framework Flask (que observa mudanças).
- `command: /bin/sh -c "g++ ... && javac ... && flask run"`: Substitui o comando inicial do Dockerfile e impõe uma ordem restrita: Compilar C++ **->** Compilar Java **->** Iniciar WebServer.

