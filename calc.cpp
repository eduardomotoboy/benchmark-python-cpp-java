// Bibliotecas base necessárias para entrada e saída, medição de tempo, matemática, conversão e manipulação de arrays
#include <iostream>
#include <string>
#include <chrono>
#include <cmath>
#include <sstream>
#include <vector>
#include <algorithm>

// Função auxiliar que procura por "sqrt(...)" na expressão textual e resolve as raízes quadradas antes do cálculo base
std::string processSqrt(std::string expr) {
    size_t pos = 0;
    // O loop encontra todas as ocorrências da palavra "sqrt("
    while ((pos = expr.find("sqrt(", pos)) != std::string::npos) {
        size_t end = expr.find(")", pos); // Procura o parêntese de fechamento
        if (end == std::string::npos) break; // Sai se a string estiver mal formatada
        
        // Extrai o número que está dentro do sqrt() e converte para double
        double val = std::stod(expr.substr(pos + 5, end - (pos + 5)));
        // Tira a raiz usando a biblioteca cmath e converte o resultado final de volta para texto
        std::string res = std::to_string(std::sqrt(val));
        
        // Substitui "sqrt(numero)" pelo resultado real dentro da expressão de texto
        expr.replace(pos, end - pos + 1, res);
    }
    return expr; // Retorna a expressão "limpa", pronta para ser calculada normalmente
}

// Função principal de interpretação matemática que avalia uma expressão numérica
double evaluate(std::string expr) {
    expr = processSqrt(expr); // Primeiro resolve raízes quadradas
    std::stringstream ss(expr); // Transforma a string em um "stream" fácil de processar número a número
    
    double num;
    char op;
    
    std::vector<double> vals; // Array para armazenar os números
    std::vector<char> ops;    // Array para armazenar os operadores matemáticos
    
    // O stream processa e separa automaticamente números e caracteres (+, -, *, /, ^)
    if (ss >> num) vals.push_back(num); // Captura o primeiro número
    while (ss >> op >> num) {           // Captura a sequência infinita de [operador] [número]
        ops.push_back(op);
        vals.push_back(num);
    }
    
    if (vals.empty()) return 0; // Proteção contra cálculo vazio

    // 1. Prioridade: Processa potências (^)
    for (int i = 0; i < (int)ops.size(); ) {
        if (ops[i] == '^') {
            vals[i] = std::pow(vals[i], vals[i + 1]); // Calcula base elevada ao expoente
            vals.erase(vals.begin() + i + 1);         // Remove o número da direita já usado
            ops.erase(ops.begin() + i);               // Remove o operador já usado
        } else {
            i++; // Se não foi potência, avança
        }
    }

    // 2. Prioridade: Processa multiplicações e divisões (*, /) da esquerda para a direita
    for (int i = 0; i < (int)ops.size(); ) {
        if (ops[i] == '*') {
            vals[i] *= vals[i + 1];
            vals.erase(vals.begin() + i + 1);
            ops.erase(ops.begin() + i);
        } else if (ops[i] == '/') {
            // Se o divisor for zero, usa 1 temporariamente para não travar (ou poderia lançar erro)
            vals[i] /= (vals[i + 1] != 0 ? vals[i + 1] : 1);
            vals.erase(vals.begin() + i + 1);
            ops.erase(ops.begin() + i);
        } else {
            i++; // Se não foi *, nem /, avança
        }
    }

    // 3. Prioridade Final: Processa somas e subtrações (+, -) varrendo até o final
    double total = vals[0];
    for (size_t i = 0; i < ops.size(); ++i) {
        if (ops[i] == '+') total += vals[i + 1];
        if (ops[i] == '-') total -= vals[i + 1];
    }
    
    return total; // Retorna o valor numérico final calculado
}

// Função raiz do binário C++
int main(int argc, char* argv[]) {
    // Retorna erro se não for passado nenhum argumento
    if (argc < 2) return 1;
    
    // Inicia a medição de tempo com o relógio de mais alta resolução disponível no Sistema Operacional
    auto start = std::chrono::high_resolution_clock::now();
    
    // Dispara a avaliação, passando o texto digitado via shell (argv[1])
    double result = evaluate(argv[1]);
    
    // Finaliza a medição e calcula a diferença de tempo percorrido
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::nano> elapsed = end - start;
    
    // Imprime a resposta na formatação padrão que o Python está aguardando (resultado|microssegundos)
    // Usamos endl ao final. 1 microssegundo equivale a 1000 nanossegundos.
    std::cout << result << "|" << (elapsed.count() / 1000.0) << std::endl;
    return 0;
}
