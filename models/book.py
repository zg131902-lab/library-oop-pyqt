from datetime import datetime

from models.entity import Entity


class Book(Entity):
    """Книга в каталоге библиотеки."""

    GENRES = ("Роман", "Фантастика", "Детектив", "Поэзия", "Научная литература", "Учебник")
    MIN_YEAR = 1450

    def __init__(self, book_id, title, author, year, genre):
        super().__init__(book_id)
        self._title = ""
        self._author = ""
        self._year = Book.MIN_YEAR
        self._genre = Book.GENRES[0]
        self.title = title
        self.author = author
        self.year = year
        self.genre = genre

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = Entity.check_text(value, "Название")

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, value):
        self._author = Entity.check_text(value, "Автор")

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("Год издания должен быть целым числом")
        max_year = datetime.now().year
        if not Book.MIN_YEAR <= value <= max_year:
            raise ValueError(f"Год издания должен быть от {Book.MIN_YEAR} до {max_year}")
        self._year = value

    @property
    def genre(self):
        return self._genre

    @genre.setter
    def genre(self, value):
        if value not in Book.GENRES:
            raise ValueError(f"Неизвестный жанр: {value}")
        self._genre = value

    def sort_key(self):
        return (self._title.lower(), self._author.lower(), self._year)

    def to_row(self):
        return (str(self.id), self._title, self._author, str(self._year), self._genre)

    def matches(self, text):
        text = text.strip().lower()
        return text in self._title.lower() or text in self._author.lower()

    def __eq__(self, other):
        if not isinstance(other, Book):
            return NotImplemented
        return self.sort_key() == other.sort_key()

    def __hash__(self):
        return hash(self.sort_key())

    def __repr__(self):
        return (f"Book(id={self.id}, title={self._title!r}, author={self._author!r}, "
                f"year={self._year}, genre={self._genre!r})")

    def __str__(self):
        return f"«{self._title}» — {self._author} ({self._year})"
