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

    def ler(self, tipo_esperado):
        if self.token_atual.tipo == tipo_esperado:
            self.avancar()
        else:
            self.erro(f"Esperado token do tipo '{tipo_esperado}', encontrado '{self.token_atual.tipo}'")

    def ler_simbolo(self, simbolo_esperado):
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
        self.ler(tipo)

        if self.token_atual.tipo == 'ID':
            nome = self.token_atual.valor
            self.ler('ID')
            if self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ',':
                self.lista_ids_continua()
                self.ler_simbolo(';')
            elif self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ';':
                self.ler_simbolo(';')
            elif self.token_atual.tipo == 'DELIM' and self.token_atual.valor == '(':
                self.ler_simbolo('(')
                if not (self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ')'):
                    self.parametros_formais()
                self.ler_simbolo(')')
                self.bloco()
            else:
                self.erro(f"Esperado ';', ',' ou '(' após identificador '{nome}'")
        else:
            self.erro("Esperado identificador após tipo")

    @rastrear("parametros_formais")
    def parametros_formais(self):
        self.parametro()
        while self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ',':
            self.ler_simbolo(',')
            self.parametro()

    @rastrear("parametro")
    def parametro(self):
        if self.token_atual.tipo in {'INT', 'FLOAT', 'CHAR', 'BOOL'}:
            self.ler(self.token_atual.tipo)
            self.ler('ID')
        else:
            self.erro("Esperado tipo de parâmetro")

    @rastrear("lista_ids_continua")
    def lista_ids_continua(self):
        while self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ',':
            self.ler_simbolo(',')
            self.ler('ID')

    @rastrear("bloco")
    def bloco(self):
        self.ler_simbolo('{')
        while not (self.token_atual.tipo == 'DELIM' and self.token_atual.valor == '}'):
            self.comando()
        self.ler_simbolo('}')

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
            self.ler('BREAK')
            self.ler_simbolo(';')
        elif self.token_atual.tipo == 'CONTINUE':
            self.ler('CONTINUE')
            self.ler_simbolo(';')
        elif self.token_atual.tipo == 'DELIM' and self.token_atual.valor == '{':
            self.bloco()
        else:
            self.erro("Comando inválido")

    @rastrear("decl_var")
    def decl_var(self):
        tipo = self.token_atual.tipo
        self.ler(tipo)
        self.ler('ID')
        self.lista_ids_continua()
        self.ler_simbolo(';')

    @rastrear("decl_var_for")
    def decl_var_for(self):
        tipo = self.token_atual.tipo
        self.ler(tipo)
        self.ler('ID')
        if self.token_atual.tipo == 'ATRIB':
            self.ler('ATRIB')
            self.expressao()
        self.lista_ids_continua_for()

    @rastrear("lista_ids_continua_for")
    def lista_ids_continua_for(self):
        while self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ',':
            self.ler_simbolo(',')
            self.ler('ID')
            if self.token_atual.tipo == 'ATRIB':
                self.ler('ATRIB')
                self.expressao()

    @rastrear("atribuicao_for")
    def atribuicao_for(self):
        self.ler('ID')
        self.ler('ATRIB')
        self.expressao()

    @rastrear("atribuicao")
    def atribuicao(self):
        self.ler('ID')
        self.ler('ATRIB')
        self.expressao()
        self.ler_simbolo(';')

    @rastrear("chamada_funcao")
    def chamada_funcao(self):
        self.ler('ID')
        self.ler_simbolo('(')
        if not (self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ')'):
            self.lista_argumentos()
        self.ler_simbolo(')')
        self.ler_simbolo(';')

    @rastrear("lista_argumentos")
    def lista_argumentos(self):
        self.expressao()
        while self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ',':
            self.ler_simbolo(',')
            self.expressao()

    @rastrear("comando_if")
    def comando_if(self):
        self.ler('IF')
        self.ler_simbolo('(')
        self.expressao()
        self.ler_simbolo(')')
        self.comando()
        if self.token_atual.tipo == 'ELSE':
            self.ler('ELSE')
            self.comando()

    @rastrear("comando_while")
    def comando_while(self):
        self.ler('WHILE')
        self.ler_simbolo('(')
        self.expressao()
        self.ler_simbolo(')')
        self.comando()

    @rastrear("comando_for")
    def comando_for(self):
        self.ler('FOR')
        self.ler_simbolo('(')

        if self.token_atual.tipo in {'INT', 'FLOAT', 'CHAR', 'BOOL'}:
            self.decl_var_for()
        elif self.token_atual.tipo == 'ID':
            self.atribuicao_for()
        else:
            self.erro("Esperado declaração com inicialização ou atribuição na inicialização do for")

        self.ler_simbolo(';')

        self.expressao()
        self.ler_simbolo(';')

        if self.token_atual.tipo == 'ID':
            self.atribuicao_for()
        else:
            self.erro("Esperado atribuição no incremento do for")

        self.ler_simbolo(')')
        self.comando()

    @rastrear("comando_return")
    def comando_return(self):
        self.ler('RETURN')
        if self.token_atual.tipo != 'DELIM' or (self.token_atual.tipo == 'DELIM' and self.token_atual.valor != ';'):
            self.expressao()
        self.ler_simbolo(';')

    @rastrear("expressao")
    def expressao(self):
        self.expressao_logica()

    def expressao_logica(self):
        self.expressao_logica2()
        while self.token_atual.tipo == 'OP_LOG' and self.token_atual.valor == '||':
            self.ler('OP_LOG')
            self.expressao_logica2()

    def expressao_logica2(self):
        self.expressao_logica3()
        while self.token_atual.tipo == 'OP_LOG' and self.token_atual.valor == '&&':
            self.ler('OP_LOG')
            self.expressao_logica3()

    def expressao_logica3(self):
        if self.token_atual.tipo == 'OP_LOG' and self.token_atual.valor == '!':
            self.ler('OP_LOG')
            self.expressao_logica3()
        else:
            self.expressao_relacional()

    @rastrear("expressao_relacional")
    def expressao_relacional(self):
        self.expressao_aritmetica()
        if self.token_atual.tipo == 'OP_REL':
            self.ler('OP_REL')
            self.expressao_aritmetica()

    @rastrear("expressao_aritmetica")
    def expressao_aritmetica(self):
        self.termo()
        while self.token_atual.tipo == 'OP_ARIT' and self.token_atual.valor in ('+', '-'):
            self.ler('OP_ARIT')
            self.termo()

    @rastrear("termo da expressão")
    def termo(self):
        self.fator()
        while self.token_atual.tipo == 'OP_ARIT' and self.token_atual.valor in ('*', '/', '%'):
            self.ler('OP_ARIT')
            self.fator()

    @rastrear("fator da expressão")
    def fator(self):
        if self.token_atual.tipo == 'NUM_INT':
            self.ler('NUM_INT')
        elif self.token_atual.tipo == 'ID':
            proximo = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if proximo and proximo.tipo == 'DELIM' and proximo.valor == '(':
                self.ler('ID')
                self.ler_simbolo('(')
                if not (self.token_atual.tipo == 'DELIM' and self.token_atual.valor == ')'):
                    self.lista_argumentos()
                self.ler_simbolo(')')
            else:
                self.ler('ID')
        elif self.token_atual.tipo in {'TRUE', 'FALSE'}:
            self.ler(self.token_atual.tipo)
        elif self.token_atual.tipo == 'DELIM' and self.token_atual.valor == '(':
            self.ler_simbolo('(')
            self.expressao()
            self.ler_simbolo(')')
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
