# main del compilador Patito

import sys
from patito_lexer import lexer, clear_lex_errors, get_lex_errors
from patito_parser import parser, clear_errors, get_errors, set_quiet
from dir_funciones import reset_dir, dir_func
from generador_cuadruplos import gen, reset_gen
from direcciones_virtuales import dv, reset_dv


def compile_string(
    source: str,
    label: str = "input",
    show_dir: bool = False,
    show_quad: bool = False,
    show_dv: bool = False,
    quiet: bool = False,
) -> bool:
    clear_errors()
    clear_lex_errors()
    reset_dir()
    reset_gen()
    reset_dv()
    set_quiet(quiet)
    lex_clone = lexer.clone()
    lex_clone.lineno = 1
    parser.parse(source, lexer=lex_clone)
    set_quiet(False)
    all_errors = get_lex_errors() + get_errors()
    if all_errors:
        if not quiet:
            print(f"  [FAIL] {label}: {len(all_errors)} error(s)")
            for e in all_errors:
                print(f"         {e}")
        return False
    if not quiet:
        print(f"  [OK]   {label}")
    if show_dir:
        dir_func.imprimir()
    if show_quad:
        gen.imprimir_cuadruplos()
    if show_dv:
        dv.imprimir_mapa()
    return True


def compile_file(
    filepath: str,
    show_dir: bool = False,
    show_quad: bool = False,
    show_dv: bool = False,
) -> bool:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"[Error] Archivo no encontrado: {filepath}")
        return False
    print(f"\nCompilando: {filepath}")
    print("=" * 50)
    return compile_string(
        source, filepath, show_dir=show_dir, show_quad=show_quad, show_dv=show_dv
    )


def lex_file(filepath: str) -> bool:
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


def run_quad_tests() -> bool:
    cases = [
        "hola.patito",
        "prueba_aritmetica.patito",
        "prueba_relacional.patito",
        "prueba_si.patito",
        "prueba_mientras.patito",
        "prueba_funciones.patito",
    ]
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    print("\n--- Cuadruplos de programas de prueba ---\n")
    ok_all = True
    for name in cases:
        path = os.path.join(base, name)
        if not os.path.isfile(path):
            print(f"  [SKIP] {name} (no existe)")
            continue
        if not compile_file(path, show_quad=True):
            ok_all = False
    print("\n" + ("Cuadruplos OK." if ok_all else "Hubo fallos."))
    return ok_all


def run_tests(show_dir: bool = False) -> bool:
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
        if not compile_string(src, label, show_dir=False):
            ok_all = False
    print("\n" + ("Todos OK." if ok_all else "Hubo fallos."))
    return ok_all


def run_semantic_tests() -> bool:
    must_fail = [
        ("doble var global", "programa t;\nvars\n  x : entero;\n  x : flotante;\ninicio\n{\n}\nfin\n"),
        ("doble funcion", "programa t;\nnula f()\n{\n}\nnula f()\n{\n}\ninicio\n{\n}\nfin\n"),
        ("param duplicado", "programa t;\nnula f( a : entero, a : entero )\n{\n}\ninicio\n{\n}\nfin\n"),
        ("var no declarada", "programa t;\ninicio\n{\n  y = 1;\n}\nfin\n"),
        ("func no declarada", "programa t;\ninicio\n{\n  f();\n}\nfin\n"),
    ]
    print("\n--- Tests semanticos ---\n")
    ok_all = True
    for label, src in must_fail:
        if compile_string(src, label, quiet=True):
            print(f"  [FAIL] {label}: no se detecto error semantico")
            ok_all = False
        else:
            err = get_errors()[-1] if get_errors() else "?"
            print(f"  [OK]   {label} -> {err}")
    print("\n" + ("Tests semanticos OK." if ok_all else "Hubo fallos en tests semanticos."))
    return ok_all


if __name__ == '__main__':
    argv = sys.argv[1:]
    if not argv:
        print("Uso:")
        print("  python patito.py <archivo.patito>")
        print("  python patito.py --dir <archivo.patito>")
        print("  python patito.py --quad <archivo.patito>")
        print("  python patito.py --dv <archivo.patito>")
        print("  python patito.py --test-quad")
        print("  python patito.py --test")
        print("  python patito.py --test-semantic")
        print("  python patito.py --lex <archivo.patito>")
        sys.exit(1)
    if argv[0] == '--test':
        sys.exit(0 if run_tests() else 1)
    if argv[0] == '--test-quad':
        sys.exit(0 if run_quad_tests() else 1)
    if argv[0] == '--test-semantic':
        sys.exit(0 if run_semantic_tests() else 1)
    if argv[0] == '--lex':
        if len(argv) < 2:
            print("Uso: python patito.py --lex <archivo.patito>")
            sys.exit(1)
        sys.exit(0 if lex_file(argv[1]) else 1)
    if argv[0] == '--dir':
        if len(argv) < 2:
            print("Uso: python patito.py --dir <archivo.patito>")
            sys.exit(1)
        sys.exit(0 if compile_file(argv[1], show_dir=True) else 1)
    if argv[0] == '--quad':
        if len(argv) < 2:
            print("Uso: python patito.py --quad <archivo.patito>")
            sys.exit(1)
        sys.exit(0 if compile_file(argv[1], show_quad=True) else 1)
    if argv[0] == '--dv':
        if len(argv) < 2:
            print("Uso: python patito.py --dv <archivo.patito>")
            sys.exit(1)
        sys.exit(0 if compile_file(argv[1], show_dv=True) else 1)
    ok = compile_file(argv[0])
    sys.exit(0 if ok else 1)
