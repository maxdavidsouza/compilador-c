import re


class Otimizador:
    def __init__(self, codigo_3ac):
        self.codigo = codigo_3ac
        self.funcoes = self._analisar_funcoes()

    def _obter_valor(self, operando, tabela_simbolos):
        try:
            return int(operando)
        except ValueError:
            try:
                return float(operando)
            except ValueError:
                return tabela_simbolos.get(operando, operando)

    def _avaliar_expressao(self, v1, op, v2):
        if op == '+':
            return v1 + v2
        if op == '-':
            return v1 - v2
        if op == '*':
            return v1 * v2
        if op == '/':
            if v2 != 0:
                return v1 / v2
            return None
        return None

    def _analisar_funcoes(self):
        funcoes = {}
        nome_funcao = None
        conteudo_funcao = []
        for linha in self.codigo:
            linha_limpa = linha.strip()
            if linha_limpa.endswith(':'):
                if nome_funcao:
                    funcoes[nome_funcao] = conteudo_funcao
                    conteudo_funcao = []
                nome_funcao = linha_limpa.replace(':', '')
            elif nome_funcao:
                conteudo_funcao.append(linha)
        if nome_funcao:
            funcoes[nome_funcao] = conteudo_funcao
        return funcoes

    def _passagem_inlining_e_dobramento(self, codigo):
        codigo_novo = []
        tabela_constantes = {}
        tabela_copias = {}

        for linha in codigo:
            linha_limpa = linha.strip()
            partes = re.split(r'[\s,]+', linha_limpa)
            if not partes or not partes[0] or linha_limpa.endswith(':'):
                codigo_novo.append(linha)
                continue

            instrucao = partes[0]

            novas_partes = [tabela_copias.get(p, p) for p in partes]
            partes = novas_partes

            if len(partes) >= 3 and partes[1] == '=' and partes[2] == 'call':
                dest = partes[0]
                nome_funcao = partes[3]
                if nome_funcao in self.funcoes:
                    func_code = self.funcoes[nome_funcao]
                    for func_line in func_code:
                        func_parts = func_line.strip().split()
                        if func_parts and func_parts[0] == 'return':
                            valor_retorno = self._obter_valor(func_parts[1], {})
                            if isinstance(valor_retorno, (int, float)):
                                tabela_constantes[dest] = valor_retorno
                                codigo_novo.append(f"{dest} = {valor_retorno}")
                                break
                    else:
                        codigo_novo.append(" ".join(partes))
                else:
                    codigo_novo.append(" ".join(partes))

            elif instrucao == 'call':
                codigo_novo.append(" ".join(partes))

            elif len(partes) >= 3 and partes[1] == '=':
                dest = partes[0]
                if len(partes) == 3:
                    fonte = partes[2]
                    valor_fonte = self._obter_valor(fonte, tabela_constantes)
                    if isinstance(valor_fonte, (int, float)):
                        tabela_constantes[dest] = valor_fonte
                        codigo_novo.append(f"{dest} = {valor_fonte}")
                    else:
                        tabela_copias[dest] = fonte
                        codigo_novo.append(" ".join(partes))
                elif len(partes) == 5:
                    op1_str, op, op2_str = partes[2], partes[3], partes[4]
                    v1 = self._obter_valor(op1_str, tabela_constantes)
                    v2 = self._obter_valor(op2_str, tabela_constantes)

                    if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                        resultado = self._avaliar_expressao(v1, op, v2)
                        if resultado is not None:
                            tabela_constantes[dest] = resultado
                            codigo_novo.append(f"{dest} = {resultado}")
                        else:
                            codigo_novo.append(" ".join(partes))
                    else:
                        codigo_novo.append(" ".join(partes))
            else:
                for i, parte in enumerate(partes):
                    valor = tabela_constantes.get(parte, parte)
                    if isinstance(valor, (int, float)):
                        partes[i] = str(valor)
                codigo_novo.append(" ".join(partes))
        return codigo_novo

    def _passagem_eliminacao_codigo_morto(self, codigo):
        variaveis_vivas = set()
        codigo_final = []

        for linha in reversed(codigo):
            linha_limpa = linha.strip()
            partes = re.split(r'[\s,]+', linha_limpa)
            if not partes or not partes[0] or partes[0].endswith(':'):
                codigo_final.insert(0, linha_limpa)
                continue

            instrucao = partes[0]
            dest = None
            usadas_nesta_linha = set()

            if instrucao == 'declare':
                if len(partes) > 1:
                    dest = partes[1]
                if dest not in variaveis_vivas:
                    continue

            elif len(partes) >= 3 and partes[1] == '=':
                dest = partes[0]
                usadas_nesta_linha.update(
                    p for p in partes[2:] if p and not p.isdigit() and not (p.startswith('L') and p[1:].isdigit())
                )
                if dest not in variaveis_vivas:
                    continue

            elif instrucao in ['print', 'param', 'return', 'if_false', 'goto']:
                usadas_nesta_linha.update(
                    p for p in partes[1:] if p and not p.isdigit() and not (p.startswith('L') and p[1:].isdigit())
                )
            elif instrucao == 'call':
                usadas_nesta_linha.update(
                    p for p in partes[1:] if
                    p and not p.isdigit() and not (p.startswith('L') and p[1:].isdigit()) and not p.isdigit()
                )

            if dest is not None:
                variaveis_vivas.discard(dest)

            codigo_final.insert(0, linha_limpa)
            variaveis_vivas.update(usadas_nesta_linha)

        codigo_final = [linha for linha in codigo_final if linha.strip()]
        if codigo_final and codigo_final[0].strip() == 'goto main' and codigo_final[1].strip() == 'main:':
            codigo_final.pop(0)

        return codigo_final

    def otimizar(self):
        codigo_fase1 = self._passagem_inlining_e_dobramento(self.codigo)
        codigo_fase2 = self._passagem_eliminacao_codigo_morto(codigo_fase1)
        return codigo_fase2