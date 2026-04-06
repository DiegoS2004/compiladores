# stack.py - Implementacion de un Stack (LIFO - Last In, First Out)
# basicamente es como una pila de platos, el ultimo que pones es el primero que sacas


class Stack:
    def __init__(self):
        # usamos una lista normal de python para guardar los elementos
        self.items = []

    def push(self, elemento):
        # mete un elemento arriba de la pila
        self.items.append(elemento)

    def pop(self):
        # saca el elemento de hasta arriba, si esta vacio truena
        if self.is_empty():
            raise IndexError("no puedes sacar de un stack vacio bro")
        return self.items.pop()

    def peek(self):
        # nomas ve que hay arriba sin sacarlo
        if self.is_empty():
            raise IndexError("el stack esta vacio, no hay nada que ver")
        return self.items[-1]

    def is_empty(self):
        # checa si el stack esta vacio
        return len(self.items) == 0

    def size(self):
        # regresa cuantos elementos tiene
        return len(self.items)

    def clear(self):
        # vacia todo el stack
        self.items = []

    def contains(self, elemento):
        # checa si un elemento anda por ahi en el stack
        return elemento in self.items

    def to_list(self):
        # regresa una copia de los elementos como lista
        return self.items.copy()

    def __str__(self):
        # para que se vea bonito cuando lo imprimas
        return f"Stack({self.items})"

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return self.__str__()
