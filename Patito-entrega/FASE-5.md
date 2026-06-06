Entrega 5 - Maquina Virtual y Memoria de Ejecucion

Para esta etapa partí del resultado de las fases 1, 2, 3 y 4 y cerré el ciclo del compilador en tres frentes principales: diseñé el mapa de Memoria de Ejecucion para almacenar valores en tiempo de ejecucion usando las direcciones virtuales que ya generaba el compilador, implementé una Maquina Virtual que interpreta todos los opcodes de la fila de cuadruplos, y completé la ejecucion en runtime de declaracion e invocacion de funciones (PARAM, ERA, GOSUB, ENDFUNC) con respaldo y restauracion de memoria local.


Memoria de Ejecucion

Diseñé la estructura MemoriaEjecucion en el modulo memoria_ejecucion.py. La memoria se divide en cuatro segmentos, cada uno respaldado por un diccionario interno donde la clave es la direccion virtual y el valor es el contenido en runtime. Las globales viven en 1000-1999 y corresponden a las variables del bloque vars del programa principal. Las locales ocupan 2000-4999 y contienen los parametros y variables de cada funcion. Los temporales van en 5000-7999, y las constantes numericas en 8000-9999 en modo solo lectura.

La razon de reutilizar los mismos rangos que en compilacion es que los cuadruplos ya traen enteros listos para indexar memoria. En lugar de buscar variables por nombre en runtime, la VM recibe una direccion, determina su segmento con segmento(direccion), y delega a leer() o escribir() sobre el diccionario correcto. Por ejemplo, la direccion 1000 cae en global y se accede como _global[1000]; la 2000 cae en local como _local[2000]; la 5000 en temporal; y la 8000 en constantes.

Los metodos principales de acceso son segmento(direccion) para clasificar, leer(direccion) para obtener un valor (devuelve 0 si no existe), escribir(direccion, valor) para guardar (rechaza escritura en constantes), cargar_constantes(tabla) para inicializar el segmento de constantes desde la tabla del compilador, y cargar_tipos_desde_directorio(dir_func) para registrar si cada direccion es entero o flotante. Para funciones agregue respaldar_locales(direcciones) y restaurar_locales(respaldo, direcciones), que guardan y recuperan el estado de las variables locales al entrar y salir de una llamada.


Como las direcciones virtuales indexan la estructura

En compilacion, cada variable, temporal y constante recibe un entero unico. En ejecucion, ese entero funciona como indice directo dentro del segmento correspondiente. El flujo es: cuadruplo trae direccion → segmento() decide el diccionario → leer/escribir accede al valor. Asi el compilador y la VM se comunican sin tablas de simbolos en runtime; solo necesitan la fila de cuadruplos, el directorio de funciones (para ERA y tipos) y la tabla de constantes.

Como ejemplo, el cuadruplo (=, 8000, _, 1000) en ejecucion hace mem.leer(8000) para obtener el valor 5 de la constante, y mem.escribir(1000, 5) para guardarlo en la variable global x. Un cuadruplo (+, 1000, 8001, 5000) lee ambos operandos, suma, y escribe el resultado en la direccion temporal 5000.


Maquina Virtual

Implementé la clase MaquinaVirtual en maquina_virtual.py. Recibe la lista de cuadruplos, el directorio de funciones y el mapa de direcciones virtuales del compilador. Ademas de MemoriaEjecucion, usa tres estructuras auxiliares: pila_retorno (Stack) guarda la direccion de retorno despues de cada GOSUB; parametros (lista) acumula las direcciones de argumentos que van llegando con cada PARAM; y respaldos (Stack) almacena copias de memoria local creadas en ERA para restaurarlas en ENDFUNC.

El ciclo de ejecucion recorre cuadruplos con un puntero de instruccion ip. Por cada opcode, la VM lee operandos de memoria, ejecuta la operacion, y escribe el resultado en la direccion indicada. Los opcodes soportados son:

+ - * / uminus para aritmetica
> < == != para relacional (resultado 0 o 1)
= para asignacion
PRINT para escribe (acepta letrero literal o direccion)
GOTOF y GOTO para si/sino y mientras
PARAM ERA GOSUB ENDFUNC para funciones

Para GOTOF, si el valor leido en la direccion de condicion es 0, se salta al cuadruplo indicado en resultado; en Patito 0 es falso y cualquier otro valor es verdadero. Para GOTO se salta incondicionalmente.


Ejecucion de funciones en runtime

En compilacion ya se generaban PARAM, ERA, GOSUB y ENDFUNC. Lo que agregue en esta etapa es la semantica de ejecucion. Cuando la VM encuentra PARAM, encola la direccion del argumento evaluado. Cuando encuentra ERA(nombre), consulta el directorio para obtener las direcciones de parametros y locales de esa funcion, respalda los valores locales que existian, y copia cada argumento encolado a la direccion del parametro formal correspondiente. Cuando encuentra GOSUB(quad_inicio), guarda ip+1 en pila_retorno y salta al inicio de la funcion. Cuando encuentra ENDFUNC, restaura el respaldo de memoria local, hace pop de pila_retorno, y continua en el cuadruplo que llamo a la funcion.

Tambien completé la validacion de tipos de parametros en fin_llamada: ademas de comparar cantidad, ahora se verifica que el tipo de cada argumento sea compatible con la firma (entero puede pasar a flotante, pero no al reves). Agregue en dir_funciones.py los metodos direcciones_params(nombre) y direcciones_locales(nombre), que la VM usa en ERA.

Ejemplo de prueba_funciones.patito con nula suma(a, b) y suma(x, 5). Los cuadruplos son los mismos de la entrega 4; la diferencia es que ahora se ejecutan:

0  (+, 2001, 2000, 5000)    cuerpo de suma: a + b
1  (=, 5000, _, 2002)        r = resultado
2  (PRINT, suma, _, _)
3  (PRINT, 2002, _, _)
4  (ENDFUNC, _, _, _)
5  (=, 8000, _, 1000)         main: x = 10
6  (PARAM, 1000, _, _)       argumento x
7  (PARAM, 8001, _, _)       argumento 5
8  (ERA, suma, _, _)
9  (GOSUB, _, _, 0)           salto al inicio de suma

Al ejecutar con --run, la salida impresa es: suma15


Integracion en patito.py

Agregue la funcion run_vm(source) que compila en silencio y pasa la fila de cuadruplos a MaquinaVirtual.ejecutar(). La bandera --run compila y ejecuta un archivo .patito mostrando la salida de escribe. La bandera --test-vm corre seis casos automaticos que verifican escribe, aritmetica, si/sino, mientras y llamadas a funciones con y sin parametros.


Archivos modificados o agregados

memoria_ejecucion.py es nuevo y contiene MemoriaEjecucion con los cuatro segmentos, los metodos de acceso y el respaldo de locales. maquina_virtual.py es nuevo y contiene el interprete de cuadruplos con todas las estructuras auxiliares. dir_funciones.py se modifico para agregar direcciones_params y direcciones_locales. generador_cuadruplos.py se modifico para validar tipos de parametros en fin_llamada. patito.py recibio run_vm, run_vm_file, run_vm_tests y la bandera --run. Cree prueba_vm.patito como programa de prueba adicional que combina aritmetica, funcion y escribe.


Plan de pruebas

| ID | Descripcion | Comando | Resultado |
|----|-------------|---------|-----------|
| TC-VM-01 | Asignacion y escribe en runtime | `--run hola.patito` | PASS |
| TC-VM-02 | Expresion aritmetica con temporales | `--test-vm` (caso aritmetica) | PASS |
| TC-VM-03 | Condicional si/sino | `--test-vm` (caso si sino) | PASS |
| TC-VM-04 | Ciclo mientras | `--test-vm` (caso mientras) | PASS |
| TC-VM-05 | Funcion con PARAM, ERA, GOSUB, ENDFUNC | `--run prueba_funciones.patito` | PASS |
| TC-VM-06 | Funcion sin parametros | `--test-vm` (caso funcion sin params) | PASS |
| TC-VM-07 | Demo completa aritmetica + funcion | `--run prueba_vm.patito` | PASS |

Mantuve los 24 tests sintacticos (--test), los 7 semanticos (--test-semantic) y los 6 de cuadruplos (--test-quad) de la entrega anterior. Para ejecucion en Maquina Virtual:

Resultado global: 24/24 sintacticos, 7/7 semanticos, 6/6 cuadruplos y 6/6 tests de VM pasaron.

Repositorio: https://github.com/DiegoS2004/compiladores/tree/main/Patito-entrega


python3 patito.py --run hola.patito

python3 patito.py --run prueba_funciones.patito

python3 patito.py --quad prueba_funciones.patito

python3 patito.py --test-vm


Apoyo de inteligencia artificial

A lo largo de esta etapa use Claude (claude.ai, Anthropic) y el asistente de Cursor como herramienta de consulta y guia, de manera similar a como se usaria la documentacion oficial o apuntes del curso. Las consultas fueron principalmente sobre el diseno de la Maquina Virtual: como funciona ERA en runtime, que estructuras auxiliares se necesitan para GOSUB y ENDFUNC, y como indexar la memoria de ejecucion usando los rangos de direcciones virtuales que ya tenia del compilador.

Tambien hice consultas puntuales sobre sintaxis de Python (manejo de diccionarios, pilas, excepciones personalizadas) y sobre como conectar la VM con el compilador existente sin romper las fases anteriores. En algunos casos pedi explicacion del flujo PARAM → ERA → GOSUB → ENDFUNC paso a paso para asegurarme de entenderlo antes de implementarlo, y use la IA para revisar borradores de documentacion que despues adapte a mi estilo.

La idea es que es una herramienta mas, como una calculadora o la documentacion de PLY: me oriento con ella, pero el diseno de MemoriaEjecucion, la decision de respaldar locales en ERA, la integracion con patito.py y la comprension del flujo compilacion → cuadruplos → ejecucion son mias. No delegue el diseno completo ni copie codigo sin revisarlo y adaptarlo al proyecto.
