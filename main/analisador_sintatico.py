from analisador_lexico import Lexer, Token

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.tokens = lexer.analisar()
        self.pos = 0
        self.token_atual = self.tokens[self.pos]

    def erro(self, msg="Erro sintático"):
        raise Exception(f"{msg} em linha {self.token_atual.linha}, coluna {self.token_atual.coluna}")

    def comer(self, tipo_esperado):
        if self.token_atual.tipo == tipo_esperado:
            # print(f"Consumindo token {self.token_atual}")
            self.pos += 1
            if self.pos < len(self.tokens):
                self.token_atual = self.tokens[self.pos]
            else:
                self.token_atual = Token('EOF', '', self.token_atual.linha, self.token_atual.coluna)
        else:
            self.erro(f"Esperado '{tipo_esperado}', encontrado '{self.token_atual.tipo}'")

    def analisar(self):
        self.programa()
        if self.token_atual.tipo != 'EOF':
            self.erro("Esperado EOF")
        print("Análise sintática concluída com sucesso!")

    # Programa -> { DeclFunc }
    def programa(self):
        while self.token_atual.tipo in {'INT', 'FLOAT', 'CHAR', 'BOOL', 'VOID'}:
            self.decl()
        if self.token_atual.tipo != 'EOF':
            self.erro("Esperado EOF")

    def decl(self):
        tipo = self.token_atual.tipo
        self.comer(tipo)

        if self.token_atual.tipo == 'ID':
            self.lista_ids()
            if self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ';':
                self.comer('DELIM')
            elif self.token_atual.tipo == 'DELIM' and self.token_atual.valor == '(':
                # Caso seja função
                self.comer('DELIM')  # '('
                self.comer('DELIM')  # ')'
                self.bloco()
            else:
                self.erro("Esperado ';' ou '(' após identificadores")
        else:
            self.erro("Esperado identificador após tipo")

    def lista_ids(self):
        self.comer('ID')
        while self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ',':
            self.comer('DELIM')
            self.comer('ID')

    # DeclFunc -> Tipo ID '(' ')' Bloco
    def decl_func(self):
        self.tipo()
        self.comer('ID')
        self.comer('(')
        self.comer(')')
        self.bloco()

    # Tipo -> INT | FLOAT | CHAR | BOOL | VOID
    def tipo(self):
        if self.token_atual.tipo in {'INT', 'FLOAT', 'CHAR', 'BOOL', 'VOID'}:
            self.comer(self.token_atual.tipo)
        else:
            self.erro("Esperado tipo")

    # Bloco -> '{' { Comando } '}'
    def bloco(self):
        self.comer('{')
        while self.token_atual.tipo in {'INT', 'FLOAT', 'CHAR', 'BOOL', 'ID', 'IF', 'WHILE', 'RETURN', '{'}:
            self.comando()
        self.comer('}')

    # Comando -> DeclVar | Atrib | If | While | Return | Bloco
    def comando(self):
        if self.token_atual.tipo in {'INT', 'FLOAT', 'CHAR', 'BOOL'}:
            self.decl_var()
        elif self.token_atual.tipo == 'ID':
            self.atribuicao()
        elif self.token_atual.tipo == 'IF':
            self.comando_if()
        elif self.token_atual.tipo == 'WHILE':
            self.comando_while()
        elif self.token_atual.tipo == 'RETURN':
            self.comando_return()
        elif self.token_atual.tipo == '{':
            self.bloco()
        else:
            self.erro("Comando inválido")

    # DeclVar -> Tipo ID ';'
    def decl_var(self):
        self.tipo()
        self.comer('ID')
        self.comer('DELIM')  # ponto e vírgula ';'

    # Atrib -> ID '=' Expressao ';'
    def atribuicao(self):
        self.comer('ID')
        self.comer('ATRIB')
        self.expressao()
        self.comer('DELIM')

    # If -> 'if' '(' Expressao ')' Comando [ 'else' Comando ]
    def comando_if(self):
        self.comer('IF')
        self.comer('(')
        self.expressao()
        self.comer(')')
        self.comando()
        if self.token_atual.tipo == 'ELSE':
            self.comer('ELSE')
            self.comando()

    # While -> 'while' '(' Expressao ')' Comando
    def comando_while(self):
        self.comer('WHILE')
        self.comer('(')
        self.expressao()
        self.comer(')')
        self.comando()

    # Return -> 'return' [Expressao] ';'
    def comando_return(self):
        self.comer('RETURN')
        # return pode ter expressão ou não
        if self.token_atual.tipo not in {'DELIM'}:
            self.expressao()
        self.comer('DELIM')

    # Expressao -> ExpressaoLogica
    def expressao(self):
        self.expressao_logica()

    # ExpressaoLogica -> ExpressaoLogica '||' ExpressaoLogica2 | ExpressaoLogica2
    def expressao_logica(self):
        self.expressao_logica2()
        while self.token_atual.tipo == 'OP_LOG' and self.token_atual.valor == '||':
            self.comer('OP_LOG')
            self.expressao_logica2()

    # ExpressaoLogica2 -> ExpressaoLogica3 { '&&' ExpressaoLogica3 }
    def expressao_logica2(self):
        self.expressao_logica3()
        while self.token_atual.tipo == 'OP_LOG' and self.token_atual.valor == '&&':
            self.comer('OP_LOG')
            self.expressao_logica3()

    # ExpressaoLogica3 -> '!' ExpressaoLogica3 | ExpressaoRelacional
    def expressao_logica3(self):
        if self.token_atual.tipo == 'OP_LOG' and self.token_atual.valor == '!':
            self.comer('OP_LOG')
            self.expressao_logica3()
        else:
            self.expressao_relacional()

    # ExpressaoRelacional -> ExpressaoAritmetica [ OP_REL ExpressaoAritmetica ]
    def expressao_relacional(self):
        self.expressao_aritmetica()
        if self.token_atual.tipo == 'OP_REL':
            self.comer('OP_REL')
            self.expressao_aritmetica()

    # ExpressaoAritmetica -> Termo { ('+' | '-') Termo }
    def expressao_aritmetica(self):
        self.termo()
        while self.token_atual.tipo == 'OP_ARIT' and self.token_atual.valor in ('+', '-'):
            self.comer('OP_ARIT')
            self.termo()

    # Termo -> Fator { ('*' | '/') Fator }
    def termo(self):
        self.fator()
        while self.token_atual.tipo == 'OP_ARIT' and self.token_atual.valor in ('*', '/'):
            self.comer('OP_ARIT')
            self.fator()

    # Fator -> NUM_INT | ID | '(' Expressao ')'
    def fator(self):
        if self.token_atual.tipo == 'NUM_INT':
            self.comer('NUM_INT')
        elif self.token_atual.tipo == 'ID':
            self.comer('ID')
        elif self.token_atual.tipo == 'DELIM' and self.token_atual.valor == '(':
            self.comer('DELIM')
            self.expressao()
            if self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ')':
                self.comer('DELIM')
            else:
                self.erro("Esperado ')'")
        else:
            self.erro("Esperado número, identificador ou '('")

