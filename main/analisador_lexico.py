import re

class Token:
    def __init__(self, tipo, valor, linha, coluna):
        self.tipo = tipo
        self.valor = valor
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"Token({self.tipo}, '{self.valor}', linha={self.linha}, coluna={self.coluna})"

class Lexer:
    def __init__(self, codigo):
        self.codigo = codigo
        self.linha = 1
        self.coluna = 1
        self.pos = 0
        self.tokens = []
        self.erros = []

        self.palavras_reservadas = {
            'int', 'float', 'if', 'else', 'while', 'for', 'return', 'void', 'char', 'bool', 'true', 'false'
        }

        self.regex_tokens = [
            ('NUM_INT', r'\d+'),
            ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('OP_REL', r'==|!=|<=|>=|<|>'),
            ('OP_ARIT', r'\+|-|\*|/'),
            ('OP_LOG', r'&&|\|\||!'),
            ('ATRIB', r'='),
            ('DELIM', r'[;,\(\)\{\}]'),
            ('ESPACO', r'[ \t]+'),
            ('NOVA_LINHA', r'\n'),
            ('COMENT', r'//.*'),
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
                    if tipo == 'ID' and valor in self.palavras_reservadas:
                        tipo = valor.upper()  # palavra-chave vira tipo em maiúsculo
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