# Entrada de teste que engloba todos os aspectos da
# linguagem para o analisador sintático
entrada = '''int global_var;
bool flag;

void procedimentoSemParametro() {
    int x;
    x = 5;
    print(x);
    return;
}

int funcaoComParametro(int p) {
    if (p > 0) {
        return p * 2;
    } else {
        return 0;
    }
}

int main() {
    int a, b;
    bool c;

    a = 10;
    b = funcaoComParametro(a);
    flag = true;

    while (flag) {
        if (b == 20) {
            print(b);
            break;
        } else {
            b = b - 1;
            continue;
        }
    }

    procedimentoSemParametro();
    print(global_var);

    return 0;
}
'''

import streamlit as st
from analisador_lexico import Lexer
from analisador_sintatico import Parser
from analisador_sintatico_preditivo import PredictiveParser

st.title("Analisador Léxico e Sintático para linguagem C simplificada")

codigo = st.text_area("Digite o código-fonte aqui:", height=300, value=entrada)

if st.button("Analisar"):
    try:
        st.subheader("Tokens:")
        lexer = Lexer(codigo)
        tokens = lexer.analisar()
        for t in tokens:
            st.write(t)

        st.subheader("Análise sintática (Top-Down com Backtracking)")
        parser = Parser(lexer).analisar()
        st.write("Análise sintática concluída com sucesso!")

        st.subheader("Análisa sintática (Top-Down Preditiva)")
        pparser = PredictiveParser(tokens)
        pparser.parse()
        st.write("Análise sintática concluída com sucesso!")

    except Exception as e:
        st.error(f"Erro: {e}")
