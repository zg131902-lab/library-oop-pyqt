from abc import abstractmethod

from models.base import Comparable


class Entity(Comparable):
    def __init__(self, entity_id):
        self._id = 0
        self.id = entity_id

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("Номер должен быть целым положительным числом")
        self._id = value

    @abstractmethod
    def to_row(self):
        pass

    @abstractmethod
    def matches(self, text):
        pass

    @staticmethod
    def check_text(value, field_name, max_length=100):
        if not isinstance(value, str):
            raise ValueError(f"Поле «{field_name}» должно быть строкой")
        value = " ".join(value.split())
        if not value:
            raise ValueError(f"Поле «{field_name}» не может быть пустым")
        if len(value) > max_length:
            raise ValueError(f"Поле «{field_name}» длиннее {max_length} символов")
        return value
