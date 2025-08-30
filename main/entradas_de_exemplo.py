entradas_de_exemplo = {
    "Entrada Complexa sem Erro": '''int a;
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