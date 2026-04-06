# queue.py - Implementacion de un Queue (FIFO - First In, First Out)
# es como la fila del oxxo, el primero que llega es el primero que atienden


class Queue:
    def __init__(self):
        # igual usamos una lista para guardar todo
        self.items = []

    def enqueue(self, elemento):
        # agrega un elemento al final de la fila
        self.items.append(elemento)

    def dequeue(self):
        # saca al primero de la fila (el que lleva mas tiempo esperando)
        if self.is_empty():
            raise IndexError("la queue esta vacia, no hay nadie en la fila")
        return self.items.pop(0)

    def front(self):
        # ve quien esta primero sin sacarlo
        if self.is_empty():
            raise IndexError("la queue esta vacia")
        return self.items[0]

    def rear(self):
        # ve quien es el ultimo de la fila
        if self.is_empty():
            raise IndexError("la queue esta vacia")
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def clear(self):
        # bye bye a todos los elementos
        self.items = []

    def contains(self, elemento):
        return elemento in self.items

    def to_list(self):
        return self.items.copy()

    def __str__(self):
        # el de la izquierda es el frente de la fila
        return f"Queue({self.items})"

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return self.__str__()
