from analisador_lexico import Token

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.token = self.tokens[self.pos]
        self.node_id = 0
        self.nodes = []
        self.edges = []
        self.parent_stack = []
        self.tabela_simbolos = []
        self.escopo_atual = 'global'
        self.endereco = 0
        self.nos_com_erro = set()

    def novo_no(self, label):
        self.node_id += 1
        no_atual = self.node_id
        self.nodes.append((no_atual, label))
        if self.parent_stack:
            pai = self.parent_stack[-1]
            self.edges.append((pai, no_atual))
        return no_atual

    def rastrear(label_func):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                label = label_func(self) if callable(label_func) else label_func
                no_atual = self.novo_no(label)
                self.parent_stack.append(no_atual)
                try:
                    resultado = func(self, *args, **kwargs)
                except Exception as e:
                    self.nos_com_erro.add(no_atual)
                    raise e
                finally:
                    self.parent_stack.pop()
                return resultado
            return wrapper
        return decorator

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
            self.novo_no(f"<{self.token.tipo}, {self.token.valor}>")
            if valor_esperado is None or self.token.valor == valor_esperado:
                self.avanca()
            else:
                self.erro(f"Esperado token do tipo {tipo_esperado} com valor '{valor_esperado}', encontrado valor '{self.token.valor}'")
        else:
            self.erro(f"Esperado token do tipo {tipo_esperado}, encontrado {self.token.tipo}")

    def analisar(self):
        self.programa()
        if self.token.tipo != 'EOF':
            self.erro("Esperado EOF no final")

    @rastrear("programa")
    def programa(self):
        while self.token.tipo in {'INT', 'FLOAT', 'CHAR', 'BOOL', 'VOID'}:
            self.declaracao()

    @rastrear("declaracao")
    def declaracao(self):
        tipo = self.token.tipo.lower()
        self.tipo()
        id_token = self.token
        self.match('ID')
        self.inserir_tabela(id_token.valor, tipo, self.escopo_atual)
        self.decl_continua(tipo, id_token)

    @rastrear("decl_continua")
    def decl_continua(self, tipo=None, id_token=None):
        if self.token.tipo == 'DELIM' and self.token.valor == ';':
            self.match('DELIM', ';')
        elif self.token.tipo == 'DELIM' and self.token.valor == ',':
            while self.token.tipo == 'DELIM' and self.token.valor == ',':
                self.match('DELIM', ',')
                id_token = self.token
                self.match('ID')
                self.inserir_tabela(id_token.valor, tipo, self.escopo_atual)
            self.match('DELIM', ';')
        elif self.token.tipo == 'DELIM' and self.token.valor == '(':
            self.match('DELIM', '(')
            escopo_anterior = self.escopo_atual
            self.escopo_atual = id_token.valor
            self.tipo_funcao_atual = tipo
            self.return_encontrado = False
            if not (self.token.tipo == 'DELIM' and self.token.valor == ')'):
                self.parametros_formais()
            self.match('DELIM', ')')
            self.bloco()
            if self.tipo_funcao_atual != 'void' and not self.return_encontrado:
                self.erro(f"Função '{self.escopo_atual}' do tipo {self.tipo_funcao_atual} deve ter um return")
            self.escopo_atual = escopo_anterior
            self.tipo_funcao_atual = None
            self.return_encontrado = False
        else:
            self.erro(f"Esperado ';', ',' ou '(' após identificador")

    def tipo(self):
        if self.token.tipo in {'INT', 'FLOAT', 'CHAR', 'BOOL', 'VOID'}:
            self.match(self.token.tipo)
        else:
            self.erro("Esperado tipo")

    @rastrear("parametros_de_funcao")
    def parametros_formais(self):
        self.parametro()
        while self.token.tipo == 'DELIM' and self.token.valor == ',':
            self.match('DELIM', ',')
            self.parametro()

    @rastrear("parametro")
    def parametro(self):
        tipo = self.token.tipo.lower()
        self.tipo()
        id_token = self.token
        self.match('ID')
        self.inserir_tabela(id_token.valor, tipo, self.escopo_atual)

    @rastrear("bloco de função")
    def bloco(self):
        self.match('DELIM', '{')
        while not (self.token.tipo == 'DELIM' and self.token.valor == '}'):
            self.comando()
        self.match('DELIM', '}')

    @rastrear("comando")
    def comando(self):
        if self.token.tipo in {'INT', 'FLOAT', 'CHAR', 'BOOL'}:
            self.decl_var()
        elif self.token.tipo == 'ID':
            prox = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if prox and prox.tipo == 'ATRIB':
                self.atribuicao()
            elif prox and prox.tipo == 'DELIM' and prox.valor == '(':
                self.chamada_funcao()
            else:
                self.erro("Esperado '=' ou '(' após identificador")
        elif self.token.tipo == 'PRINT':
            self.match('PRINT')
            self.match('DELIM', '(')
            self.expressao()
            self.match('DELIM', ')')
            self.match('DELIM', ';')
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

    @rastrear("decl_var")
    def decl_var(self):
        tipo = self.token.tipo.lower()
        self.tipo()
        id_token = self.token
        self.match('ID')
        self.inserir_tabela(id_token.valor, tipo, self.escopo_atual)
        while self.token.tipo == 'DELIM' and self.token.valor == ',':
            self.match('DELIM', ',')
            id_token = self.token
            self.match('ID')
            self.inserir_tabela(id_token.valor, tipo, self.escopo_atual)
        self.match('DELIM', ';')

    @rastrear("atribuição")
    def atribuicao(self):
        self.match('ID')
        self.match('ATRIB', '=')
        self.expressao()
        self.match('DELIM', ';')

    @rastrear("chamada de função")
    def chamada_funcao(self):
        self.match('ID')
        self.match('DELIM', '(')
        if not (self.token.tipo == 'DELIM' and self.token.valor == ')'):
            self.lista_argumentos()
        self.match('DELIM', ')')
        self.match('DELIM', ';')

    @rastrear("lista de argumentos")
    def lista_argumentos(self):
        self.expressao()
        while self.token.tipo == 'DELIM' and self.token.valor == ',':
            self.match('DELIM', ',')
            self.expressao()

    @rastrear("comando 'if'")
    def comando_if(self):
        self.match('IF')
        self.match('DELIM', '(')
        self.expressao()
        self.match('DELIM', ')')
        self.comando()
        if self.token.tipo == 'ELSE':
            self.match('ELSE')
            self.comando()

    @rastrear("comando 'while'")
    def comando_while(self):
        self.match('WHILE')
        self.match('DELIM', '(')
        self.expressao()
        self.match('DELIM', ')')
        self.comando()

    @rastrear("comando 'for'")
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

    @rastrear("inicialização de 'for'")
    def for_inicializacao(self):
        if self.token.tipo in {'INT', 'FLOAT', 'CHAR', 'BOOL'}:
            self.decl_var_for()
        elif self.token.tipo == 'ID':
            self.atribuicao_for()
        else:
            self.erro("Esperado declaração com inicialização ou atribuição na inicialização do for")

    @rastrear("declaração de variáveis no 'for'")
    def decl_var_for(self):
        tipo = self.token.tipo.lower()
        self.tipo()
        id_token = self.token
        self.match('ID')
        self.inserir_tabela(id_token.valor, tipo, self.escopo_atual)
        if self.token.tipo == 'ATRIB':
            self.match('ATRIB', '=')
            self.expressao()
        while self.token.tipo == 'DELIM' and self.token.valor == ',':
            self.match('DELIM', ',')
            id_token = self.token
            self.match('ID')
            self.inserir_tabela(id_token.valor, tipo, self.escopo_atual)
            if self.token.tipo == 'ATRIB':
                self.match('ATRIB', '=')
                self.expressao()

    @rastrear("atribuição de valores no 'for'")
    def atribuicao_for(self):
        self.match('ID')
        self.match('ATRIB', '=')
        self.expressao()

    @rastrear("incremento do 'for'")
    def for_incremento(self):
        self.match('ID')
        self.match('ATRIB', '=')
        self.expressao()

    @rastrear("comando 'return'")
    def comando_return(self):
        funcao_atual = self.escopo_atual
        tipo_funcao = self.tipo_funcao_atual

        self.match('RETURN')

        if tipo_funcao == 'void':
            if not (self.token.tipo == 'DELIM' and self.token.valor == ';'):
                self.erro(f"Função void '{funcao_atual}' não deve retornar valor")
            self.match('DELIM', ';')
        else:
            if self.token.tipo == 'DELIM' and self.token.valor == ';':
                self.erro(f"Função '{funcao_atual}' do tipo {tipo_funcao} deve retornar um valor")
            self.expressao()
            self.match('DELIM', ';')
            self.return_encontrado = True

    def obter_tipo_funcao(self, nome_funcao):
        for entrada in self.tabela_simbolos:
            if entrada['identificador'] == nome_funcao:
                return entrada['tipo']
        return None

    @rastrear("expressao")
    def expressao(self):
        self.expressao_logica()

    def expressao_logica(self):
        self.expressao_logica2()
        while self.token.tipo == 'OP_LOG' and self.token.valor == '||':
            self.match('OP_LOG', '||')
            self.expressao_logica2()

    def expressao_logica2(self):
        self.expressao_logica3()
        while self.token.tipo == 'OP_LOG' and self.token.valor == '&&':
            self.match('OP_LOG', '&&')
            self.expressao_logica3()

    def expressao_logica3(self):
        if self.token.tipo == 'OP_LOG' and self.token.valor == '!':
            self.match('OP_LOG', '!')
            self.expressao_logica3()
        else:
            self.expressao_relacional()

    @rastrear("expressao_relacional")
    def expressao_relacional(self):
        self.expressao_aritmetica()
        if self.token.tipo == 'OP_REL':
            self.op_relacional()
            self.expressao_aritmetica()

    def op_relacional(self):
        if self.token.valor in {'==', '!=', '<=', '>=', '<', '>'}:
            self.match('OP_REL', self.token.valor)
        else:
            self.erro("Operador relacional inválido")

    @rastrear("expressao_aritmetica")
    def expressao_aritmetica(self):
        self.termo()
        while self.token.tipo == 'OP_ARIT' and self.token.valor in ('+', '-'):
            self.op_aritmetico()
            self.termo()

    @rastrear("termo")
    def termo(self):
        self.fator()
        while self.token.tipo == 'OP_ARIT' and self.token.valor in ('*', '/', '%'):
            self.op_aritmetico()
            self.fator()

    def op_aritmetico(self):
        if self.token.valor in {'+', '-', '*', '/', '%'}:
            self.match('OP_ARIT', self.token.valor)
        else:
            self.erro("Operador aritmético inválido")

    def fator(self):
        if self.token.tipo == 'NUM_INT':
            self.match('NUM_INT')
        elif self.token.tipo == 'STRING':
            self.match('STRING')
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
            self.erro("Esperado número, string, identificador, chamada de função, true, false ou '('")

    def gerar_dot_string(self):
        linhas = [
            "digraph ParserTrace {",
            "  node [shape=box, style=filled, fillcolor=lightblue];"
        ]
        for node_id, label in self.nodes:
            label_esc = label.replace('"', '\\"')
            fill = "lightcoral" if node_id in self.nos_com_erro else "lightblue"
            linhas.append(f'  {node_id} [label="{label_esc}", fillcolor={fill}];')
        for from_id, to_id in self.edges:
            linhas.append(f'  {from_id} -> {to_id};')
        linhas.append("}")
        return "\n".join(linhas)

    def inserir_tabela(self, nome, tipo, escopo):
        self.endereco += 4
        self.tabela_simbolos.append({
            'identificador': nome,
            'tipo': tipo,
            'escopo': escopo,
            'endereco': self.endereco
        })
