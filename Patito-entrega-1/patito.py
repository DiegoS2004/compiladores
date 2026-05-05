# ================================================================
# patito.py  –  Entry point del Compilador Patito
# TC3002B – Compiladores  |  Etapa 1 
# ================================================================

import sys
from patito_lexer import lexer, clear_lex_errors, get_lex_errors
from patito_parser import parser, clear_errors, get_errors


def compile_string(source: str, label: str = "input") -> bool:
    """
    Compila un string de código Patito.
    Retorna True si no hay errores léxicos ni sintácticos.
    """
    clear_errors()
    clear_lex_errors()
    lex_clone = lexer.clone()
    lex_clone.lineno = 1
    parser.parse(source, lexer=lex_clone)
    all_errors = get_lex_errors() + get_errors()
    if all_errors:
        print(f"  [FAIL] {label}: {len(all_errors)} error(s)")
        for e in all_errors:
            print(f"         {e}")
        return False
    else:
        print(f"  [OK]   {label}")
        return True


def compile_file(filepath: str) -> bool:
    """Lee un archivo .patito y lo compila."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"[Error] Archivo no encontrado: {filepath}")
        return False
    print(f"\nCompilando: {filepath}")
    print("=" * 50)
    return compile_string(source, filepath)


def lex_file(filepath: str) -> bool:
    """Solo tokeniza un archivo (sin parsear)."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"[Error] Archivo no encontrado: {filepath}")
        return False
    clear_lex_errors()
    lex_clone = lexer.clone()
    lex_clone.lineno = 1
    lex_clone.input(source)
    print(f"Tokens: {filepath}\n" + "=" * 50)
    while True:
        tok = lex_clone.token()
        if tok is None:
            break
        print(f"  {tok.type:12} {tok.value!r}  (linea {tok.lineno})")
    errs = get_lex_errors()
    if errs:
        for e in errs:
            print(f"  [lex] {e}")
        return False
    return True


def run_tests() -> bool:
    """Casos mínimos de regresión (lexer + parser)."""
    cases = [
        ("prog vacio (sin vars)", "programa t01;\ninicio\n{\n}\nfin\n"),
        ("una var entero", "programa t02;\nvars\n  a : entero;\ninicio\n{\n}\nfin\n"),
        ("dos vars", "programa t03;\nvars\n  a, b : entero;\ninicio\n{\n}\nfin\n"),
        ("var flotante", "programa t04;\nvars\n  x : flotante;\ninicio\n{\n}\nfin\n"),
        ("asigna cte", "programa t05;\nvars\n  x : entero;\ninicio\n{\n  x = 0;\n}\nfin\n"),
        ("asigna expr aritmetica", "programa t06;\nvars\n  x : entero;\ninicio\n{\n  x = 1 + 2 * 3;\n}\nfin\n"),
        ("si", "programa t07;\nvars\n  x : entero;\ninicio\n{\n  si (x < 1) {\n  }\n}\nfin\n"),
        ("si sino", "programa t08;\nvars\n  x : entero;\ninicio\n{\n  si (x == 0) {\n  } sino {\n  }\n}\nfin\n"),
        ("mientras", "programa t09;\nvars\n  x : entero;\ninicio\n{\n  mientras (x > 0) haz {\n  };\n}\nfin\n"),
        ("escribe letrero", "programa t10;\ninicio\n{\n  escribe(\"hola\");\n}\nfin\n"),
        ("escribe mixto", "programa t11;\nvars\n  x : entero;\ninicio\n{\n  escribe(\"v\", x);\n}\nfin\n"),
        ("comparacion ==", "programa t12;\nvars\n  x : entero;\ninicio\n{\n  si (x == 1) {\n  }\n}\nfin\n"),
        ("comparacion !=", "programa t13;\nvars\n  x : entero;\ninicio\n{\n  si (x != 0) {\n  }\n}\nfin\n"),
        ("menos unario", "programa t14;\nvars\n  x : entero;\ninicio\n{\n  x = -5;\n}\nfin\n"),
        ("parentesis", "programa t15;\nvars\n  x : entero;\ninicio\n{\n  x = (1 + 2);\n}\nfin\n"),
        ("funcion nula sin params", "programa t16;\nnula f()\n{\n}\ninicio\n{\n}\nfin\n"),
        ("funcion con param", "programa t17;\nnula g( a : entero )\n{\n}\ninicio\n{\n}\nfin\n"),
        ("funcion dos params", "programa t18;\nnula h( a : entero, b : flotante )\n{\n}\ninicio\n{\n}\nfin\n"),
        ("llamada procedimiento", "programa t19;\nnula f()\n{\n}\ninicio\n{\n  f();\n}\nfin\n"),
        ("dos declaraciones vars", "programa t20;\nvars\n  a : entero;\n  b : flotante;\ninicio\n{\n}\nfin\n"),
        ("varias sentencias", "programa t21;\nvars\n  x : entero;\ninicio\n{\n  x = 1;\n  x = 2;\n}\nfin\n"),
        ("flotante en expr", "programa t22;\nvars\n  x : flotante;\ninicio\n{\n  x = 3.14;\n}\nfin\n"),
    ]
    print("\n--- Tests Patito (%d casos) ---\n" % len(cases))
    ok_all = True
    for label, src in cases:
        if not compile_string(src, label):
            ok_all = False
    print("\n" + ("Todos OK." if ok_all else "Hubo fallos."))
    return ok_all


if __name__ == '__main__':
    argv = sys.argv[1:]
    if not argv:
        print("Uso:")
        print("  python patito.py <archivo.patito>")
        print("  python patito.py --test")
        print("  python patito.py --lex <archivo.patito>")
        sys.exit(1)
    if argv[0] == '--test':
        sys.exit(0 if run_tests() else 1)
    if argv[0] == '--lex':
        if len(argv) < 2:
            print("Uso: python patito.py --lex <archivo.patito>")
            sys.exit(1)
        sys.exit(0 if lex_file(argv[1]) else 1)
    ok = compile_file(argv[0])
    sys.exit(0 if ok else 1)