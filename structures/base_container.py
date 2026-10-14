from abc import ABC, abstractmethod


class BaseContainer(ABC):
    """Абстрактный контейнер: что должна уметь любая наша коллекция."""

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
