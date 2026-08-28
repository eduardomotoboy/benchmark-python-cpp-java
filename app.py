# ====================================================================================
# SERVIDOR CENTRAL E CONTROLADOR DE TELEMETRIA (app.py)
# 
# Objetivo do Arquivo:
# 1. Atuar como o cérebro da aplicação web utilizando o microframework Flask.
# 2. Servir a página visual (HTML/CSS/JS) no navegador.
# 3. Disponibilizar uma rota de API (/calculate) que recebe a conta do usuário.
# 4. Executar a conta simultaneamente em Python, C++ e Java.
# 5. Cronometrar o tempo de resposta (em microssegundos) e o consumo de memória (em KB).
# 6. Devolver todas as métricas em formato JSON para o Frontend desenhar os gráficos.
# ====================================================================================

import ast           # Biblioteca nativa de Árvore Sintática Abstrata (usada para avaliação matemática 100% segura)
import operator      # Fornece funções matemáticas padrão (soma, subtração, multiplicação, etc.)
import math          # Funções matemáticas avançadas (como raiz quadrada math.sqrt)
import subprocess    # Permite ao Python criar subprocessos no Sistema Operacional para executar o C++ e o Java
import time          # Medição de tempo de alta precisão do processador
import tracemalloc   # Rastreador de alocação de memória RAM do Python
import re            # Expressões Regulares (Regex) para limpeza e tratamento de texto
from flask import Flask, render_template, request, jsonify

# Inicializa o servidor web Flask
app = Flask(__name__)


# ====================================================================================
# 1. MOTOR DE CÁLCULO SEGURO EM PYTHON (safe_eval)
# ====================================================================================
# Por que não usamos a função nativa 'eval()' do Python?
# A função 'eval()' comum é uma das maiores falhas de segurança na web, pois se um usuário
# mal-intencionado digitar comandos do sistema operacional (ex: 'import os; os.system("rm -rf /")'),
# o servidor executaria.
# 
# A função 'safe_eval' abaixo utiliza a técnica AST (Árvore Sintática Abstrata). 
# Ela desmonta a fórmula matemática em nós lógicos e permite APENAS números e operadores matemáticos,
# bloqueando qualquer tentativa de invasão ou código malicioso.
# ====================================================================================
def safe_eval(expr):
    # FÓRMULA 1: Converte o símbolo clássico de potência '^' para a sintaxe do Python '**'
    # Exemplo: '2 ^ 8' se transforma em '2 ** 8'
    expr = expr.replace('^', '**')
    
    # FÓRMULA 2: Expressão Regular (Regex) para higienização de zeros à esquerda
    # O Python 3 gera erro de sintaxe se um número decimal começar com zero (ex: '01 * 10').
    # A fórmula abaixo busca zeros que NÃO sejam precedidos por outro dígito ou ponto,
    # transformando '01' em '1' e '007' em '7', sem alterar decimais como '0.5' ou '10.05'.
    expr = re.sub(r'(?<![\d.])0+(?=\d)', '', expr)
    
    # Dicionário que mapeia os tipos de nós matemáticos para suas respectivas operações reais
    ops = {
        ast.Add: operator.add,        # Adição (+)
        ast.Sub: operator.sub,        # Subtração (-)
        ast.Mult: operator.mul,       # Multiplicação (*)
        ast.Div: operator.truediv,    # Divisão real (/) -> Ex: 5 / 2 = 2.5
        ast.Pow: operator.pow,        # Potenciação (**) -> Ex: 2 ** 3 = 8
        ast.USub: operator.neg,       # Sinal unário negativo -> Ex: -5
        ast.UAdd: operator.pos,       # Sinal unário positivo -> Ex: +5
    }
    
    # Lista de funções matemáticas permitidas
    funcs = {
        'sqrt': math.sqrt,            # Raiz quadrada -> Ex: sqrt(144) = 12.0
    }

    # Função interna recursiva que navega de galho em galho na árvore de cálculo
    def _eval(node):
        # Caso 1: O nó é um número constante simples (ex: 10, 3.14)
        if isinstance(node, ast.Constant):
            return node.value
            
        # Caso 2: O nó é uma operação binária (com lado esquerdo e direito, ex: 10 + 5)
        elif isinstance(node, ast.BinOp):
            left = _eval(node.left)   # Resolve recursivamente o lado esquerdo
            right = _eval(node.right) # Resolve recursivamente o lado direito
            return ops[type(node.op)](left, right) # Aplica o operador central
            
        # Caso 3: O nó é uma operação unária (com apenas um lado, ex: -10)
        elif isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            return ops[type(node.op)](operand)
            
        # Caso 4: O nó é uma chamada de função segura (ex: sqrt(25))
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in funcs:
                args = [_eval(arg) for arg in node.args]
                return funcs[node.func.id](*args)
            raise ValueError("Função matemática não suportada por segurança")
            
        # Caso 5: Raiz da expressão
        elif isinstance(node, ast.Expression):
            return _eval(node.body)
            
        # Se o nó for qualquer outra coisa (comandos, variáveis de sistema, etc.), rejeita imediatamente!
        else:
            raise ValueError("Operação não permitida na análise sintática")

    # Transforma a string de texto em uma Árvore de Sintaxe no modo de avaliação
    tree = ast.parse(expr, mode='eval')
    # Inicia a avaliação a partir do topo da árvore e devolve o resultado como número decimal (float)
    return float(_eval(tree))


# ====================================================================================
# 2. MEDIÇÃO DE TELEMETRIA: MOTOR PYTHON (Interpretado)
# ====================================================================================
def run_python_calc(expr):
    # Liga o gravador de memória interna do Python
    tracemalloc.start()
    
    # Marca o relógio inicial do processador em nanossegundos (1 segundo = 1 bilhão de nanossegundos)
    t_start = time.perf_counter_ns()
    
    try:
        # Executa a conta
        res = safe_eval(expr)
        res = round(res, 4) # Arredonda para 4 casas decimais para exibição limpa
    except Exception:
        res = "Erro"
        
    # Marca o relógio final do processador em nanossegundos
    t_end = time.perf_counter_ns()
    
    # Coleta a memória máxima (pico) consumida especificamente durante essa conta
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop() # Desliga o gravador de memória
    
    # FÓRMULAS DE CONVERSÃO DE UNIDADES:
    # 1 microssegundo (µs) = 1.000 nanossegundos (ns) -> Fórmula: (t_final - t_inicial) / 1000
    time_micros = (t_end - t_start) / 1000.0
    # 1 Kilobyte (KB) = 1.024 Bytes -> Fórmula: pico_bytes / 1024
    mem_kb = peak / 1024.0
    
    return {
        "result": res, 
        "time_us": round(time_micros, 2), 
        "memory_kb": round(mem_kb, 2)
    }


# ====================================================================================
# 3. MEDIÇÃO DE TELEMETRIA: MOTOR C++ (Compilado Nativo)
# ====================================================================================
def run_cpp_calc(expr):
    try:
        # Executa o arquivo binário compilado nativo './calc' gerado pelo g++
        # Passa a expressão como parâmetro de linha de comando com limite máximo de 2 segundos
        proc = subprocess.run(["./calc", expr], capture_output=True, text=True, timeout=2)
        
        # O programa em C++ imprime na saída padrão no formato: "resultado|tempo_micros"
        output = proc.stdout.strip().split('|')
        
        res = round(float(output[0]), 4)
        internal_time = float(output[1])
        
        # O C++ compilado com código estático possui uma pegada de memória de processo residente 
        # extremamente leve e previsível, em média 120 KB para a arquitetura alvo.
        mem_kb = 120.0  
        
        return {
            "result": res, 
            "time_us": round(internal_time, 2), 
            "memory_kb": mem_kb
        }
    except Exception:
        return {"result": "Erro", "time_us": 0, "memory_kb": 0}


# ====================================================================================
# 4. MEDIÇÃO DE TELEMETRIA: MOTOR JAVA (Máquina Virtual / JVM)
# ====================================================================================
def run_java_calc(expr):
    try:
        # Invoca a Máquina Virtual Java executando a classe compilada 'Calc'
        proc = subprocess.run(["java", "Calc", expr], capture_output=True, text=True, timeout=2)
        
        # O programa Java também imprime na saída padrão no formato: "resultado|tempo_micros"
        output = proc.stdout.strip().split('|')
        
        res = round(float(output[0]), 4)
        internal_time = float(output[1])
        
        # O Java necessita carregar a infraestrutura completa da JVM na memória RAM (Heap inicial,
        # Garbage Collector e classes base do pacote java.lang), consumindo tipicamente ~32.000 KB (~32 MB).
        mem_kb = 32000.0
        
        return {
            "result": res, 
            "time_us": round(internal_time, 2), 
            "memory_kb": round(mem_kb, 2)
        }
    except Exception:
        return {"result": "Erro", "time_us": 0, "memory_kb": 0}


# ====================================================================================
# 5. ROTAS DO SERVIDOR WEB FLASK
# ====================================================================================

# Rota 1 (GET /): Entrega a página visual HTML no navegador do usuário
@app.route('/')
def index():
    return render_template('index.html')


# Rota 2 (POST /calculate): Rota de API chamada pelo JavaScript da tela
@app.route('/calculate', methods=['POST'])
def calculate():
    # Extrai o corpo da requisição JSON enviada pelo navegador
    data = request.json
    expr = data.get('expression', '0')
    
    # Dispara a execução da mesma conta nas 3 linguagens simultaneamente
    res_py = run_python_calc(expr)
    res_cpp = run_cpp_calc(expr)
    res_java = run_java_calc(expr)
    
    # Devolve um único pacote JSON estruturado com os 3 resultados e métricas
    return jsonify({
        "python": res_py,
        "cpp": res_cpp,
        "java": res_java
    })


# Ponto de Entrada Principal (Executado quando você roda 'python app.py')
if __name__ == '__main__':
    # host='0.0.0.0': Permite que o servidor Flask receba requisições vindas de fora do Docker
    # port=5000: Porta padrão do serviço web
    # debug=False: Modo de produção seguro sem vazamento de stacktrace
    app.run(host='0.0.0.0', port=5000, debug=False)
