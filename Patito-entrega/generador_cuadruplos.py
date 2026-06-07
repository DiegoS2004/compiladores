# =============================================================================
# GENERADOR_CUADRUPLOS.PY — Corazón del compilador (código intermedio)
# =============================================================================
# Traduce expresiones y estatutos a cuádruplos usando el algoritmo de pilas:
#
#   Pilas:
#     operadores  → +, -, *, /, >, <, etc. (con precedencia)
#     operandos   → direcciones virtuales (1000, 5001, 8000...)
#     tipos       → entero/flotante (para el cubo semántico)
#
#   Fila:
#     cuadruplos  → secuencia final que ejecuta la VM
#
# Ejemplo: x = 1 + 2 * 3
#   Genera: (*, 8001, 8002, 5000)  →  (+, 8000, 5000, 5001)  →  (=, 5001, _, 1000)
#
# Para la entrevista: dimensión A (expresiones), B (escribe), C (si/mientras).
# =============================================================================

from stack import Stack
from queue import Queue
from semantic_cube import check_type, ERROR, ENTERO, FLOTANTE
from direcciones_virtuales import dv
from dir_funciones import dir_func

# Precedencia: * / antes que + - ; relacionales al final
PREC_ARIT = {'*': 3, '/': 3, '+': 2, '-': 2}
PREC_REL = {'>': 1, '<': 1, '!=': 1, '==': 1}


class GeneradorCuadruplos:
    def __init__(self):
        # Pilas para evaluar expresiones (algoritmo clásico de compiladores)
        self.operadores = Stack()
        self.operandos = Stack()
        self.tipos = Stack()
        self.cuadruplos = Queue()       # fila de código intermedio
        self.pila_saltos = Stack()      # índices de GOTOF/GOTO pendientes de rellenar
        self._contador = 0              # índice del siguiente cuádruplo
        self._ciclo_inicio = None       # dónde empieza el mientras (para el GOTO al final)
        self._params_llamada = 0          # cuántos args llevamos en una llamada
        self._tipos_llamada = []          # tipos de esos args (validar con params)

    def reset(self):
        self.operadores.clear()
        self.operandos.clear()
        self.tipos.clear()
        self.cuadruplos.clear()
        self.pila_saltos.clear()
        self._contador = 0
        self._ciclo_inicio = None
        self._params_llamada = 0
        self._tipos_llamada = []

    @property
    def contador(self):
        return self._contador

    def _nueva_temporal(self):
        return dv.temporal_dir()

    def _agregar(self, operador, op1, op2, resultado):
        # Cada cuádruplo = (operador, arg1, arg2, resultado) — 4 campos fijos
        idx = self._contador
        self.cuadruplos.enqueue((operador, op1, op2, resultado))
        self._contador += 1
        return idx

    def _precedencia(self, op):
        if op in PREC_ARIT:
            return PREC_ARIT[op]
        if op in PREC_REL:
            return PREC_REL[op]
        return -1

    def _generar_cuadruplo(self):
        # Saca operador y dos operandos, valida tipos con cubo semántico, genera cuádruplo
        op = self.operadores.pop()
        der = self.operandos.pop()
        izq = self.operandos.pop()
        tipo_der = self.tipos.pop()
        tipo_izq = self.tipos.pop()
        res_tipo = check_type(tipo_izq, tipo_der, op)
        if res_tipo == ERROR:
            raise ValueError(
                f"operacion invalida: {tipo_izq} {op} {tipo_der}"
            )
        temp = self._nueva_temporal()  # dirección 5000+ para el resultado
        self._agregar(op, izq, der, temp)
        self.operandos.push(temp)       # el resultado vuelve a la pila de operandos
        self.tipos.push(res_tipo)

    def _vaciar_operadores(self, limite):
        # Genera cuádruplos mientras haya ops con precedencia >= limite
        # limite=2 para +-, limite=3 para */, limite=0 para relacionales
        while not self.operadores.is_empty():
            top = self.operadores.peek()
            if top == '(':
                break
            if self._precedencia(top) < limite:
                break
            self._generar_cuadruplo()

    def push_operador(self, op):
        self.operadores.push(op)

    def push_parentesis_abre(self):
        self.operadores.push('(')

    def push_parentesis_cierra(self):
        # Al cerrar "(", generamos todo lo que quedó adentro hasta el "("
        while not self.operadores.is_empty() and self.operadores.peek() != '(':
            self._generar_cuadruplo()
        if not self.operadores.is_empty():
            self.operadores.pop()  # quitar el '('

    def push_operando(self, direccion, tipo):
        # Variable: metemos su dirección virtual y tipo a las pilas
        self.operandos.push(direccion)
        self.tipos.push(tipo)

    def push_constante(self, valor, tipo):
        # Constante: primero le pedimos dirección al mapa (8000+), luego push
        direccion = dv.constante_dir(valor, tipo)
        self.push_operando(direccion, tipo)

    def procesar_aritmetico(self, limite):
        # Se llama al ver + - * / : vacía ops de mayor o igual precedencia
        self._vaciar_operadores(limite)

    def procesar_relacional(self):
        # Relacionales van al final: vacía TODO y genera un cuádruplo (da 0 o 1)
        self._vaciar_operadores(0)
        if self.operadores.is_empty():
            return
        self._generar_cuadruplo()

    def terminar_expresion(self):
        # Al terminar una expresión (asignación, condición, etc.) vacía lo que quede
        self._vaciar_operadores(0)

    def aplicar_unario(self, operador):
        # Menos unario: -5 → cuádruplo (uminus, dir_5, _, temp)
        if self.operandos.is_empty():
            return
        op = self.operandos.pop()
        tipo = self.tipos.pop()
        temp = self._nueva_temporal()
        self._agregar(operador, op, None, temp)
        self.operandos.push(temp)
        self.tipos.push(tipo)

    @staticmethod
    def _compatible_asignacion(tipo_val, tipo_var):
        if tipo_val == tipo_var:
            return True
        return tipo_var == FLOTANTE and tipo_val == ENTERO

    @staticmethod
    def _compatible_param(tipo_arg, tipo_param):
        if tipo_arg == tipo_param:
            return True
        return tipo_param == FLOTANTE and tipo_arg == ENTERO

    def asignar(self, direccion_var, tipo_var):
        # x = expr  →  (=, dir_resultado, _, dir_x)
        self.terminar_expresion()
        if self.operandos.is_empty():
            return
        valor = self.operandos.pop()
        tipo_val = self.tipos.pop()
        if not self._compatible_asignacion(tipo_val, tipo_var):
            raise ValueError(
                f"asignacion invalida: {tipo_val} a variable tipo {tipo_var}"
            )
        self._agregar('=', valor, None, direccion_var)

    def imprimir_operando(self):
        # escribe(expr)  →  (PRINT, dir_expr, _, _)
        self.terminar_expresion()
        if self.operandos.is_empty():
            return
        op = self.operandos.pop()
        self.tipos.pop()
        self._agregar('PRINT', op, None, None)

    def imprimir_letrero(self, texto):
        # escribe("hola")  →  (PRINT, "hola", _, _)  — el texto va directo en arg1
        self._agregar('PRINT', texto, None, None)

    # ----- SI / SINO (control de flujo con saltos) -----
    # si (cond) { A } sino { B }:
    #   GOTOF cond → salta al sino si cond es falsa
    #   ... código A ...
    #   GOTO → salta al final (saltarse B)
    #   ... código B ...

    def condicion_inicio(self):
        # Justo después de ")" del si: genera GOTOF con destino pendiente
        self.terminar_expresion()
        if self.operandos.is_empty():
            return
        cond = self.operandos.pop()
        self.tipos.pop()
        idx = self._agregar('GOTOF', cond, None, None)  # destino se rellena después
        self.pila_saltos.push(idx)

    def condicion_sin_sino(self):
        # Si no hay sino: rellena el GOTOF para que apunte al final del bloque
        if self.pila_saltos.is_empty():
            return
        idx = self.pila_saltos.pop()
        self._rellenar(idx, self._contador)

    def condicion_sino_inicio(self):
        # Al ver "sino": el GOTOF salta aquí; agregamos GOTO para brincar el sino
        if self.pila_saltos.is_empty():
            return
        idx_falso = self.pila_saltos.pop()
        idx_goto = self._agregar('GOTO', None, None, None)
        self._rellenar(idx_falso, self._contador)  # GOTOF ahora apunta al sino
        self.pila_saltos.push(idx_goto)

    def condicion_sino_fin(self):
        # Fin del bloque sino: rellena el GOTO para saltar al final
        if self.pila_saltos.is_empty():
            return
        idx = self.pila_saltos.pop()
        self._rellenar(idx, self._contador)

    # ----- MIENTRAS (ciclo) -----
    # mientras (cond) haz { cuerpo }:
    #   inicio ← aquí vuelve el GOTO del final
    #   GOTOF cond → sale del ciclo si es falsa
    #   ... cuerpo ...
    #   GOTO inicio

    def ciclo_inicio(self):
        self._ciclo_inicio = self._contador  # marcamos dónde empieza el ciclo

    def ciclo_condicion(self):
        self.terminar_expresion()
        if self.operandos.is_empty():
            return
        cond = self.operandos.pop()
        self.tipos.pop()
        idx = self._agregar('GOTOF', cond, None, None)
        self.pila_saltos.push(idx)

    def ciclo_fin(self):
        if self._ciclo_inicio is None:
            return
        self._agregar('GOTO', None, None, self._ciclo_inicio)  # regresa al inicio
        if not self.pila_saltos.is_empty():
            idx = self.pila_saltos.pop()
            self._rellenar(idx, self._contador)  # GOTOF apunta aquí (salir del ciclo)
        self._ciclo_inicio = None

    # ----- LLAMADAS A FUNCIONES -----
    # suma(x, 5) genera:
    #   PARAM dir_x, PARAM dir_5, ERA suma, GOSUB quad_inicio_suma

    def inicio_llamada(self):
        self._params_llamada = 0
        self._tipos_llamada = []

    def parametro(self):
        # Cada argumento → cuádruplo PARAM con su dirección
        self.terminar_expresion()
        if self.operandos.is_empty():
            return
        arg = self.operandos.pop()
        tipo_arg = self.tipos.pop()
        self._agregar('PARAM', arg, None, None)
        self._params_llamada += 1
        self._tipos_llamada.append(tipo_arg)

    def fin_llamada(self, nombre_func, num_esperados):
        # Valida cantidad y tipos de args, luego ERA + GOSUB
        if self._params_llamada != num_esperados:
            raise ValueError(
                f"funcion '{nombre_func}' espera {num_esperados} "
                f"parametros, recibio {self._params_llamada}"
            )
        func = dir_func.buscar_funcion(nombre_func)
        if func is None:
            raise ValueError(f"funcion '{nombre_func}' no declarada")

        for i, tipo_arg in enumerate(self._tipos_llamada):
            tipo_param = func['params'][i]['tipo']
            if not self._compatible_param(tipo_arg, tipo_param):
                raise ValueError(
                    f"parametro {i + 1} de '{nombre_func}': "
                    f"esperaba {tipo_param}, recibio {tipo_arg}"
                )

        quad_inicio = func.get('quad_inicio')
        if quad_inicio is None:
            raise ValueError(
                f"funcion '{nombre_func}' sin punto de entrada (quad_inicio)"
            )
        self._agregar('ERA', nombre_func, None, None)
        self._agregar('GOSUB', None, None, quad_inicio)
        self._params_llamada = 0
        self._tipos_llamada = []

    def endfunc(self):
        # Al terminar el cuerpo de una función
        self._agregar('ENDFUNC', None, None, None)

    def _rellenar(self, idx, destino):
        # Los saltos (GOTOF/GOTO) se generan sin saber el destino; aquí lo ponemos
        op, a1, a2, _ = self.cuadruplos.to_list()[idx]
        nueva = list(self.cuadruplos.to_list())
        nueva[idx] = (op, a1, a2, destino)
        self.cuadruplos.clear()
        for c in nueva:
            self.cuadruplos.enqueue(c)

    def imprimir_cuadruplos(self):
        sep = "-" * 60
        print("\n" + sep)
        print("  FILA DE CUADRUPLOS")
        print(sep)
        for i, (op, a1, a2, res) in enumerate(self.cuadruplos.to_list()):
            a1s = a1 if a1 is not None else "_"
            a2s = a2 if a2 is not None else "_"
            ress = res if res is not None else "_"
            print(f"  {i:4}  ({op}, {a1s}, {a2s}, {ress})")
        print(sep)


gen = GeneradorCuadruplos()


def reset_gen():
    gen.reset()
