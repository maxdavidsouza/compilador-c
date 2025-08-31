entradas_de_exemplo = {
    "Teste 1: Variáveis Locais e Globais, Laço e Condicional Simples": '''int g;
int loopTest(int x) {
    int sum;
    sum = 0;
    while (x > 0) {
        sum = sum + x;
        x = x - 1;
    }
    return sum;
}

int main() {
    int y;
    y = loopTest(5);
    print(y); // Deve imprimir 15
    if (y > 10) {
        g = 2;
    } else {
        g = 3;
    }
    print(g); // Deve imprimir 2
    return 0;
}       
''',
    "Teste 2: Atribuições Múltiplas e Expressões Complexas": '''int int_var;
float float_var;
bool bool_var;

void complexCalc() {
    int_var = 10 + 2 * 5 - 3;
    float_var = 5.5 / 2.0;
    bool_var = int_var > 15 && float_var < 3.0;
    print(int_var); // Deve imprimir 17
    print(float_var); // Deve imprimir 2.75
    printBool(bool_var); // Deve imprimir 1 (true)
}

int main() {
    complexCalc();
    return 0;
}
''',
    "Teste 3: Recursão e return Múltiplos": '''int fibonacci(int n) {
    if (n <= 1) {
        return n;
    } else {
        return fibonacci(n-1) + fibonacci(n-2);
    }
}

int main() {
    int result;
    result = fibonacci(8);
    print(result); // Deve imprimir 21
    return 0;
}
''',
    "Teste 4: Entrada Complexa com Múltiplas Funções": '''int a;
int soma(int a, int b) {
    a = 4;
    return a + b;
}

bool maiorQueDez(int x) {
    a = 2;
    return x > 10;
}

void printBool(bool x) {
    a = 5;
    if (x) {
        print(1);
    } else {
        print(0);
    }
}

int fatorial(int n) {
    a = 10;
    if (n == 0) {
        return 1;
    } else {
        return n * fatorial(n - 1);
    }
}

int main() {
    a = 9;
    int x;
    int y;
    int z;
    bool cond;

    x = a;
    y = 12;
    z = soma(x, y);

    cond = maiorQueDez(z);

    print(z);
    printBool(cond);

    z = fatorial(5);
    print(z);

    return 0;
}
''',
    "Teste 5: Gerador de Código 3AC": '''int soma(int x, int y){
    return x + y;
}
    
int soma2(int x, int y){
    return soma(x,y) + soma(x,y);
}
    
int main() {
    int x, y, z;
    x = 10;
    y = 5;
    z = soma2(x,y);
    print(z);
    return 0;
}       
''',
    "Teste 6: Otimizador de Código 3AC": '''int main() {
        int x, y;
        x = 10;
        y = 5;
        print(x+y);
        return 0;
    }       
''',
    "Erro 1: tipo incompatível": '''int main() {
    int a;
    a = true; // Erro Semântico!
    return 0;
}
''',

    "Erro 2: variável não declarada": '''int main() {
    x = 10; // Erro: 'x' não foi declarado
    return 0;
}
''',

    "Erro 3: função void atribuída a variável": '''void imprime(int x) {
    print(x);
}

int main() {
    int y;
    y = imprime(5); // ERRO: função 'imprime' é void
    return 0;
}
''',

    "Erro 4: break fora de laço": '''int main() {
    break; // ERRO: break só pode estar dentro de laços
    return 0;
}
''',

    "Erro 5: return em função void": '''void f() {
    return 10; // ERRO: função void não pode retornar valor
}

int main() {
    f();
    return 0;
}
''',

    "Erro 6: função sem return": '''int f() {
    int x;
    x = 5;
} // ERRO: função int 'f' não retorna valor

int main() {
    return 0;
}
''',

    "Erro 7: número de parâmetros incorreto": '''int soma(int a, int b) {
    return a + b;
}

int main() {
    int x;
    x = soma(1); // ERRO: espera 2 parâmetros, recebeu 1
    return 0;
}
''',

    "Erro 8: tipos de parâmetros incompatíveis": '''bool ehPositivo(int x) {
    return x > 0;
}

int main() {
    bool r;
    r = ehPositivo(true); // ERRO: esperado int, recebeu bool
    return 0;
}
''',

    "Erro 9: expressão lógica inválida": '''int main() {
    int a, b;
    a = 1;
    b = 2;
    bool c;
    c = a && b; // ERRO: && só pode ser usado entre bools
    return 0;
}
''',

    "Erro 10: expressão aritmética com tipos misturados": '''int main() {
    int a;
    bool b;
    b = false;
    float c;
    c = 2.5
    a = (3 + 2) * (b || 5); // ERRO: mistura int e bool em aritmética
    return 0;
}
''',

    "Erro 11: função de retorno de tipos diferentes": '''float s(int a, bool b){
        return a + b;
    }
    
    int main() {
        print(s(1, false));
        return 0;
    }
''',
}