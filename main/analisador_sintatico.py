from analisador_lexico import Lexer, Token

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.tokens = lexer.analisar()
        self.pos = 0
        self.token_atual = self.tokens[self.pos]

        # Grafo de rastreabilidade
        self.node_id = 0
        self.nodes = []
        self.edges = []
        self.parent_stack = []

    def novo_no(self, label):
        self.node_id += 1
        no_atual = self.node_id
        self.nodes.append((no_atual, label))
        if self.parent_stack:
            pai = self.parent_stack[-1]
            self.edges.append((pai, no_atual))
        return no_atual

    def rastrear(label):
        """
        Decorador de função para rastrear chamadas em métodos do Parser.
        """

        def decorator(func):
            def wrapper(self, *args, **kwargs):
                no_atual = self.novo_no(label)
                self.parent_stack.append(no_atual)
                resultado = func(self, *args, **kwargs)
                self.parent_stack.pop()
                return resultado

            return wrapper

        return decorator

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

    @rastrear("analisar")
    def analisar(self):
        self.programa()
        if self.token_atual.tipo != 'EOF':
            self.erro("Esperado EOF")
        print("Análise sintática concluída com sucesso!")

    @rastrear("programa")
    def programa(self):
        while self.token_atual.tipo in {'INT', 'FLOAT', 'CHAR', 'BOOL', 'VOID'}:
            self.decl()

    @rastrear("declaração de variável")
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

    @rastrear("parametros_formais")
    def parametros_formais(self):
        self.parametro()
        while self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ',':
            self.comer_simbolo(',')
            self.parametro()

    @rastrear("parametro")
    def parametro(self):
        if self.token_atual.tipo in {'INT', 'FLOAT', 'CHAR', 'BOOL'}:
            self.comer(self.token_atual.tipo)
            self.comer('ID')
        else:
            self.erro("Esperado tipo de parâmetro")

    @rastrear("lista_ids_continua")
    def lista_ids_continua(self):
        while self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ',':
            self.comer_simbolo(',')
            self.comer('ID')

    @rastrear("bloco")
    def bloco(self):
        self.comer_simbolo('{')
        while not (self.token_atual.tipo == 'DELIM' and self.token_atual.valor == '}'):
            self.comando()
        self.comer_simbolo('}')

    @rastrear("comando")
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

    @rastrear("decl_var")
    def decl_var(self):
        tipo = self.token_atual.tipo
        self.comer(tipo)
        self.comer('ID')
        self.lista_ids_continua()
        self.comer_simbolo(';')

    # Versões para uso interno no 'for' (não consomem ';')
    @rastrear("decl_var_for")
    def decl_var_for(self):
        tipo = self.token_atual.tipo
        self.comer(tipo)
        self.comer('ID')
        # Agora permite inicialização: '=' expressao
        if self.token_atual.tipo == 'ATRIB':
            self.comer('ATRIB')
            self.expressao()
        self.lista_ids_continua_for()

    @rastrear("lista_ids_continua_for")
    def lista_ids_continua_for(self):
        # Essa versão para for, não consome ';'
        while self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ',':
            self.comer_simbolo(',')
            self.comer('ID')
            if self.token_atual.tipo == 'ATRIB':
                self.comer('ATRIB')
                self.expressao()

    @rastrear("atribuicao_for")
    def atribuicao_for(self):
        self.comer('ID')
        self.comer('ATRIB')
        self.expressao()
        # Não come ';' aqui

    @rastrear("atribuicao")
    def atribuicao(self):
        self.comer('ID')
        self.comer('ATRIB')
        self.expressao()
        self.comer_simbolo(';')

    @rastrear("chamada_funcao")
    def chamada_funcao(self):
        self.comer('ID')
        self.comer_simbolo('(')
        if not (self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ')'):
            self.lista_argumentos()
        self.comer_simbolo(')')
        self.comer_simbolo(';')

    @rastrear("lista_argumentos")
    def lista_argumentos(self):
        self.expressao()
        while self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ',':
            self.comer_simbolo(',')
            self.expressao()

    @rastrear("comando_if")
    def comando_if(self):
        self.comer('IF')
        self.comer_simbolo('(')
        self.expressao()
        self.comer_simbolo(')')
        self.comando()
        if self.token_atual.tipo == 'ELSE':
            self.comer('ELSE')
            self.comando()

    @rastrear("comando_while")
    def comando_while(self):
        self.comer('WHILE')
        self.comer_simbolo('(')
        self.expressao()
        self.comer_simbolo(')')
        self.comando()

    @rastrear("comando_for")
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

    @rastrear("comando_return")
    def comando_return(self):
        self.comer('RETURN')
        if self.token_atual.tipo != 'DELIM' or (self.token_atual.tipo == 'DELIM' and self.token_atual.valor != ';'):
            self.expressao()
        self.comer_simbolo(';')

    @rastrear("expressao")
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

    @rastrear("expressao_relacional")
    def expressao_relacional(self):
        self.expressao_aritmetica()
        if self.token_atual.tipo == 'OP_REL':
            self.comer('OP_REL')
            self.expressao_aritmetica()

    @rastrear("expressao_aritmetica")
    def expressao_aritmetica(self):
        self.termo()
        while self.token_atual.tipo == 'OP_ARIT' and self.token_atual.valor in ('+', '-'):
            self.comer('OP_ARIT')
            self.termo()

    @rastrear("termo da expressão")
    def termo(self):
        self.fator()
        while self.token_atual.tipo == 'OP_ARIT' and self.token_atual.valor in ('*', '/', '%'):
            self.comer('OP_ARIT')
            self.fator()

    @rastrear("fator da expressão")
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

    def exportar_graphviz(self, nome_arquivo="grafo_parser.dot"):
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write("digraph ParserTrace {\n")
            f.write("  node [shape=box, style=filled, fillcolor=lightblue];\n")
            for node_id, label in self.nodes:
                label_esc = label.replace('"', '\\"')
                f.write(f'  {node_id} [label="{label_esc}"];\n')
            for from_id, to_id in self.edges:
                f.write(f'  {from_id} -> {to_id};\n')
            f.write("}\n")
        print(f"Grafo exportado para {nome_arquivo}")

    def gerar_dot_string(self):
        linhas = [
            "digraph ParserTrace {",
            "  node [shape=box, style=filled, fillcolor=lightblue];"
        ]
        for node_id, label in self.nodes:
            label_esc = label.replace('"', '\\"')
            linhas.append(f'  {node_id} [label="{label_esc}"];')
        for from_id, to_id in self.edges:
            linhas.append(f'  {from_id} -> {to_id};')
        linhas.append("}")
        return "\n".join(linhas)
