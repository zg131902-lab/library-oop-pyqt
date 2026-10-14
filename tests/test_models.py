import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from models.book import Book
from models.reader import Reader
from models.session import Session
from services.library import Library, LibraryError
from services.report import ReportWriter
from structures.my_map import MyMap


class BookTest(unittest.TestCase):

    def test_compare_and_sort(self):
        first = Book(1, "Солярис", "С. Лем", 1961, "Фантастика")
        second = Book(2, "Анна Каренина", "Л. Н. Толстой", 1878, "Роман")
        self.assertTrue(second < first)
        self.assertEqual(sorted([first, second]), [second, first])

    def test_equal_books(self):
        first = Book(1, "Солярис", "С. Лем", 1961, "Фантастика")
        second = Book(7, "солярис", "с. лем", 1961, "Фантастика")
        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))

    def test_str_and_repr(self):
        book = Book(1, "Солярис", "С. Лем", 1961, "Фантастика")
        self.assertEqual(str(book), "«Солярис» — С. Лем (1961)")
        self.assertIn("Book(id=1", repr(book))

    def test_setters_check_values(self):
        book = Book(1, "Солярис", "С. Лем", 1961, "Фантастика")
        with self.assertRaises(ValueError):
            book.title = "   "
        with self.assertRaises(ValueError):
            book.year = 3000
        with self.assertRaises(ValueError):
            book.genre = "Комиксы"


class ReaderTest(unittest.TestCase):

    def test_phone(self):
        reader = Reader(1, "Иванов Иван", "+7 914 100-20-30")
        self.assertEqual(reader.phone_digits(), "79141002030")
        with self.assertRaises(ValueError):
            reader.phone = "123"


class MyMapTest(unittest.TestCase):

    def test_put_get_remove(self):
        my_map = MyMap()
        my_map["a"] = 1
        my_map.put("b", 2)
        my_map["a"] = 10
        self.assertEqual(len(my_map), 2)
        self.assertEqual(my_map["a"], 10)
        self.assertIn("b", my_map)
        del my_map["b"]
        self.assertNotIn("b", my_map)
        self.assertEqual(my_map.get("b", 0), 0)
        with self.assertRaises(KeyError):
            my_map.remove("b")

    def test_equal(self):
        first = MyMap()
        second = MyMap()
        first.put(1, "x")
        first.put(2, "y")
        second.put(2, "y")
        second.put(1, "x")
        self.assertEqual(first, second)


class LibraryTest(unittest.TestCase):

    def setUp(self):
        self.library = Library.create_demo()

    def test_demo_has_ten_objects(self):
        self.assertGreaterEqual(len(self.library.books), 10)
        self.assertGreaterEqual(len(self.library.readers), 10)

    def test_issue_and_return(self):
        loan = self.library.issue_book(2, 3)
        self.assertFalse(self.library.is_available(loan.book))
        with self.assertRaises(LibraryError):
            self.library.issue_book(2, 4)
        self.library.return_book(2)
        self.assertTrue(self.library.is_available(loan.book))

    def test_cannot_add_duplicate(self):
        with self.assertRaises(LibraryError):
            self.library.add_book("Солярис", "С. Лем", 1961, "Фантастика")

    def test_cannot_remove_issued_book(self):
        with self.assertRaises(LibraryError):
            self.library.remove_book(1)

    def test_limit_per_reader(self):
        self.library.issue_book(2, 3)
        self.library.issue_book(3, 3)
        self.library.issue_book(5, 3)
        with self.assertRaises(LibraryError):
            self.library.issue_book(6, 3)


class ReportTest(unittest.TestCase):

    def test_report_table(self):
        with tempfile.TemporaryDirectory() as folder:
            writer = ReportWriter(Path(folder) / "report.txt")
            time_in = datetime(2026, 10, 14, 10, 0, 0)
            writer.save(Session("student", time_in, time_in + timedelta(minutes=5)))
            writer.save(Session("admin", time_in + timedelta(hours=1), time_in + timedelta(hours=2)))
            lines = writer.path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(lines[0], lines[-1])
            self.assertTrue(lines[1].startswith("| login"))
            self.assertIn("| student | 14.10.2026 10:00:00 | 14.10.2026 10:05:00 |", lines)
            self.assertEqual(len(writer.load()), 2)


if __name__ == "__main__":
    unittest.main()
