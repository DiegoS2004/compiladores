# memoria de ejecucion, guarda valores usando direcciones virtuales

from direcciones_virtuales import (
    GLOB_INI, GLOB_FIN,
    LOCAL_INI, LOCAL_FIN,
    TEMP_INI, TEMP_FIN,
    CONST_INI, CONST_FIN,
)


class MemoriaEjecucion:
    # 4 segmentos: global, local, temporal, constante

    def __init__(self):
        self._global = {}       # vars del programa
        self._local = {}        # vars y params de funciones
        self._temporal = {}     # resultados de expresiones
        self._constantes = {}   # solo lectura
        self._tipos = {}        # dir -> entero o flotante

    @staticmethod
    def segmento(direccion):
        # dice en que segmento cae una direccion
        if GLOB_INI <= direccion <= GLOB_FIN:
            return 'global'
        if LOCAL_INI <= direccion <= LOCAL_FIN:
            return 'local'
        if TEMP_INI <= direccion <= TEMP_FIN:
            return 'temporal'
        if CONST_INI <= direccion <= CONST_FIN:
            return 'constante'
        raise ValueError(f"direccion fuera de rango: {direccion}")

    def _tabla(self, direccion):
        seg = self.segmento(direccion)
        if seg == 'global':
            return self._global
        if seg == 'local':
            return self._local
        if seg == 'temporal':
            return self._temporal
        return self._constantes

    def leer(self, direccion):
        tabla = self._tabla(direccion)
        return tabla.get(direccion, 0)

    def escribir(self, direccion, valor):
        if self.segmento(direccion) == 'constante':
            raise ValueError(
                f"no se puede escribir en constante (dir {direccion})"
            )
        self._tabla(direccion)[direccion] = valor

    def tipo_de(self, direccion):
        return self._tipos.get(direccion, 'entero')

    def registrar_tipo(self, direccion, tipo):
        self._tipos[direccion] = tipo

    def cargar_constantes(self, tabla_const):
        for (valor, tipo), direccion in tabla_const.items():
            self._constantes[direccion] = valor
            self._tipos[direccion] = tipo

    def cargar_tipos_desde_directorio(self, dir_func):
        for _fname, fdata in dir_func._dir.items():
            for _nombre, info in fdata['tabla_vars'].items():
                self.registrar_tipo(info['direccion'], info['tipo'])

    def respaldar_locales(self, direcciones):
        # guarda valores antes de entrar a una funcion
        return {d: self._local[d] for d in direcciones if d in self._local}

    def restaurar_locales(self, respaldo, direcciones_funcion):
        # restaura al salir de la funcion
        for d in direcciones_funcion:
            if d in respaldo:
                self._local[d] = respaldo[d]
            elif d in self._local:
                del self._local[d]

    def limpiar_temporales(self):
        self._temporal.clear()

    def imprimir_estado(self):
        sep = "-" * 52
        print("\n" + sep)
        print("  ESTADO DE MEMORIA DE EJECUCION")
        print(sep)
        for nombre, tabla in [
            ("Globales", self._global),
            ("Locales", self._local),
            ("Temporales", self._temporal),
            ("Constantes", self._constantes),
        ]:
            if tabla:
                print(f"  {nombre}:")
                for d in sorted(tabla):
                    t = self._tipos.get(d, '?')
                    print(f"      {d:<6}  {tabla[d]!r}  ({t})")
        print(sep)
