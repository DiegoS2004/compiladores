# tabla_hash.py - Implementacion de una Tabla Hash / Diccionario
# es como un diccionario real: buscas una palabra (key) y te da su definicion (value)
# internamente usa "buckets" para guardar las cosas con una funcion hash


class TablaHash:
    def __init__(self, capacidad=16):
        # creamos los buckets (cajones) donde van a caer los datos
        self.capacidad = capacidad
        self.buckets = [[] for _ in range(capacidad)]
        self.num_elementos = 0

    def _hash(self, key):
        # funcion hash sencilla, usa el hash de python y lo ajusta al tamaño
        return hash(key) % self.capacidad

    def put(self, key, value):
        # mete un par key-value, si la key ya existe la actualiza
        indice = self._hash(key)
        bucket = self.buckets[indice]

        # checamos si ya existe esa key para actualizarla
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return

        # si no existia, la agregamos
        bucket.append((key, value))
        self.num_elementos += 1

    def get(self, key):
        # busca el valor de una key, si no existe truena
        indice = self._hash(key)
        bucket = self.buckets[indice]

        for k, v in bucket:
            if k == key:
                return v

        raise KeyError(f"la key '{key}' no existe en la tabla")

    def remove(self, key):
        # elimina un par key-value
        indice = self._hash(key)
        bucket = self.buckets[indice]

        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self.num_elementos -= 1
                return v

        raise KeyError(f"no se encontro la key '{key}' para borrar")

    def contains_key(self, key):
        # checa si una key existe
        indice = self._hash(key)
        for k, v in self.buckets[indice]:
            if k == key:
                return True
        return False

    def keys(self):
        # regresa todas las keys
        todas = []
        for bucket in self.buckets:
            for k, v in bucket:
                todas.append(k)
        return todas

    def values(self):
        # regresa todos los values
        todos = []
        for bucket in self.buckets:
            for k, v in bucket:
                todos.append(v)
        return todos

    def items(self):
        # regresa todos los pares (key, value)
        todos = []
        for bucket in self.buckets:
            for par in bucket:
                todos.append(par)
        return todos

    def size(self):
        return self.num_elementos

    def is_empty(self):
        return self.num_elementos == 0

    def clear(self):
        self.buckets = [[] for _ in range(self.capacidad)]
        self.num_elementos = 0

    def __str__(self):
        pares = self.items()
        contenido = ", ".join(f"{k}: {v}" for k, v in pares)
        return "{" + contenido + "}"

    def __len__(self):
        return self.num_elementos

    def __repr__(self):
        return self.__str__()
