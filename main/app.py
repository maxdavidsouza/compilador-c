# Entrada de teste que engloba todos os aspectos da
# linguagem para o analisador sintático
#import graphviz

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
import pandas as pd
from analisador_lexico import Lexer
from analisador_sintatico import Parser
from analisador_semantico import AnalisadorSemantico

st.title("Analisador Léxico, Semântico e Sintático para linguagem C simplificada")

# Código de exemplo com um erro semântico (atribuição de bool para int)
entrada_com_erro = '''
int main() {
    int a;
    a = true; // Erro Semântico!
    return 0;
}
'''

codigo = st.text_area("Digite o código-fonte aqui:", height=300, value=entrada_com_erro)

if st.button("Analisar"):
    try:
        # Análise Léxica (sem mudanças)
        st.subheader("Tokens:")
        lexer = Lexer(codigo)
        tokens = lexer.analisar()
        for t in tokens:
            st.write(t)

        # 🔹 Mostrando a Tabela de Símbolos
        st.subheader("Tabela de Símbolos (Pós Analisador Léxico)")
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
        parser = AnalisadorSemantico(tokens) # MUDANÇA AQUI
        
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

    except Exception as e:
        st.error(str(e)) # Vai mostrar tanto erros sintáticos quanto semânticos
