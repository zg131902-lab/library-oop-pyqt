from structures.base_container import BaseContainer
from structures.pair import Pair


class MyMap(BaseContainer):
    def __init__(self, pairs=()):
        self._pairs = []
        self.pairs = pairs

    @property
    def pairs(self):
        return tuple(self._pairs)

    @pairs.setter
    def pairs(self, value):
        self._pairs = []
        for pair in value:
            if not isinstance(pair, Pair):
                raise TypeError("MyMap хранит только объекты Pair")
            self.put(pair.key, pair.value)

    def _index_of(self, key):
        for index, pair in enumerate(self._pairs):
            if pair.key == key:
                return index
        return -1

    def put(self, key, value):
        index = self._index_of(key)
        if index == -1:
            self._pairs.append(Pair(key, value))
        else:
            self._pairs[index].value = value

    def get(self, key, default=None):
        index = self._index_of(key)
        return default if index == -1 else self._pairs[index].value

    def remove(self, key):
        index = self._index_of(key)
        if index == -1:
            raise KeyError(key)
        return self._pairs.pop(index).value

    def contains_key(self, key):
        return self._index_of(key) != -1

    def keys(self):
        return [pair.key for pair in self._pairs]

    def values(self):
        return [pair.value for pair in self._pairs]

    def items(self):
        return list(self._pairs)

    def clear(self):
        self._pairs = []

    def __len__(self):
        return len(self._pairs)

    def __iter__(self):
        return iter(self.keys())

    def __contains__(self, key):
        return self.contains_key(key)

    def __getitem__(self, key):
        index = self._index_of(key)
        if index == -1:
            raise KeyError(key)
        return self._pairs[index].value

    def __setitem__(self, key, value):
        self.put(key, value)

    def __delitem__(self, key):
        self.remove(key)

    def __eq__(self, other):
        if not isinstance(other, MyMap):
            return NotImplemented
        if len(self) != len(other):
            return False
        for pair in self._pairs:
            if not other.contains_key(pair.key) or other.get(pair.key) != pair.value:
                return False
        return True

    __hash__ = None

    def __repr__(self):
        return f"MyMap([{', '.join(repr(pair) for pair in self._pairs)}])"

    def __str__(self):
        return "{" + ", ".join(str(pair) for pair in self._pairs) + "}"
