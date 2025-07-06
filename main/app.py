entrada = '''int x, y;
bool flag;

int soma(int a, int b) {
    int resultado;
    resultado = a + b;
    return resultado;
}

int main() {
    x = 10;
    y = 20;
    flag = true;
    if (x < y) {
        printf(x);
    } else {
        printf(y);
    }
        return 0;
    }
'''

import streamlit as st
from analisador_lexico import Lexer
from analisador_sintatico import Parser

st.title("Analisador Léxico e Sintático para linguagem C simplificada")

codigo = st.text_area("Digite o código-fonte aqui:", height=300, value=entrada)

if st.button("Analisar"):
    try:
        st.subheader("Tokens:")
        lexer = Lexer(codigo)
        tokens = lexer.analisar()
        for t in tokens:
            st.write(t)

        st.subheader("Análise sintática: ")
        parser = Parser(lexer).analisar()
        if parser is None:
            st.write("Análise sintática completa sem erros.")

    except Exception as e:
        st.error(f"Erro: {e}")
