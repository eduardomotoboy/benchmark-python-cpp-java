// ====================================================================================
// MOTOR DE CÁLCULO NATIVO EM C++ (calc.cpp)
// 
// Objetivo do Arquivo:
// 1. Receber uma fórmula matemática como argumento de linha de comando (ex: ./calc "2 ^ 8 + sqrt(144)").
// 2. Resolver as operações respeitando estritamente a Ordem de Precedência Matemática (PEMDAS):
//    - Passo 0: Resolução de Raízes Quadradas (sqrt)
//    - Passo 1: Potenciação (^)
//    - Passo 2: Multiplicação (*) e Divisão (/)
//    - Passo 3: Adição (+) e Subtração (-)
// 3. Cronometrar o tempo de cálculo em nanossegundos usando std::chrono.
// 4. Imprimir na tela no formato padronizado "RESULTADO|TEMPO_MICROSSEGUNDOS".
// ====================================================================================

#include <iostream>   // Biblioteca padrão para entrada e saída de dados (std::cout)
#include <string>     // Manipulação avançada de textos (std::string)
#include <chrono>     // Biblioteca de alta precisão para medição de tempo do hardware (std::chrono)
#include <cmath>      // Biblioteca com funções matemáticas avançadas (std::sqrt, std::pow)
#include <sstream>    // Conversão de fluxos de texto para números e vice-versa (std::stringstream)
#include <vector>     // Estrutura de dados de vetores dinâmicos (std::vector)
#include <algorithm>  // Algoritmos de busca e manipulação de coleções


// ====================================================================================
// FUNÇÃO 1: PRÉ-PROCESSADOR DE RAÍZES QUADRADAS (processSqrt)
// Objetivo: Localizar termos como 'sqrt(144)' e substituí-los pelo valor numérico '12.0'
// antes de começar a resolver as 4 operações básicas.
// ====================================================================================
std::string processSqrt(std::string expr) {
    size_t pos = 0;
    
    // Procura pela palavra "sqrt(" dentro da string até não encontrar mais nenhuma
    while ((pos = expr.find("sqrt(", pos)) != std::string::npos) {
        // Encontra o parêntese correspondente que fecha a raiz ")"
        size_t end = expr.find(")", pos);
        if (end == std::string::npos) break; // Proteção contra parênteses não fechados
        
        // FÓRMULA DE RECORTE: Extrai apenas o número que está entre "sqrt(" e ")"
        // pos + 5 pula os 5 caracteres da palavra "sqrt("
        std::string innerNumStr = expr.substr(pos + 5, end - (pos + 5));
        
        // Converte o texto para número decimal (double)
        double val = std::stod(innerNumStr);
        
        // FÓRMULA MATEMÁTICA: Calcula a raiz quadrada real usando std::sqrt()
        std::string res = std::to_string(std::sqrt(val));
        
        // Substitui a expressão inteira "sqrt(X)" pelo seu resultado calculado dentro da string original
        expr.replace(pos, end - pos + 1, res);
    }
    
    return expr; // Devolve a expressão pronta para o avaliador principal
}


// ====================================================================================
// FUNÇÃO 2: AVALIADOR MATEMÁTICO (evaluate)
// Objetivo: Interpretar a sequência de números e operadores seguindo a precedência matemática.
// ====================================================================================
double evaluate(std::string expr) {
    // Passo 0: Limpa todas as raízes quadradas primeiro
    expr = processSqrt(expr);
    
    // Cria um fluxo de leitura a partir do texto
    std::stringstream ss(expr);
    
    double num;
    char op;
    
    // Vetores dinâmicos para separar a conta em duas listas paralelas:
    std::vector<double> vals; // Armazena a lista de números (ex: [2, 8, 12])
    std::vector<char> ops;    // Armazena a lista de operadores (ex: ['^', '+'])
    
    // O operador '>>' do C++ lê automaticamente o primeiro número
    if (ss >> num) vals.push_back(num);
    
    // Loop de leitura: Lê pares alternados de [OPERADOR] e [NÚMERO]
    while (ss >> op >> num) {
        ops.push_back(op);
        vals.push_back(num);
    }
    
    // Se a expressão estiver vazia, retorna zero
    if (vals.empty()) return 0;

    // ========================================================================
    // REGRA DE PRECEDÊNCIA 1: POTÊNCIAS (^)
    // Resolve todas as potenciações da esquerda para a direita
    // ========================================================================
    for (int i = 0; i < (int)ops.size(); ) {
        if (ops[i] == '^') {
            // FÓRMULA MATEMÁTICA: std::pow(base, expoente) -> Ex: 2 ^ 3 = 8
            vals[i] = std::pow(vals[i], vals[i + 1]);
            
            // Remove o segundo número e o operador '^' que já foram calculados
            vals.erase(vals.begin() + i + 1);
            ops.erase(ops.begin() + i);
        } else {
            i++; // Avança para o próximo operador se não for potência
        }
    }

    // ========================================================================
    // REGRA DE PRECEDÊNCIA 2: MULTIPLICAÇÃO (*) E DIVISÃO (/)
    // Resolve multiplicações e divisões da esquerda para a direita
    // ========================================================================
    for (int i = 0; i < (int)ops.size(); ) {
        if (ops[i] == '*') {
            // FÓRMULA: número1 * número2
            vals[i] *= vals[i + 1];
            vals.erase(vals.begin() + i + 1);
            ops.erase(ops.begin() + i);
        } else if (ops[i] == '/') {
            // FÓRMULA: número1 / número2 (Proteção contra divisão por zero)
            vals[i] /= (vals[i + 1] != 0 ? vals[i + 1] : 1);
            vals.erase(vals.begin() + i + 1);
            ops.erase(ops.begin() + i);
        } else {
            i++; // Avança se for soma ou subtração
        }
    }

    // ========================================================================
    // REGRA DE PRECEDÊNCIA 3: ADIÇÃO (+) E SUBTRAÇÃO (-)
    // Por fim, acumula todas as somas e subtrações restantes
    // ========================================================================
    double total = vals[0];
    for (size_t i = 0; i < ops.size(); ++i) {
        if (ops[i] == '+') total += vals[i + 1]; // FÓRMULA: total + próximo
        if (ops[i] == '-') total -= vals[i + 1]; // FÓRMULA: total - próximo
    }
    
    return total; // Retorna o valor numérico final exato
}


// ====================================================================================
// FUNÇÃO PRINCIPAL DE ENTRADA DO PROGRAMA (main)
// ====================================================================================
int main(int argc, char* argv[]) {
    // Validação de entrada: Se não for passada uma conta no terminal, finaliza com código de erro 1
    if (argc < 2) return 1;
    
    // MEDIÇÃO DE TEMPO ULTRA PRECISA:
    // Inicia o cronômetro utilizando o relógio de mais alta resolução nativo do processador
    auto start = std::chrono::high_resolution_clock::now();
    
    // Executa a avaliação da fórmula passada em argv[1]
    double result = evaluate(argv[1]);
    
    // Para o cronômetro
    auto end = std::chrono::high_resolution_clock::now();
    
    // FÓRMULA DE CÁLCULO DE DURAÇÃO:
    // Calcula o tempo decorrido em nanossegundos
    std::chrono::duration<double, std::nano> elapsed = end - start;
    
    // FÓRMULA DE CONVERSÃO DE UNIDADES:
    // 1 microssegundo (µs) = 1.000 nanossegundos (ns) -> Fórmula: nanos / 1000.0
    double timeMicros = elapsed.count() / 1000.0;
    
    // Imprime na tela a saída padronizada com o caractere delimitador pipe '|'
    // Exemplo de saída: "268|77.81"
    std::cout << result << "|" << timeMicros << std::endl;
    
    return 0; // Código 0 indica término com sucesso
}
