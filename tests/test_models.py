import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from models.book import Book
from models.reader import Reader
from models.session import Session
from services.library import Library, LibraryError
from services.report import ReportWriter
from structures.my_map import MyMap


class ModelsTest(unittest.TestCase):

    def test_book(self):
        book = Book(1, "Солярис", "С. Лем", 1961, "Фантастика")
        other = Book(2, "Анна Каренина", "Л. Н. Толстой", 1878, "Роман")
        self.assertTrue(other < book)
        self.assertEqual(book, Book(7, "солярис", "с. лем", 1961, "Фантастика"))
        self.assertEqual(str(book), "«Солярис» — С. Лем (1961)")
        with self.assertRaises(ValueError):
            book.year = 3000

    def test_reader(self):
        with self.assertRaises(ValueError):
            Reader(1, "Иванов Иван", "123")

    def test_my_map(self):
        my_map = MyMap()
        my_map["a"] = 1
        my_map["a"] = 2
        self.assertEqual(my_map["a"], 2)
        self.assertEqual(len(my_map), 1)
        del my_map["a"]
        self.assertNotIn("a", my_map)


class LibraryTest(unittest.TestCase):

    def setUp(self):
        self.library = Library.create_demo()

    def test_demo_data(self):
        self.assertGreaterEqual(len(self.library.books), 10)
        self.assertGreaterEqual(len(self.library.readers), 10)

    def test_issue_and_return(self):
        self.library.issue_book(2, 3)
        with self.assertRaises(LibraryError):
            self.library.issue_book(2, 4)
        self.library.return_book(2)
        self.assertTrue(self.library.is_available(self.library.find_book(2)))

    def test_rules(self):
        with self.assertRaises(LibraryError):
            self.library.add_book("Солярис", "С. Лем", 1961, "Фантастика")
        with self.assertRaises(LibraryError):
            self.library.remove_book(1)
        for book_id in (2, 3, 5):
            self.library.issue_book(book_id, 3)
        with self.assertRaises(LibraryError):
            self.library.issue_book(6, 3)


class ReportTest(unittest.TestCase):

    def test_report(self):
        with tempfile.TemporaryDirectory() as folder:
            report = ReportWriter(Path(folder) / "report.txt")
            time_in = datetime(2026, 10, 14, 10, 0)
            report.save(Session("student", time_in, time_in.replace(minute=5)))
            text = report.path.read_text(encoding="utf-8")
            self.assertIn("| student | 14.10.2026 10:00:00 | 14.10.2026 10:05:00 |", text)
            self.assertEqual(len(report), 1)


if __name__ == "__main__":
    unittest.main()
