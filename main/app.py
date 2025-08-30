import streamlit as st
import pandas as pd
from analisador_lexico import Lexer
from analisador_semantico import AnalisadorSemantico
from entradas_de_exemplo import entradas_de_exemplo

st.title("Analisador Léxico, Sintático e Semântico para linguagem C simplificada")

codigo_selecionado = st.selectbox("Escolha um exemplo de código", list(entradas_de_exemplo.keys()))
codigo = st.text_area(
    "Código-fonte selecionado (pode editar):",
    value=entradas_de_exemplo[codigo_selecionado],
    height=300
)

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
            {"Nome": s.nome, "Tipo": s.tipo, "Escopo": s.escopo, "Endereço": s.endereco}
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

        # Árvore de Derivação Sintática
        st.subheader("Árvore de Derivação Sintática")
        st.graphviz_chart(parser.gerar_dot_string())

        # Tabela de Símbolos (pós semântico)
        st.subheader("Tabela de Símbolos (Pós Análise Semântica)")
        if parser.tabela_simbolos:
            df = pd.DataFrame(parser.tabela_simbolos)
            st.table(df)
        else:
            st.write("Nenhum símbolo registrado.")

        # Grafo de dependências
        st.subheader("Grafo de Dependências")
        st.graphviz_chart(parser.gerar_grafo_dependencias())

    except Exception as e:
        st.error(str(e))
