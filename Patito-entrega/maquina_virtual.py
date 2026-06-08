# maquina virtual — ejecuta cuadruplos con registros de activacion (RA)

from estructura.stack import Stack
from memoria_ejecucion import MemoriaEjecucion


class VMError(Exception):
    pass


class MaquinaVirtual:

    def __init__(self, cuadruplos, dir_func, dv):
        self.cuadruplos = cuadruplos
        self.dir_func = dir_func
        self.dv = dv
        self.mem = MemoriaEjecucion()
        self.pila_retorno = Stack()          # direcciones de retorno (GOSUB)
        self.pila_retorno_valores = Stack()  # valores de funciones con retorno
        self.parametros = []
        self.salida = []

    def _leer(self, direccion):
        if direccion is None:
            return None
        return self.mem.leer(direccion)

    def _escribir(self, direccion, valor):
        self.mem.escribir(direccion, valor)

    def _es_verdadero(self, valor):
        return valor != 0

    def _operar(self, op, izq, der, res):
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
        func = self.dir_func.buscar_funcion(nombre_func)
        if func is None:
            raise VMError(f"funcion '{nombre_func}' no encontrada en ERA")

        dir_params = self.dir_func.direcciones_params(nombre_func)
        if len(self.parametros) != len(dir_params):
            raise VMError(
                f"ERA '{nombre_func}': esperaba {len(dir_params)} params, "
                f"recibio {len(self.parametros)}"
            )

        # leer args del RA activo (caller) antes de crear el nuevo RA
        valores = [self._leer(arg) for arg in self.parametros]
        self.parametros.clear()

        params = list(zip(dir_params, valores))
        self.mem.entrar_funcion(nombre_func, params)

    def _endfunc(self):
        self.mem.salir_funcion()
        if self.pila_retorno.is_empty():
            raise VMError("ENDFUNC sin direccion de retorno en pila")
        return self.pila_retorno.pop()

    def _inicializar_memoria(self):
        self.mem.cargar_constantes(self.dv._tabla_const)
        self.mem.cargar_tipos_desde_directorio(self.dir_func)
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
        self.salida.clear()
        self.pila_retorno.clear()
        self.pila_retorno_valores.clear()
        self.parametros.clear()
        self.mem.limpiar_ra()
        self.mem.limpiar_temporales()
        self._inicializar_memoria()

        ip = ip_inicio
        total = len(self.cuadruplos)

        while ip < total:
            op, a1, a2, res = self.cuadruplos[ip]

            if debug:
                ra = self.mem.ra_actual
                ra_txt = ra.nombre if ra else "global"
                print(f"  IP={ip:4}  ({op}, {a1}, {a2}, {res})  RA={ra_txt}")

            if op == '=':
                self._escribir(res, self._leer(a1))

            elif op in ('+', '-', '*', '/', '>', '<', '==', '!=', 'uminus'):
                self._operar(op, a1, a2, res)

            elif op == 'PRINT':
                if isinstance(a1, str):
                    self.salida.append(a1)
                    print(a1, end='')
                else:
                    val = self._leer(a1)
                    self.salida.append(val)
                    print(val, end='')

            elif op == 'GOTOF':
                if not self._es_verdadero(self._leer(a1)):
                    ip = res
                    continue
            elif op == 'GOTO':
                ip = res
                continue

            elif op == 'PARAM':
                self.parametros.append(a1)
            elif op == 'ERA':
                self._era(a1)
            elif op == 'GOSUB':
                self.pila_retorno.push(ip + 1)
                ip = res
                continue
            elif op == 'RETURN':
                self.pila_retorno_valores.push(self._leer(a1))
                ip = self._endfunc()
                continue
            elif op == 'RETORNO':
                if self.pila_retorno_valores.is_empty():
                    raise VMError("RETORNO sin valor en pila de retorno")
                self._escribir(res, self.pila_retorno_valores.pop())
            elif op == 'POPRET':
                if self.pila_retorno_valores.is_empty():
                    raise VMError("POPRET sin valor de retorno en pila")
                self.pila_retorno_valores.pop()
            elif op == 'ENDFUNC':
                ip = self._endfunc()
                continue

            else:
                raise VMError(f"opcode desconocido: {op}")

            ip += 1

        return self.salida
