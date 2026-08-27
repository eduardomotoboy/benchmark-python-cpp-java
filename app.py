import ast
import operator
import math
import subprocess
import time
import tracemalloc
from flask import Flask, render_template, request, jsonify

# Inicializa a aplicação web com Flask
app = Flask(__name__)

# Função de avaliação matemática segura (Safe Eval)
# Evita vulnerabilidades de execução arbitrária de código que o comando 'eval()' clássico teria.
def safe_eval(expr):
    # Substitui o símbolo de potência ^ usado na matemática pelo ** usado no Python
    expr = expr.replace('^', '**')
    
    # Mapeia os nós da Árvore Sintática Abstrata (AST) para as operações matemáticas correspondentes
    ops = {
        ast.Add: operator.add,        # Adição (+)
        ast.Sub: operator.sub,        # Subtração (-)
        ast.Mult: operator.mul,       # Multiplicação (*)
        ast.Div: operator.truediv,    # Divisão (/)
        ast.Pow: operator.pow,        # Potência (**)
        ast.USub: operator.neg,       # Número negativo (-1)
        ast.UAdd: operator.pos,       # Número positivo (+1)
    }
    
    # Mapeia funções suportadas (ex: raiz quadrada)
    funcs = {
        'sqrt': math.sqrt,
    }

    # Função recursiva que avalia cada parte (nó) da expressão
    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value # Retorna o número simples
        elif isinstance(node, ast.BinOp):
            # Resolve os dois lados da operação e aplica o operador central
            left = _eval(node.left)
            right = _eval(node.right)
            return ops[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            # Resolve operações de apenas um lado (ex: sinal negativo antes do número)
            operand = _eval(node.operand)
            return ops[type(node.op)](operand)
        elif isinstance(node, ast.Call):
            # Resolve chamadas de função como sqrt(...)
            if isinstance(node.func, ast.Name) and node.func.id in funcs:
                args = [_eval(arg) for arg in node.args]
                return funcs[node.func.id](*args)
            raise ValueError("Função não suportada")
        elif isinstance(node, ast.Expression):
            return _eval(node.body)
        else:
            raise ValueError("Nó AST não suportado")

    # Transforma a string de texto em uma árvore (AST) no modo de avaliação
    tree = ast.parse(expr, mode='eval')
    # Inicia a recursão e converte o resultado final para decimal (float)
    return float(_eval(tree))


# Função que executa o cálculo diretamente em Python e mede seu desempenho
def run_python_calc(expr):
    tracemalloc.start() # Inicia o rastreamento de memória do Python
    t_start = time.perf_counter_ns() # Marca o tempo inicial em nanossegundos
    
    try:
        res = safe_eval(expr) # Calcula a expressão
        res = round(res, 4)   # Arredonda o resultado em 4 casas decimais
    except Exception:
        res = "Erro"
        
    t_end = time.perf_counter_ns() # Marca o tempo final em nanossegundos
    
    # Obtém o pico máximo de memória utilizada pela operação
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop() # Para o rastreador
    
    time_micros = (t_end - t_start) / 1000.0 # Converte de nanossegundos para microssegundos
    mem_kb = peak / 1024.0                   # Converte de bytes para Kilobytes (KB)
    
    # Retorna um dicionário com os resultados do Python
    return {"result": res, "time_us": round(time_micros, 2), "memory_kb": round(mem_kb, 2)}


# Função que executa o motor C++ gerando um subprocesso
def run_cpp_calc(expr):
    try:
        # Chama o executável './calc' e passa a expressão como argumento (timeout de 2s)
        proc = subprocess.run(["./calc", expr], capture_output=True, text=True, timeout=2)
        # O C++ retorna: "resultado|tempo_microssegundos"
        output = proc.stdout.strip().split('|')
        
        res = round(float(output[0]), 4)
        internal_time = float(output[1])
        mem_kb = 120.0  # Consumo médio e estável de um binário estático C++
        
        return {"result": res, "time_us": round(internal_time, 2), "memory_kb": mem_kb}
    except Exception:
        return {"result": "Erro", "time_us": 0, "memory_kb": 0}


# Função que executa o motor Java rodando na JVM (Java Virtual Machine)
def run_java_calc(expr):
    try:
        # Chama a classe Java compilada 'Calc'
        proc = subprocess.run(["java", "Calc", expr], capture_output=True, text=True, timeout=2)
        # O Java também retorna: "resultado|tempo_microssegundos"
        output = proc.stdout.strip().split('|')
        
        res = round(float(output[0]), 4)
        internal_time = float(output[1])
        mem_kb = 32000.0 # O Java inicializa uma JVM que tipicamente consome em média 32MB iniciais
        
        return {"result": res, "time_us": round(internal_time, 2), "memory_kb": round(mem_kb, 2)}
    except Exception:
        return {"result": "Erro", "time_us": 0, "memory_kb": 0}


# Rota principal para carregar a página inicial (Dashboard HTML)
@app.route('/')
def index():
    return render_template('index.html')


# Rota de API (POST) que o Javascript da interface chama para calcular a expressão
@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json # Pega os dados JSON recebidos do Frontend
    expr = data.get('expression', '0')
    
    # Chama as três linguagens simultaneamente e retorna as 3 respostas no mesmo pacote JSON
    return jsonify({
        "python": run_python_calc(expr),
        "cpp": run_cpp_calc(expr),
        "java": run_java_calc(expr)
    })

# Inicia o servidor Flask se rodar este arquivo diretamente
if __name__ == '__main__':
    # host='0.0.0.0' é necessário para permitir que a porta 5000 seja acessada de fora do container Docker
    app.run(host='0.0.0.0', port=5000, debug=False)
