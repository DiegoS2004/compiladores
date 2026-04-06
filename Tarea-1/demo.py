# demo.py - Programa que muestra como funcionan las 3 estructuras
# aqui nomas le picamos a todo para ver que jalan bien

from stack import Stack
from queue import Queue
from tabla_hash import TablaHash


def separador(titulo):
    print(f"\n{'='*50}")
    print(f"  {titulo}")
    print(f"{'='*50}\n")


# ============================================================
#  DEMO DEL STACK
# ============================================================
separador("DEMO - STACK (pila de platos)")

mi_stack = Stack()
print(f"Stack recien creado: {mi_stack}")
print(f"Esta vacio? {mi_stack.is_empty()}")

# vamos metiendo cosas
print("\nPusheando: 'python', 'java', 'c++'")
mi_stack.push("python")
mi_stack.push("java")
mi_stack.push("c++")
print(f"Stack ahora: {mi_stack}")
print(f"Tamaño: {mi_stack.size()}")

# vemos que hay arriba
print(f"\nPeek (ver arriba sin sacar): {mi_stack.peek()}")

# sacamos uno
sacado = mi_stack.pop()
print(f"Pop (sacamos): {sacado}")
print(f"Stack despues del pop: {mi_stack}")

# checamos si tiene algo
print(f"\nContiene 'python'? {mi_stack.contains('python')}")
print(f"Contiene 'c++'? {mi_stack.contains('c++')}")

# lo vaciamos
mi_stack.clear()
print(f"\nDespues de clear: {mi_stack}")
print(f"Esta vacio? {mi_stack.is_empty()}")


# ============================================================
#  DEMO DEL QUEUE
# ============================================================
separador("DEMO - QUEUE (fila del oxxo)")

mi_queue = Queue()
print(f"Queue recien creado: {mi_queue}")

# metemos gente a la fila
print("\nEnqueue: 'cliente1', 'cliente2', 'cliente3'")
mi_queue.enqueue("cliente1")
mi_queue.enqueue("cliente2")
mi_queue.enqueue("cliente3")
print(f"Queue ahora: {mi_queue}")

# vemos quien es el primero y el ultimo
print(f"\nFront (primero): {mi_queue.front()}")
print(f"Rear (ultimo): {mi_queue.rear()}")

# atendemos al primero
atendido = mi_queue.dequeue()
print(f"\nDequeue (atendimos a): {atendido}")
print(f"Queue despues: {mi_queue}")
print(f"Tamaño: {mi_queue.size()}")

# metemos otro
mi_queue.enqueue("cliente4")
print(f"\nDespues de meter 'cliente4': {mi_queue}")
print(f"Contiene 'cliente1'? {mi_queue.contains('cliente1')}")
print(f"Contiene 'cliente2'? {mi_queue.contains('cliente2')}")


# ============================================================
#  DEMO DE LA TABLA HASH
# ============================================================
separador("DEMO - TABLA HASH (diccionario)")

mi_tabla = TablaHash()
print(f"Tabla recien creada: {mi_tabla}")
print(f"Esta vacia? {mi_tabla.is_empty()}")

# metemos algunos datos, como un directorio de contactos
print("\nAgregando contactos...")
mi_tabla.put("diego", "555-1234")
mi_tabla.put("maria", "555-5678")
mi_tabla.put("carlos", "555-9012")
print(f"Tabla: {mi_tabla}")
print(f"Tamaño: {mi_tabla.size()}")

# buscamos un contacto
print(f"\nBuscando a diego: {mi_tabla.get('diego')}")
print(f"Existe 'maria'? {mi_tabla.contains_key('maria')}")
print(f"Existe 'pedro'? {mi_tabla.contains_key('pedro')}")

# actualizamos un telefono
mi_tabla.put("diego", "555-0000")
print(f"\nActualizamos tel de diego: {mi_tabla.get('diego')}")

# vemos keys y values por separado
print(f"\nKeys: {mi_tabla.keys()}")
print(f"Values: {mi_tabla.values()}")
print(f"Items: {mi_tabla.items()}")

# eliminamos uno
eliminado = mi_tabla.remove("carlos")
print(f"\nEliminamos a carlos (tel: {eliminado})")
print(f"Tabla ahora: {mi_tabla}")
print(f"Tamaño: {mi_tabla.size()}")

separador("FIN DEL DEMO")
print("todo jalo bien! las 3 estructuras funcionan correctamente")
