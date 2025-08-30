import re

class Token:
    def __init__(self, tipo, valor, linha, coluna):
        self.tipo = tipo
        self.valor = valor
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"Token({self.tipo}, '{self.valor}', linha={self.linha}, coluna={self.coluna})"


class Simbolo:
    def __init__(self, nome, tipo=None, escopo="global", endereco=None):
        self.nome = nome
        self.tipo = tipo
        self.escopo = escopo
        self.endereco = endereco

    def __repr__(self):
        return f"Simbolo(nome={self.nome}, tipo={self.tipo}, escopo={self.escopo}, endereco={self.endereco})"


class TabelaSimbolos:
    def __init__(self):
        self.tabela = {}

    def adicionar(self, nome, tipo=None, escopo="global"):
        if nome not in self.tabela:
            self.tabela[nome] = Simbolo(nome, tipo, escopo)
        return self.tabela[nome]

    def buscar(self, nome):
        return self.tabela.get(nome)

    def __repr__(self):
        return str(self.tabela)


class Lexer:
    def __init__(self, codigo):
        self.codigo = codigo
        self.linha = 1
        self.coluna = 1
        self.pos = 0
        self.tokens = []
        self.erros = []
        self.tabela_simbolos = TabelaSimbolos()

        self.palavras_reservadas = {
            'int', 'float', 'if', 'else', 'while', 'for', 'break', 'continue', 'return', 'void',
            'char', 'bool', 'true', 'false', 'print'
        }

        self.regex_tokens = [
            ('COMENT', r'//.*'),
            ('STRING', r'"[^"\n]*"'),
            ('NUM_INT', r'\d+'),
            ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('OP_REL', r'==|!=|<=|>=|<|>'),
            ('OP_ARIT', r'\+|-|\*|/|%'),
            ('OP_LOG', r'&&|\|\||!'),
            ('ATRIB', r'='),
            ('DELIM', r'[;,\(\)\{\}]'),
            ('ESPACO', r'[ \t]+'),
            ('NOVA_LINHA', r'\n'),
        ]

        self.regex_geral = '|'.join(f'(?P<{nome}>{padrao})' for nome, padrao in self.regex_tokens)
        self.pattern = re.compile(self.regex_geral)

    def analisar(self):
        while self.pos < len(self.codigo):
            match = self.pattern.match(self.codigo, self.pos)
            if match:
                tipo = match.lastgroup
                valor = match.group(tipo)
                if tipo == 'NOVA_LINHA':
                    self.linha += 1
                    self.coluna = 1
                elif tipo == 'ESPACO' or tipo == 'COMENT':
                    self.coluna += len(valor)
                else:
                    if tipo == 'ID':
                        if valor in self.palavras_reservadas:
                            tipo = valor.upper()
                        else:
                            self.tabela_simbolos.adicionar(valor)

                    token = Token(tipo, valor, self.linha, self.coluna)
                    self.tokens.append(token)
                    self.coluna += len(valor)

                self.pos += len(valor)
            else:
                erro_char = self.codigo[self.pos]
                self.erros.append(f"Caractere inválido '{erro_char}' na linha {self.linha}, coluna {self.coluna}")
                self.pos += 1
                self.coluna += 1

        self.tokens.append(Token('EOF', '', self.linha, self.coluna))
        return self.tokens
