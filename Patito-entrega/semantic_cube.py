# cubo semantico — valida tipos en operaciones (tipo1, tipo2, op) -> tipo_resultado

ENTERO = 'entero'
FLOTANTE = 'flotante'
ERROR = 'error'

# comparaciones siempre producen entero (0/1), aunque los operandos sean flotante
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
    try:
        return _cube[tipo1][tipo2][operador]
    except KeyError:
        return ERROR
