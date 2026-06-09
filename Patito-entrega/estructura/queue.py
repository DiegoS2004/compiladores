# Fila FIFO donde generador_cuadruplos guarda los cuadruplos en orden de generacion.
# La VM los convierte a lista y los recorre con el puntero de instruccion (IP).


class Queue:
    def __init__(self):
        self._items = []

    def enqueue(self, elemento):
        self._items.append(elemento)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("fila vacia")
        return self._items.pop(0)

    def front(self):
        if self.is_empty():
            raise IndexError("fila vacia")
        return self._items[0]

    def is_empty(self):
        return len(self._items) == 0

    def clear(self):
        self._items.clear()

    def to_list(self):
        return self._items.copy()

    def __len__(self):
        return len(self._items)
