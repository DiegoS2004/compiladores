# parser Patito

import ply.yacc as yacc
from patito_lexer import tokens  # noqa: F401
from dir_funciones import dir_func, SemanticError
from generador_cuadruplos import gen

_errors = []
_quiet = False


def set_quiet(value=True):
    global _quiet
    _quiet = value


def get_errors():
    return list(_errors)


def clear_errors():
    _errors.clear()


def _sem_error(msg):
    _errors.append(msg)
    if not _quiet:
        print(f"[Semantico] {msg}")


def _sem_try(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except SemanticError as e:
        _sem_error(str(e))
        return None


def _gen_try(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except ValueError as e:
        _sem_error(str(e))
        return None


def _declarar_vars(nombres, tipo):
    for nombre in nombres:
        _sem_try(dir_func.nueva_variable, nombre, tipo)


def _check_var_uso(nombre):
    if dir_func.buscar_variable(nombre) is None:
        _sem_error(f"Variable '{nombre}' no declarada")


def _check_func_uso(nombre):
    if dir_func.buscar_funcion(nombre) is None:
        _sem_error(f"Funcion '{nombre}' no declarada")


def p_programa(p):
    'programa : programa_header vars funcs INICIO cuerpo FIN'


def p_programa_header(p):
    'programa_header : PROGRAMA ID SEMICOLON'
    _sem_try(dir_func.inicio_programa, p[2])


def p_vars(p):
    '''vars : VARS vars_decl
            | empty'''


def p_vars_decl(p):
    'vars_decl : ID vars_ids COLON tipo SEMICOLON vars_decl_prime'
    _declarar_vars([p[1]] + p[2], p[4])


def p_vars_ids(p):
    '''vars_ids : COMMA ID vars_ids
               | empty'''
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = [p[2]] + p[3]


def p_vars_decl_prime(p):
    '''vars_decl_prime : ID vars_ids COLON tipo SEMICOLON vars_decl_prime
                       | empty'''
    if len(p) == 7:
        _declarar_vars([p[1]] + p[2], p[4])


def p_tipo(p):
    '''tipo : ENTERO
            | FLOTANTE'''
    p[0] = 'entero' if p[1] == 'entero' else 'flotante'


def p_funcs(p):
    '''funcs : func funcs
             | empty'''


def p_func(p):
    'func : func_header params func_params_fin vars cuerpo func_footer'


def p_func_header(p):
    'func_header : tipo_func ID LPAREN'
    _sem_try(dir_func.nueva_funcion, p[2], p[1])


def p_func_params_fin(p):
    'func_params_fin : RPAREN'
    _sem_try(dir_func.marca_inicio_funcion, gen.contador)


def p_func_footer(p):
    'func_footer :'
    _gen_try(gen.endfunc)
    _sem_try(dir_func.fin_funcion)


def p_tipo_func(p):
    '''tipo_func : NULA
                | tipo'''
    p[0] = 'nula' if p[1] == 'nula' else p[1]


def p_params(p):
    '''params : ID COLON tipo params_prime
              | empty'''
    if len(p) == 5:
        _sem_try(dir_func.nuevo_param, p[1], p[3])


def p_params_prime(p):
    '''params_prime : COMMA ID COLON tipo params_prime
                    | empty'''
    if len(p) == 6:
        _sem_try(dir_func.nuevo_param, p[2], p[4])


def p_cuerpo(p):
    'cuerpo : LBRACE estatutos RBRACE'


def p_estatutos(p):
    '''estatutos : estatuto estatutos
                 | empty'''


def p_estatuto(p):
    '''estatuto : ID ASSIGN expresion SEMICOLON
                | call_id LPAREN llamada_args RPAREN SEMICOLON
                | condicion
                | ciclo
                | imprime'''
    if len(p) == 5 and p.slice[2].type == 'ASSIGN':
        _check_var_uso(p[1])
        info = dir_func.buscar_variable(p[1])
        if info:
            _gen_try(gen.asignar, info['direccion'], info['tipo'])
    elif len(p) == 6:
        nombre = p[1]
        func = dir_func.buscar_funcion(nombre)
        if func:
            _gen_try(gen.fin_llamada, nombre, func['num_params'])


def p_call_id(p):
    'call_id : ID'
    _check_func_uso(p[1])
    p[0] = p[1]
    _gen_try(gen.inicio_llamada)


def p_llamada_args(p):
    '''llamada_args : llamada_arg llamada_args_tail
                    | empty'''


def p_llamada_arg(p):
    'llamada_arg : expresion'
    _gen_try(gen.parametro)


def p_llamada_args_tail(p):
    '''llamada_args_tail : COMMA llamada_arg llamada_args_tail
                         | empty'''


def p_condicion(p):
    'condicion : SI LPAREN expresion cond_paren_cierra cuerpo condicion_prime'


def p_cond_paren_cierra(p):
    'cond_paren_cierra : RPAREN'
    _gen_try(gen.condicion_inicio)


def p_condicion_prime(p):
    '''condicion_prime : sino_mark cuerpo
                       | empty'''
    if len(p) == 2:
        _gen_try(gen.condicion_sin_sino)
    else:
        _gen_try(gen.condicion_sino_fin)


def p_sino_mark(p):
    'sino_mark : SINO'
    _gen_try(gen.condicion_sino_inicio)


def p_ciclo_mark(p):
    'ciclo_mark : MIENTRAS LPAREN'
    _gen_try(gen.ciclo_inicio)


def p_ciclo_cond_fin(p):
    'ciclo_cond_fin : RPAREN'
    _gen_try(gen.ciclo_condicion)


def p_ciclo(p):
    'ciclo : ciclo_mark expresion ciclo_cond_fin HAZ cuerpo SEMICOLON'
    _gen_try(gen.ciclo_fin)


def p_imprime(p):
    'imprime : ESCRIBE LPAREN imprime_val imprime_prime RPAREN SEMICOLON'


def p_imprime_val_expr(p):
    'imprime_val : expresion'
    _gen_try(gen.imprimir_operando)


def p_imprime_val_str(p):
    'imprime_val : LETRERO'
    _gen_try(gen.imprimir_letrero, p[1])


def p_imprime_prime(p):
    '''imprime_prime : COMMA imprime_val imprime_prime
                     | empty'''


def p_expresion(p):
    'expresion : exp expresion_prime'


def p_expresion_prime(p):
    '''expresion_prime : op_rel exp
                       | empty'''
    if len(p) == 3:
        _gen_try(gen.procesar_relacional)


def p_op_rel_gt(p):
    'op_rel : GT'
    _gen_try(gen.push_operador, '>')


def p_op_rel_lt(p):
    'op_rel : LT'
    _gen_try(gen.push_operador, '<')


def p_op_rel_ne(p):
    'op_rel : NE'
    _gen_try(gen.push_operador, '!=')


def p_op_rel_eq(p):
    'op_rel : EQ'
    _gen_try(gen.push_operador, '==')


def p_exp(p):
    'exp : termino exp_prime'


def p_exp_prime(p):
    '''exp_prime : op_suma termino exp_prime
                 | op_resta termino exp_prime
                 | empty'''
    if len(p) > 1:
        _gen_try(gen.procesar_aritmetico, 2)


def p_op_suma(p):
    'op_suma : PLUS'
    _gen_try(gen.push_operador, '+')


def p_op_resta(p):
    'op_resta : MINUS'
    _gen_try(gen.push_operador, '-')


def p_termino(p):
    'termino : factor termino_prime'


def p_termino_prime(p):
    '''termino_prime : op_mult factor termino_prime
                     | op_div factor termino_prime
                     | empty'''
    if len(p) > 1:
        _gen_try(gen.procesar_aritmetico, 3)


def p_op_mult(p):
    'op_mult : MULT'
    _gen_try(gen.push_operador, '*')


def p_op_div(p):
    'op_div : DIV'
    _gen_try(gen.push_operador, '/')


def p_factor(p):
    '''factor : MINUS factor_prime
              | PLUS factor_prime
              | factor_prime'''
    if len(p) == 3 and p[1] == 'MINUS':
        _gen_try(gen.aplicar_unario, 'uminus')


def p_factor_prime_id(p):
    'factor_prime : ID'
    _check_var_uso(p[1])
    info = dir_func.buscar_variable(p[1])
    if info:
        _gen_try(gen.push_operando, info['direccion'], info['tipo'])


def p_par_abre(p):
    'par_abre : LPAREN'
    _gen_try(gen.push_parentesis_abre)


def p_par_cierra(p):
    'par_cierra : RPAREN'
    _gen_try(gen.push_parentesis_cierra)


def p_factor_prime_paren(p):
    'factor_prime : par_abre expresion par_cierra'


def p_factor_prime_cte(p):
    'factor_prime : cte'


def p_cte(p):
    '''cte : CTE_ENT
           | CTE_FLOT'''
    if p.slice[1].type == 'CTE_ENT':
        _gen_try(gen.push_constante, p[1], 'entero')
    else:
        _gen_try(gen.push_constante, p[1], 'flotante')


def p_empty(p):
    'empty :'


def p_error(p):
    if p:
        msg = f"Error sintactico: '{p.value}' inesperado (linea {p.lineno}, tipo {p.type})"
    else:
        msg = "Error sintactico: fin de archivo inesperado (programa incompleto)"
    _errors.append(msg)
    print(f"[Parser] {msg}")


parser = yacc.yacc(write_tables=False, debug=False)
