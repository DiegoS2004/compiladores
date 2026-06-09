# =============================================================================
# FASE 1 — LEXER (analisis lexico)
# =============================================================================
# Convierte el texto del .patito en una secuencia de tokens.
# Ejemplo:  "x = 1 + 2;"  →  ID(x) ASSIGN CTE_ENT(1) PLUS CTE_ENT(2) SEMICOLON
#
# El parser (patito_parser.py) consume esos tokens; el lexer no valida tipos ni
# genera cuadruplos, solo reconoce palabras, numeros, operadores y simbolos.
# =============================================================================

import ply.lex as lex

# Palabras reservadas del lenguaje → tipo de token en mayusculas
reserved = {
    'programa': 'PROGRAMA',
    'inicio':   'INICIO',
    'fin':      'FIN',
    'vars':     'VARS',
    'entero':   'ENTERO',
    'flotante': 'FLOTANTE',
    'si':       'SI',
    'sino':     'SINO',
    'mientras': 'MIENTRAS',
    'haz':      'HAZ',
    'escribe':  'ESCRIBE',
    'nula':     'NULA',
    'retorna':  'RETORNA',
}

# Lista completa de tipos de token que PLY puede devolver
tokens = list(reserved.values()) + [
    'ID', 'CTE_ENT', 'CTE_FLOT', 'LETRERO',
    'PLUS', 'MINUS', 'MULT', 'DIV',
    'ASSIGN', 'LT', 'GT', 'NE', 'EQ',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
    'SEMICOLON', 'COMMA', 'COLON',
]

t_PLUS      = r'\+'
t_MINUS     = r'-'
t_MULT      = r'\*'
t_DIV       = r'/'
t_LT        = r'<'
t_GT        = r'>'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'
t_SEMICOLON = r';'
t_COMMA     = r','
t_COLON     = r':'

# != y == van antes que = (si no, == se parte en = =)

def t_NE(t):
    r'!='
    return t

def t_EQ(t):
    r'=='
    return t

def t_ASSIGN(t):
    r'='
    return t

# flotante antes que entero (si no, 3.14 se lee como 3)

def t_CTE_FLOT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_CTE_ENT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_LETRERO(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t\r'

_lex_errors = []  # caracteres ilegales encontrados durante el tokenizado

def get_lex_errors():
    return list(_lex_errors)

def clear_lex_errors():
    _lex_errors.clear()

def t_error(t):
    msg = f"Caracter ilegal '{t.value[0]}' en linea {t.lexer.lineno}"
    _lex_errors.append(msg)
    print(f"[Lexico] {msg}")
    t.lexer.skip(1)

# Instancia global del lexer; patito_parser hace lexer.clone() por compilacion
lexer = lex.lex()
