import streamlit as st
import pandas as pd
from analisador_lexico import Lexer
from analisador_sintatico import Parser
from analisador_semantico import AnalisadorSemantico

st.title("Analisador Léxico, Sintático e Semântico para linguagem C simplificada")

# Código de exemplo com um erro semântico (atribuição de bool para int)
entrada_com_erro = '''
int main() {
    int a;
    a = true; // Erro Semântico!
    return 0;
}
'''

entrada_sem_erro = '''
int a;
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
'''

codigo = st.text_area("Digite o código-fonte aqui:", height=300, value=entrada_sem_erro)

if st.button("Analisar"):
    try:
        # Análise Léxica
        st.subheader("Tokens Obtidos:")
        lexer = Lexer(codigo)
        tokens = lexer.analisar()
        for t in tokens:
            st.write(t)

        # Tabela de Símbolos
        st.subheader("Tabela de Símbolos (Pós Análise Léxica)")
        simbolos = [
            {
                "Nome": s.nome,
                "Tipo": s.tipo,
                "Escopo": s.escopo,
                "Endereço": s.endereco
            }
            for s in lexer.tabela_simbolos.tabela.values()
        ]
        if simbolos:
            df = pd.DataFrame(simbolos)
            st.table(df)
        else:
            st.write("Nenhum identificador encontrado.")

        # Análise Sintática e Semântica
        parser = AnalisadorSemantico(tokens)

        st.subheader("Análise Sintática e Semântica")
        parser.analisar()
        st.success("Análise Sintática e Semântica concluída com sucesso!")

        st.subheader("Árvore de Derivação Sintática")
        st.graphviz_chart(parser.gerar_dot_string())

        st.subheader("Tabela de Símbolos (Pós Análise Semântica)")
        if parser.tabela_simbolos:
            df = pd.DataFrame(parser.tabela_simbolos)
            st.table(df)
        else:
            st.write("Nenhum símbolo registrado.")

        st.subheader("Grafo de Dependências")
        st.graphviz_chart(parser.gerar_grafo_dependencias())

    except Exception as e:
        st.error(str(e))  # Vai mostrar tanto erros sintáticos quanto semânticos
