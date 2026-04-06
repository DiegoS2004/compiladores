# tests.py - Aqui probamos que todo funcione como debe
# si algo falla, python nos va a avisar con un AssertionError

from stack import Stack
from queue import Queue
from tabla_hash import TablaHash

aprobados = 0
fallidos = 0


def test(nombre, condicion):
    global aprobados, fallidos
    if condicion:
        print(f"  [PASS] {nombre}")
        aprobados += 1
    else:
        print(f"  [FAIL] {nombre}")
        fallidos += 1


def test_error(nombre, funcion, error_esperado):
    """checa que una funcion lance el error que esperamos"""
    global aprobados, fallidos
    try:
        funcion()
        print(f"  [FAIL] {nombre} - no lanzo error")
        fallidos += 1
    except error_esperado:
        print(f"  [PASS] {nombre}")
        aprobados += 1
    except Exception as e:
        print(f"  [FAIL] {nombre} - lanzo {type(e).__name__} en vez de {error_esperado.__name__}")
        fallidos += 1


# ===== TESTS PARA STACK =====
print("\n--- Tests del Stack ---")

# test 1: stack nuevo esta vacio
s = Stack()
test("stack nuevo esta vacio", s.is_empty())
test("size de stack nuevo es 0", s.size() == 0)

# test 2: push y size
s.push(10)
s.push(20)
s.push(30)
test("push 3 elementos -> size es 3", s.size() == 3)
test("ya no esta vacio", not s.is_empty())

# test 3: peek ve el ultimo que metimos
test("peek regresa 30 (el ultimo)", s.peek() == 30)
test("peek no cambia el size", s.size() == 3)

# test 4: pop saca el ultimo
test("pop regresa 30", s.pop() == 30)
test("despues del pop size es 2", s.size() == 2)
test("ahora peek es 20", s.peek() == 20)

# test 5: pop hasta vaciar
s.pop()
s.pop()
test("vaciamos todo, is_empty es True", s.is_empty())

# test 6: pop en stack vacio lanza error
test_error("pop en stack vacio lanza IndexError", lambda: s.pop(), IndexError)
test_error("peek en stack vacio lanza IndexError", lambda: s.peek(), IndexError)

# test 7: contains
s.push("a")
s.push("b")
test("contains 'a' es True", s.contains("a"))
test("contains 'z' es False", not s.contains("z"))

# test 8: clear
s.clear()
test("despues de clear esta vacio", s.is_empty())

# test 9: to_list
s.push(1)
s.push(2)
test("to_list regresa [1, 2]", s.to_list() == [1, 2])

# test 10: len funciona
test("len(stack) funciona", len(s) == 2)


# ===== TESTS PARA QUEUE =====
print("\n--- Tests del Queue ---")

# test 1: queue nuevo esta vacio
q = Queue()
test("queue nuevo esta vacio", q.is_empty())
test("size es 0", q.size() == 0)

# test 2: enqueue y size
q.enqueue("primero")
q.enqueue("segundo")
q.enqueue("tercero")
test("enqueue 3 -> size es 3", q.size() == 3)

# test 3: front y rear
test("front es 'primero'", q.front() == "primero")
test("rear es 'tercero'", q.rear() == "tercero")

# test 4: dequeue saca al primero (FIFO)
test("dequeue saca 'primero'", q.dequeue() == "primero")
test("ahora front es 'segundo'", q.front() == "segundo")
test("size ahora es 2", q.size() == 2)

# test 5: dequeue hasta vaciar
q.dequeue()
q.dequeue()
test("vaciamos todo", q.is_empty())

# test 6: errores con queue vacia
test_error("dequeue en queue vacia lanza IndexError", lambda: q.dequeue(), IndexError)
test_error("front en queue vacia lanza IndexError", lambda: q.front(), IndexError)
test_error("rear en queue vacia lanza IndexError", lambda: q.rear(), IndexError)

# test 7: contains
q.enqueue(100)
q.enqueue(200)
test("contains 100 es True", q.contains(100))
test("contains 999 es False", not q.contains(999))

# test 8: clear
q.clear()
test("clear vacia la queue", q.is_empty())

# test 9: orden FIFO se mantiene
q.enqueue("a")
q.enqueue("b")
q.enqueue("c")
test("FIFO: sale a, luego b, luego c",
     q.dequeue() == "a" and q.dequeue() == "b" and q.dequeue() == "c")

# test 10: to_list y len
q.enqueue(1)
q.enqueue(2)
test("to_list regresa [1, 2]", q.to_list() == [1, 2])
test("len funciona", len(q) == 2)


# ===== TESTS PARA TABLA HASH =====
print("\n--- Tests de la Tabla Hash ---")

# test 1: tabla nueva esta vacia
t = TablaHash()
test("tabla nueva esta vacia", t.is_empty())
test("size es 0", t.size() == 0)

# test 2: put y get
t.put("nombre", "diego")
t.put("edad", 22)
test("get 'nombre' regresa 'diego'", t.get("nombre") == "diego")
test("get 'edad' regresa 22", t.get("edad") == 22)
test("size es 2", t.size() == 2)

# test 3: actualizar valor existente
t.put("edad", 23)
test("actualizar edad a 23", t.get("edad") == 23)
test("size sigue siendo 2 (no duplica)", t.size() == 2)

# test 4: contains_key
test("contains_key 'nombre' es True", t.contains_key("nombre"))
test("contains_key 'telefono' es False", not t.contains_key("telefono"))

# test 5: remove
t.put("temp", "borrame")
test("size con temp es 3", t.size() == 3)
val = t.remove("temp")
test("remove regresa el valor 'borrame'", val == "borrame")
test("size vuelve a 2", t.size() == 2)
test("ya no existe 'temp'", not t.contains_key("temp"))

# test 6: get con key que no existe
test_error("get key inexistente lanza KeyError", lambda: t.get("noexisto"), KeyError)
test_error("remove key inexistente lanza KeyError", lambda: t.remove("noexisto"), KeyError)

# test 7: keys y values
keys = t.keys()
vals = t.values()
test("keys contiene 'nombre' y 'edad'", "nombre" in keys and "edad" in keys)
test("values contiene 'diego' y 23", "diego" in vals and 23 in vals)

# test 8: items regresa tuplas
items = t.items()
test("items tiene los pares correctos",
     ("nombre", "diego") in items and ("edad", 23) in items)

# test 9: clear
t.clear()
test("clear vacia la tabla", t.is_empty())
test("size es 0 despues de clear", t.size() == 0)

# test 10: muchos elementos (para probar que los buckets jalen)
t2 = TablaHash(capacidad=4)  # capacidad chica para forzar colisiones
for i in range(20):
    t2.put(f"key_{i}", i)
test("meter 20 elementos en tabla chica", t2.size() == 20)
test("podemos recuperar todos",
     all(t2.get(f"key_{i}") == i for i in range(20)))

# test 11: len funciona
test("len funciona", len(t2) == 20)


# ===== RESUMEN =====
print(f"\n{'='*50}")
print(f"  RESULTADOS: {aprobados} passed, {fallidos} failed")
print(f"{'='*50}")

if fallidos == 0:
    print("  todo jalo perfecto!")
else:
    print(f"  hay {fallidos} test(s) que fallaron, revisa arriba")
