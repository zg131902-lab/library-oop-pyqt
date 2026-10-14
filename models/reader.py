import re

from models.entity import Entity


class Reader(Entity):
    """Читатель библиотеки."""

    PHONE_PATTERN = re.compile(r"^\+?[0-9\s\-()]+$")
    MIN_PHONE_DIGITS = 10
    MAX_PHONE_DIGITS = 15

    def __init__(self, reader_id, full_name, phone):
        super().__init__(reader_id)
        self._full_name = ""
        self._phone = ""
        self.full_name = full_name
        self.phone = phone

    @property
    def full_name(self):
        return self._full_name

    @full_name.setter
    def full_name(self, value):
        self._full_name = Entity.check_text(value, "ФИО")

    @property
    def phone(self):
        return self._phone

    @phone.setter
    def phone(self, value):
        value = Entity.check_text(value, "Телефон", 25)
        digits = Reader.only_digits(value)
        if not Reader.PHONE_PATTERN.match(value) or not (
                Reader.MIN_PHONE_DIGITS <= len(digits) <= Reader.MAX_PHONE_DIGITS):
            raise ValueError("Телефон указан неверно, пример: +7 914 123-45-67")
        self._phone = value

    @staticmethod
    def only_digits(text):
        return "".join(symbol for symbol in text if symbol.isdigit())

    def short_name(self):
        """Фамилия и инициалы: Иванов И. И."""
        parts = self._full_name.split()
        return " ".join(parts[:1] + [part[0] + "." for part in parts[1:]])

    def phone_digits(self):
        return Reader.only_digits(self._phone)

    def sort_key(self):
        return (self._full_name.lower(), self.phone_digits())

    def to_row(self):
        return (str(self.id), self._full_name, self._phone)

    def matches(self, text):
        text = text.strip().lower()
        return text in self._full_name.lower() or text in self._phone

    def __eq__(self, other):
        if not isinstance(other, Reader):
            return NotImplemented
        return self.sort_key() == other.sort_key()

    def __hash__(self):
        return hash(self.sort_key())

    def __repr__(self):
        return f"Reader(id={self.id}, full_name={self._full_name!r}, phone={self._phone!r})"

    def __str__(self):
        return f"{self._full_name} ({self._phone})"
