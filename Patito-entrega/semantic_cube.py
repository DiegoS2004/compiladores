# =============================================================================
# SEMANTIC_CUBE.PY — Cubo semántico de tipos
# =============================================================================
# Antes de generar un cuádruplo aritmético/relacional, preguntamos:
#   "¿entero + flotante tiene sentido? ¿y qué tipo da?"
#
# Estructura: cubo[tipo_izq][tipo_der][operador] → tipo_resultado
# Si no existe la combinación → ERROR (ej. sumar entero con letrero)
#
# Para la entrevista: esto evita errores de tipos en TIEMPO DE COMPILACIÓN.
# =============================================================================

ENTERO = 'entero'
FLOTANTE = 'flotante'
ERROR = 'error'

# Reglas: int+int=int, int+float=float, comparaciones siempre dan entero (0 o 1)
_cube = {
    ENTERO: {
        ENTERO: {
            '+': ENTERO, '-': ENTERO, '*': ENTERO, '/': ENTERO,
            '>': ENTERO, '<': ENTERO, '!=': ENTERO, '==': ENTERO,
        },
        FLOTANTE: {
            '+': FLOTANTE, '-': FLOTANTE, '*': FLOTANTE, '/': FLOTANTE,
            '>': ENTERO, '<': ENTERO, '!=': ENTERO, '==': ENTERO,
        },
    },
    FLOTANTE: {
        ENTERO: {
            '+': FLOTANTE, '-': FLOTANTE, '*': FLOTANTE, '/': FLOTANTE,
            '>': ENTERO, '<': ENTERO, '!=': ENTERO, '==': ENTERO,
        },
        FLOTANTE: {
            '+': FLOTANTE, '-': FLOTANTE, '*': FLOTANTE, '/': FLOTANTE,
            '>': ENTERO, '<': ENTERO, '!=': ENTERO, '==': ENTERO,
        },
    },
}


def check_type(tipo1, tipo2, operador):
    """Devuelve el tipo resultante o 'error' si la operación no es válida."""
    try:
        return _cube[tipo1][tipo2][operador]
    except KeyError:
        return ERROR
