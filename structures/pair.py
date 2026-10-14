from models.base import Comparable


class Pair(Comparable):
    """Пара «ключ — значение» для MyMap."""

    def __init__(self, key, value):
        self._key = key
        self._value = value

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._key = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def sort_key(self):
        return (self._key,)

    def __eq__(self, other):
        if not isinstance(other, Pair):
            return NotImplemented
        return self._key == other.key and self._value == other.value

    def __hash__(self):
        return hash(self._key)

    def __repr__(self):
        return f"Pair({self._key!r}, {self._value!r})"

    def __str__(self):
        return f"{self._key}: {self._value}"
