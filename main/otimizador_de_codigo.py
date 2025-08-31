import operator


class Otimizador:
    def __init__(self, codigo_3ac):
        self.codigo_3ac = codigo_3ac

    def otimizar(self):
        while True:
            tamanho_antes = len(self.codigo_3ac)

            self.codigo_3ac = [linha for linha in self.codigo_3ac if linha.strip()]
            self.codigo_3ac = self._propagacao_constantes()
            self.codigo_3ac = self._avaliar_chamadas_funcao()
            self.codigo_3ac = self._remover_atribuicoes_redundantes()
            self.codigo_3ac = self._remover_codigo_morto()

            if len(self.codigo_3ac) == tamanho_antes:
                break

        return self.codigo_3ac

    def _get_variaveis_lidas_e_escritas(self, linha):
        partes = linha.split()
        if not partes:
            return [], []

        escritas = []
        lidas = []

        if '=' in linha:
            if len(partes) > 0:
                escritas.append(partes[0])
            if len(partes) > 2:
                lidas = partes[2:]
        elif partes[0] == 'param':
            if len(partes) > 1:
                lidas.append(partes[1])
        elif partes[0] == 'call':
            if len(partes) > 2:
                escritas.append(partes[2].strip(','))
            if len(partes) > 1 and partes[1] != 'main':
                lidas.append(partes[1].strip(','))
        elif partes[0] in ['print', 'return', 'if_false']:
            if len(partes) > 1:
                lidas.append(partes[1].strip('(),'))

        return escritas, lidas

    def _remover_atribuicoes_redundantes(self):
        novo_codigo = []

        for i, linha in enumerate(self.codigo_3ac):
            partes = linha.split()
            if len(partes) == 3 and partes[1] == '=' and partes[0].startswith('t') and partes[2].startswith('t'):
                temp_alvo = partes[0]
                temp_origem = partes[2]

                usos = sum(1 for linha_futura in self.codigo_3ac[i + 1:] if temp_alvo in linha_futura.split())

                if usos == 1:
                    for j, linha_futura in enumerate(self.codigo_3ac[i + 1:]):
                        if temp_alvo in linha_futura.split():
                            linha_substituida = linha_futura.replace(f' {temp_alvo}', f' {temp_origem}')
                            self.codigo_3ac[i + 1 + j] = linha_substituida
                            break
                    continue

            novo_codigo.append(linha)

        return novo_codigo

    def _propagacao_constantes(self):
        tabela_constantes = {}
        novo_codigo = []

        for linha in self.codigo_3ac:
            partes = linha.split()
            if not partes: continue

            var_alvo = partes[0] if '=' in linha else None
            linha_atualizada = linha

            for var, val in tabela_constantes.items():
                linha_atualizada = linha_atualizada.replace(f' {var}', f' {val}')
                linha_atualizada = linha_atualizada.replace(f'({var})', f'({val})')
                linha_atualizada = linha_atualizada.replace(f'{var},', f'{val},')

            if var_alvo and len(partes) > 2:
                expressao = ' '.join(linha_atualizada.split()[2:])
                try:
                    valor = eval(expressao)
                    if isinstance(valor, (int, float)):
                        tabela_constantes[var_alvo] = str(valor)
                except (NameError, SyntaxError):
                    if var_alvo in tabela_constantes:
                        del tabela_constantes[var_alvo]

            novo_codigo.append(linha_atualizada)

        return novo_codigo

    def _avaliar_chamadas_funcao(self):
        funcoes = self._dividir_em_funcoes()
        novo_codigo_final = []

        for nome_func, codigo_func in funcoes.items():
            if nome_func == 'main':
                main_otimizado = []
                i = 0
                while i < len(codigo_func):
                    linha = codigo_func[i]
                    partes = linha.split()

                    if len(partes) > 1 and partes[0] == 'param' and partes[1].isdigit():
                        params_constantes = []
                        j = i
                        while j < len(codigo_func) and codigo_func[j].split()[0] == 'param' and codigo_func[j].split()[
                            1].isdigit():
                            params_constantes.append(int(codigo_func[j].split()[1]))
                            j += 1

                        if j < len(codigo_func) and codigo_func[j].split()[0] == 'call':
                            nome_chamada = codigo_func[j].split(',')[0].split()[1]
                            var_retorno = codigo_func[j].split(',')[1].strip()

                            if nome_chamada in funcoes and self._e_pura(funcoes[nome_chamada]):
                                resultado = self._executar_funcao(nome_chamada, params_constantes, funcoes)
                                if resultado is not None:
                                    main_otimizado.append(f'{var_retorno} = {resultado}')
                                    i = j + 1
                                    continue

                    main_otimizado.append(linha)
                    i += 1

                novo_codigo_final.extend(main_otimizado)
            else:
                novo_codigo_final.extend(codigo_func)

        funcoes_chamadas = set()
        for linha in novo_codigo_final:
            partes = linha.split()
            if len(partes) > 1 and partes[0] == 'call':
                funcoes_chamadas.add(partes[1].strip(','))

        funcoes_restantes = []
        for nome_func, codigo_func in funcoes.items():
            if nome_func in funcoes_chamadas or nome_func == 'main' or nome_func.startswith(('L', 't')):
                funcoes_restantes.extend(codigo_func)

        return funcoes_restantes

    def _remover_codigo_morto(self):
        variaveis_vivas = set()
        novo_codigo = []

        for linha in reversed(self.codigo_3ac):
            partes = linha.split()
            if not partes: continue

            escritas, lidas = self._get_variaveis_lidas_e_escritas(linha)

            deve_manter = True
            if escritas and not escritas[0].startswith('t'):
                if escritas[0] not in variaveis_vivas:
                    deve_manter = False

            if escritas and escritas[0].startswith('t'):
                if escritas[0] not in variaveis_vivas:
                    deve_manter = False

            if partes[0] == 'declare':
                if len(partes) > 1 and partes[1] not in variaveis_vivas:
                    deve_manter = False

            if deve_manter:
                novo_codigo.append(linha)
                for var in lidas:
                    if not var.isdigit() and not var.startswith(('t', 'L')):
                        variaveis_vivas.add(var.strip('(),'))
                for var in escritas:
                    if var in variaveis_vivas:
                        variaveis_vivas.remove(var)

        return list(reversed(novo_codigo))

    def _dividir_em_funcoes(self):
        funcoes = {}
        func_atual = 'global'
        codigo_atual = []
        for linha in self.codigo_3ac:
            partes = linha.split()
            if len(partes) == 1 and partes[0].endswith(':'):
                if func_atual != 'global':
                    funcoes[func_atual] = codigo_atual
                func_atual = partes[0].strip(':')
                codigo_atual = [linha]
            else:
                codigo_atual.append(linha)
        if func_atual != 'global':
            funcoes[func_atual] = codigo_atual
        return funcoes

    def _e_pura(self, codigo_func):
        for linha in codigo_func:
            partes = linha.split()
            if not partes: continue
            if partes[0] in ['print', 'call']:
                return False
        return True

    def _executar_funcao(self, nome_func, args, funcoes):
        codigo_func = funcoes.get(nome_func, [])
        tabela_vars = {}

        parametros = []
        for linha in codigo_func:
            partes = linha.split()
            if partes[0] == 'param' and len(partes) > 1:
                parametros.append(partes[1])

        if len(parametros) != len(args):
            return None

        for i, param in enumerate(parametros):
            tabela_vars[param] = args[i]

        for linha in codigo_func:
            partes = linha.split()
            if len(partes) > 2 and partes[1] == '=':
                expr = ' '.join(partes[2:])
                for var, val in tabela_vars.items():
                    expr = expr.replace(var, str(val))
                try:
                    resultado = eval(expr, {}, {'operator': operator, **tabela_vars})
                    tabela_vars[partes[0]] = resultado
                except:
                    return None
            elif partes[0] == 'return':
                if len(partes) > 1:
                    val_retorno = partes[1]
                    if val_retorno.isdigit():
                        return int(val_retorno)
                    else:
                        return tabela_vars.get(val_retorno)
        return None