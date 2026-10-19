from abc import ABC, abstractmethod


class Comparable(ABC):
    @abstractmethod
    def sort_key(self):
        pass

    def _is_same_type(self, other):
        return type(self) is type(other)

    def __lt__(self, other):
        if not self._is_same_type(other):
            return NotImplemented
        return self.sort_key() < other.sort_key()

    def __le__(self, other):
        if not self._is_same_type(other):
            return NotImplemented
        return self.sort_key() <= other.sort_key()

    def __gt__(self, other):
        if not self._is_same_type(other):
            return NotImplemented
        return self.sort_key() > other.sort_key()

    def __ge__(self, other):
        if not self._is_same_type(other):
            return NotImplemented
        return self.sort_key() >= other.sort_key()
