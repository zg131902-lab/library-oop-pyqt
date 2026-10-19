from datetime import datetime, timedelta

from models.base import Comparable
from models.book import Book
from models.loan import Loan
from models.reader import Reader
from structures.my_map import MyMap


class LibraryError(Exception):
    """Ошибка бизнес-логики, текст показывается пользователю."""


class Library(Comparable):
    """Каталог книг, список читателей и выданные книги."""

    MAX_BOOKS_PER_READER = 3

    def __init__(self, name="Библиотека"):
        self._name = ""
        self._books = []
        self._readers = []
        self._loans = MyMap()  # номер книги -> выдача
        self._next_book_id = 1
        self._next_reader_id = 1
        self._next_loan_id = 1
        self.name = name

    # ---------- свойства ----------

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        value = " ".join(str(value).split())
        if not value:
            raise ValueError("Название библиотеки не может быть пустым")
        self._name = value

    @property
    def books(self):
        return tuple(self._books)

    @books.setter
    def books(self, value):
        books = list(value)
        for book in books:
            if not isinstance(book, Book):
                raise TypeError("В каталоге могут быть только книги")
        self._books = books
        self._next_book_id = max((book.id for book in books), default=0) + 1
        for book_id in self._loans.keys():
            if Library._find_in(self._books, book_id) is None:
                self._loans.remove(book_id)

    @property
    def readers(self):
        return tuple(self._readers)

    @readers.setter
    def readers(self, value):
        readers = list(value)
        for reader in readers:
            if not isinstance(reader, Reader):
                raise TypeError("В списке читателей могут быть только читатели")
        self._readers = readers
        self._next_reader_id = max((reader.id for reader in readers), default=0) + 1
        for loan in self._loans.values():
            if Library._find_in(self._readers, loan.reader.id) is None:
                self._loans.remove(loan.book.id)

    @property
    def loans(self):
        return tuple(sorted(self._loans.values()))

    @loans.setter
    def loans(self, value):
        loans = MyMap()
        for loan in value:
            if not isinstance(loan, Loan):
                raise TypeError("Нужен список выдач")
            if loan.book.id in loans:
                raise LibraryError(f"Книга {loan.book} выдана дважды")
            loans.put(loan.book.id, loan)
        self._loans = loans
        self._next_loan_id = max((loan.id for loan in loans.values()), default=0) + 1

    # ---------- книги ----------

    @staticmethod
    def _find_in(items, item_id):
        for item in items:
            if item.id == item_id:
                return item
        return None

    def find_book(self, book_id):
        book = Library._find_in(self._books, book_id)
        if book is None:
            raise LibraryError(f"Книга с номером {book_id} не найдена")
        return book

    def add_book(self, title, author, year, genre):
        book = Book(self._next_book_id, title, author, year, genre)
        if book in self._books:
            raise LibraryError(f"Книга {book} уже есть в каталоге")
        self._books.append(book)
        self._next_book_id += 1
        return book

    def update_book(self, book_id, title, author, year, genre):
        book = self.find_book(book_id)
        changed = Book(book_id, title, author, year, genre)  # сразу проверяем все поля
        for other in self._books:
            if other.id != book_id and other == changed:
                raise LibraryError(f"Книга {changed} уже есть в каталоге")
        book.title = changed.title
        book.author = changed.author
        book.year = changed.year
        book.genre = changed.genre
        return book

    def remove_book(self, book_id):
        book = self.find_book(book_id)
        if not self.is_available(book):
            raise LibraryError(f"Книга {book} сейчас у читателя, сначала её нужно вернуть")
        self._books.remove(book)
        return book

    def search_books(self, text="", genre=None):
        return [book for book in self._books
                if book.matches(text) and (genre is None or book.genre == genre)]

    def is_available(self, book):
        return book.id not in self._loans

    def available_books(self):
        return [book for book in self._books if self.is_available(book)]

    def holder_of(self, book):
        loan = self._loans.get(book.id)
        return None if loan is None else loan.reader

    # ---------- читатели ----------

    def find_reader(self, reader_id):
        reader = Library._find_in(self._readers, reader_id)
        if reader is None:
            raise LibraryError(f"Читатель с номером {reader_id} не найден")
        return reader

    def _check_phone_free(self, reader):
        for other in self._readers:
            if other.id != reader.id and other.phone_digits() == reader.phone_digits():
                raise LibraryError(f"Телефон {reader.phone} уже записан у читателя {other.full_name}")

    def add_reader(self, full_name, phone):
        reader = Reader(self._next_reader_id, full_name, phone)
        self._check_phone_free(reader)
        self._readers.append(reader)
        self._next_reader_id += 1
        return reader

    def update_reader(self, reader_id, full_name, phone):
        reader = self.find_reader(reader_id)
        changed = Reader(reader_id, full_name, phone)
        self._check_phone_free(changed)
        reader.full_name = changed.full_name
        reader.phone = changed.phone
        return reader

    def remove_reader(self, reader_id):
        reader = self.find_reader(reader_id)
        if self.reader_loans(reader):
            raise LibraryError(f"У читателя {reader.full_name} есть невозвращённые книги")
        self._readers.remove(reader)
        return reader

    def search_readers(self, text=""):
        return [reader for reader in self._readers if reader.matches(text)]

    def reader_loans(self, reader):
        return sorted(loan for loan in self._loans.values() if loan.reader.id == reader.id)

    # ---------- выдача ----------

    def find_loan(self, loan_id):
        loan = Library._find_in(self._loans.values(), loan_id)
        if loan is None:
            raise LibraryError(f"Выдача с номером {loan_id} не найдена")
        return loan

    def issue_book(self, book_id, reader_id, issued_at=None):
        book = self.find_book(book_id)
        reader = self.find_reader(reader_id)
        if not self.is_available(book):
            raise LibraryError(f"Книга {book} уже выдана читателю {self.holder_of(book).full_name}")
        if len(self.reader_loans(reader)) >= Library.MAX_BOOKS_PER_READER:
            raise LibraryError(f"У читателя {reader.full_name} уже "
                               f"{Library.MAX_BOOKS_PER_READER} книги, больше выдавать нельзя")
        loan = Loan(self._next_loan_id, book, reader, issued_at or datetime.now())
        self._loans.put(book.id, loan)
        self._next_loan_id += 1
        return loan

    def return_book(self, book_id):
        book = self.find_book(book_id)
        if self.is_available(book):
            raise LibraryError(f"Книга {book} и так в библиотеке")
        return self._loans.remove(book.id)

    def genre_stats(self):
        """Жанр -> (всего книг, из них выдано). Возвращает MyMap."""
        stats = MyMap()
        for genre in Book.GENRES:
            stats.put(genre, (0, 0))
        for book in self._books:
            total, issued = stats.get(book.genre)
            stats.put(book.genre, (total + 1, issued + (0 if self.is_available(book) else 1)))
        return stats

    # ---------- специальные методы ----------

    def sort_key(self):
        return (self._name.lower(), len(self._books), len(self._readers))

    def __len__(self):
        """Количество книг в каталоге."""
        return len(self._books)

    def __iter__(self):
        return iter(self.books)

    def __contains__(self, item):
        """Можно проверить и книгу, и читателя: book in library, reader in library."""
        if isinstance(item, Book):
            return item in self._books
        if isinstance(item, Reader):
            return item in self._readers
        return False

    def __eq__(self, other):
        if not isinstance(other, Library):
            return NotImplemented
        return (self._name == other.name and self.books == other.books
                and self.readers == other.readers and self.loans == other.loans)

    def __hash__(self):
        return hash(self._name)

    def __repr__(self):
        return (f"Library(name={self._name!r}, books={len(self._books)}, "
                f"readers={len(self._readers)}, loans={len(self._loans)})")

    def __str__(self):
        return (f"{self._name}: книг {len(self._books)}, читателей {len(self._readers)}, "
                f"выдано {len(self._loans)}")

    # ---------- тестовые данные ----------

    @staticmethod
    def create_demo():
        library = Library("Библиотека МТИ")
        books = (
            ("Мастер и Маргарита", "М. А. Булгаков", 1967, "Роман"),
            ("Преступление и наказание", "Ф. М. Достоевский", 1866, "Роман"),
            ("Война и мир", "Л. Н. Толстой", 1869, "Роман"),
            ("Пикник на обочине", "А. и Б. Стругацкие", 1972, "Фантастика"),
            ("Солярис", "С. Лем", 1961, "Фантастика"),
            ("Убийство в «Восточном экспрессе»", "А. Кристи", 1934, "Детектив"),
            ("Собака Баскервилей", "А. Конан Дойл", 1902, "Детектив"),
            ("Евгений Онегин", "А. С. Пушкин", 1833, "Поэзия"),
            ("Краткая история времени", "С. Хокинг", 1988, "Научная литература"),
            ("Совершенный код", "С. Макконнелл", 2004, "Учебник"),
            ("Изучаем Python", "М. Лутц", 2019, "Учебник"),
            ("Чистый код", "Р. Мартин", 2008, "Учебник"),
        )
        for title, author, year, genre in books:
            library.add_book(title, author, year, genre)

        readers = (
            ("Иванов Иван Иванович", "+7 914 100-20-30"),
            ("Петрова Анна Сергеевна", "+7 914 200-30-40"),
            ("Сидоров Пётр Алексеевич", "+7 924 300-40-50"),
            ("Кузнецова Мария Игоревна", "+7 924 400-50-60"),
            ("Смирнов Алексей Петрович", "+7 914 500-60-70"),
            ("Васильева Ольга Николаевна", "+7 984 600-70-80"),
            ("Николаев Дмитрий Олегович", "+7 984 700-80-90"),
            ("Федорова Екатерина Андреевна", "+7 914 800-90-10"),
            ("Алексеев Сергей Викторович", "+7 924 900-10-20"),
            ("Григорьева Наталья Павловна", "+7 914 111-22-33"),
        )
        for full_name, phone in readers:
            library.add_reader(full_name, phone)

        now = datetime.now()
        library.issue_book(1, 2, now - timedelta(days=5))
        library.issue_book(4, 1, now - timedelta(days=3))
        library.issue_book(11, 5, now - timedelta(days=1))
        return library
