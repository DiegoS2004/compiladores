# directorio de funciones y tablas de variables

from direcciones_virtuales import dv


class SemanticError(Exception):
    pass


class TablaVariables:

    def __init__(self):
        self._tabla = {}  # nombre -> tipo y direccion

    def agregar(self, nombre, tipo, direccion):
        if nombre in self._tabla:
            raise SemanticError(
                f"Variable '{nombre}' ya fue declarada en este scope"
            )
        self._tabla[nombre] = {'tipo': tipo, 'direccion': direccion}

    def buscar(self, nombre):
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

    def __init__(self):
        self._dir = {}
        self._scope_stack = []  # scope actual: global o nombre de funcion
        self.nombre_programa = None

    @property
    def scope_actual(self):
        return self._scope_stack[-1] if self._scope_stack else None

    def inicio_programa(self, nombre):
        if self._scope_stack:
            raise SemanticError("Programa ya iniciado")
        self.nombre_programa = nombre
        self._dir['global'] = {
            'tipo': 'programa',
            'params': [],
            'num_params': 0,
            'quad_inicio': None,
            'tabla_vars': TablaVariables(),
        }
        self._scope_stack.append('global')

    def nueva_funcion(self, nombre, tipo):
        if nombre in self._dir:
            raise SemanticError(f"Funcion '{nombre}' ya fue declarada")
        if nombre == 'global':
            raise SemanticError("Nombre de funcion reservado")
        self._dir[nombre] = {
            'tipo': tipo,
            'params': [],
            'num_params': 0,
            'quad_inicio': None,
            'tabla_vars': TablaVariables(),
        }
        self._scope_stack.append(nombre)

    def fin_funcion(self):
        if not self._scope_stack:
            raise SemanticError("fin_funcion sin scope activo")
        self._scope_stack.pop()

    def marca_inicio_funcion(self, quad_idx):
        scope = self.scope_actual
        if scope and scope != 'global' and scope in self._dir:
            self._dir[scope]['quad_inicio'] = quad_idx

    def marca_inicio_main(self, quad_idx):
        if 'global' in self._dir:
            self._dir['global']['quad_inicio'] = quad_idx

    def buscar_funcion(self, nombre):
        return self._dir.get(nombre)

    def _asignar_direccion(self, tipo_scope):
        if tipo_scope == 'global':
            return dv.global_dir()
        return dv.local_dir()

    def nueva_variable(self, nombre, tipo):
        scope = self.scope_actual
        if scope is None or scope not in self._dir:
            raise SemanticError("No hay scope activo")
        direccion = self._asignar_direccion(scope)
        self._dir[scope]['tabla_vars'].agregar(nombre, tipo, direccion)

    def nuevo_param(self, nombre, tipo):
        scope = self.scope_actual
        if scope is None or scope == 'global':
            raise SemanticError("No hay funcion activa para agregar parametro")
        func = self._dir[scope]
        func['params'].append({'nombre': nombre, 'tipo': tipo})
        func['num_params'] += 1
        self.nueva_variable(nombre, tipo)

    def buscar_variable(self, nombre):
        scope = self.scope_actual
        if scope and scope in self._dir:
            v = self._dir[scope]['tabla_vars'].buscar(nombre)
            if v:
                return v
        if 'global' in self._dir:
            return self._dir['global']['tabla_vars'].buscar(nombre)
        return None

    def direcciones_params(self, nombre_func):
        func = self.buscar_funcion(nombre_func)
        if func is None:
            return []
        addrs = []
        for p in func['params']:
            info = func['tabla_vars'].buscar(p['nombre'])
            if info:
                addrs.append(info['direccion'])
        return addrs

    def direcciones_locales(self, nombre_func):
        func = self.buscar_funcion(nombre_func)
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
        for fname, fdata in self._dir.items():
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


dir_func = DirectorioFunciones()


def reset_dir():
    dir_func._dir.clear()
    dir_func._scope_stack.clear()
    dir_func.nombre_programa = None
