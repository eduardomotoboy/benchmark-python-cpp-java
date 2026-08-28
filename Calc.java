// ====================================================================================
// MOTOR DE CÁLCULO EM JAVA (Calc.java)
// 
// Objetivo do Arquivo:
// 1. Ser executado sobre a Máquina Virtual Java (JVM).
// 2. Receber a fórmula matemática via argumento de linha de comando (args[0]).
// 3. Fazer a separação léxica (Tokenização) e avaliar as operações com precedência matemática:
//    - Passo 0: Resolução prévia de raízes quadradas (sqrt)
//    - Passo 1: Potenciação (^)
//    - Passo 2: Multiplicação (*) e Divisão (/)
//    - Passo 3: Adição (+) e Subtração (-)
// 4. Medir o tempo de cálculo em nanossegundos via System.nanoTime().
// 5. Imprimir o resultado padronizado "RESULTADO|TEMPO_MICROSSEGUNDOS".
// ====================================================================================

import java.util.*; // Importa coleções fundamentais como List, ArrayList

public class Calc {

    // ================================================================================
    // FUNÇÃO 1: PRÉ-PROCESSADOR DE RAÍZES QUADRADAS (processSqrt)
    // Objetivo: Encontra e calcula expressões como 'sqrt(144)', substituindo por '12.0'
    // ================================================================================
    private static String processSqrt(String expr) {
        // Enquanto houver ocorrência de "sqrt(" no texto da fórmula
        while (expr.contains("sqrt(")) {
            int start = expr.indexOf("sqrt(");
            int end = expr.indexOf(")", start);
            if (end == -1) break; // Proteção contra sintaxe mal formatada
            
            // FÓRMULA DE RECORTE: Extrai o número entre 'sqrt(' e ')'
            String innerNum = expr.substring(start + 5, end).trim();
            double val = Double.parseDouble(innerNum);
            
            // FÓRMULA MATEMÁTICA: Calcula a raiz quadrada com Math.sqrt()
            double sqrtResult = Math.sqrt(val);
            
            // Substitui o bloco "sqrt(X)" pelo valor calculado na string original
            expr = expr.substring(0, start) + sqrtResult + expr.substring(end + 1);
        }
        return expr; // Devolve a fórmula limpa
    }


    // ================================================================================
    // FUNÇÃO 2: AVALIADOR MATEMÁTICO PRINCIPAL (evaluate)
    // Objetivo: Separar tokens e resolver na ordem estrita de precedência
    // ================================================================================
    public static double evaluate(String expr) {
        // Passo 0: Trata as raízes quadradas
        expr = processSqrt(expr);
        
        // FÓRMULA REGEX DE TOKENIZAÇÃO:
        // Divide o texto mantendo os operadores (+, -, *, /, ^) na lista de tokens
        // O lookahead (?=[...]) e lookbehind (?<=[...]) dividem antes e depois dos símbolos
        String[] tokens = expr.split("(?<=[-+*/^])|(?=[-+*/^])");
        
        // Listas dinâmicas para armazenar números e operadores separadamente
        List<Double> numbers = new ArrayList<>();
        List<Character> ops = new ArrayList<>();

        // Percorre cada pedaço de texto (token) e classifica se é número ou operador
        for (String t : tokens) {
            t = t.trim();
            if (t.isEmpty()) continue;
            
            // Se for um operador aritmético
            if ("+-*/^".contains(t)) {
                ops.add(t.charAt(0));
            } else {
                // Se for um número, converte para decimal de dupla precisão (Double)
                numbers.add(Double.parseDouble(t));
            }
        }

        // Se a lista estiver vazia, retorna zero
        if (numbers.isEmpty()) return 0;

        // ============================================================================
        // REGRA DE PRECEDÊNCIA 1: POTÊNCIA (^)
        // ============================================================================
        for (int i = 0; i < ops.size(); ) {
            if (ops.get(i) == '^') {
                // FÓRMULA MATEMÁTICA: Math.pow(base, expoente) -> Ex: 2 ^ 4 = 16
                double base = numbers.get(i);
                double exponent = numbers.get(i + 1);
                double powerResult = Math.pow(base, exponent);
                
                numbers.set(i, powerResult); // Atualiza a posição com o resultado
                numbers.remove(i + 1);       // Remove o número da direita já usado
                ops.remove(i);               // Remove o operador já usado
            } else {
                i++; // Avança se não for potência
            }
        }

        // ============================================================================
        // REGRA DE PRECEDÊNCIA 2: MULTIPLICAÇÃO (*) E DIVISÃO (/)
        // ============================================================================
        for (int i = 0; i < ops.size(); ) {
            char op = ops.get(i);
            if (op == '*' || op == '/') {
                double num1 = numbers.get(i);
                double num2 = numbers.get(i + 1);
                
                // FÓRMULA MATEMÁTICA: Multiplica ou Divide (com proteção contra divisão por zero)
                double res = (op == '*') ? (num1 * num2) : (num1 / (num2 == 0 ? 1 : num2));
                
                numbers.set(i, res);   // Substitui pelo resultado
                numbers.remove(i + 1); // Remove elementos usados
                ops.remove(i);
            } else {
                i++; // Avança se for soma ou subtração
            }
        }

        // ============================================================================
        // REGRA DE PRECEDÊNCIA 3: ADIÇÃO (+) E SUBTRAÇÃO (-)
        // ============================================================================
        double total = numbers.get(0);
        for (int i = 0; i < ops.size(); i++) {
            if (ops.get(i) == '+') total += numbers.get(i + 1); // FÓRMULA: total + próximo
            if (ops.get(i) == '-') total -= numbers.get(i + 1); // FÓRMULA: total - próximo
        }
        
        return total; // Retorna o valor final calculado
    }


    // ================================================================================
    // FUNÇÃO PRINCIPAL DE ENTRADA DO JAVA (main)
    // ================================================================================
    public static void main(String[] args) {
        // Validação: Exige que a fórmula tenha sido passada como primeiro argumento
        if (args.length < 1) return;
        
        // MEDIÇÃO DE TEMPO NATIVO DA JVM:
        // Marca o tempo inicial do processador em nanossegundos
        long start = System.nanoTime();
        
        // Executa a conta
        double res = evaluate(args[0]);
        
        // Marca o tempo final em nanossegundos
        long end = System.nanoTime();
        
        // FÓRMULA DE CONVERSÃO DE UNIDADES:
        // 1 microssegundo (µs) = 1.000 nanossegundos (ns) -> Fórmula: (end - start) / 1000.0
        double timeMicros = (end - start) / 1000.0;
        
        // Imprime a resposta padronizada com delimitador pipe '|'
        // Exemplo: "268.0|110854.02"
        System.out.println(res + "|" + timeMicros);
    }
}
