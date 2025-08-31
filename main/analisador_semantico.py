from collections import defaultdict
from analisador_lexico import Token
import operator


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
        self.tipo_funcao_atual = None
        self.return_encontrado = False
        self.funcoes_declaradas = set()
        self.dependencias_funcao = defaultdict(set)
        self.leitura_variaveis = defaultdict(set)
        self.escrita_variaveis = defaultdict(set)
        self.codigo_3ac = []
        self.temp_count = 0
        self.label_count = 0

    def novo_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def novo_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

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
            f"Erro de sintaxe na linha {self.token.linha}, coluna {self.token.coluna}: {msg} (token: {self.token})")

    def erro_semantico(self, msg):
        raise Exception(f"Erro semântico na linha {self.token.linha}, coluna {self.token.coluna}: {msg}")

    def match(self, tipo_esperado, valor_esperado=None):
        if self.token.tipo == tipo_esperado:
            self.novo_no(f"<{self.token.tipo}, {self.token.valor}>")
            if valor_esperado is None or self.token.valor == valor_esperado:
                self.avanca()
            else:
                self.erro_sintatico(f"Esperado '{valor_esperado}', encontrado '{self.token.valor}'")
        else:
            self.erro_sintatico(f"Esperado token do tipo {tipo_esperado}, encontrado {self.token.tipo}")

    # --- Alteração na inserção na tabela ---
    def inserir_tabela(self, nome, tipo, escopo, params=None):
        if self.buscar_simbolo(nome, escopo_local=True):
            self.erro_semantico(f"Identificador '{nome}' já declarado no escopo '{escopo}'.")

        self.endereco += 4
        simbolo = {
            'identificador': nome,
            'tipo': tipo,
            'escopo': escopo,
            'endereco': self.endereco,
            'params': params if params is not None else [],
            'inicializada': False
        }
        self.tabela_simbolos.append(simbolo)
        if params is None:
            self.codigo_3ac.append(f'declare {nome}, {tipo}')

    def buscar_simbolo(self, nome, escopo_local=False):
        for simbolo in reversed(self.tabela_simbolos):
            if simbolo['identificador'] == nome and simbolo['escopo'] == self.escopo_atual:
                return simbolo

        if not escopo_local:
            for simbolo in reversed(self.tabela_simbolos):
                if simbolo['identificador'] == nome and simbolo['escopo'] == 'global':
                    return simbolo
        return None

    def analisar(self):
        self.programa()
        if self.token.tipo != 'EOF':
            self.erro_sintatico("Esperado EOF no final")
        print("Análise semântica concluída com sucesso.")

        main_simbolo = self.buscar_simbolo('main')
        if not main_simbolo:
            self.erro_semantico("Função 'main' não declarada.")
        else:
            if main_simbolo['tipo'] != 'int':
                self.erro_semantico("Função 'main' deve ter tipo 'int'.")
            if main_simbolo.get('params'):
                self.erro_semantico("Função 'main' não deve ter parâmetros.")

        self.codigo_3ac.insert(0, 'goto main')
        self.codigo_3ac.append('halt')

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
        self.decl_continua(tipo, id_token)

    @rastrear("decl_continua")
    def decl_continua(self, tipo, id_token):
        if self.token.tipo == 'DELIM' and self.token.valor in {';', ','}:
            self.inserir_tabela(id_token.valor, tipo, self.escopo_atual)
            while self.token.tipo == 'DELIM' and self.token.valor == ',':
                self.match('DELIM', ',')
                id_var_token = self.token
                self.match('ID')
                self.inserir_tabela(id_var_token.valor, tipo, self.escopo_atual)
            self.match('DELIM', ';')
        elif self.token.tipo == 'DELIM' and self.token.valor == '(':
            self.match('DELIM', '(')
            escopo_anterior = self.escopo_atual
            self.escopo_atual = id_token.valor
            self.tipo_funcao_atual = tipo
            self.return_encontrado = False

            self.codigo_3ac.append(f'\n{self.escopo_atual}:')
            self.codigo_3ac.append('push_stack')

            params = []
            if not (self.token.tipo == 'DELIM' and self.token.valor == ')'):
                params = self.parametros_formais()

            simbolo = {
                'identificador': id_token.valor,
                'tipo': tipo,
                'escopo': escopo_anterior,
                'endereco': self.endereco,
                'params': params,
                'inicializada': True
            }
            self.tabela_simbolos.append(simbolo)
            self.funcoes_declaradas.add(id_token.valor)

            self.match('DELIM', ')')
            self.bloco()

            if self.tipo_funcao_atual != 'void' and not self.return_encontrado:
                self.erro_semantico(
                    f"Função '{self.escopo_atual}' do tipo {self.tipo_funcao_atual} deve ter um comando 'return'.")

            self.codigo_3ac.append('pop_stack')
            self.codigo_3ac.append('ret')

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
        simbolo = {
            'identificador': id_token.valor,
            'tipo': tipo,
            'escopo': self.escopo_atual,
            'endereco': self.endereco + 4,
            'params': [],
            'inicializada': True
        }
        self.endereco += 4
        self.tabela_simbolos.append(simbolo)
        self.codigo_3ac.append(f'param {id_token.valor}')
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
            end_expr, _ = self.expressao()
            self.codigo_3ac.append(f'print {end_expr}')
            self.match('DELIM', ')')
            self.match('DELIM', ';')
        else:
            self.erro_sintatico("Comando inválido")

    @rastrear("decl_var")
    def decl_var(self):
        tipo = self.token.tipo.lower()
        self.tipo()
        id_token = self.token
        self.inserir_tabela(id_token.valor, tipo, self.escopo_atual)
        self.match('ID')
        while self.token.tipo == 'DELIM' and self.token.valor == ',':
            self.match('DELIM', ',')
            id_token = self.token
            self.match('ID')
            self.inserir_tabela(id_token.valor, tipo, self.escopo_atual)
        self.match('DELIM', ';')

    @rastrear("atribuicao")
    def atribuicao(self):
        id_token = self.token
        self.match('ID')

        simbolo = self.buscar_simbolo(id_token.valor)
        if not simbolo:
            self.erro_semantico(f"Variável '{id_token.valor}' não declarada.")

        tipo_variavel = simbolo['tipo']

        self.match('ATRIB', '=')
        end_expr, tipo_expressao = self.expressao()

        if tipo_variavel != tipo_expressao:
            if not (tipo_variavel == 'float' and tipo_expressao == 'int'):
                self.erro_semantico(
                    f"Não é possível atribuir um valor do tipo '{tipo_expressao}' a uma variável do tipo '{tipo_variavel}'.")

        self.codigo_3ac.append(f'{id_token.valor} = {end_expr}')
        simbolo['inicializada'] = True

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

        self.match('DELIM', '(')

        tipos_argumentos = []
        if not (self.token.tipo == 'DELIM' and self.token.valor == ')'):
            tipos_argumentos = self.lista_argumentos()

        for end_arg in tipos_argumentos:
            self.codigo_3ac.append(f'param {end_arg}')

        params_esperados = funcao_simbolo.get('params', [])
        if len(tipos_argumentos) != len(params_esperados):
            self.erro_semantico(
                f"Função '{id_token.valor}' espera {len(params_esperados)} argumentos, mas recebeu {len(tipos_argumentos)}.")

        for i, (end_arg, arg_tipo) in enumerate(zip(tipos_argumentos, [p['tipo'] for p in params_esperados])):
            param_tipo = params_esperados[i]['tipo']
            if arg_tipo != param_tipo:
                self.erro_semantico(
                    f"Argumento {i + 1} da chamada da função '{id_token.valor}': esperado tipo '{param_tipo}', mas recebeu '{arg_tipo}'.")

        self.match('DELIM', ')')

        end_retorno = None
        if funcao_simbolo['tipo'] != 'void':
            end_retorno = self.novo_temp()
            self.codigo_3ac.append(f'call {id_token.valor}, {end_retorno}')
        else:
            self.codigo_3ac.append(f'call {id_token.valor}')

        if self.escopo_atual != 'global':
            self.dependencias_funcao[self.escopo_atual].add(id_token.valor)

        return end_retorno, funcao_simbolo['tipo']

    @rastrear("lista de argumentos")
    def lista_argumentos(self):
        enderecos_tipos = []
        end, tipo = self.expressao()
        enderecos_tipos.append((end, tipo))
        while self.token.tipo == 'DELIM' and self.token.valor == ',':
            self.match('DELIM', ',')
            end, tipo = self.expressao()
            enderecos_tipos.append((end, tipo))

        return [end for end, tipo in enderecos_tipos]

    @rastrear("comando 'return'")
    def comando_return(self):
        self.match('RETURN')

        if self.tipo_funcao_atual == 'void':
            if not (self.token.tipo == 'DELIM' and self.token.valor == ';'):
                self.erro_semantico(f"Função 'void' '{self.escopo_atual}' não pode retornar um valor.")
            self.codigo_3ac.append('ret')
        else:
            if self.token.tipo == 'DELIM' and self.token.valor == ';':
                self.erro_semantico(
                    f"Função '{self.escopo_atual}' deve retornar um valor do tipo '{self.tipo_funcao_atual}'.")

            end_retorno, tipo_retorno = self.expressao()
            if tipo_retorno != self.tipo_funcao_atual:
                self.erro_semantico(
                    f"Tipo de retorno incompatível. A função '{self.escopo_atual}' espera '{self.tipo_funcao_atual}' mas recebeu '{tipo_retorno}'.")
            self.codigo_3ac.append(f'return {end_retorno}')

        self.match('DELIM', ';')
        self.return_encontrado = True

    @rastrear("expressao")
    def expressao(self):
        return self.expressao_logica()

    @rastrear("expressao_logica")
    def expressao_logica(self):
        end_esq, tipo_esq = self.expressao_relacional()
        while self.token.tipo == 'OP_LOG' and self.token.valor in ('&&', '||'):
            op = self.token.valor
            self.match('OP_LOG', op)
            end_dir, tipo_dir = self.expressao_relacional()
            if tipo_esq != 'bool' or tipo_dir != 'bool':
                self.erro_semantico(f"Operação lógica '{op}' exige operandos booleanos.")

            end_temp = self.novo_temp()
            self.codigo_3ac.append(f'{end_temp} = {end_esq} {op} {end_dir}')
            end_esq = end_temp
            tipo_esq = 'bool'
        return end_esq, tipo_esq

    @rastrear("expressao_relacional")
    def expressao_relacional(self):
        end_esq, tipo_esq = self.expressao_aritmetica()
        while self.token.tipo == 'OP_REL':
            op = self.token.valor
            self.match('OP_REL')
            end_dir, tipo_dir = self.expressao_aritmetica()
            if tipo_esq != tipo_dir:
                self.erro_semantico(
                    f"Operação relacional '{op}' entre tipos incompatíveis: '{tipo_esq}' e '{tipo_dir}'.")

            end_temp = self.novo_temp()
            self.codigo_3ac.append(f'{end_temp} = {end_esq} {op} {end_dir}')
            end_esq = end_temp
            tipo_esq = 'bool'
        return end_esq, tipo_esq

    @rastrear("expressao_aritmetica")
    def expressao_aritmetica(self):
        end_esq, tipo_esq = self.termo()
        while self.token.tipo == 'OP_ARIT' and self.token.valor in ('+', '-'):
            op = self.token.valor
            self.match('OP_ARIT', op)
            end_dir, tipo_dir = self.termo()
            if tipo_esq not in ('int', 'float') or tipo_dir not in ('int', 'float'):
                self.erro_semantico(
                    f"Operação aritmética '{op}' entre tipos incompatíveis: '{tipo_esq}' e '{tipo_dir}'.")

            end_temp = self.novo_temp()
            self.codigo_3ac.append(f'{end_temp} = {end_esq} {op} {end_dir}')
            end_esq = end_temp
            if tipo_esq == 'float' or tipo_dir == 'float':
                tipo_esq = 'float'
        return end_esq, tipo_esq

    @rastrear("termo")
    def termo(self):
        end_esq, tipo_esq = self.fator()
        while self.token.tipo == 'OP_ARIT' and self.token.valor in ('*', '/', '%'):
            op = self.token.valor
            self.match('OP_ARIT', op)
            end_dir, tipo_dir = self.fator()
            if tipo_esq not in ('int', 'float') or tipo_dir not in ('int', 'float'):
                self.erro_semantico(
                    f"Operação aritmética '{op}' entre tipos incompatíveis: '{tipo_esq}' e '{tipo_dir}'.")

            end_temp = self.novo_temp()
            self.codigo_3ac.append(f'{end_temp} = {end_esq} {op} {end_dir}')
            end_esq = end_temp
            if tipo_esq == 'float' or tipo_dir == 'float':
                tipo_esq = 'float'
        return end_esq, tipo_esq

    @rastrear("fator")
    def fator(self):
        if self.token.tipo == 'NUM_INT':
            valor = self.token.valor
            self.match('NUM_INT')
            end_temp = self.novo_temp()
            self.codigo_3ac.append(f'{end_temp} = {valor}')
            return end_temp, 'int'
        elif self.token.tipo == 'NUM_FLOAT':
            valor = self.token.valor
            self.match('NUM_FLOAT')
            end_temp = self.novo_temp()
            self.codigo_3ac.append(f'{end_temp} = {valor}')
            return end_temp, 'float'
        elif self.token.tipo == 'STRING':
            valor = self.token.valor
            self.match('STRING')
            end_temp = self.novo_temp()
            self.codigo_3ac.append(f'{end_temp} = {valor}')
            return end_temp, 'char'
        elif self.token.tipo in {'TRUE', 'FALSE'}:
            valor = self.token.valor
            self.match(self.token.tipo)
            end_temp = self.novo_temp()
            self.codigo_3ac.append(f'{end_temp} = {valor}')
            return end_temp, 'bool'
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
                if not simbolo.get('inicializada', False):
                    self.erro_semantico(f"Variável '{id_token.valor}' usada antes de ser inicializada.")
                if self.escopo_atual != 'global':
                    self.leitura_variaveis[id_token.valor].add(self.escopo_atual)
                return id_token.valor, simbolo['tipo']
        elif self.token.tipo == 'DELIM' and self.token.valor == '(':
            self.match('DELIM', '(')
            end_expr, tipo_expr = self.expressao()
            self.match('DELIM', ')')
            return end_expr, tipo_expr
        elif self.token.tipo == 'OP_LOG' and self.token.valor == '!':
            self.match('OP_LOG', '!')
            end_fat, tipo_fat = self.fator()
            if tipo_fat != 'bool':
                self.erro_semantico(f"Operador '!' exige operando booleano, encontrou '{tipo_fat}'.")

            end_temp = self.novo_temp()
            self.codigo_3ac.append(f'{end_temp} = !{end_fat}')
            return end_temp, 'bool'
        else:
            self.erro_sintatico(
                f"Fator inválido na expressão: esperado número, ID, bool, ou '('. Encontrado {self.token.valor}")

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

    @rastrear("comando 'if'")
    def comando_if(self):
        self.match('IF')
        self.match('DELIM', '(')
        end_cond, _ = self.expressao()
        self.match('DELIM', ')')

        label_else = self.novo_label()
        label_fim = self.novo_label()

        self.codigo_3ac.append(f'if_false {end_cond} goto {label_else}')

        self.comando()

        self.codigo_3ac.append(f'goto {label_fim}')

        if self.token.tipo == 'ELSE':
            self.match('ELSE')
            self.codigo_3ac.append(f'{label_else}:')
            self.comando()
        else:
            self.codigo_3ac.append(f'{label_else}:')

        self.codigo_3ac.append(f'{label_fim}:')

    @rastrear("comando 'while'")
    def comando_while(self):
        self.profundidade_loop += 1
        label_inicio = self.novo_label()
        label_fim = self.novo_label()

        self.codigo_3ac.append(f'{label_inicio}:')

        self.match('WHILE')
        self.match('DELIM', '(')
        end_cond, _ = self.expressao()
        self.match('DELIM', ')')
        self.codigo_3ac.append(f'if_false {end_cond} goto {label_fim}')

        self.comando()

        self.codigo_3ac.append(f'goto {label_inicio}')
        self.codigo_3ac.append(f'{label_fim}:')

        self.profundidade_loop -= 1

    @rastrear("break")
    def comando_break(self):
        if self.profundidade_loop == 0:
            self.erro_semantico("'break' só pode ser usado dentro de laços")
        self.match('BREAK')
        self.match('DELIM', ';')
        self.codigo_3ac.append(f'goto FIM_LOOP_{self.profundidade_loop}')

    def gerar_grafo_dependencias(self):
        linhas = ["digraph Dependencias {"]
        linhas.append("  node [shape=box, style=filled, fillcolor=lightblue];")

        funcoes = [s['identificador'] for s in self.tabela_simbolos if s.get('params') is not None]
        for f in funcoes:
            linhas.append(f'  "{f}" [shape=ellipse, style=filled, fillcolor=lightgray, color=black];')

        variaveis_por_escopo = {}
        for s in self.tabela_simbolos:
            if s.get('params') is None:
                nome_completo = f"{s['escopo']}_{s['identificador']}" if s['escopo'] != 'global' else s['identificador']
                variaveis_por_escopo[s['identificador']] = nome_completo
                linhas.append(f'  "{nome_completo}" [shape=box, style=filled, fillcolor=white, color=black];')

        for f, chamadas in self.dependencias_funcao.items():
            for c in chamadas:
                linhas.append(f'  "{f}" -> "{c}" [label="chama", color=black, style=solid];')

        for f, vars_escritas in self.escrita_variaveis.items():
            for v in vars_escritas:
                nome_completo = f"{f}_{v}"
                linhas.append(
                    f'  "{f}" -> "{nome_completo}" [label="escreve", fontcolor=blue, color=blue, style=solid, arrowhead=vee];')

        for v, funcoes_que_leem in self.leitura_variaveis.items():
            for f in funcoes_que_leem:
                nome_completo = f"{f}_{v}"
                linhas.append(
                    f'  "{nome_completo}" -> "{f}" [label="lê", fontcolor=red, color=red, style=dashed, arrowhead=vee];')

        linhas.append("}")
        return "\n".join(linhas)