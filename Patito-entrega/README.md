# Patito — Entrega 3 (Generación de cuádruplos)

Compilador del lenguaje **Patito** (TC3002B): lexer, parser, análisis semántico (directorio de funciones + cubo semántico) y **generación de código intermedio en cuádruplos**.

## Requisitos

- Python 3.10+
- [PLY](https://github.com/dabeaz/ply): `pip install -r requirements.txt`

## Uso

```bash
cd Patito-entrega
python3 patito.py hola.patito              # compilar
python3 patito.py --quad hola.patito       # compilar + fila de cuádruplos
python3 patito.py --dir hola.patito        # compilar + directorio de funciones
python3 patito.py --test                   # pruebas sintácticas
python3 patito.py --test-semantic          # pruebas semánticas (deben fallar)
python3 patito.py --test-quad              # cuádruplos de programas de prueba
```

## Estructuras de la etapa 3

### Pilas (LIFO) — `stack.py` + `generador_cuadruplos.py`

| Pila | Contenido | Uso |
|------|-----------|-----|
| **Operadores** | Símbolos `+`, `-`, `*`, `/`, `>`, `<`, `==`, `!=`, `(` | Orden de evaluación por precedencia; `(` marca subexpresiones |
| **Operandos** | Nombres de variables, constantes, temporales `t1`, `t2`, … | Argumentos y resultados de cuádruplos |
| **Tipos** | `entero` / `flotante` | Validación con el cubo semántico al generar cada operación |
| **Saltos** (auxiliar) | Índices de cuádruplos incompletos | Rellenar destinos de `GOTOF` / `GOTO` en `si`/`sino` y `mientras` |

### Fila (FIFO) — `queue.py`

| Fila | Elemento | Formato |
|------|----------|---------|
| **Cuádruplos** | Tupla `(operador, operando1, operando2, resultado)` | Orden de ejecución futura; `_` = vacío en impresión |

Operadores de cuádruplo usados: `+`, `-`, `*`, `/`, `uminus`, `>`, `<`, `==`, `!=`, `=`, `PRINT`, `GOTOF`, `GOTO`.

## Algoritmos implementados

1. **Expresiones aritméticas** (`exp`, `termino`, `factor`): al ver un operador se apila; al terminar el operando de la derecha se vacían operadores de mayor o igual precedencia y se emite un cuádruplo; temporales en `tN`.
2. **Expresiones relacionales** (`expresion`): tras la parte aritmética izquierda, operador relacional y `exp` derecha → cuádruplo relacional.
3. **Asignación** `id = expresion;`: vacía operadores, cuádruplo `(=, valor, _, id)`.
4. **escribe** `(...)`: `(PRINT, operando, _, _)` por cada argumento.
5. **si / sino**: `(GOTOF, cond, _, destino)`; con `sino`, `(GOTO, _, _, destino)` y relleno de índices.
6. **mientras**: marca de inicio, `(GOTOF, cond, _, salida)`, cuerpo, `(GOTO, _, _, inicio)`.

## Programas de prueba

| Archivo | Qué ejercita |
|---------|----------------|
| `hola.patito` | Asignación y `escribe` |
| `prueba_aritmetica.patito` | Precedencia `*`/`+` y paréntesis |
| `prueba_relacional.patito` | `si` con `>` |
| `prueba_si.patito` | `si` / `sino` |
| `prueba_mientras.patito` | Ciclo `mientras` |

## Puntos neurálgicos (resumen)

Reglas auxiliares (`op_suma`, `par_abre`, `cond_paren_cierra`, etc.) marcan el momento en que el parser reduce y se ejecuta la acción semántica de generación.

### `exp` / `exp_prime` (suma y resta)

```
exp → termino exp_prime
exp_prime → op_suma termino exp_prime | op_resta termino exp_prime | ε
```

- **● `op_suma` / `op_resta`**: apilar `+` o `-`.
- **● Fin de `op_* termino`**: `procesar_aritmetico(2)` — genera `*`/`/` pendientes y luego `+`/`-` si aplica.

### `termino` / `termino_prime` (mult y div)

- **● `op_mult` / `op_div`**: apilar `*` o `/`.
- **● Fin de `op_* factor`**: `procesar_aritmetico(3)`.

### `factor` (unario y operandos)

- **● `factor_prime : ID`**: apilar variable y su tipo (tabla de símbolos).
- **● `factor_prime : cte`**: apilar constante y tipo.
- **● `par_abre` / `par_cierra`**: apilar `(`; al cerrar, generar hasta `(`.
- **● `MINUS factor_prime`**: cuádruplo `uminus`.

### `expresion` (relacional)

- **● `op_rel`**: apilar `>`, `<`, `==`, `!=`.
- **● `op_rel exp`**: `procesar_relacional()` — un cuádruplo relacional.

### Estatutos

| Producción | Punto neurálgico | Acción |
|------------|------------------|--------|
| `ID = expresion ;` | Al reducir estatuto | `asignar(id)` |
| `escribe(...)` | Cada `imprime_val` | `PRINT` |
| `si ( exp )` | `cond_paren_cierra` | `GOTOF` (destino pendiente) |
| `sino` | `sino_mark` | `GOTO` + rellenar `GOTOF` |
| Fin `si` sin `sino` | `condicion_prime : ε` | Rellenar `GOTOF` |
| Fin `si` con `sino` | Tras cuerpo del `sino` | Rellenar `GOTO` |
| `mientras (` | `ciclo_mark` | Guardar índice de inicio |
| `)` tras condición | `ciclo_cond_fin` | `GOTOF` |
| Fin `mientras` | Reducir `ciclo` | `GOTO` inicio + rellenar `GOTOF` |

## Diagrama de gramática (expresión + estatuto lineal)

```mermaid
flowchart TB
  subgraph arit["Aritmética"]
    E[exp] --> T[termino]
    E --> EP[exp_prime]
    EP -->|"+ termino"| EP
    EP -->|"- termino"| EP
    T --> F[factor]
    T --> TP[termino_prime]
    TP -->|"* factor"| TP
    TP -->|"/ factor"| TP
    F -->|ID ●| PUSH1[push operando/tipo]
    F -->|cte ●| PUSH2[push operando/tipo]
    F -->|"( exp )" ●| PAREN[par_abre / par_cierra]
  end
  subgraph rel["Relacional"]
    EX[expresion] --> E
    EX --> RP[expresion_prime]
    RP -->|"op_rel exp ●"| REL[procesar_relacional]
  end
  subgraph est["Estatutos"]
    ASG["ID = exp ; ●"] --> ASGN[= cuádruplo]
    PR[escribe ●] --> PRT[PRINT]
    SI[si ( exp ) ●] --> GF[GOTOF]
    WH[mientras ●] --> LOOP[GOTOF / GOTO]
  end
```

(● = punto neurálgico en la reducción de esa regla.)

## Archivos del proyecto

| Archivo | Rol |
|---------|-----|
| `patito_lexer.py` | Tokens |
| `patito_parser.py` | Gramática + acciones semánticas y neurálgicas |
| `dir_funciones.py` | Directorio de funciones y variables |
| `semantic_cube.py` | Cubo semántico |
| `stack.py`, `queue.py` | Pilas y fila |
| `generador_cuadruplos.py` | Algoritmos de traducción |
| `patito.py` | Punto de entrada |

## Etapas anteriores

Las entregas 1–2 cubren scanner, parser y semántica de declaraciones; la etapa 3 añade código intermedio sin máquina virtual aún.
