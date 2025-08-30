class GeradorCodigoIntermediario:
    def __init__(self):
        self.codigo = []       # Lista de instruções intermediárias
        self.temp_count = 0    # Contador para variáveis temporárias
        self.label_count = 0   # Contador para rótulos

    # --- Geração de temporário ---
    def novo_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    # --- Geração de rótulo ---
    def novo_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    # --- Inserir instrução ---
    def emitir(self, instrucao):
        self.codigo.append(instrucao)

    # --- Expressões ---
    # Representadas por tuplas (ex: {'tipo':'add', 'esq':'a', 'dir':'b'})
    # Retorna: nome do temporário onde o resultado é armazenado
    def gerar_expressao(self, expr):

        if isinstance(expr, (int, float, str)):
            return expr  # constante
        elif isinstance(expr, dict):
            op = expr['op']
            esq = self.gerar_expressao(expr['esq'])
            dir_ = self.gerar_expressao(expr['dir'])
            temp = self.novo_temp()
            self.emitir(f"{temp} = {esq} {op} {dir_}")
            return temp
        elif isinstance(expr, str):
            return expr  # variável
        else:
            raise Exception(f"Expressão inválida: {expr}")

    # --- Comandos ---
    def gerar_atribuicao(self, var, expr):
        resultado = self.gerar_expressao(expr)
        self.emitir(f"{var} = {resultado}")

    def gerar_if(self, condicao, label_true, label_false):
        resultado = self.gerar_expressao(condicao)
        self.emitir(f"if {resultado} goto {label_true}")
        self.emitir(f"goto {label_false}")

    def gerar_while(self, condicao, bloco_instr):
        inicio = self.novo_label()
        fim = self.novo_label()
        self.emitir(f"{inicio}:")
        cond_result = self.gerar_expressao(condicao)
        self.emitir(f"ifnot {cond_result} goto {fim}")
        for instr in bloco_instr:
            self.emitir(instr)
        self.emitir(f"goto {inicio}")
        self.emitir(f"{fim}:")

    def gerar_return(self, expr=None):
        if expr:
            resultado = self.gerar_expressao(expr)
            self.emitir(f"return {resultado}")
        else:
            self.emitir("return")

    # --- Funções auxiliares ---
    def obter_codigo(self):
        return "\n".join(self.codigo)
