# Analisadores Léxico e Sintático para Linguagem baseada em C

**Disciplina:** Compiladores  
**Curso:** BCC  
**Discentes:** Max David e Rogério Lacerda  

---

## Objetivo

Este projeto tem como objetivo a implementação de um compilador para um subconjunto da linguagem C, com foco na construção dos analisadores léxico e sintático, utilizando Python como linguagem de desenvolvimento.

---

## Tecnologias Utilizadas

- **Python** – Linguagem de implementação
- **re (Regex)** – Implementação de expressões regulares para o analisador léxico
- **Graphviz** – Geração da árvore de derivação para o analisador sintático
- **Streamlit** – Interface gráfica web para testes em tempo real

---

## Estrutura do Projeto

- `analisador_lexico.py` – Responsável pela geração da tabela de tokens alinhada à entrada.
- `analisador_sintatico.py` – Utilizando a estratégia parser top-down preditivo para análise sintática.
- `app.py` – Interface interativa via Streamlit.

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

- OBS: tenha o Python instalado
```bash
pip install streamlit graphviz
streamlit run app.py
```

---

## Imagens de execução do Projeto

![image](https://github.com/user-attachments/assets/2c4747b3-77f9-4f66-845b-25fb63a4df19)
![image](https://github.com/user-attachments/assets/9166ec76-03f4-4252-9f4e-f1e4d71a5068)
![image](https://github.com/user-attachments/assets/0bfcd474-6213-4e94-bbdc-b5c98bab3c49)
![image](https://github.com/user-attachments/assets/95269ecd-6a1d-4caf-bf54-6b8857bdbe96)
