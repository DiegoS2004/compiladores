# Flujo del compilador Patito — start to finish

Este documento explica **de punta a punta** cómo funciona el compilador usando dos testcases:

- `testcases/prueba_aritmetica.patito` — expresiones y asignaciones
- `testcases/prueba_funciones.patito` — funciones con retorno y llamadas

```bash
python patito.py --run prueba_aritmetica.patito
python patito.py --run prueba_funciones.patito   # imprime: suma15
```

---

## 1. Panorama general

```
  .patito
     │
     ▼
┌─────────┐     tokens      ┌─────────┐    cuádruplos + tablas    ┌──────────────┐
│  Lexer  │ ──────────────► │ Parser  │ ────────────────────────► │ VM ejecuta   │
│ ply.lex │                 │ ply.yacc│   dir_funciones, dv, gen    │ cuádruplos   │
└─────────┘                 └─────────┘                             └──────────────┘
```

| Archivo | Rol |
|---------|-----|
| `patito.py` | Orquesta: compilar → crear VM → ejecutar desde `quad_inicio` del `main` |
| `patito_lexer.py` | Texto → tokens (`ID`, `CTE_ENT`, `PLUS`, …) |
| `patito_parser.py` | Tokens → árbol; acciones semánticas en puntos neurálgicos |
| `dir_funciones.py` | Directorio de funciones y variables (tipos + direcciones) |
| `direcciones_virtuales.py` | Asigna enteros únicos a vars, temporales y constantes |
| `generador_cuadruplos.py` | Pilas de operadores/operandos → fila de cuádruplos |
| `semantic_cube.py` | Valida tipos en operaciones |
| `maquina_virtual.py` | Interpreta cuádruplos |
| `memoria_ejecucion.py` | Memoria global, constantes, temporales y **registros de activación** |

---

## 2. Direcciones virtuales

Cada variable y resultado intermedio se representa con un **entero** (no con el nombre):

| Segmento | Rango | Uso |
|----------|-------|-----|
| Global | 1000–1999 | Variables del `vars` del programa |
| Local | 2000–4999 | Parámetros y locales de funciones |
| Temporal | 5000–7999 | Resultados intermedios en `main` |
| Constante | 8000–9999 | Literales (`1`, `2`, `"suma"`, …) |

---

## 3. Caso A — `prueba_aritmetica.patito`

### Código fuente

```patito
programa arit;
vars
  x, y : entero;
inicio
{
  x = 1 + 2 * 3;
  y = (4 - 1) / 3;
}
fin
```

### Paso 1 — `patito.py` lee y compila

```python
compilar_fuente(source)   # en patito_parser.py
```

Reinicia los singletons (`dir_func`, `gen`, `dv`), tokeniza y parsea.

### Paso 2 — Lexer (`patito_lexer.py`)

Convierte el texto en tokens. Fragmento relevante de `x = 1 + 2 * 3`:

```
ID(x)  ASSIGN  CTE_ENT(1)  PLUS  CTE_ENT(2)  MULT  CTE_ENT(3)  SEMICOLON
```

### Paso 3 — Parser + semántica (`patito_parser.py`)

En puntos neurálgicos (●) del recorrido bottom-up:

| Momento | Acción |
|---------|--------|
| `programa arit ;` | `dir_func.inicio_programa("arit")` |
| `vars x, y : entero` | `dir_func.nueva_variable` → x=**1000**, y=**1001** |
| `inicio` | `dir_func.marca_inicio_main(gen.contador)` → main empieza en cuádruplo **0** |
| `x = expresion` | Al cerrar la expresión: `gen.asignar(1000, entero)` |

El cubo semántico (`semantic_cube.py`) valida que `entero + entero`, `entero * entero`, etc. sean válidos.

### Paso 4 — Generación de cuádruplos para `x = 1 + 2 * 3`

El generador (`generador_cuadruplos.py`) usa **pilas**:

- `operandos` / `tipos` — direcciones virtuales pendientes
- `operadores` — `+`, `*`, `(`, …

Recorrido con precedencia (`*` antes que `+`):

```
1. push constante 1  → dir 8000
2. push operador +
3. push constante 2  → dir 8001
4. push operador *
5. push constante 3  → dir 8002
6. vaciar hasta *    → (*, 8001, 8002, 5000)   temp = 2*3 = 6
7. vaciar hasta +    → (+, 8000, 5000, 5001)   temp = 1+6 = 7
8. asignar           → (=, 5001, _, 1000)       x = 7
```

Para `y = (4 - 1) / 3` se repite el mismo esquema con constantes 8003=4, 8000=1, 8002=3.

### Cuádruplos finales

```
 0  (*, 8001, 8002, 5000)    # 2 * 3 → t5000
 1  (+, 8000, 5000, 5001)    # 1 + t5000 → t5001
 2  (=, 5001, _, 1000)       # x = t5001
 3  (-, 8003, 8000, 5002)    # 4 - 1 → t5002
 4  (/, 5002, 8002, 5003)    # t5002 / 3 → t5003
 5  (=, 5003, _, 1001)       # y = t5003
```

### Paso 5 — Ejecución en la VM

`patito.py` crea la VM y arranca en `quad_inicio = 0` (no hay funciones antes del `main`).

```
IP=0  (*, 8001, 8002, 5000)  →  mem[5000] = 6
IP=1  (+, 8000, 5000, 5001)  →  mem[5001] = 7
IP=2  (=, 5001, _, 1000)     →  mem[1000] = 7   (x)
IP=3  (-, 8003, 8000, 5002)  →  mem[5002] = 3
IP=4  (/, 5002, 8002, 5003)  →  mem[5003] = 1
IP=5  (=, 5003, _, 1001)     →  mem[1001] = 1   (y)
```

**Estado final:** `x = 7`, `y = 1`. Este programa no tiene `escribe`, así que no imprime nada.

---

## 4. Caso B — `prueba_funciones.patito`

### Código fuente

```patito
programa funcs;
vars
  x : entero;
entero suma( a : entero, b : entero )
{
  retorna a + b;
}
inicio
{
  x = 10;
  x = suma(x, 5);
  escribe("suma", x);
}
fin
```

### Paso 1 — Declaración de `suma`

| Momento | Acción |
|---------|--------|
| `entero suma (` | `dir_func.nueva_funcion("suma", "entero")` — tipo de retorno entero |
| `a : entero` | param `a` → dir local **2001** |
| `b : entero` | param `b` → dir local **2000** |
| `)` | `marca_inicio_funcion(0)` — cuerpo de suma empieza en cuádruplo **0** |
| `retorna a + b` | cuádruplos `+` y `RETURN` |
| fin de función | `ENDFUNC` |

Cuádruplos de `suma` (índices 0–2):

```
 0  (+, 2001, 2000, 2002)   # a + b → temp local 2002
 1  (RETURN, 2002, _, _)    # devuelve valor, sale de la función
 2  (ENDFUNC, _, _, _)      # fin implícito (no se alcanza si hay retorna)
```

### Paso 2 — Bloque `inicio` (main empieza en cuádruplo 3)

Las funciones se declaran **antes** de `inicio`, así que sus cuádruplos van primero.  
`marca_inicio_main` guarda `quad_inicio = 3` para `global`.

Cuádruplos del main (índices 3–11):

```
 3  (=, 8000, _, 1000)       # x = 10
 4  (PARAM, 1000, _, _)      # arg1: x
 5  (PARAM, 8001, _, _)       # arg2: 5
 6  (ERA, suma, _, _)        # nuevo registro de activación
 7  (GOSUB, _, _, 0)          # saltar a cuádruplo 0 (suma)
 8  (RETORNO, _, _, 5000)     # guardar valor devuelto en temporal 5000
 9  (=, 5000, _, 1000)       # x = resultado
10  (PRINT, "suma", _, _)
11  (PRINT, 1000, _, _)
```

### Paso 3 — Llamada a función: `suma(x, 5)`

Secuencia estándar de cuádruplos:

```
PARAM  →  encola dirección de cada argumento
ERA    →  crea Registro de Activación (RA) y carga parámetros
GOSUB  →  guarda IP de retorno y salta a quad_inicio de la función
...      ejecuta cuerpo ...
RETURN →  empuja valor a pila de retorno y destruye RA
RETORNO→  (en el caller) escribe ese valor en un temporal
```

Diagrama de la llamada `suma(10, 5)`:

```
  main (RA vacío, memoria global)
    │
    │  PARAM 1000  (x=10)
    │  PARAM 8001  (5)
    │  ERA suma    →  nuevo RA: { a=10 en 2001, b=5 en 2000 }
    │  GOSUB 0     →  IP=0, pila_retorno=[4]
    ▼
  suma (RA activo)
    IP=0  (+, 2001, 2000, 2002)  →  10+5=15 en dir local 2002
    IP=1  (RETURN, 2002)         →  pila_valores=[15], destruye RA de suma
    ▼
  main (restaura RA anterior = ninguno)
    IP=8  (RETORNO, _, _, 5000)  →  mem[5000] = 15
    IP=9  (=, 5000, _, 1000)     →  x = 15
    IP=10 (PRINT, "suma")        →  imprime suma
    IP=11 (PRINT, 1000)          →  imprime 15
```

**Salida:** `suma15`

### Paso 4 — Registro de activación (`memoria_ejecucion.py`)

Cada `ERA` crea un `ActivationRecord`:

```python
class ActivationRecord:
    nombre   # "suma"
    locales  # { 2001: 10, 2000: 5, 2002: 15, ... }
```

- **Pila de RA:** cada llamada anidada o recursiva apila un RA nuevo.
- **Direcciones locales (2000+):** se leen/escriben en el RA activo (`pila_ra.peek()`).
- **Globales (1000+):** viven fuera de la pila, persisten todo el programa.
- **Temporales en main (5000+):** segmento global de temporales.

Dentro de funciones, los temporales de expresión también usan rango local (2000+) para que cada invocación tenga los suyos dentro del RA.

---

## 5. Resumen comparativo

| | `prueba_aritmetica` | `prueba_funciones` |
|--|---------------------|-------------------|
| Funciones | No | `entero suma(a, b)` con `retorna` |
| `quad_inicio` main | 0 | 3 (funciones ocupan 0–2) |
| Cuádruplos clave | `+`, `*`, `=`, `/` | `PARAM`, `ERA`, `GOSUB`, `RETURN`, `RETORNO`, `PRINT` |
| Memoria | Solo globales + temporales | RA con locales + globales |
| Salida | (ninguna) | `suma15` |

---

## 6. Archivos del proyecto (mapa rápido)

```
Patito-entrega/
├── patito.py              ← main (--run)
├── patito_lexer.py        ← tokens
├── patito_parser.py       ← gramática + compilar_fuente()
├── dir_funciones.py       ← tabla de símbolos
├── direcciones_virtuales.py
├── generador_cuadruplos.py
├── semantic_cube.py
├── maquina_virtual.py
├── memoria_ejecucion.py   ← ActivationRecord
├── estructura/
│   ├── stack.py           ← pilas (expresiones, RA, retornos)
│   └── queue.py           ← fila de cuádruplos
└── testcases/
    ├── prueba_aritmetica.patito
    └── prueba_funciones.patito
```

---

## 7. Para la entrevista — frase corta

> *"Patito compila en tres fases: lexer tokeniza, parser valida semántica y genera cuádruplos con direcciones virtuales, y la VM ejecuta esa fila usando registros de activación para las llamadas a función."*
