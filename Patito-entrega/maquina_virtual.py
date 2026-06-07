# =============================================================================
# MAQUINA_VIRTUAL.PY — Ejecuta los cuádruplos (interprete)
# =============================================================================
# Recorre la fila de cuádruplos con un IP (instruction pointer).
# Cada cuádruplo le dice qué hacer: sumar, asignar, saltar, llamar función, etc.
#
# Estructuras clave:
#   mem            → MemoriaEjecucion (valores por dirección virtual)
#   pila_retorno   → dónde regresar después de GOSUB
#   parametros[]   → args que van llegando con PARAM (antes del ERA)
#   respaldos      → memoria local guardada en cada ERA
#
# Para la entrevista: dimensión D (funciones) — explica ERA/GOSUB/ENDFUNC/PARAM.
# =============================================================================

from stack import Stack
from memoria_ejecucion import MemoriaEjecucion


class VMError(Exception):
    pass


class MaquinaVirtual:

    def __init__(self, cuadruplos, dir_func, dv):
        self.cuadruplos = cuadruplos
        self.dir_func = dir_func
        self.dv = dv
        self.mem = MemoriaEjecucion()
        self.pila_retorno = Stack()   # para volver despues de GOSUB
        self.parametros = []          # args que van llegando con PARAM
        self.respaldos = Stack()      # memoria local guardada en ERA
        self.salida = []              # lo que imprime escribe

    def _leer(self, direccion):
        if direccion is None:
            return None
        return self.mem.leer(direccion)

    def _escribir(self, direccion, valor):
        self.mem.escribir(direccion, valor)

    def _es_verdadero(self, valor):
        # En Patito: 0 = falso, cualquier otro número = verdadero (para si/mientras)
        return valor != 0

    def _operar(self, op, izq, der, res):
        # Ejecuta + - * / > < == != uminus: lee operandos, escribe resultado en res
        if op == 'uminus':
            self._escribir(res, -self._leer(izq))
            return
        a = self._leer(izq)
        b = self._leer(der)
        tipo_res = self.mem.tipo_de(res)

        if op == '+':
            self._escribir(res, a + b)
        elif op == '-':
            self._escribir(res, a - b)
        elif op == '*':
            self._escribir(res, a * b)
        elif op == '/':
            if tipo_res == 'entero':
                self._escribir(res, int(a // b) if b != 0 else 0)
            else:
                self._escribir(res, a / b if b != 0 else 0.0)
        elif op == '>':
            self._escribir(res, 1 if a > b else 0)
        elif op == '<':
            self._escribir(res, 1 if a < b else 0)
        elif op == '==':
            self._escribir(res, 1 if a == b else 0)
        elif op == '!=':
            self._escribir(res, 1 if a != b else 0)
        else:
            raise VMError(f"operador desconocido: {op}")

    def _era(self, nombre_func):
        # ERA = Activation Record: crea el "contexto" de la función
        # 1. Respalda memoria local (por si había una llamada previa)
        # 2. Copia los args (PARAM) a las direcciones de los parámetros formales
        func = self.dir_func.buscar_funcion(nombre_func)
        if func is None:
            raise VMError(f"funcion '{nombre_func}' no encontrada en ERA")

        dir_params = self.dir_func.direcciones_params(nombre_func)
        dir_locales = self.dir_func.direcciones_locales(nombre_func)

        respaldo = self.mem.respaldar_locales(dir_locales)
        self.respaldos.push((respaldo, dir_locales))

        if len(self.parametros) != len(dir_params):
            raise VMError(
                f"ERA '{nombre_func}': esperaba {len(dir_params)} params, "
                f"recibio {len(self.parametros)}"
            )
        for param_dir, arg_dir in zip(dir_params, self.parametros):
            self._escribir(param_dir, self._leer(arg_dir))
        self.parametros.clear()

    def _endfunc(self):
        # Fin de función: restaura memoria local y salta al IP que guardó GOSUB
        if self.respaldos.is_empty():
            raise VMError("ENDFUNC sin registro de activacion activo")
        respaldo, dir_locales = self.respaldos.pop()
        self.mem.restaurar_locales(respaldo, dir_locales)

        if self.pila_retorno.is_empty():
            raise VMError("ENDFUNC sin direccion de retorno en pila")
        return self.pila_retorno.pop()

    def _inicializar_memoria(self):
        # Antes de ejecutar: cargar constantes, tipos de variables, tipos de temporales
        self.mem.cargar_constantes(self.dv._tabla_const)
        self.mem.cargar_tipos_desde_directorio(self.dir_func)
        # Inferir tipos de temporales según la operación que los generó
        for i in range(len(self.cuadruplos)):
            op, a1, a2, res = self.cuadruplos[i]
            if res is not None and 5000 <= res <= 7999:
                if op in ('+', '-', '*', '/'):
                    t1 = self.mem.tipo_de(a1) if a1 else 'entero'
                    t2 = self.mem.tipo_de(a2) if a2 else 'entero'
                    if t1 == 'flotante' or t2 == 'flotante':
                        self.mem.registrar_tipo(res, 'flotante')
                    else:
                        self.mem.registrar_tipo(res, 'entero')
                elif op in ('>', '<', '==', '!='):
                    self.mem.registrar_tipo(res, 'entero')
                elif op == 'uminus':
                    self.mem.registrar_tipo(res, self.mem.tipo_de(a1))

    def ejecutar(self, ip_inicio=0, debug=False):
        """Loop principal: lee cuádruplo, ejecuta, avanza IP (o salta con GOTO/GOSUB)."""
        self.salida.clear()
        self.pila_retorno.clear()
        self.parametros.clear()
        self.respaldos.clear()
        self.mem.limpiar_temporales()
        self._inicializar_memoria()

        ip = ip_inicio  # instruction pointer — índice en la fila de cuádruplos
        total = len(self.cuadruplos)

        while ip < total:
            op, a1, a2, res = self.cuadruplos[ip]

            if debug:
                print(f"  IP={ip:4}  ({op}, {a1}, {a2}, {res})")

            if op == '=':
                # Asignación: copiar valor de a1 a la dirección res
                self._escribir(res, self._leer(a1))

            elif op in ('+', '-', '*', '/', '>', '<', '==', '!=', 'uminus'):
                self._operar(op, a1, a2, res)

            elif op == 'PRINT':
                # escribe() — imprime letrero (str) o valor numérico
                if isinstance(a1, str):
                    self.salida.append(a1)
                    print(a1, end='')
                else:
                    val = self._leer(a1)
                    self.salida.append(val)
                    print(val, end='')

            elif op == 'GOTOF':
                # Salto condicional: si la condición es falsa (0), brinca a res
                if not self._es_verdadero(self._leer(a1)):
                    ip = res
                    continue
            elif op == 'GOTO':
                # Salto incondicional
                ip = res
                continue

            elif op == 'PARAM':
                # Encola la dirección del argumento; ERA los usará después
                self.parametros.append(a1)
            elif op == 'ERA':
                self._era(a1)
            elif op == 'GOSUB':
                # Llamada: guarda IP+1 para regresar, salta al inicio de la función
                self.pila_retorno.push(ip + 1)
                ip = res
                continue
            elif op == 'ENDFUNC':
                ip = self._endfunc()
                continue

            else:
                raise VMError(f"opcode desconocido: {op}")

            ip += 1  # cuádruplo normal: avanzar al siguiente

        return self.salida
