# direcciones virtuales, asigna un numero a cada variable y constante

GLOB_INI = 1000
GLOB_FIN = 1999
LOCAL_INI = 2000
LOCAL_FIN = 4999
TEMP_INI = 5000
TEMP_FIN = 7999
CONST_INI = 8000
CONST_FIN = 9999


class DireccionesVirtuales:

    def __init__(self):
        self._glob = GLOB_INI
        self._local = LOCAL_INI
        self._temp = TEMP_INI
        self._const = CONST_INI
        self._tabla_const = {}

    def reset(self):
        self._glob = GLOB_INI
        self._local = LOCAL_INI
        self._temp = TEMP_INI
        self._const = CONST_INI
        self._tabla_const.clear()

    def _siguiente(self, contador, fin, segmento):
        if contador > fin:
            raise ValueError(f"se agotaron direcciones del segmento {segmento}")
        d = contador
        return d, contador + 1

    def global_dir(self):
        d, self._glob = self._siguiente(self._glob, GLOB_FIN, "global")
        return d

    def local_dir(self):
        d, self._local = self._siguiente(self._local, LOCAL_FIN, "local")
        return d

    def temporal_dir(self):
        d, self._temp = self._siguiente(self._temp, TEMP_FIN, "temporal")
        return d

    def constante_dir(self, valor, tipo):
        clave = (valor, tipo)
        if clave not in self._tabla_const:
            d, self._const = self._siguiente(self._const, CONST_FIN, "constante")
            self._tabla_const[clave] = d
        return self._tabla_const[clave]

    def imprimir_mapa(self):
        sep = "-" * 52
        print("\n" + sep)
        print("  MAPA DE DIRECCIONES VIRTUALES")
        print(sep)
        print(f"  Globales   : {GLOB_INI} - {GLOB_FIN}")
        print(f"  Locales    : {LOCAL_INI} - {LOCAL_FIN}")
        print(f"  Temporales : {TEMP_INI} - {TEMP_FIN}")
        print(f"  Constantes : {CONST_INI} - {CONST_FIN}")
        print(f"  Siguiente global   : {self._glob}")
        print(f"  Siguiente local    : {self._local}")
        print(f"  Siguiente temporal : {self._temp}")
        print(f"  Siguiente constante: {self._const}")
        if self._tabla_const:
            print("  Tabla de constantes:")
            for (val, tipo), d in sorted(self._tabla_const.items(), key=lambda x: x[1]):
                print(f"      {d:<6}  {val!r}  ({tipo})")
        print(sep)


dv = DireccionesVirtuales()


def reset_dv():
    dv.reset()
