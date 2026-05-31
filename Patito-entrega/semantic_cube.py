ENTERO = 'entero'
FLOTANTE = 'flotante'
ERROR = 'error'

# cubo[tipo1][tipo2][op] -> tipo resultado
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
