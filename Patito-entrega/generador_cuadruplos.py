# =============================================================================
# GENERADOR DE CUADRUPLOS (codigo intermedio)
# =============================================================================
# Produce la fila de cuadruplos: (operador, arg1, arg2, resultado)
#
# Expresiones — algoritmo con pilas (patron clasico de compiladores):
#   operandos  → direcciones virtuales pendientes (vars, ctes, temps)
#   operadores → +, -, *, /, (, etc.
#   Al encontrar operador de menor precedencia, genera cuadruplo y empuja temporal.
#
# Control de flujo — GOTOF/GOTO con pila_saltos (rellenar destino al cerrar bloque).
# Funciones — PARAM, ERA, GOSUB, RETURN, RETORNO, ENDFUNC.
#
# Singleton global: gen
# =============================================================================

from estructura.stack import Stack
from estructura.queue import Queue
from semantic_cube import check_type, ERROR, ENTERO, FLOTANTE
from direcciones_virtuales import dv
from dir_funciones import dir_func

# Precedencia: * / antes que + - ; relacionales al final
PREC_ARIT = {'*': 3, '/': 3, '+': 2, '-': 2}
PREC_REL = {'>': 1, '<': 1, '!=': 1, '==': 1}


class GeneradorCuadruplos:
    """Construye la fila de cuadruplos mientras el parser recorre el programa."""

    def __init__(self):
        # Pilas para evaluacion de expresiones
        self.operadores = Stack()
        self.operandos = Stack()
        self.tipos = Stack()
        # Fila FIFO del codigo intermedio que ejecutara la VM
        self.cuadruplos = Queue()
        # Indices de saltos pendientes de rellenar (si/sino/mientras)
        self.pila_saltos = Stack()
        self._contador = 0
        self._ciclo_inicio = None
        self._params_llamada = 0
        self._tipos_llamada = []
        self._pila_ctx = Stack()  # respaldo de pilas al evaluar args de llamada

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
        self._pila_ctx.clear()

    def _restaurar_ctx(self):
        if self._pila_ctx.is_empty():
            return
        ops, tips, opers = self._pila_ctx.pop()
        self.operandos.clear()
        self.tipos.clear()
        self.operadores.clear()
        for x in ops:
            self.operandos.push(x)
        for x in tips:
            self.tipos.push(x)
        for x in opers:
            self.operadores.push(x)

    @property
    def contador(self):
        return self._contador

    def _nueva_temporal(self):
        # dentro de funcion: temporales en locales para que ERA los respalde
        if dir_func.scope_actual and dir_func.scope_actual != 'global':
            return dv.local_dir()
        return dv.temporal_dir()

    def _agregar(self, operador, op1, op2, resultado):
        idx = self._contador
        self.cuadruplos.enqueue((operador, op1, op2, resultado))
        self._contador += 1
        return idx  # los saltos guardan este indice para patch despues

    def _precedencia(self, op):
        if op in PREC_ARIT:
            return PREC_ARIT[op]
        if op in PREC_REL:
            return PREC_REL[op]
        return -1

    def _generar_cuadruplo(self):
        op = self.operadores.pop()
        der = self.operandos.pop()   # el ultimo en entrar es el operando derecho
        izq = self.operandos.pop()
        tipo_der = self.tipos.pop()
        tipo_izq = self.tipos.pop()
        res_tipo = check_type(tipo_izq, tipo_der, op)
        if res_tipo == ERROR:
            raise ValueError(
                f"operacion invalida: {tipo_izq} {op} {tipo_der}"
            )
        temp = self._nueva_temporal()
        self._agregar(op, izq, der, temp)
        self.operandos.push(temp)
        self.tipos.push(res_tipo)

    def _vaciar_operadores(self, limite):
        # limite 3=*//, 2=+-, 0=relacionales (vacia todo lo aritmetico)
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
        while not self.operadores.is_empty() and self.operadores.peek() != '(':
            self._generar_cuadruplo()
        if not self.operadores.is_empty():
            self.operadores.pop()

    def push_operando(self, direccion, tipo):
        self.operandos.push(direccion)
        self.tipos.push(tipo)

    def push_constante(self, valor, tipo):
        direccion = dv.constante_dir(valor, tipo)
        self.push_operando(direccion, tipo)

    def procesar_aritmetico(self, limite):
        self._vaciar_operadores(limite)

    def procesar_relacional(self):
        self._vaciar_operadores(0)
        if self.operadores.is_empty():
            return
        self._generar_cuadruplo()

    def terminar_expresion(self):
        self._vaciar_operadores(0)

    def aplicar_unario(self, operador):
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
        # entero cabe en flotante, al reves no
        return tipo_var == FLOTANTE and tipo_val == ENTERO

    @staticmethod
    def _compatible_param(tipo_arg, tipo_param):
        if tipo_arg == tipo_param:
            return True
        return tipo_param == FLOTANTE and tipo_arg == ENTERO

    # --- Asignacion e impresion ---

    def asignar(self, direccion_var, tipo_var):
        """x = expresion ; — vacia pilas y genera (=, valor, _, dir_x)"""
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
        self.terminar_expresion()
        if self.operandos.is_empty():
            return
        op = self.operandos.pop()
        self.tipos.pop()
        self._agregar('PRINT', op, None, None)

    def imprimir_letrero(self, texto):
        self._agregar('PRINT', texto, None, None)

    # --- si / sino (GOTOF + GOTO) ---

    def condicion_inicio(self):
        """Tras si (exp) — genera GOTOF si la condicion es falsa."""
        self.terminar_expresion()
        if self.operandos.is_empty():
            return
        cond = self.operandos.pop()
        self.tipos.pop()
        idx = self._agregar('GOTOF', cond, None, None)
        self.pila_saltos.push(idx)

    def condicion_sin_sino(self):
        if self.pila_saltos.is_empty():
            return
        idx = self.pila_saltos.pop()
        self._rellenar(idx, self._contador)

    def condicion_sino_inicio(self):
        if self.pila_saltos.is_empty():
            return
        idx_falso = self.pila_saltos.pop()
        idx_goto = self._agregar('GOTO', None, None, None)  # brinca el sino al terminar el then
        self._rellenar(idx_falso, self._contador)             # GOTOF ahora cae aqui
        self.pila_saltos.push(idx_goto)

    def condicion_sino_fin(self):
        if self.pila_saltos.is_empty():
            return
        idx = self.pila_saltos.pop()
        self._rellenar(idx, self._contador)

    # --- mientras (GOTOF + GOTO al inicio) ---

    def ciclo_inicio(self):
        """Marca donde regresa el GOTO al final del ciclo."""
        self._ciclo_inicio = self._contador

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
        self._agregar('GOTO', None, None, self._ciclo_inicio)
        if not self.pila_saltos.is_empty():
            idx = self.pila_saltos.pop()
            self._rellenar(idx, self._contador)
        self._ciclo_inicio = None

    # --- Llamadas a funcion (PARAM → ERA → GOSUB → RETORNO) ---

    def inicio_llamada(self):
        """Al ver id ( — guarda pilas de expresion para no mezclar con args."""
        self._params_llamada = 0
        self._tipos_llamada = []
        # no mezclar args de la llamada con la expresion que la contiene
        self._pila_ctx.push((
            self.operandos.to_list(),
            self.tipos.to_list(),
            self.operadores.to_list(),
        ))
        self.operandos.clear()
        self.tipos.clear()
        self.operadores.clear()

    def parametro(self):
        self.terminar_expresion()
        if self.operandos.is_empty():
            return
        arg = self.operandos.pop()
        tipo_arg = self.tipos.pop()
        self._agregar('PARAM', arg, None, None)
        self._params_llamada += 1
        self._tipos_llamada.append(tipo_arg)

    def fin_llamada(self, nombre_func, num_esperados, como_expresion=False):
        """Cierra llamada: valida args, genera ERA+GOSUB, y RETORNO si tiene valor."""
        if self._params_llamada != num_esperados:
            raise ValueError(
                f"funcion '{nombre_func}' espera {num_esperados} "
                f"parametros, recibio {self._params_llamada}"
            )
        func = dir_func.obtener_funcion(nombre_func)
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

        tipo_ret = func.get('tipo', 'nula')
        if como_expresion and tipo_ret == 'nula':
            raise ValueError(
                f"funcion '{nombre_func}' es nula, no puede usarse en expresion"
            )

        self._agregar('ERA', nombre_func, None, None)
        self._agregar('GOSUB', None, None, quad_inicio)

        self._restaurar_ctx()

        if tipo_ret != 'nula':
            if como_expresion:
                temp = self._nueva_temporal()
                self._agregar('RETORNO', None, None, temp)
                self.operandos.push(temp)
                self.tipos.push(tipo_ret)
            else:
                self._agregar('POPRET', None, None, None)

        self._params_llamada = 0
        self._tipos_llamada = []

    def retorna(self, tipo_esperado):
        """retorna expresion ; — genera RETURN con el valor en la pila de operandos."""
        self.terminar_expresion()
        if self.operandos.is_empty():
            return
        valor = self.operandos.pop()
        tipo_val = self.tipos.pop()
        if not self._compatible_asignacion(tipo_val, tipo_esperado):
            raise ValueError(
                f"retorna tipo invalido: {tipo_val}, esperaba {tipo_esperado}"
            )
        self._agregar('RETURN', valor, None, None)

    def endfunc(self):
        """Fin del cuerpo de una funcion (funciones nula o cierre implicito)."""
        self._agregar('ENDFUNC', None, None, None)

    def _rellenar(self, idx, destino):
        # al generar GOTOF/GOTO aun no sabemos el destino; se patcha al cerrar el bloque
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
