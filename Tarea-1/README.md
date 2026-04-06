# Tarea 1 - Estructuras de Datos

Implementación desde cero de 3 estructuras de datos clásicas en Python.

## Archivos

| Archivo | Qué tiene |
|---|---|
| `stack.py` | Clase Stack (LIFO - Last In, First Out) |
| `queue.py` | Clase Queue (FIFO - First In, First Out) |
| `tabla_hash.py` | Clase TablaHash (Diccionario con buckets y función hash) |
| `demo.py` | Programa demo que muestra el uso de las 3 estructuras |
| `tests.py` | 58 test cases para validar que todo funcione |

## Cómo correr

```bash
# demo
python3 demo.py

# tests
python3 tests.py
```

## Estructuras y sus operaciones

### Stack (Pila - LIFO)
- `push(elemento)` - Agrega un elemento arriba de la pila
- `pop()` - Saca y regresa el elemento de arriba
- `peek()` - Ve qué hay arriba sin sacarlo
- `is_empty()` - Checa si está vacío
- `size()` - Cuántos elementos tiene
- `clear()` - Vacía el stack
- `contains(elemento)` - Checa si un elemento está en el stack
- `to_list()` - Regresa los elementos como lista

### Queue (Fila - FIFO)
- `enqueue(elemento)` - Agrega al final de la fila
- `dequeue()` - Saca al primero de la fila
- `front()` - Ve quién es el primero
- `rear()` - Ve quién es el último
- `is_empty()` - Checa si está vacía
- `size()` - Cuántos elementos tiene
- `clear()` - Vacía la queue
- `contains(elemento)` - Checa si un elemento está en la queue
- `to_list()` - Regresa los elementos como lista

### Tabla Hash (Diccionario)
- `put(key, value)` - Inserta o actualiza un par key-value
- `get(key)` - Busca el valor de una key
- `remove(key)` - Elimina un par key-value
- `contains_key(key)` - Checa si existe una key
- `keys()` - Regresa todas las keys
- `values()` - Regresa todos los values
- `items()` - Regresa todos los pares (key, value)
- `is_empty()` - Checa si está vacía
- `size()` - Cuántos elementos tiene
- `clear()` - Vacía la tabla

## Descripción de Test Cases

### Tests del Stack (17 tests)
1. **Stack vacío** - Un stack nuevo debe estar vacío y tener size 0
2. **Push y size** - Al meter 3 elementos el size debe ser 3 y ya no debe estar vacío
3. **Peek** - Debe regresar el último elemento sin modificar el size
4. **Pop** - Debe sacar el último elemento y reducir el size
5. **Vaciar con pop** - Hacer pop hasta vaciar debe dejar is_empty en True
6. **Errores** - Pop y peek en stack vacío deben lanzar IndexError
7. **Contains** - Debe encontrar elementos que existen y no encontrar los que no
8. **Clear** - Debe vaciar completamente el stack
9. **To list** - Debe regresar una copia correcta de los elementos
10. **Len** - El operador len() debe funcionar con el stack

### Tests del Queue (18 tests)
1. **Queue vacía** - Una queue nueva debe estar vacía
2. **Enqueue y size** - Meter 3 elementos debe dar size 3
3. **Front y rear** - Front debe ser el primero y rear el último que metimos
4. **Dequeue (FIFO)** - Debe sacar al primero que entró y actualizar el frente
5. **Vaciar con dequeue** - Sacar todo debe dejar la queue vacía
6. **Errores** - Dequeue, front y rear en queue vacía deben lanzar IndexError
7. **Contains** - Buscar elementos que sí y que no están
8. **Clear** - Vaciar la queue
9. **Orden FIFO** - Verificar que el orden de salida es el correcto (a -> b -> c)
10. **To list y len** - Funciones auxiliares deben funcionar

### Tests de la Tabla Hash (23 tests)
1. **Tabla vacía** - Nueva tabla debe estar vacía con size 0
2. **Put y get** - Insertar y recuperar valores correctamente
3. **Actualizar** - Put con key existente debe actualizar sin duplicar
4. **Contains key** - Buscar keys que existen y que no
5. **Remove** - Eliminar un par y verificar que ya no existe
6. **Errores** - Get y remove con keys inexistentes deben lanzar KeyError
7. **Keys y values** - Deben regresar las listas correctas
8. **Items** - Debe regresar las tuplas (key, value) correctas
9. **Clear** - Vaciar la tabla completamente
10. **Colisiones** - Meter 20 elementos en tabla con capacidad 4 (fuerza colisiones en los buckets) y verificar que se pueden recuperar todos
11. **Len** - El operador len() debe funcionar
