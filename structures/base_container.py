from abc import abstractmethod

from models.base import Comparable


class BaseContainer(Comparable):
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
