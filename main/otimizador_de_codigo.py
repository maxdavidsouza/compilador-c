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
                return tabela_simbolos.get(operando)

    def _avaliar_expressao(self, op1, op, op2, tabela_simbolos):
        v1 = self._obter_valor(op1, tabela_simbolos)
        v2 = self._obter_valor(op2, tabela_simbolos)

        if v1 is not None and v2 is not None:
            if op == '+': return v1 + v2
            if op == '-': return v1 - v2
            if op == '*': return v1 * v2
            if op == '/':
                if v2 != 0:
                    return v1 / v2
                else:
                    return None
            if op == '==': return int(v1 == v2)
            if op == '>':  return int(v1 > v2)
            if op == '<':  return int(v1 < v2)
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
        tabela_simbolos = {}

        for linha in codigo:
            linha_limpa = linha.strip()
            partes = re.split(r'[\s,]+', linha_limpa)
            if not partes or linha_limpa.endswith(':'):
                codigo_novo.append(linha)
                continue

            instrucao = partes[0]

            # --- Inlining de Funções ---
            if instrucao == 'call':
                if len(partes) >= 3:
                    nome_funcao = partes[1]
                    dest = partes[2]

                    if nome_funcao in self.funcoes:
                        func_code = self.funcoes[nome_funcao]
                        # Tenta encontrar o valor de retorno
                        for func_line in func_code:
                            func_parts = func_line.strip().split()
                            if func_parts and func_parts[0] == 'return':
                                valor_retorno = self._obter_valor(func_parts[1], {})
                                if valor_retorno is not None:
                                    codigo_novo.append(f"{dest} = {valor_retorno}")
                                    break
                        else:  # Se o loop terminar sem break, a função não retornou uma constante
                            codigo_novo.append(linha)
                    else:
                        codigo_novo.append(linha)

            # --- Dobramento e Propagação ---
            elif len(partes) >= 3 and partes[1] == '=':
                dest = partes[0]
                if len(partes) == 3:  # Atribuição simples: a = t1
                    valor = self._obter_valor(partes[2], tabela_simbolos)
                    if valor is not None:
                        tabela_simbolos[dest] = valor
                        codigo_novo.append(f"{dest} = {valor}")
                    else:
                        tabela_simbolos[dest] = partes[2]
                        codigo_novo.append(linha)
                elif len(partes) == 5:  # Expressão: t3 = a < 5
                    op1, op, op2 = partes[2], partes[3], partes[4]
                    resultado = self._avaliar_expressao(op1, op, op2, tabela_simbolos)
                    if resultado is not None:
                        tabela_simbolos[dest] = resultado
                        codigo_novo.append(f"{dest} = {resultado}")
                    else:
                        codigo_novo.append(linha)

            # --- Propagação para outros comandos ---
            else:
                for i, parte in enumerate(partes):
                    valor = self._obter_valor(parte, tabela_simbolos)
                    if valor is not None:
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
                    continue  # Pula a declaração morta

            elif len(partes) >= 3 and partes[1] == '=':
                dest = partes[0]
                usadas_nesta_linha.update(
                    p for p in partes[2:] if p and not p.isdigit() and not (p.startswith('L') and p[1:].isdigit()))
                if dest not in variaveis_vivas:
                    continue  # Pula a atribuição morta

            elif instrucao in ['print', 'param', 'return', 'if_false', 'goto', 'call']:
                usadas_nesta_linha.update(
                    p for p in partes[1:] if p and not p.isdigit() and not (p.startswith('L') and p[1:].isdigit()))

            if dest is not None:
                variaveis_vivas.discard(dest)

            codigo_final.insert(0, linha_limpa)
            variaveis_vivas.update(usadas_nesta_linha)

        # Limpeza final de linhas vazias e goto redundante
        codigo_final = [linha for linha in codigo_final if linha.strip()]
        if codigo_final and codigo_final[0].strip() == 'goto main' and codigo_final[1].strip() == 'main:':
            codigo_final.pop(0)

        return codigo_final

    def otimizar(self):
        codigo_fase1 = self._passagem_inlining_e_dobramento(self.codigo)
        codigo_fase2 = self._passagem_eliminacao_codigo_morto(codigo_fase1)
        return codigo_fase2
