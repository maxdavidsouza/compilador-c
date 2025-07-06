from analisador_lexico import Token

class PredictiveParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.token = self.tokens[self.pos]

    def avanca(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.token = self.tokens[self.pos]
        else:
            self.token = Token('EOF', '', -1, -1)

    def erro(self, msg):
        raise Exception(f"Erro de sintaxe em token {self.token}. {msg}")

    def match(self, tipo_esperado, valor_esperado=None):
        if self.token.tipo == tipo_esperado:
            if valor_esperado is None or self.token.valor == valor_esperado:
                self.avanca()
            else:
                self.erro(f"Esperado token do tipo {tipo_esperado} com valor '{valor_esperado}', encontrado valor '{self.token.valor}'")
        else:
            self.erro(f"Esperado token do tipo {tipo_esperado}, encontrado {self.token.tipo}")

    def parse(self):
        self.programa()
        if self.token.tipo != 'EOF':
            self.erro("Esperado EOF no final")

    # <programa> ::= { <declaracao> }
    def programa(self):
        while self.token.tipo in {'INT', 'FLOAT', 'CHAR', 'BOOL', 'VOID'}:
            self.declaracao()

    # <declaracao> ::= <tipo> ID <decl_continua>
    def declaracao(self):
        self.tipo()
        self.match('ID')
        self.decl_continua()

    # <decl_continua> ::= ;
    #                  | , ID { , ID } ;
    #                  | ( [ <parametros_formais> ] ) <bloco>
    def decl_continua(self):
        if self.token.tipo == 'DELIM' and self.token.valor == ';':
            self.match('DELIM', ';')
        elif self.token.tipo == 'DELIM' and self.token.valor == ',':
            while self.token.tipo == 'DELIM' and self.token.valor == ',':
                self.match('DELIM', ',')
                self.match('ID')
            self.match('DELIM', ';')
        elif self.token.tipo == 'DELIM' and self.token.valor == '(':
            self.match('DELIM', '(')
            if not (self.token.tipo == 'DELIM' and self.token.valor == ')'):
                self.parametros_formais()
            self.match('DELIM', ')')
            self.bloco()
        else:
            self.erro(f"Esperado ';', ',' ou '(' após identificador")

    # <tipo> ::= int | float | char | bool | void
    def tipo(self):
        if self.token.tipo in {'INT', 'FLOAT', 'CHAR', 'BOOL', 'VOID'}:
            self.match(self.token.tipo)
        else:
            self.erro("Esperado tipo")

    # <parametros_formais> ::= <parametro> { , <parametro> }
    def parametros_formais(self):
        self.parametro()
        while self.token.tipo == 'DELIM' and self.token.valor == ',':
            self.match('DELIM', ',')
            self.parametro()

    # <parametro> ::= <tipo> ID
    def parametro(self):
        self.tipo()
        self.match('ID')

    # <bloco> ::= { { <comando> } }
    def bloco(self):
        self.match('DELIM', '{')
        while not (self.token.tipo == 'DELIM' and self.token.valor == '}'):
            self.comando()
        self.match('DELIM', '}')

    # <comando> ::= <decl_var>
    #             | <atribuicao>
    #             | <chamada_funcao>
    #             | <comando_if>
    #             | <comando_while>
    #             | <comando_for>
    #             | <comando_return>
    #             | break ;
    #             | continue ;
    #             | <bloco>
    def comando(self):
        if self.token.tipo in {'INT', 'FLOAT', 'CHAR', 'BOOL'}:
            self.decl_var()
        elif self.token.tipo == 'ID':
            # lookahead para decidir atribuição ou chamada de função
            prox = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if prox and prox.tipo == 'ATRIB':
                self.atribuicao()
            elif prox and prox.tipo == 'DELIM' and prox.valor == '(':
                self.chamada_funcao()
            else:
                self.erro("Esperado '=' ou '(' após identificador")
        elif self.token.tipo == 'IF':
            self.comando_if()
        elif self.token.tipo == 'WHILE':
            self.comando_while()
        elif self.token.tipo == 'FOR':
            self.comando_for()
        elif self.token.tipo == 'RETURN':
            self.comando_return()
        elif self.token.tipo == 'BREAK':
            self.match('BREAK')
            self.match('DELIM', ';')
        elif self.token.tipo == 'CONTINUE':
            self.match('CONTINUE')
            self.match('DELIM', ';')
        elif self.token.tipo == 'DELIM' and self.token.valor == '{':
            self.bloco()
        else:
            self.erro("Comando inválido")

    # <decl_var> ::= <tipo> ID { , ID } ;
    def decl_var(self):
        self.tipo()
        self.match('ID')
        while self.token.tipo == 'DELIM' and self.token.valor == ',':
            self.match('DELIM', ',')
            self.match('ID')
        self.match('DELIM', ';')

    # <atribuicao> ::= ID = <expressao> ;
    def atribuicao(self):
        self.match('ID')
        self.match('ATRIB', '=')
        self.expressao()
        self.match('DELIM', ';')

    # <chamada_funcao> ::= ID ( [ <lista_argumentos> ] ) ;
    def chamada_funcao(self):
        self.match('ID')
        self.match('DELIM', '(')
        if not (self.token.tipo == 'DELIM' and self.token.valor == ')'):
            self.lista_argumentos()
        self.match('DELIM', ')')
        self.match('DELIM', ';')

    # <lista_argumentos> ::= <expressao> { , <expressao> }
    def lista_argumentos(self):
        self.expressao()
        while self.token.tipo == 'DELIM' and self.token.valor == ',':
            self.match('DELIM', ',')
            self.expressao()

    # <comando_if> ::= if ( <expressao> ) <comando> [ else <comando> ]
    def comando_if(self):
        self.match('IF')
        self.match('DELIM', '(')
        self.expressao()
        self.match('DELIM', ')')
        self.comando()
        if self.token.tipo == 'ELSE':
            self.match('ELSE')
            self.comando()

    # <comando_while> ::= while ( <expressao> ) <comando>
    def comando_while(self):
        self.match('WHILE')
        self.match('DELIM', '(')
        self.expressao()
        self.match('DELIM', ')')
        self.comando()

    # <comando_for> ::= for ( <for_inicializacao> ; <expressao> ; <for_incremento> ) <comando>
    def comando_for(self):
        self.match('FOR')
        self.match('DELIM', '(')
        self.for_inicializacao()
        self.match('DELIM', ';')
        self.expressao()
        self.match('DELIM', ';')
        self.for_incremento()
        self.match('DELIM', ')')
        self.comando()

    # <for_inicializacao> ::= <decl_var_for> | <atribuicao_for>
    def for_inicializacao(self):
        if self.token.tipo in {'INT', 'FLOAT', 'CHAR', 'BOOL'}:
            self.decl_var_for()
        elif self.token.tipo == 'ID':
            self.atribuicao_for()
        else:
            self.erro("Esperado declaração com inicialização ou atribuição na inicialização do for")

    # <decl_var_for> ::= <tipo> ID [ = <expressao> ] { , ID [ = <expressao> ] }
    def decl_var_for(self):
        self.tipo()
        self.match('ID')
        if self.token.tipo == 'ATRIB':
            self.match('ATRIB', '=')
            self.expressao()
        while self.token.tipo == 'DELIM' and self.token.valor == ',':
            self.match('DELIM', ',')
            self.match('ID')
            if self.token.tipo == 'ATRIB':
                self.match('ATRIB', '=')
                self.expressao()

    # <atribuicao_for> ::= ID = <expressao>
    def atribuicao_for(self):
        self.match('ID')
        self.match('ATRIB', '=')
        self.expressao()

    # <for_incremento> ::= ID = <expressao>
    def for_incremento(self):
        self.match('ID')
        self.match('ATRIB', '=')
        self.expressao()

    # <comando_return> ::= return [ <expressao> ] ;
    def comando_return(self):
        self.match('RETURN')
        if not (self.token.tipo == 'DELIM' and self.token.valor == ';'):
            self.expressao()
        self.match('DELIM', ';')

    # <expressao> ::= <expressao_logica>
    def expressao(self):
        self.expressao_logica()

    # <expressao_logica> ::= <expressao_logica2> { || <expressao_logica2> }
    def expressao_logica(self):
        self.expressao_logica2()
        while self.token.tipo == 'OP_LOG' and self.token.valor == '||':
            self.match('OP_LOG', '||')
            self.expressao_logica2()

    # <expressao_logica2> ::= <expressao_logica3> { && <expressao_logica3> }
    def expressao_logica2(self):
        self.expressao_logica3()
        while self.token.tipo == 'OP_LOG' and self.token.valor == '&&':
            self.match('OP_LOG', '&&')
            self.expressao_logica3()

    # <expressao_logica3> ::= [ ! ] <expressao_relacional>
    def expressao_logica3(self):
        if self.token.tipo == 'OP_LOG' and self.token.valor == '!':
            self.match('OP_LOG', '!')
            self.expressao_logica3()
        else:
            self.expressao_relacional()

    # <expressao_relacional> ::= <expressao_aritmetica> [ <op_relacional> <expressao_aritmetica> ]
    def expressao_relacional(self):
        self.expressao_aritmetica()
        if self.token.tipo == 'OP_REL':
            self.op_relacional()
            self.expressao_aritmetica()

    # <op_relacional> ::= == | != | <= | >= | < | >
    def op_relacional(self):
        if self.token.valor in {'==', '!=', '<=', '>=', '<', '>'}:
            self.match('OP_REL', self.token.valor)
        else:
            self.erro("Operador relacional inválido")

    # <expressao_aritmetica> ::= <termo> { ( + | - ) <termo> }
    def expressao_aritmetica(self):
        self.termo()
        while self.token.tipo == 'OP_ARIT' and self.token.valor in ('+', '-'):
            self.match('OP_ARIT', self.token.valor)
            self.termo()

    # <termo> ::= <fator> { ( * | / | % ) <fator> }
    def termo(self):
        self.fator()
        while self.token.tipo == 'OP_ARIT' and self.token.valor in ('*', '/', '%'):
            self.match('OP_ARIT', self.token.valor)
            self.fator()

    # <fator> ::= NUM_INT
    #           | ID [ ( [ <lista_argumentos> ] ) ]
    #           | true
    #           | false
    #           | ( <expressao> )
    def fator(self):
        if self.token.tipo == 'NUM_INT':
            self.match('NUM_INT')
        elif self.token.tipo == 'ID':
            prox = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if prox and prox.tipo == 'DELIM' and prox.valor == '(':
                self.match('ID')
                self.match('DELIM', '(')
                if not (self.token.tipo == 'DELIM' and self.token.valor == ')'):
                    self.lista_argumentos()
                self.match('DELIM', ')')
            else:
                self.match('ID')
        elif self.token.tipo in {'TRUE', 'FALSE'}:
            self.match(self.token.tipo)
        elif self.token.tipo == 'DELIM' and self.token.valor == '(':
            self.match('DELIM', '(')
            self.expressao()
            self.match('DELIM', ')')
        else:
            self.erro("Esperado número, identificador, chamada de função, true, false ou '('")

