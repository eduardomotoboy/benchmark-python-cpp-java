// Biblioteca para usar as listas nativas (ArrayList, List)
import java.util.*;

public class Calc {

    // Função que substitui a presença de 'sqrt(...)' pelos seus respectivos valores calculados antes de avaliar o resto
    private static String processSqrt(String expr) {
        while (expr.contains("sqrt(")) {
            int start = expr.indexOf("sqrt(");
            int end = expr.indexOf(")", start);
            if (end == -1) break; // Garante que a expressão está bem formatada
            
            // Pega o número dentro dos parênteses e transforma num tipo Double
            double val = Double.parseDouble(expr.substring(start + 5, end).trim());
            // Substitui 'sqrt(x)' pelo seu resultado raiz na string principal
            expr = expr.substring(0, start) + Math.sqrt(val) + expr.substring(end + 1);
        }
        return expr;
    }

    // Função principal que lê a string inteira da conta e converte no resultado numérico
    public static double evaluate(String expr) {
        expr = processSqrt(expr); // Tratamento inicial para as raízes
        
        // Expressão regular que divide o texto sempre que há um sinal (mantendo os sinais no array de resultados)
        String[] tokens = expr.split("(?<=[-+*/^])|(?=[-+*/^])");
        
        List<Double> numbers = new ArrayList<>();   // Lista de números da conta
        List<Character> ops = new ArrayList<>();    // Lista de operadores aritméticos
        
        // O loop classifica os pedaços separados de texto (tokens) entre números e operadores
        for (String t : tokens) {
            t = t.trim();
            if (t.isEmpty()) continue;
            if ("+-*/^".contains(t)) {
                ops.add(t.charAt(0)); // Adiciona na lista de caracteres/operadores
            } else {
                numbers.add(Double.parseDouble(t)); // Adiciona na lista de números decimais
            }
        }

        if (numbers.isEmpty()) return 0; // Proteção contra cálculo fantasma/vazio

        // PASSO 1: Resolve todas as potências antes de todo o resto
        for (int i = 0; i < ops.size(); ) {
            if (ops.get(i) == '^') {
                numbers.set(i, Math.pow(numbers.get(i), numbers.get(i + 1))); // Calcula a base elevada ao expoente
                numbers.remove(i + 1); // Remove os elementos já usados das duas listas
                ops.remove(i);
            } else {
                i++;
            }
        }

        // PASSO 2: Resolve todas as multiplicações e divisões da esquerda para a direita
        for (int i = 0; i < ops.size(); ) {
            char op = ops.get(i);
            if (op == '*' || op == '/') {
                double next = numbers.get(i + 1);
                // Proteção simples contra divisão por zero para não falhar a execução do teste
                double res = (op == '*') ? numbers.get(i) * next : numbers.get(i) / (next == 0 ? 1 : next);
                
                numbers.set(i, res);   // Armazena a resposta no lugar do primeiro número
                numbers.remove(i + 1); // Limpa as sobras usadas
                ops.remove(i);
            } else {
                i++;
            }
        }

        // PASSO 3: Conclui processando todas as adições e subtrações 
        double total = numbers.get(0);
        for (int i = 0; i < ops.size(); i++) {
            if (ops.get(i) == '+') total += numbers.get(i + 1);
            if (ops.get(i) == '-') total -= numbers.get(i + 1);
        }
        
        return total; // Devolve o número com a conta totalmente encerrada
    }

    // Função de entrada do Java que o console ou processo principal do sistema chamará
    public static void main(String[] args) {
        // Exige que um argumento textual (a conta) seja passado
        if (args.length < 1) return;
        
        // Medição do tempo de execução da JVM com alta precisão (nanoTime)
        long start = System.nanoTime();
        double res = evaluate(args[0]); // Invoca o avaliador
        long end = System.nanoTime();
        
        // Converte nanossegundos para microssegundos, mantendo precisão decimal
        double timeMicros = (end - start) / 1000.0;
        
        // Cospe os dados (resultado e tempo) divididos pelo pipe '|' que o servidor Python irá interpretar
        System.out.println(res + "|" + timeMicros);
    }
}
