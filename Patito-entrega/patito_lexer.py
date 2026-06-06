# lexer de patito, convierte el codigo fuente en tokens

import ply.lex as lex

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
}

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

# != y == van antes que =

def t_NE(t):
    r'!='
    return t

def t_EQ(t):
    r'=='
    return t

def t_ASSIGN(t):
    r'='
    return t

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

_lex_errors = []

def get_lex_errors():
    return list(_lex_errors)

def clear_lex_errors():
    _lex_errors.clear()

def t_error(t):
    msg = f"Caracter ilegal '{t.value[0]}' en linea {t.lexer.lineno}"
    _lex_errors.append(msg)
    print(f"[Lexico] {msg}")
    t.lexer.skip(1)

lexer = lex.lex()
