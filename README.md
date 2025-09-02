# Compilador de Linguagem baseada em C com Aproximação Didática

**Disciplina:** Compiladores  
**Curso:** BCC  
**Discentes:** Max David e Rogério Lacerda  

---

## Objetivo

Este projeto tem como objetivo a implementação de um compilador para um subconjunto da linguagem C, com foco na construção dos analisadores léxico e sintático, utilizando Python como linguagem de desenvolvimento.

---

## Tecnologias Utilizadas

- **Python** – Linguagem de implementação
- **re (Regex)** – Implementação de expressões regulares para o analisador léxico e otimizador de código intermediário
- **Graphviz** – Geração da árvore de derivação para o analisador sintático
- **Pandas** - Geração da tabela de símbolos para o analisador semântico
- **Streamlit** – Interface gráfica web para testes em tempo real

---

## Estrutura do Projeto

- `analisador_lexico.py` – Responsável pela geração da tabela de tokens e tabela de símbolos inicial alinhada à entrada.
- `analisador_sintatico.py` – Responsável pela análise sintática top-down preditiva.
- `analisador_semantico.py` – Responsável pela análise semântica, atualização da tabela de símbolos e geração de código intermediário.
- `otimizador_de_codigo.py` – Responsável pela redução de termos necessários para se alcançar o resultado do programa obtido no código intermediário.
- `entradas_de_exemplo.py` – Conjunto de entradas de código para corretude e desenvolvimento de testes do compilador.
- `app.py` – Interface interativa via Streamlit para entrada de códigos de testes.

---

## Gramática Inicial (Simplificada)

### 1. Estrutura de programa e declarações

```bnf
<programa> ::= <decls> <funcoes> <main>
<decls> ::= { <decl_var> }
<decl_var> ::= <tipo> <id> { , <id> } ;
<tipo> ::= int | bool
```

### 2. Funções e procedimentos

```bnf
<funcoes> ::= { <funcao> }
<funcao> ::= <tipo> <id> ( <params_opcional> ) { <decls> <comandos> }
<params_opcional> ::= ε | <param> { , <param> }
<param> ::= <tipo> <id>
<main> ::= int main ( ) { <decls> <comandos> }
```

### 3. Comandos principais

```bnf
<comando> ::= <comando_id> ;
            | <decl_if>
            | <decl_while>
            | <decl_return> ;
            | break ;
            | continue ;
            | <decl_printf> ;
            | { <comandos> }

<comando_id> ::= <id> <sufixo_id>
<sufixo_id> ::= = <expressao> | ( <args_opcional> )
<args_opcional> ::= ε | <expressao> { , <expressao> }
```

### 4. Controle de fluxo e outros

```bnf
<decl_if> ::= if ( <expressao> ) <comando> [ else <comando> ]
<decl_while> ::= while ( <expressao> ) <comando>
<decl_return> ::= return [ <expressao> ]
<decl_printf> ::= printf ( <expressao> )
```

### 5. Expressões

```bnf
<expressao> ::= <soma_ou_sub> [ <op_relacional> <soma_ou_sub> ]
<op_relacional> ::= == | != | < | <= | > | >=
<soma_ou_sub> ::= <mult_div_and> { ( + | - | || ) <mult_div_and> }
<mult_div_and> ::= <fator> { ( * | / | && ) <fator> }
<fator> ::= <id> <fator_s> | <numero> | true | false | ( <expressao> ) | ! <fator>
<fator_s> ::= ( <args_opcional> ) | ε
```

### 6. Identificadores e números

```bnf
<id> ::= <letra> { <letra> | <digito> }
<numero> ::= <digito> { <digito> }
<letra> ::= a..z | A..Z | _
<digito> ::= 0..9
```

---

## Evolução da Gramática

Durante a implementação, a gramática original foi adaptada para uma versão LL(1), eliminando recursão à esquerda e fatorando produções para possibilitar a análise preditiva. A nova forma da gramática ficou:

```bnf
<programa> ::= { <declaracao> }

<declaracao> ::= <tipo> ID <decl_continua>
<decl_continua> ::= ;
                 | , ID { , ID } ;
                 | ( [ <parametros_formais> ] ) <bloco>

<tipo> ::= int | float | char | bool | void
<parametros_formais> ::= <parametro> { , <parametro> }
<parametro> ::= <tipo> ID
<bloco> ::= { { <comando> } }
```

### Comandos Suportados

```bnf
<comando> ::= <decl_var>
            | <atribuicao>
            | <chamada_funcao>
            | <comando_if>
            | <comando_while>
            | <comando_for>
            | <comando_return>
            | break ;
            | continue ;
            | <bloco>

<decl_var> ::= <tipo> ID { , ID } ;
<atribuicao> ::= ID = <expressao> ;
<chamada_funcao> ::= ID ( [ <lista_argumentos> ] ) ;
<lista_argumentos> ::= <expressao> { , <expressao> }
<comando_if> ::= if ( <expressao> ) <comando> [ else <comando> ]
<comando_while> ::= while ( <expressao> ) <comando>
<comando_for> ::= for ( <for_inicializacao> ; <expressao> ; <for_incremento> ) <comando>
<for_inicializacao> ::= <decl_var_for> | <atribuicao_for>
<decl_var_for> ::= <tipo> ID [ = <expressao> ] { , ID [ = <expressao> ] }
<atribuicao_for> ::= ID = <expressao>
<for_incremento> ::= ID = <expressao>
<comando_return> ::= return [ <expressao> ] ;
```

### Expressões

```bnf
<expressao> ::= <expressao_logica>
<expressao_logica> ::= <expressao_logica2> { || <expressao_logica2> }
<expressao_logica2> ::= <expressao_logica3> { && <expressao_logica3> }
<expressao_logica3> ::= [ ! ] <expressao_relacional>
<expressao_relacional> ::= <expressao_aritmetica> [ <op_relacional> <expressao_aritmetica> ]
<op_relacional> ::= == | != | <= | >= | < | >

<expressao_aritmetica> ::= <termo> { ( + | - ) <termo> }
<termo> ::= <fator> { ( * | / | % ) <fator> }

<fator> ::= NUM_INT
          | ID [ ( [ <lista_argumentos> ] ) ]
          | true
          | false
          | ( <expressao> )
```

---

## Quais funcionalidades foram implementadas?

- **Análise Léxica:** Tokenização com informações de tipo, valor, linha e coluna.
- **Análise Sintática:** Parser descendente com árvore de derivação gerada automaticamente via Graphviz.
- **Interface Interativa:** Entrada e saída de código-fonte via Streamlit com feedback em tempo real.
- **Mensagens de Erro:** Identificação clara e precisa de erros léxicos e sintáticos com rastreabilidade.

---

## Como executar o projeto?

Para executar o projeto:

- OBS: tenha o Python instalado e esteja com o cmd aberto dentro da pasta /main/ do projeto
```bash
pip install streamlit graphviz
streamlit run app.py
```

---

## Imagens de execução do Projeto usando um Código Simples

<img width="750" height="930" alt="e-1" src="https://github.com/user-attachments/assets/a5aa6e74-3bf6-4bb9-ab2e-54077761988e" />
<img width="526" height="1043" alt="e-2" src="https://github.com/user-attachments/assets/c9bfe8e6-8406-4770-8b48-2c385c7b914d" />
<img width="344" height="799" alt="e-3" src="https://github.com/user-attachments/assets/cd662456-dc06-460c-91fe-3a5350b97de9" />
<img width="723" height="1066" alt="e-4" src="https://github.com/user-attachments/assets/a31a8f07-9bfc-455d-b0a0-076cc3ee9c29" />
<img width="738" height="583" alt="e-5" src="https://github.com/user-attachments/assets/d3565f3b-3b0a-4c7b-b1e2-0aca3b69a347" />
<img width="728" height="938" alt="e-6" src="https://github.com/user-attachments/assets/7205414b-8889-4c80-8fb0-b200eaa432d9" />
<img width="735" height="719" alt="e-7" src="https://github.com/user-attachments/assets/1dbfc49d-99d6-4c00-abab-2dabe47fd666" />

