from abc import abstractmethod

from models.base import Comparable


class BaseContainer(Comparable):
    """Абстрактный контейнер: что должна уметь любая наша коллекция.

    По умолчанию контейнеры сравниваются по количеству элементов.
    """

    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __contains__(self, item):
        pass

    @abstractmethod
    def clear(self):
        pass

    def is_empty(self):
        return len(self) == 0

    def sort_key(self):
        return (len(self),)
