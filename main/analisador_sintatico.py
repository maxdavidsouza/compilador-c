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
            self.avancar()
        else:
            self.erro(f"Esperado token do tipo '{tipo_esperado}', encontrado '{self.token_atual.tipo}'")

    def comer_simbolo(self, simbolo_esperado):
        if self.token_atual.tipo == 'DELIM' and self.token_atual.valor == simbolo_esperado:
            self.avancar()
        else:
            self.erro(f"Esperado símbolo '{simbolo_esperado}', encontrado '{self.token_atual.valor}'")

    def avancar(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.token_atual = self.tokens[self.pos]
        else:
            self.token_atual = Token('EOF', '', self.token_atual.linha, self.token_atual.coluna)

    def analisar(self):
        self.programa()
        if self.token_atual.tipo != 'EOF':
            self.erro("Esperado EOF")
        print("Análise sintática concluída com sucesso!")

    def programa(self):
        while self.token_atual.tipo in {'INT', 'FLOAT', 'CHAR', 'BOOL', 'VOID'}:
            self.decl()

    def decl(self):
        tipo = self.token_atual.tipo
        self.comer(tipo)

        if self.token_atual.tipo == 'ID':
            nome = self.token_atual.valor
            self.comer('ID')
            if self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ',':
                self.lista_ids_continua()
                self.comer_simbolo(';')
            elif self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ';':
                self.comer_simbolo(';')
            elif self.token_atual.tipo == 'DELIM' and self.token_atual.valor == '(':
                self.comer_simbolo('(')
                if not (self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ')'):
                    self.parametros_formais()
                self.comer_simbolo(')')
                self.bloco()
            else:
                self.erro(f"Esperado ';', ',' ou '(' após identificador '{nome}'")
        else:
            self.erro("Esperado identificador após tipo")

    def parametros_formais(self):
        self.parametro()
        while self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ',':
            self.comer_simbolo(',')
            self.parametro()

    def parametro(self):
        if self.token_atual.tipo in {'INT', 'FLOAT', 'CHAR', 'BOOL'}:
            self.comer(self.token_atual.tipo)
            self.comer('ID')
        else:
            self.erro("Esperado tipo de parâmetro")

    def lista_ids_continua(self):
        while self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ',':
            self.comer_simbolo(',')
            self.comer('ID')

    def bloco(self):
        self.comer_simbolo('{')
        while not (self.token_atual.tipo == 'DELIM' and self.token_atual.valor == '}'):
            self.comando()
        self.comer_simbolo('}')

    def comando(self):
        if self.token_atual.tipo in {'INT', 'FLOAT', 'CHAR', 'BOOL'}:
            self.decl_var()
        elif self.token_atual.tipo == 'ID':
            proximo = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if proximo and proximo.tipo == 'ATRIB':
                self.atribuicao()
            elif proximo and proximo.tipo == 'DELIM' and proximo.valor == '(':
                self.chamada_funcao()
            else:
                self.erro("Esperado '=' ou '(' após identificador")
        elif self.token_atual.tipo == 'IF':
            self.comando_if()
        elif self.token_atual.tipo == 'WHILE':
            self.comando_while()
        elif self.token_atual.tipo == 'FOR':
            self.comando_for()
        elif self.token_atual.tipo == 'RETURN':
            self.comando_return()
        elif self.token_atual.tipo == 'BREAK':
            self.comer('BREAK')
            self.comer_simbolo(';')
        elif self.token_atual.tipo == 'CONTINUE':
            self.comer('CONTINUE')
            self.comer_simbolo(';')
        elif self.token_atual.tipo == 'DELIM' and self.token_atual.valor == '{':
            self.bloco()
        else:
            self.erro("Comando inválido")

    def decl_var(self):
        tipo = self.token_atual.tipo
        self.comer(tipo)
        self.comer('ID')
        self.lista_ids_continua()
        self.comer_simbolo(';')

    # Versões para uso interno no 'for' (não consomem ';')
    def decl_var_for(self):
        tipo = self.token_atual.tipo
        self.comer(tipo)
        self.comer('ID')
        # Agora permite inicialização: '=' expressao
        if self.token_atual.tipo == 'ATRIB':
            self.comer('ATRIB')
            self.expressao()
        self.lista_ids_continua_for()

    def lista_ids_continua_for(self):
        # Essa versão para for, não consome ';'
        while self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ',':
            self.comer_simbolo(',')
            self.comer('ID')
            if self.token_atual.tipo == 'ATRIB':
                self.comer('ATRIB')
                self.expressao()

    def atribuicao_for(self):
        self.comer('ID')
        self.comer('ATRIB')
        self.expressao()
        # Não come ';' aqui

    def atribuicao(self):
        self.comer('ID')
        self.comer('ATRIB')
        self.expressao()
        self.comer_simbolo(';')

    def chamada_funcao(self):
        self.comer('ID')
        self.comer_simbolo('(')
        if not (self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ')'):
            self.lista_argumentos()
        self.comer_simbolo(')')
        self.comer_simbolo(';')

    def lista_argumentos(self):
        self.expressao()
        while self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ',':
            self.comer_simbolo(',')
            self.expressao()

    def comando_if(self):
        self.comer('IF')
        self.comer_simbolo('(')
        self.expressao()
        self.comer_simbolo(')')
        self.comando()
        if self.token_atual.tipo == 'ELSE':
            self.comer('ELSE')
            self.comando()

    def comando_while(self):
        self.comer('WHILE')
        self.comer_simbolo('(')
        self.expressao()
        self.comer_simbolo(')')
        self.comando()

    def comando_for(self):
        self.comer('FOR')
        self.comer_simbolo('(')

        # Inicialização: declaração com inicialização ou atribuição
        if self.token_atual.tipo in {'INT', 'FLOAT', 'CHAR', 'BOOL'}:
            self.decl_var_for()
        elif self.token_atual.tipo == 'ID':
            self.atribuicao_for()
        else:
            self.erro("Esperado declaração com inicialização ou atribuição na inicialização do for")

        self.comer_simbolo(';')

        # Condição
        self.expressao()
        self.comer_simbolo(';')

        # Incremento
        if self.token_atual.tipo == 'ID':
            self.atribuicao_for()
        else:
            self.erro("Esperado atribuição no incremento do for")

        self.comer_simbolo(')')
        self.comando()

    def comando_return(self):
        self.comer('RETURN')
        if self.token_atual.tipo != 'DELIM' or (self.token_atual.tipo == 'DELIM' and self.token_atual.valor != ';'):
            self.expressao()
        self.comer_simbolo(';')

    def expressao(self):
        self.expressao_logica()

    def expressao_logica(self):
        self.expressao_logica2()
        while self.token_atual.tipo == 'OP_LOG' and self.token_atual.valor == '||':
            self.comer('OP_LOG')
            self.expressao_logica2()

    def expressao_logica2(self):
        self.expressao_logica3()
        while self.token_atual.tipo == 'OP_LOG' and self.token_atual.valor == '&&':
            self.comer('OP_LOG')
            self.expressao_logica3()

    def expressao_logica3(self):
        if self.token_atual.tipo == 'OP_LOG' and self.token_atual.valor == '!':
            self.comer('OP_LOG')
            self.expressao_logica3()
        else:
            self.expressao_relacional()

    def expressao_relacional(self):
        self.expressao_aritmetica()
        if self.token_atual.tipo == 'OP_REL':
            self.comer('OP_REL')
            self.expressao_aritmetica()

    def expressao_aritmetica(self):
        self.termo()
        while self.token_atual.tipo == 'OP_ARIT' and self.token_atual.valor in ('+', '-'):
            self.comer('OP_ARIT')
            self.termo()

    def termo(self):
        self.fator()
        while self.token_atual.tipo == 'OP_ARIT' and self.token_atual.valor in ('*', '/', '%'):
            self.comer('OP_ARIT')
            self.fator()

    def fator(self):
        if self.token_atual.tipo == 'NUM_INT':
            self.comer('NUM_INT')
        elif self.token_atual.tipo == 'ID':
            proximo = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if proximo and proximo.tipo == 'DELIM' and proximo.valor == '(':
                self.comer('ID')
                self.comer_simbolo('(')
                if not (self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ')'):
                    self.lista_argumentos()
                self.comer_simbolo(')')
            else:
                self.comer('ID')
        elif self.token_atual.tipo in {'TRUE', 'FALSE'}:
            self.comer(self.token_atual.tipo)
        elif self.token_atual.tipo == 'DELIM' and self.token_atual.valor == '(':
            self.comer_simbolo('(')
            self.expressao()
            self.comer_simbolo(')')
        else:
            self.erro("Esperado número, identificador, chamada de função, true, false ou '('")
