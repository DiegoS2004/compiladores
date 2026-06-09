# =============================================================================
# MEMORIA DE EJECUCION
# =============================================================================
# Almacena valores en tiempo de ejecucion, indexados por direccion virtual.
#
# Segmentos fijos (fuera de funciones):
#   _global     → vars del programa (1000+)
#   _temporal   → temps del main (5000+)
#   _constantes → literales (8000+, solo lectura)
#
# Segmento local (dentro de funciones):
#   ActivationRecord en _pila_ra → params, locales y temps de cada invocacion
#
# La VM decide donde leer/escribir segun el rango del entero (ver segmento()).
# =============================================================================

from direcciones_virtuales import (
    GLOB_INI, GLOB_FIN,
    LOCAL_INI, LOCAL_FIN,
    TEMP_INI, TEMP_FIN,
    CONST_INI, CONST_FIN,
)
from estructura.stack import Stack


class ActivationRecord:
    """Registro de activacion (RA): memoria local de una invocacion de funcion."""

    def __init__(self, nombre_func):
        self.nombre = nombre_func
        self.locales = {}  # direccion virtual -> valor

    def leer(self, direccion):
        return self.locales.get(direccion, 0)

    def escribir(self, direccion, valor):
        self.locales[direccion] = valor


class MemoriaEjecucion:
    """Memoria runtime del programa Patito."""

    def __init__(self):
        self._global = {}
        self._temporal = {}
        self._constantes = {}
        self._tipos = {}
        self._pila_ra = Stack()  # pila de registros de activacion

    @property
    def ra_actual(self):
        if self._pila_ra.is_empty():
            return None
        return self._pila_ra.peek()

    @staticmethod
    def segmento(direccion):
        if GLOB_INI <= direccion <= GLOB_FIN:
            return 'global'
        if LOCAL_INI <= direccion <= LOCAL_FIN:
            return 'local'
        if TEMP_INI <= direccion <= TEMP_FIN:
            return 'temporal'
        if CONST_INI <= direccion <= CONST_FIN:
            return 'constante'
        raise ValueError(f"direccion fuera de rango: {direccion}")

    def _tabla_fija(self, direccion):
        seg = self.segmento(direccion)
        if seg == 'global':
            return self._global
        if seg == 'temporal':
            return self._temporal
        return self._constantes

    def leer(self, direccion):
        """Lee valor; direcciones locales van al RA activo (tope de pila_ra)."""
        if self.segmento(direccion) == 'local':
            ra = self.ra_actual
            if ra is None:
                return 0
            return ra.leer(direccion)
        return self._tabla_fija(direccion).get(direccion, 0)

    def escribir(self, direccion, valor):
        if self.segmento(direccion) == 'constante':
            raise ValueError(
                f"no se puede escribir en constante (dir {direccion})"
            )
        if self.segmento(direccion) == 'local':
            ra = self.ra_actual
            if ra is None:
                raise ValueError(f"escritura local sin RA activo (dir {direccion})")
            ra.escribir(direccion, valor)
            return
        self._tabla_fija(direccion)[direccion] = valor

    def tipo_de(self, direccion):
        return self._tipos.get(direccion, 'entero')

    def registrar_tipo(self, direccion, tipo):
        self._tipos[direccion] = tipo

    def cargar_constantes(self, tabla_const):
        for (valor, tipo), direccion in tabla_const.items():
            self._constantes[direccion] = valor
            self._tipos[direccion] = tipo

    def cargar_tipos_desde_directorio(self, dir_func):
        for _fname, fdata in dir_func._funciones.items():
            for _nombre, info in fdata['tabla_vars'].items():
                self.registrar_tipo(info['direccion'], info['tipo'])

    def entrar_funcion(self, nombre_func, params):
        """ERA: crea un RA nuevo y carga parametros."""
        ra = ActivationRecord(nombre_func)
        for direccion, valor in params:
            ra.escribir(direccion, valor)
        self._pila_ra.push(ra)

    def salir_funcion(self):
        """ENDFUNC / RETURN: destruye el RA activo."""
        if self._pila_ra.is_empty():
            raise ValueError("salir_funcion sin RA activo")
        self._pila_ra.pop()

    def limpiar_temporales(self):
        self._temporal.clear()

    def limpiar_ra(self):
        self._pila_ra.clear()

    def imprimir_estado(self):
        sep = "-" * 52
        print("\n" + sep)
        print("  ESTADO DE MEMORIA DE EJECUCION")
        print(sep)
        for nombre, tabla in [
            ("Globales", self._global),
            ("Temporales", self._temporal),
            ("Constantes", self._constantes),
        ]:
            if tabla:
                print(f"  {nombre}:")
                for d in sorted(tabla):
                    t = self._tipos.get(d, '?')
                    print(f"      {d:<6}  {tabla[d]!r}  ({t})")
        if not self._pila_ra.is_empty():
            print("  Registros de activacion (pila):")
            for i, ra in enumerate(self._pila_ra.to_list()):
                print(f"    [{i}] {ra.nombre}:")
                for d in sorted(ra.locales):
                    t = self._tipos.get(d, '?')
                    print(f"        {d:<6}  {ra.locales[d]!r}  ({t})")
        print(sep)
