from collections import defaultdict

from analisador_lexico import Token


class AnalisadorSemantico:
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
        self.profundidade_loop = 0
        self.tipo_funcao_atual = None  # Para checar o return
        self.return_encontrado = False
        self.funcoes_declaradas = set()
        self.dependencias_funcao = defaultdict(set)  # funcoes chamando funcoes
        self.leitura_variaveis = defaultdict(set)  # variavel -> funções que leem
        self.escrita_variaveis = defaultdict(set)  # função -> variaveis que escreve

    # --- Funções de controle da árvore e da análise (iguais ao seu Parser) ---
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

    # --- Funções de Erro (Sintático e Semântico) ---
    def erro_sintatico(self, msg):
        raise Exception(
            f"Erro de Sintaxe na linha {self.token.linha}, coluna {self.token.coluna}: {msg} (token: {self.token})")

    def erro_semantico(self, msg):
        raise Exception(f"Erro Semântico na linha {self.token.linha}, coluna {self.token.coluna}: {msg}")

    def match(self, tipo_esperado, valor_esperado=None):
        if self.token.tipo == tipo_esperado:
            self.novo_no(f"<{self.token.tipo}, {self.token.valor}>")
            if valor_esperado is None or self.token.valor == valor_esperado:
                self.avanca()
            else:
                self.erro_sintatico(f"Esperado '{valor_esperado}', encontrado '{self.token.valor}'")
        else:
            self.erro_sintatico(f"Esperado token do tipo {tipo_esperado}, encontrado {self.token.tipo}")

    # --- Funções da Tabela de Símbolos (Aprimoradas) ---
    def inserir_tabela(self, nome, tipo, escopo, params=None):
        # Verifica se o símbolo já foi declarado no escopo local
        if self.buscar_simbolo(nome, escopo_local=True):
            self.erro_semantico(f"Identificador '{nome}' já declarado no escopo '{escopo}'.")

        self.endereco += 4
        simbolo = {
            'identificador': nome,
            'tipo': tipo,
            'escopo': escopo,
            'endereco': self.endereco,
            'params': params if params is not None else []
        }
        self.tabela_simbolos.append(simbolo)

    def buscar_simbolo(self, nome, escopo_local=False):
        # Busca no escopo atual
        for simbolo in reversed(self.tabela_simbolos):
            if simbolo['identificador'] == nome and simbolo['escopo'] == self.escopo_atual:
                return simbolo

        # Se não for busca local, busca também no escopo global
        if not escopo_local:
            for simbolo in reversed(self.tabela_simbolos):
                if simbolo['identificador'] == nome and simbolo['escopo'] == 'global':
                    return simbolo
        return None

    # --- Início da Análise Gramatical com Ações Semânticas ---
    def analisar(self):
        self.programa()
        if self.token.tipo != 'EOF':
            self.erro_sintatico("Esperado EOF no final")
        print("Análise semântica concluída com sucesso.")

        # Verificação obrigatória do main
        main_simbolo = self.buscar_simbolo('main')
        if not main_simbolo:
            self.erro_semantico("Função 'main' não declarada.")
        else:
            # Main deve ser int e sem parâmetros
            if main_simbolo['tipo'] != 'int':
                self.erro_semantico("Função 'main' deve ter tipo 'int'.")
            if main_simbolo.get('params'):
                self.erro_semantico("Função 'main' não deve ter parâmetros.")

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
        # A inserção na tabela é adiada para decl_continua para diferenciar var de função
        self.decl_continua(tipo, id_token)

    @rastrear("decl_continua")
    def decl_continua(self, tipo, id_token):
        # Declaração de variável
        if self.token.tipo == 'DELIM' and self.token.valor in {';', ','}:
            self.inserir_tabela(id_token.valor, tipo, self.escopo_atual)
            while self.token.tipo == 'DELIM' and self.token.valor == ',':
                self.match('DELIM', ',')
                id_var_token = self.token
                self.match('ID')
                self.inserir_tabela(id_var_token.valor, tipo, self.escopo_atual)
            self.match('DELIM', ';')
        # Declaração de função
        elif self.token.tipo == 'DELIM' and self.token.valor == '(':
            self.match('DELIM', '(')
            escopo_anterior = self.escopo_atual
            self.escopo_atual = id_token.valor
            self.tipo_funcao_atual = tipo
            self.return_encontrado = False

            params = []
            if not (self.token.tipo == 'DELIM' and self.token.valor == ')'):
                params = self.parametros_formais()

            self.inserir_tabela(id_token.valor, tipo, escopo_anterior, params)
            self.funcoes_declaradas.add(id_token.valor)
            self.match('DELIM', ')')
            self.bloco()

            if self.tipo_funcao_atual != 'void' and not self.return_encontrado:
                self.erro_semantico(
                    f"Função '{self.escopo_atual}' do tipo {self.tipo_funcao_atual} deve ter um comando 'return'.")

            self.escopo_atual = escopo_anterior
            self.tipo_funcao_atual = None
        else:
            self.erro_sintatico(f"Esperado ';', ',' ou '(' após identificador")

    def tipo(self):
        if self.token.tipo in {'INT', 'FLOAT', 'CHAR', 'BOOL', 'VOID'}:
            self.match(self.token.tipo)
        else:
            self.erro_sintatico("Esperado um tipo (int, float, etc.)")

    @rastrear("parametros_de_funcao")
    def parametros_formais(self):
        params = []
        params.append(self.parametro())
        while self.token.tipo == 'DELIM' and self.token.valor == ',':
            self.match('DELIM', ',')
            params.append(self.parametro())
        return params

    @rastrear("parametro")
    def parametro(self):
        tipo = self.token.tipo.lower()
        self.tipo()
        id_token = self.token
        self.match('ID')
        self.inserir_tabela(id_token.valor, tipo, self.escopo_atual)
        return {'tipo': tipo, 'nome': id_token.valor}

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
                self.match('DELIM', ';')
            else:
                self.erro_sintatico("Esperado '=' ou '(' após identificador")
        elif self.token.tipo == 'IF':
            self.comando_if()
        elif self.token.tipo == 'WHILE':
            self.comando_while()
        elif self.token.tipo == 'BREAK':
            self.comando_break()
        elif self.token.tipo == 'RETURN':
            self.comando_return()
        elif self.token.tipo == 'DELIM' and self.token.valor == '{':
            self.bloco()
        elif self.token.tipo == 'PRINT':
            self.match('PRINT')
            self.match('DELIM', '(')
            self.expressao()
            self.match('DELIM', ')')
            self.match('DELIM', ';')
        else:
            self.erro_sintatico("Comando inválido")

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
        id_token = self.token
        self.match('ID')

        simbolo = self.buscar_simbolo(id_token.valor)
        if not simbolo:
            self.erro_semantico(f"Variável '{id_token.valor}' não declarada.")

        tipo_variavel = simbolo['tipo']

        self.match('ATRIB', '=')
        tipo_expressao = self.expressao()

        # REQUISITO: Não permitir atribuição de valores a tipos diferentes
        if tipo_variavel != tipo_expressao:
            self.erro_semantico(
                f"Não é possível atribuir um valor do tipo '{tipo_expressao}' a uma variável do tipo '{tipo_variavel}'.")

        self.match('DELIM', ';')
        if self.escopo_atual != 'global':
            self.escrita_variaveis[self.escopo_atual].add(id_token.valor)

    @rastrear("chamada de função")
    def chamada_funcao(self):
        id_token = self.token
        self.match('ID')

        funcao_simbolo = self.buscar_simbolo(id_token.valor)
        if not funcao_simbolo:
            self.erro_semantico(f"Função '{id_token.valor}' não declarada.")
        if not funcao_simbolo['params']:  # Verifica se é realmente uma função
            if self.buscar_simbolo(id_token.valor)['tipo'] != 'void':  # Hack para aceitar funções sem params
                pass  # Aceita, mas idealmente a estrutura do símbolo seria melhor

        self.match('DELIM', '(')

        tipos_argumentos = []
        if not (self.token.tipo == 'DELIM' and self.token.valor == ')'):
            tipos_argumentos = self.lista_argumentos()

        # REQUISITO: Checar se uma chamada de função faz sentido
        params_esperados = funcao_simbolo.get('params', [])
        if len(tipos_argumentos) != len(params_esperados):
            self.erro_semantico(
                f"Função '{id_token.valor}' espera {len(params_esperados)} argumentos, mas recebeu {len(tipos_argumentos)}.")

        for i, arg_tipo in enumerate(tipos_argumentos):
            param_tipo = params_esperados[i]['tipo']
            if arg_tipo != param_tipo:
                self.erro_semantico(
                    f"Argumento {i + 1} da chamada da função '{id_token.valor}': esperado tipo '{param_tipo}', mas recebeu '{arg_tipo}'.")

        self.match('DELIM', ')')
        if self.escopo_atual != 'global':
            self.dependencias_funcao[self.escopo_atual].add(id_token.valor)
        return funcao_simbolo['tipo']  # Retorna o tipo de retorno da função

    @rastrear("lista de argumentos")
    def lista_argumentos(self):
        tipos = []
        tipos.append(self.expressao())
        while self.token.tipo == 'DELIM' and self.token.valor == ',':
            self.match('DELIM', ',')
            tipos.append(self.expressao())
        return tipos

    @rastrear("comando 'return'")
    def comando_return(self):
        self.match('RETURN')

        # Função void com return de valor
        if self.tipo_funcao_atual == 'void':
            if not (self.token.tipo == 'DELIM' and self.token.valor == ';'):
                self.erro_semantico(f"Função 'void' '{self.escopo_atual}' não pode retornar um valor.")
        else:  # Função não-void
            if self.token.tipo == 'DELIM' and self.token.valor == ';':
                self.erro_semantico(
                    f"Função '{self.escopo_atual}' deve retornar um valor do tipo '{self.tipo_funcao_atual}'.")

            tipo_retorno = self.expressao()
            if tipo_retorno != self.tipo_funcao_atual:
                self.erro_semantico(
                    f"Tipo de retorno incompatível. A função '{self.escopo_atual}' espera '{self.tipo_funcao_atual}' mas recebeu '{tipo_retorno}'.")

        self.match('DELIM', ';')
        self.return_encontrado = True

    # ---- EXPRESSÕES LÓGICAS, RELACIONAIS E ARITMÉTICAS COMPLETAS ----
    @rastrear("expressao")
    def expressao(self):
        return self.expressao_logica()

    @rastrear("expressao_logica")
    def expressao_logica(self):
        tipo_esq = self.expressao_relacional()
        while self.token.tipo == 'OP_LOG' and self.token.valor in ('&&', '||'):
            op = self.token.valor
            self.match('OP_LOG', op)
            tipo_dir = self.expressao_relacional()
            if tipo_esq != 'bool' or tipo_dir != 'bool':
                self.erro_semantico(f"Operação lógica '{op}' exige operandos booleanos.")
            tipo_esq = 'bool'
        return tipo_esq

    @rastrear("expressao_relacional")
    def expressao_relacional(self):
        tipo_esq = self.expressao_aritmetica()
        while self.token.tipo == 'OP_REL':
            op = self.token.valor
            self.match('OP_REL')
            tipo_dir = self.expressao_aritmetica()
            if tipo_esq != tipo_dir:
                self.erro_semantico(
                    f"Operação relacional '{op}' entre tipos incompatíveis: '{tipo_esq}' e '{tipo_dir}'.")
            tipo_esq = 'bool'
        return tipo_esq

    @rastrear("expressao_aritmetica")
    def expressao_aritmetica(self):
        tipo_esq = self.termo()
        while self.token.tipo == 'OP_ARIT' and self.token.valor in ('+', '-'):
            op = self.token.valor
            self.match('OP_ARIT', op)
            tipo_dir = self.termo()
            if tipo_esq != tipo_dir or tipo_esq not in ('int', 'float'):
                self.erro_semantico(
                    f"Operação aritmética '{op}' entre tipos incompatíveis: '{tipo_esq}' e '{tipo_dir}'.")
        return tipo_esq

    @rastrear("termo")
    def termo(self):
        tipo_esq = self.fator()
        while self.token.tipo == 'OP_ARIT' and self.token.valor in ('*', '/', '%'):
            op = self.token.valor
            self.match('OP_ARIT', op)
            tipo_dir = self.fator()
            if tipo_esq != tipo_dir or tipo_esq not in ('int', 'float'):
                self.erro_semantico(
                    f"Operação aritmética '{op}' entre tipos incompatíveis: '{tipo_esq}' e '{tipo_dir}'.")
        return tipo_esq

    @rastrear("fator")
    def fator(self):
        if self.token.tipo == 'NUM_INT':
            self.match('NUM_INT')
            return 'int'
        elif self.token.tipo == 'STRING':
            self.match('STRING')
            return 'char'
        elif self.token.tipo in {'TRUE', 'FALSE'}:
            self.match(self.token.tipo)
            return 'bool'
        elif self.token.tipo == 'ID':
            prox = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if prox and prox.tipo == 'DELIM' and prox.valor == '(':
                return self.chamada_funcao()
            else:
                id_token = self.token
                self.match('ID')
                simbolo = self.buscar_simbolo(id_token.valor)
                if not simbolo:
                    self.erro_semantico(f"Variável '{id_token.valor}' não declarada.")
                if self.escopo_atual != 'global':
                    self.leitura_variaveis[id_token.valor].add(self.escopo_atual)
                return simbolo['tipo']
        elif self.token.tipo == 'DELIM' and self.token.valor == '(':
            self.match('DELIM', '(')
            tipo_expr = self.expressao()
            self.match('DELIM', ')')
            return tipo_expr
        elif self.token.tipo == 'OP_LOG' and self.token.valor == '!':
            self.match('OP_LOG', '!')
            tipo_fat = self.fator()
            if tipo_fat != 'bool':
                self.erro_semantico(f"Operador '!' exige operando booleano, encontrou '{tipo_fat}'.")
            return 'bool'
        else:
            self.erro_sintatico("Fator inválido na expressão: esperado número, ID, bool, ou '('")

    def gerar_dot_string(self):
        # (código idêntico ao que você já tem)
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

    @rastrear("comando 'if'")
    def comando_if(self):
        self.match('IF')
        self.match('DELIM', '(')
        self.expressao()
        self.match('DELIM', ')')
        self.comando()  # comando do if

        # else opcional
        if self.token.tipo == 'ELSE':
            self.match('ELSE')
            self.comando()  # comando do else

    @rastrear("comando 'while'")
    def comando_while(self):
        self.match('WHILE')
        self.match('DELIM', '(')
        self.expressao()
        self.match('DELIM', ')')

        self.profundidade_loop += 1
        self.comando()  # corpo do while
        self.profundidade_loop -= 1

    @rastrear("break")
    def comando_break(self):
        if self.profundidade_loop == 0:
            self.erro_semantico("'break' só pode ser usado dentro de laços")
        self.match('BREAK')
        self.match('DELIM', ';')

    def gerar_grafo_dependencias(self):
        linhas = ["digraph Dependencias {"]

        # Funções: elipses cinzas com borda preta
        funcoes = [s['identificador'] for s in self.tabela_simbolos if s.get('params') is not None]
        for f in funcoes:
            linhas.append(f'  "{f}" [shape=ellipse, style=filled, fillcolor=lightgray, color=black];')

        # Variáveis: quadrados brancos com borda preta
        variaveis = [s['identificador'] for s in self.tabela_simbolos if s.get('params') is None]
        for v in variaveis:
            linhas.append(f'  "{v}" [shape=box, style=filled, fillcolor=white, color=black];')

        # Chamadas de função: seta sólida preta
        for f, chamadas in self.dependencias_funcao.items():
            for c in chamadas:
                linhas.append(f'  "{f}" -> "{c}" [label="chama", color=black, style=solid];')

        # Escrita: seta sólida preta com ponta fina
        for f, vars_escritas in self.escrita_variaveis.items():
            for v in vars_escritas:
                linhas.append(f'  "{f}" -> "{v}" [label="escreve", fontcolor=blue, color=blue, style=solid, arrowhead=vee];')

        # Leitura: seta pontilhada preta com ponta fina
        for v, funcoes_que_leem in self.leitura_variaveis.items():
            for f in funcoes_que_leem:
                linhas.append(f'  "{v}" -> "{f}" [label="lê", fontcolor=red, color=red, style=dashed, arrowhead=vee];')

        linhas.append("}")
        return "\n".join(linhas)
