# =============================================================================
# PATITO — PUNTO DE ENTRADA
# =============================================================================
# Orquesta las 3 fases del compilador:
#
#   1. Lexer   (patito_lexer)     → texto a tokens
#   2. Parser  (patito_parser)    → tokens a cuadruplos + tablas
#   3. VM      (maquina_virtual)   → ejecuta cuadruplos
#
# Uso:
#   python patito.py --run hola.patito
#   python patito.py --run prueba_funciones.patito
#
# Si el .patito no esta en el directorio actual, busca en testcases/
# =============================================================================

import os
import sys

from patito_parser import compilar_fuente
from dir_funciones import dir_func
from generador_cuadruplos import gen
from direcciones_virtuales import dv
from maquina_virtual import MaquinaVirtual, VMError

# Rutas base para resolver archivos .patito
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TESTCASES_DIR = os.path.join(BASE_DIR, 'testcases')


def resolve_filepath(filepath: str) -> str:
    """Busca el archivo: ruta dada → testcases/ por nombre."""
    if os.path.isfile(filepath):
        return os.path.abspath(filepath)
    en_testcases = os.path.join(TESTCASES_DIR, os.path.basename(filepath))
    if os.path.isfile(en_testcases):
        return en_testcases
    return filepath


def compilar(source: str) -> bool:
    """Lexer + parser. Al terminar, dir_func, gen y dv tienen el resultado."""
    errores = compilar_fuente(source)
    if errores:
        print("Errores de compilacion:")
        for e in errores:
            print(f"  {e}")
        return False
    return True


def ejecutar(source: str):
    """
    Compila y corre el programa en la máquina virtual.
    La VM imprime directamente lo que el programa escribe con 'escribe'.
    """
    if not compilar(source):
        raise VMError("compilacion fallida")

    cuadruplos = gen.cuadruplos.to_list()
    vm = MaquinaVirtual(cuadruplos, dir_func, dv)

    # El bloque 'inicio' no siempre es el cuádruplo 0:
    # las funciones declaradas arriba generan cuádruplos primero
    main = dir_func.obtener_funcion('global')
    ip_inicio = main.get('quad_inicio', 0) if main else 0

    return vm.ejecutar(ip_inicio=ip_inicio)


def ejecutar_archivo(filepath: str) -> bool:
    """Lee un .patito del disco, compila y ejecuta."""
    filepath = resolve_filepath(filepath)
    try:
        with open(filepath, encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Archivo no encontrado: {filepath}")
        return False

    try:
        ejecutar(source)
        print()  # salto de línea después de la salida de escribe
        return True
    except VMError as e:
        print(f"Error: {e}")
        return False


if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] != '--run':
        print("Uso: python patito.py --run <archivo.patito>")
        print("     python patito.py --run hola.patito")
        sys.exit(1)

    sys.exit(0 if ejecutar_archivo(sys.argv[2]) else 1)
