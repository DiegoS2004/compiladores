# stack.py - Pila LIFO para operadores, operandos y tipos (etapa 3)


class Stack:
    def __init__(self):
        self._items = []

    def push(self, elemento):
        self._items.append(elemento)

    def pop(self):
        if self.is_empty():
            raise IndexError("pila vacia")
        return self._items.pop()

    def peek(self):
        if self.is_empty():
            raise IndexError("pila vacia")
        return self._items[-1]

    def is_empty(self):
        return len(self._items) == 0

    def clear(self):
        self._items.clear()

    def to_list(self):
        return self._items.copy()

    def __len__(self):
        return len(self._items)
