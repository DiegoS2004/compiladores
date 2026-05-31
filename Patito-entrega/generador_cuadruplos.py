# generador de cuadruplos

from stack import Stack
from queue import Queue
from semantic_cube import check_type, ERROR, ENTERO, FLOTANTE
from direcciones_virtuales import dv
from dir_funciones import dir_func

PREC_ARIT = {'*': 3, '/': 3, '+': 2, '-': 2}
PREC_REL = {'>': 1, '<': 1, '!=': 1, '==': 1}


class GeneradorCuadruplos:
    def __init__(self):
        self.operadores = Stack()
        self.operandos = Stack()
        self.tipos = Stack()
        self.cuadruplos = Queue()
        self.pila_saltos = Stack()
        self._contador = 0
        self._ciclo_inicio = None
        self._params_llamada = 0

    def reset(self):
        self.operadores.clear()
        self.operandos.clear()
        self.tipos.clear()
        self.cuadruplos.clear()
        self.pila_saltos.clear()
        self._contador = 0
        self._ciclo_inicio = None
        self._params_llamada = 0

    @property
    def contador(self):
        return self._contador

    def _nueva_temporal(self):
        return dv.temporal_dir()

    def _agregar(self, operador, op1, op2, resultado):
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
        temp = self._nueva_temporal()
        self._agregar(op, izq, der, temp)
        self.operandos.push(temp)
        self.tipos.push(res_tipo)

    def _vaciar_operadores(self, limite):
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
        return tipo_var == FLOTANTE and tipo_val == ENTERO

    def asignar(self, direccion_var, tipo_var):
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

    def condicion_inicio(self):
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
        idx_goto = self._agregar('GOTO', None, None, None)
        self._rellenar(idx_falso, self._contador)
        self.pila_saltos.push(idx_goto)

    def condicion_sino_fin(self):
        if self.pila_saltos.is_empty():
            return
        idx = self.pila_saltos.pop()
        self._rellenar(idx, self._contador)

    def ciclo_inicio(self):
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

    def inicio_llamada(self):
        self._params_llamada = 0

    def parametro(self):
        self.terminar_expresion()
        if self.operandos.is_empty():
            return
        arg = self.operandos.pop()
        self.tipos.pop()
        self._agregar('PARAM', arg, None, None)
        self._params_llamada += 1

    def fin_llamada(self, nombre_func, num_esperados):
        if self._params_llamada != num_esperados:
            raise ValueError(
                f"funcion '{nombre_func}' espera {num_esperados} "
                f"parametros, recibio {self._params_llamada}"
            )
        func = dir_func.buscar_funcion(nombre_func)
        if func is None:
            raise ValueError(f"funcion '{nombre_func}' no declarada")
        quad_inicio = func.get('quad_inicio')
        if quad_inicio is None:
            raise ValueError(
                f"funcion '{nombre_func}' sin punto de entrada (quad_inicio)"
            )
        self._agregar('ERA', nombre_func, None, None)
        self._agregar('GOSUB', None, None, quad_inicio)
        self._params_llamada = 0

    def endfunc(self):
        self._agregar('ENDFUNC', None, None, None)

    def _rellenar(self, idx, destino):
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
