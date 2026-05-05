# ================================================================
# patito_parser.py  –  Analizador Sintáctico para Patito
# TC3002B – Compiladores  |  Etapa 1
#
# Gramática en notación de Diego (primes):
#   VARS_IDS, VARS_DECL', EXP', TERMINO', FACTOR', etc.
# En PLY los primes se escriben como _prime / _double_prime
# porque los nombres de función son identificadores Python.
# ================================================================

import ply.yacc as yacc
from patito_lexer import tokens  # noqa: F401

# Lista de errores (se limpia en cada parseo)
_errors = []

def get_errors():
    return list(_errors)

def clear_errors():
    _errors.clear()

# ────────────────────────────────────────────────────────────────
# PROGRAMA
# PROGRAMA → programa id ; VARS FUNCS inicio CUERPO fin
# ────────────────────────────────────────────────────────────────
def p_programa(p):
    'programa : PROGRAMA ID SEMICOLON vars funcs INICIO cuerpo FIN'
    pass

# ────────────────────────────────────────────────────────────────
# VARS Definición
# VARS → vars VARS_DECL | ε
# ────────────────────────────────────────────────────────────────
def p_vars(p):
    '''vars : VARS vars_decl
            | empty'''
    pass

def p_vars_decl(p):
    'vars_decl : ID vars_ids COLON tipo SEMICOLON vars_decl_prime'
    pass

# VARS_IDS Definición
# VARS_IDS → , id VARS_IDS | ε
def p_vars_ids(p):
    '''vars_ids : COMMA ID vars_ids
               | empty'''
    pass

# VARS_DECL' Definición
# VARS_DECL' → id VARS_IDS : TIPO ; VARS_DECL' | ε
def p_vars_decl_prime(p):
    '''vars_decl_prime : ID vars_ids COLON tipo SEMICOLON vars_decl_prime
                       | empty'''
    pass

# ────────────────────────────────────────────────────────────────
# TIPO Definición
# TIPO → entero | flotante
# ────────────────────────────────────────────────────────────────
def p_tipo(p):
    '''tipo : ENTERO
            | FLOTANTE'''
    pass

# ────────────────────────────────────────────────────────────────
# FUNCS Definición
# FUNCS → FUNC FUNCS | ε
# ────────────────────────────────────────────────────────────────
def p_funcs(p):
    '''funcs : func funcs
             | empty'''
    pass

def p_func(p):
    'func : tipo_func ID LPAREN params RPAREN vars cuerpo'
    pass

def p_tipo_func(p):
    '''tipo_func : NULA
                | tipo'''
    pass

# PARAMS Definición
# PARAMS → id : TIPO PARAMS' | ε
def p_params(p):
    '''params : ID COLON tipo params_prime
              | empty'''
    pass

# PARAMS' Definición
# PARAMS' → , id : TIPO PARAMS' | ε
def p_params_prime(p):
    '''params_prime : COMMA ID COLON tipo params_prime
                    | empty'''
    pass

# ────────────────────────────────────────────────────────────────
# CUERPO Definición
# CUERPO → { ESTATUTOS }
# ────────────────────────────────────────────────────────────────
def p_cuerpo(p):
    'cuerpo : LBRACE estatutos RBRACE'
    pass

def p_estatutos(p):
    '''estatutos : estatuto estatutos
                 | empty'''
    pass

# ────────────────────────────────────────────────────────────────
# ESTATUTO Definición  (con FCI para id)
# ESTATUTO  → id ESTATUTO' | CONDICION | CICLO | IMPRIME
# ESTATUTO' → = EXPRESION ;  |  ( LLAMADA' ) ;
# ────────────────────────────────────────────────────────────────
def p_estatuto(p):
    '''estatuto : ID estatuto_prime
                | condicion
                | ciclo
                | imprime'''
    pass

def p_estatuto_prime(p):
    '''estatuto_prime : ASSIGN expresion SEMICOLON
                      | LPAREN llamada_prime RPAREN SEMICOLON'''
    pass

# ────────────────────────────────────────────────────────────────
# CONDICION Definición
# CONDICION  → si ( EXPRESION ) CUERPO CONDICION'
# CONDICION' → sino CUERPO | ε
# ────────────────────────────────────────────────────────────────
def p_condicion(p):
    'condicion : SI LPAREN expresion RPAREN cuerpo condicion_prime'
    pass

def p_condicion_prime(p):
    '''condicion_prime : SINO cuerpo
                       | empty'''
    pass

# ────────────────────────────────────────────────────────────────
# CICLO Definición
# CICLO → mientras ( EXPRESION ) haz CUERPO ;
# ────────────────────────────────────────────────────────────────
def p_ciclo(p):
    'ciclo : MIENTRAS LPAREN expresion RPAREN HAZ cuerpo SEMICOLON'
    pass

# ────────────────────────────────────────────────────────────────
# IMPRIME Definición
# IMPRIME → escribe ( IMPRIME_VAL IMPRIME' ) ;
# ────────────────────────────────────────────────────────────────
def p_imprime(p):
    'imprime : ESCRIBE LPAREN imprime_val imprime_prime RPAREN SEMICOLON'
    pass

def p_imprime_val(p):
    '''imprime_val : expresion
                   | LETRERO'''
    pass

# IMPRIME' Definición
# IMPRIME' → , IMPRIME_VAL IMPRIME' | ε
def p_imprime_prime(p):
    '''imprime_prime : COMMA imprime_val imprime_prime
                     | empty'''
    pass

# ────────────────────────────────────────────────────────────────
# EXPRESION Definición
# EXPRESION  → EXP EXPRESION'
# EXPRESION' → > EXP | < EXP | != EXP | == EXP | ε
# ────────────────────────────────────────────────────────────────
def p_expresion(p):
    'expresion : exp expresion_prime'
    pass

def p_expresion_prime(p):
    '''expresion_prime : GT exp
                       | LT exp
                       | NE exp
                       | EQ exp
                       | empty'''
    pass

# ────────────────────────────────────────────────────────────────
# EXP Definición
# EXP  → TERMINO EXP'
# EXP' → + TERMINO EXP' | - TERMINO EXP' | ε
# ────────────────────────────────────────────────────────────────
def p_exp(p):
    'exp : termino exp_prime'
    pass

def p_exp_prime(p):
    '''exp_prime : PLUS termino exp_prime
                 | MINUS termino exp_prime
                 | empty'''
    pass

# ────────────────────────────────────────────────────────────────
# TERMINO Definición
# TERMINO  → FACTOR TERMINO'
# TERMINO' → * FACTOR TERMINO' | / FACTOR TERMINO' | ε
# ────────────────────────────────────────────────────────────────
def p_termino(p):
    'termino : factor termino_prime'
    pass

def p_termino_prime(p):
    '''termino_prime : MULT factor termino_prime
                     | DIV factor termino_prime
                     | empty'''
    pass

# ────────────────────────────────────────────────────────────────
# FACTOR Definición
# FACTOR  → + FACTOR' | - FACTOR' | FACTOR'
# FACTOR' → ( EXPRESION ) | id | CTE
# ────────────────────────────────────────────────────────────────
def p_factor(p):
    '''factor : PLUS factor_prime
              | MINUS factor_prime
              | factor_prime'''
    pass

def p_factor_prime(p):
    '''factor_prime : LPAREN expresion RPAREN
                    | ID
                    | cte'''
    pass

# ────────────────────────────────────────────────────────────────
# CTE Definición
# CTE → cte_ent | cte_flot
# ────────────────────────────────────────────────────────────────
def p_cte(p):
    '''cte : CTE_ENT
           | CTE_FLOT'''
    pass

# ────────────────────────────────────────────────────────────────
# LLAMADA Definición  (vive dentro de estatuto_prime)
# LLAMADA'  → EXPRESION LLAMADA'' | ε
# LLAMADA'' → , EXPRESION LLAMADA'' | ε
# ────────────────────────────────────────────────────────────────
def p_llamada_prime(p):
    '''llamada_prime : expresion llamada_double_prime
                     | empty'''
    pass

def p_llamada_double_prime(p):
    '''llamada_double_prime : COMMA expresion llamada_double_prime
                            | empty'''
    pass

# ────────────────────────────────────────────────────────────────
# EMPTY
# ────────────────────────────────────────────────────────────────
def p_empty(p):
    'empty :'
    pass

# ────────────────────────────────────────────────────────────────
# ERROR
# ────────────────────────────────────────────────────────────────
def p_error(p):
    if p:
        msg = f"Error sintactico: '{p.value}' inesperado (linea {p.lineno}, tipo {p.type})"
    else:
        msg = "Error sintactico: fin de archivo inesperado (programa incompleto)"
    _errors.append(msg)
    print(f"[Parser] {msg}")

# ── Build ────────────────────────────────────────────────────────
parser = yacc.yacc(write_tables=False, debug=False)
