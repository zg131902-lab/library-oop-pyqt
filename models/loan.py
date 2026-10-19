from datetime import datetime

from models.book import Book
from models.entity import Entity
from models.reader import Reader


class Loan(Entity):
    DATE_FORMAT = "%d.%m.%Y %H:%M"

    def __init__(self, loan_id, book, reader, issued_at):
        super().__init__(loan_id)
        self._book = None
        self._reader = None
        self._issued_at = None
        self.book = book
        self.reader = reader
        self.issued_at = issued_at

    @property
    def book(self):
        return self._book

    @book.setter
    def book(self, value):
        if not isinstance(value, Book):
            raise ValueError("Выдать можно только книгу")
        self._book = value

    @property
    def reader(self):
        return self._reader

    @reader.setter
    def reader(self, value):
        if not isinstance(value, Reader):
            raise ValueError("Книгу можно выдать только читателю")
        self._reader = value

    @property
    def issued_at(self):
        return self._issued_at

    @issued_at.setter
    def issued_at(self, value):
        if not isinstance(value, datetime):
            raise ValueError("Дата выдачи должна быть датой")
        self._issued_at = value

    def sort_key(self):
        return (self._issued_at, self.id)

    def to_row(self):
        return (str(self.id), str(self._book), self._reader.full_name,
                self._issued_at.strftime(Loan.DATE_FORMAT))

    def matches(self, text):
        return self._book.matches(text) or self._reader.matches(text)

    def __eq__(self, other):
        if not isinstance(other, Loan):
            return NotImplemented
        return self.sort_key() == other.sort_key()

    def __hash__(self):
        return hash(self.sort_key())

    def __repr__(self):
        return (f"Loan(id={self.id}, book={self._book!r}, reader={self._reader!r}, "
                f"issued_at={self._issued_at!r})")

    def __str__(self):
        return (f"{self._book} → {self._reader.full_name}, "
                f"{self._issued_at.strftime(Loan.DATE_FORMAT)}")
