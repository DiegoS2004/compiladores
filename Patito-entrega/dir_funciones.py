# =============================================================================
# TABLA DE SIMBOLOS (directorio de funciones)
# =============================================================================
# Guarda todo lo que el programa declara: variables, funciones, tipos y
# direcciones virtuales. El parser lo llena; la VM lo consulta en ERA/GOSUB.
#
# Quien llama cada metodo (desde patito_parser.py):
#   registrar_programa        →  programa id ;
#   declarar_variable         →  vars x : entero;
#   registrar_funcion         →  entero suma (
#   declarar_parametro        →  a : entero
#   marcar_inicio_codigo_*    →  ) o inicio
#   resolver_variable         →  uso de x en expresiones
#   obtener_funcion           →  llamadas a suma(...)
#
# Singleton global: dir_func
# =============================================================================

from direcciones_virtuales import dv


class SemanticError(Exception):
    pass


class TablaVariables:
    """Variables de un solo scope (global o una funcion)."""

    def __init__(self):
        self._tabla = {}  # nombre -> {tipo, direccion}

    def registrar(self, nombre, tipo, direccion):
        """Agrega una variable nueva al scope. Falla si el nombre ya existe."""
        if nombre in self._tabla:
            raise SemanticError(
                f"Variable '{nombre}' ya fue declarada en este scope"
            )
        self._tabla[nombre] = {'tipo': tipo, 'direccion': direccion}

    def obtener(self, nombre):
        """Devuelve {tipo, direccion} o None si no esta declarada."""
        return self._tabla.get(nombre)

    def existe(self, nombre):
        return nombre in self._tabla

    def items(self):
        return self._tabla.items()

    def __repr__(self):
        if not self._tabla:
            return "      (vacia)"
        lines = [
            f"      {n:<16} {v['tipo']:<10} dir={v['direccion']}"
            for n, v in self._tabla.items()
        ]
        return "\n".join(lines)


class DirectorioFunciones:
    """
    Directorio completo del programa compilado.

    Guarda por cada funcion:
      - tipo de retorno (nula / entero / flotante)
      - lista de parametros
      - quad_inicio (primer cuadruplo ejecutable)
      - tabla de variables de ese scope
    """

    def __init__(self):
        self._funciones = {}       # nombre -> info de la funcion
        self._pila_scopes = []     # tope = scope donde estamos parseando
        self.nombre_programa = None

    @property
    def scope_actual(self):
        """'global' dentro del programa, o el nombre de la funcion activa."""
        return self._pila_scopes[-1] if self._pila_scopes else None

    # --- registro del programa y funciones (lo llama patito_parser) ---

    def registrar_programa(self, nombre):
        """Punto neurálgico: programa id ;"""
        if self._pila_scopes:
            raise SemanticError("Programa ya iniciado")
        self.nombre_programa = nombre
        self._funciones['global'] = {
            'tipo': 'programa',
            'params': [],
            'num_params': 0,
            'quad_inicio': None,
            'tabla_vars': TablaVariables(),
        }
        self._pila_scopes.append('global')

    def registrar_funcion(self, nombre, tipo_retorno):
        """Punto neurálgico: tipo_func id ( — entra al scope de la funcion."""
        if nombre in self._funciones:
            raise SemanticError(f"Funcion '{nombre}' ya fue declarada")
        if nombre == 'global':
            raise SemanticError("Nombre de funcion reservado")
        self._funciones[nombre] = {
            'tipo': tipo_retorno,
            'params': [],
            'num_params': 0,
            'quad_inicio': None,
            'tabla_vars': TablaVariables(),
        }
        self._pila_scopes.append(nombre)

    def cerrar_scope_funcion(self):
        """Punto neurálgico: al terminar el cuerpo de una funcion."""
        if not self._pila_scopes:
            raise SemanticError("cerrar_scope_funcion sin scope activo")
        self._pila_scopes.pop()

    def marcar_inicio_codigo_funcion(self, indice_quad):
        """Punto neurálgico: ) despues de params — aqui empieza el codigo de la funcion."""
        scope = self.scope_actual
        if scope and scope != 'global' and scope in self._funciones:
            self._funciones[scope]['quad_inicio'] = indice_quad

    def marcar_inicio_codigo_main(self, indice_quad):
        """Punto neurálgico: token inicio — aqui empieza el bloque principal."""
        if 'global' in self._funciones:
            self._funciones['global']['quad_inicio'] = indice_quad

    # --- variables y parametros ---

    def _pedir_direccion_virtual(self, scope):
        """Global usa rango 1000+, locales/params de funcion usan 2000+."""
        if scope == 'global':
            return dv.global_dir()
        return dv.local_dir()

    def declarar_variable(self, nombre, tipo):
        """
        Registra una variable en el scope actual.
        Lo llama el parser al ver: vars x, y : entero;
        """
        scope = self.scope_actual
        if scope is None or scope not in self._funciones:
            raise SemanticError("No hay scope activo")
        direccion = self._pedir_direccion_virtual(scope)
        self._funciones[scope]['tabla_vars'].registrar(nombre, tipo, direccion)

    def declarar_parametro(self, nombre, tipo):
        """
        Registra un parametro de funcion.
        Un parametro es una variable local con direccion propia.
        """
        scope = self.scope_actual
        if scope is None or scope == 'global':
            raise SemanticError("No hay funcion activa para declarar parametro")
        func = self._funciones[scope]
        func['params'].append({'nombre': nombre, 'tipo': tipo})
        func['num_params'] += 1
        self.declarar_variable(nombre, tipo)

    # --- consultas (parser y VM) ---

    def obtener_funcion(self, nombre):
        """Busca info de 'global', 'suma', etc."""
        return self._funciones.get(nombre)

    def resolver_variable(self, nombre):
        """
        Busca una variable primero en el scope actual;
        si no esta, busca en globales (visibles dentro de funciones).
        """
        scope = self.scope_actual
        if scope and scope in self._funciones:
            var = self._funciones[scope]['tabla_vars'].obtener(nombre)
            if var:
                return var
        if 'global' in self._funciones:
            return self._funciones['global']['tabla_vars'].obtener(nombre)
        return None

    def dirs_parametros_de(self, nombre_func):
        """Direcciones virtuales de los params, en orden, para el cuadruplo ERA."""
        func = self.obtener_funcion(nombre_func)
        if func is None:
            return []
        dirs = []
        for param in func['params']:
            info = func['tabla_vars'].obtener(param['nombre'])
            if info:
                dirs.append(info['direccion'])
        return dirs

    def dirs_locales_de(self, nombre_func):
        """Todas las direcciones locales declaradas de una funcion."""
        func = self.obtener_funcion(nombre_func)
        if func is None:
            return []
        return [
            info['direccion']
            for _, info in func['tabla_vars'].items()
        ]

    def imprimir(self):
        sep = "-" * 52
        print("\n" + sep)
        print("  DIRECTORIO DE FUNCIONES")
        print(sep)
        if self.nombre_programa:
            print(f"  programa: {self.nombre_programa}")
        for fname, fdata in self._funciones.items():
            plist = ", ".join(
                f"{p['nombre']}:{p['tipo']}" for p in fdata['params']
            ) or "--"
            qini = fdata['quad_inicio']
            qtxt = str(qini) if qini is not None else "--"
            print(
                f"  [{fname}]  tipo={fdata['tipo']}  "
                f"params=({plist})  quad_inicio={qtxt}"
            )
            print("    Variables:")
            print(fdata['tabla_vars'])
        print(sep)


# Singleton global — se reinicia en cada compilacion
dir_func = DirectorioFunciones()


def reiniciar_directorio():
    """Limpia el directorio entre corridas de patito.py."""
    dir_func._funciones.clear()
    dir_func._pila_scopes.clear()
    dir_func.nombre_programa = None


# Alias del nombre anterior por si algo externo aun lo usa
reset_dir = reiniciar_directorio
