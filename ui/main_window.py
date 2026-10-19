from datetime import datetime

from PyQt5.QtWidgets import QHBoxLayout, QMainWindow, QVBoxLayout, QWidget

from services.library import LibraryError
from ui.styles import Styles
from ui.widgets import (AppButton, AppMenuBar, AppStatusBar, AppTabWidget, DangerButton, DataTable,
                        EntityComboBox, EntityList, FormGroupBox, GenreComboBox,
                        MessageBox, SearchLineEdit, SecondaryButton, SortComboBox, TextLineEdit,
                        TextList, TitleLabel, YearSpinBox)


class MainWindow(QMainWindow):
    BOOK_HEADERS = ("№", "Название", "Автор", "Год", "Жанр", "Статус")
    LOAN_HEADERS = ("№", "Книга", "Читатель", "Дата выдачи")

    def __init__(self, library, session, report_writer, parent=None):
        super().__init__(parent)
        self._library = library
        self._session = session
        self._report_writer = report_writer
        self._report_saved = False

        self.setWindowTitle(f"{library.name} — учёт книг и читателей")
        self.resize(1300, 720)
        self.setMinimumSize(1100, 620)
        self.setStyleSheet(Styles.MAIN)

        self._init_menu()
        self._init_status_bar()
        self._init_tabs()
        self.refresh_all()
        self._status_bar.show_info(f"Добро пожаловать, {session.login}!")

    @property
    def library(self):
        return self._library

    @library.setter
    def library(self, value):
        self._library = value
        self.refresh_all()

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value
        self._update_user_text()

    @property
    def report_writer(self):
        return self._report_writer

    @report_writer.setter
    def report_writer(self, value):
        self._report_writer = value

    def _init_menu(self):
        menu_bar = AppMenuBar(self)
        menu_bar.exit_requested.connect(self.close)
        menu_bar.about_requested.connect(self.show_about)
        self.setMenuBar(menu_bar)

    def _init_status_bar(self):
        self._status_bar = AppStatusBar(self)
        self.setStatusBar(self._status_bar)
        self._update_user_text()

    def _update_user_text(self):
        self._status_bar.user_text = (f"Пользователь: {self._session.login}  |  "
                                      f"вход: {self._session.to_row()[1]}")

    def _init_tabs(self):
        tabs = AppTabWidget(self)
        tabs.addTab(self._create_books_tab(), "Книги")
        tabs.addTab(self._create_readers_tab(), "Читатели")
        tabs.addTab(self._create_loans_tab(), "Выдача книг")
        self.setCentralWidget(tabs)

    def _create_books_tab(self):
        page = QWidget()
        root = QHBoxLayout(page)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        left = QVBoxLayout()
        left.addWidget(TitleLabel("Каталог книг"))
        filters = QHBoxLayout()
        self._book_search = SearchLineEdit("Поиск по названию или автору (Esc — очистить)")
        self._genre_filter = GenreComboBox(with_all=True)
        self._book_sort = SortComboBox()
        filters.addWidget(self._book_search, 3)
        filters.addWidget(self._genre_filter, 1)
        filters.addWidget(self._book_sort, 1)
        left.addLayout(filters)
        self._books_table = DataTable(MainWindow.BOOK_HEADERS)
        left.addWidget(self._books_table)
        root.addLayout(left, 3)

        right = QVBoxLayout()
        form = FormGroupBox("Карточка книги")
        self._title_edit = TextLineEdit("Например: Мастер и Маргарита")
        self._author_edit = TextLineEdit("Например: М. А. Булгаков")
        self._year_spin = YearSpinBox()
        self._genre_combo = GenreComboBox()
        form.add_row("Название:", self._title_edit)
        form.add_row("Автор:", self._author_edit)
        form.add_row("Год издания:", self._year_spin)
        form.add_row("Жанр:", self._genre_combo)
        right.addWidget(form)

        add_button = AppButton("Добавить книгу")
        save_button = AppButton("Сохранить изменения")
        clear_button = SecondaryButton("Очистить форму")
        delete_button = DangerButton("Удалить книгу")
        for button in (add_button, save_button, clear_button, delete_button):
            right.addWidget(button)
        right.addStretch()
        root.addLayout(right, 1)

        self._book_search.textChanged.connect(self.refresh_books)
        self._genre_filter.currentIndexChanged.connect(self.refresh_books)
        self._book_sort.currentIndexChanged.connect(self.refresh_books)
        self._books_table.itemSelectionChanged.connect(self.on_book_selected)
        add_button.clicked.connect(self.on_add_book)
        save_button.clicked.connect(self.on_save_book)
        clear_button.clicked.connect(self.clear_book_form)
        delete_button.clicked.connect(self.on_delete_book)
        return page

    def _create_readers_tab(self):
        page = QWidget()
        root = QHBoxLayout(page)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        left = QVBoxLayout()
        left.addWidget(TitleLabel("Читатели"))
        filters = QHBoxLayout()
        self._reader_search = SearchLineEdit("Поиск по ФИО или телефону (Esc — очистить)")
        self._reader_sort = SortComboBox()
        filters.addWidget(self._reader_search, 3)
        filters.addWidget(self._reader_sort, 1)
        left.addLayout(filters)
        self._readers_list = EntityList()
        left.addWidget(self._readers_list)
        root.addLayout(left, 3)

        right = QVBoxLayout()
        form = FormGroupBox("Карточка читателя")
        self._name_edit = TextLineEdit("Фамилия Имя Отчество")
        self._phone_edit = TextLineEdit("+7 914 123-45-67", 25)
        form.add_row("ФИО:", self._name_edit)
        form.add_row("Телефон:", self._phone_edit)
        right.addWidget(form)
        books_box = FormGroupBox("Книги на руках")
        self._reader_books_list = TextList()
        self._reader_books_list.setMaximumHeight(110)
        books_box.add_widget(self._reader_books_list)
        right.addWidget(books_box)

        add_button = AppButton("Добавить читателя")
        save_button = AppButton("Сохранить изменения")
        clear_button = SecondaryButton("Очистить форму")
        delete_button = DangerButton("Удалить читателя")
        for button in (add_button, save_button, clear_button, delete_button):
            right.addWidget(button)
        right.addStretch()
        root.addLayout(right, 2)

        self._reader_search.textChanged.connect(self.refresh_readers)
        self._reader_sort.currentIndexChanged.connect(self.refresh_readers)
        self._readers_list.itemSelectionChanged.connect(self.on_reader_selected)
        add_button.clicked.connect(self.on_add_reader)
        save_button.clicked.connect(self.on_save_reader)
        clear_button.clicked.connect(self.clear_reader_form)
        delete_button.clicked.connect(self.on_delete_reader)
        return page

    def _create_loans_tab(self):
        page = QWidget()
        root = QHBoxLayout(page)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        left = QVBoxLayout()
        form = FormGroupBox("Выдать книгу")
        self._loan_book_combo = EntityComboBox("Нет свободных книг")
        self._loan_reader_combo = EntityComboBox("Нет читателей")
        form.add_row("Книга:", self._loan_book_combo)
        form.add_row("Читатель:", self._loan_reader_combo)
        issue_button = AppButton("Выдать")
        form.add_widget(issue_button)
        left.addWidget(form)
        left.addWidget(TitleLabel("Книги на руках"))
        self._loans_table = DataTable(MainWindow.LOAN_HEADERS)
        left.addWidget(self._loans_table)
        return_button = AppButton("Вернуть выбранную книгу")
        left.addWidget(return_button)
        root.addLayout(left, 5)

        right = QVBoxLayout()
        right.addWidget(TitleLabel("Статистика по жанрам"))
        self._stats_list = TextList()
        right.addWidget(self._stats_list)
        root.addLayout(right, 2)

        issue_button.clicked.connect(self.on_issue_book)
        return_button.clicked.connect(self.on_return_book)
        return page

    def refresh_all(self):
        self.refresh_books()
        self.refresh_readers()
        self.refresh_loans()

    def refresh_books(self):
        books = self._library.search_books(self._book_search.value(),
                                           self._genre_filter.current_genre())
        rows = []
        for book in self._book_sort.apply(books):
            holder = self._library.holder_of(book)
            status = "В наличии" if holder is None else f"Выдана: {holder.short_name()}"
            rows.append(book.to_row() + (status,))
        selected = self._books_table.selected_id()
        self._books_table.fill(rows)
        if selected is not None:
            self._books_table.select_by_id(selected)

    def refresh_readers(self):
        readers = self._library.search_readers(self._reader_search.value())
        self._readers_list.fill(self._reader_sort.apply(readers))
        self.on_reader_selected()

    def refresh_loans(self):
        self._loan_book_combo.fill(sorted(self._library.available_books()))
        self._loan_reader_combo.fill(sorted(self._library.readers))
        self._loans_table.fill([loan.to_row() for loan in self._library.loans])
        lines = []
        for pair in self._library.genre_stats().items():
            total, issued = pair.value
            lines.append(f"{pair.key}: {total} шт., выдано {issued}")
        self._stats_list.fill_lines(lines)

    def on_book_selected(self):
        book_id = self._books_table.selected_id()
        if book_id is None:
            return
        book = self._library.find_book(book_id)
        self._title_edit.setText(book.title)
        self._author_edit.setText(book.author)
        self._year_spin.setValue(book.year)
        self._genre_combo.set_genre(book.genre)

    def _book_form_values(self):
        return (self._title_edit.value(), self._author_edit.value(),
                self._year_spin.value(), self._genre_combo.current_genre())

    def on_add_book(self):
        try:
            book = self._library.add_book(*self._book_form_values())
        except (ValueError, LibraryError) as error:
            MessageBox.error(self, "Книга не добавлена", str(error))
            return
        self.refresh_all()
        self._books_table.select_by_id(book.id)
        self._status_bar.show_info(f"Добавлена книга {book}")

    def on_save_book(self):
        book_id = self._books_table.selected_id()
        if book_id is None:
            MessageBox.error(self, "Нет книги", "Сначала выберите книгу в таблице")
            return
        try:
            book = self._library.update_book(book_id, *self._book_form_values())
        except (ValueError, LibraryError) as error:
            MessageBox.error(self, "Изменения не сохранены", str(error))
            return
        self.refresh_all()
        self._status_bar.show_info(f"Сохранена книга {book}")

    def on_delete_book(self):
        book_id = self._books_table.selected_id()
        if book_id is None:
            MessageBox.error(self, "Нет книги", "Сначала выберите книгу в таблице")
            return
        book = self._library.find_book(book_id)
        if not MessageBox.confirm(self, "Удаление", f"Удалить книгу {book}?"):
            return
        try:
            self._library.remove_book(book_id)
        except LibraryError as error:
            MessageBox.error(self, "Книга не удалена", str(error))
            return
        self.clear_book_form()
        self.refresh_all()
        self._status_bar.show_info(f"Удалена книга {book}")

    def clear_book_form(self):
        self._books_table.clearSelection()
        self._title_edit.clear()
        self._author_edit.clear()
        self._year_spin.setValue(2000)
        self._genre_combo.setCurrentIndex(0)

    def on_reader_selected(self):
        reader_id = self._readers_list.selected_id()
        if reader_id is None:
            self._reader_books_list.fill_lines(("Выберите читателя в списке",))
            return
        reader = self._library.find_reader(reader_id)
        self._name_edit.setText(reader.full_name)
        self._phone_edit.setText(reader.phone)
        loans = self._library.reader_loans(reader)
        if loans:
            self._reader_books_list.fill_lines(str(loan.book) for loan in loans)
        else:
            self._reader_books_list.fill_lines(("Книг на руках нет",))

    def on_add_reader(self):
        try:
            reader = self._library.add_reader(self._name_edit.value(), self._phone_edit.value())
        except (ValueError, LibraryError) as error:
            MessageBox.error(self, "Читатель не добавлен", str(error))
            return
        self.refresh_all()
        self._status_bar.show_info(f"Добавлен читатель {reader.full_name}")

    def on_save_reader(self):
        reader_id = self._readers_list.selected_id()
        if reader_id is None:
            MessageBox.error(self, "Нет читателя", "Сначала выберите читателя в списке")
            return
        try:
            reader = self._library.update_reader(reader_id, self._name_edit.value(),
                                                 self._phone_edit.value())
        except (ValueError, LibraryError) as error:
            MessageBox.error(self, "Изменения не сохранены", str(error))
            return
        self.refresh_all()
        self._status_bar.show_info(f"Сохранён читатель {reader.full_name}")

    def on_delete_reader(self):
        reader_id = self._readers_list.selected_id()
        if reader_id is None:
            MessageBox.error(self, "Нет читателя", "Сначала выберите читателя в списке")
            return
        reader = self._library.find_reader(reader_id)
        if not MessageBox.confirm(self, "Удаление", f"Удалить читателя {reader.full_name}?"):
            return
        try:
            self._library.remove_reader(reader_id)
        except LibraryError as error:
            MessageBox.error(self, "Читатель не удалён", str(error))
            return
        self.clear_reader_form()
        self.refresh_all()
        self._status_bar.show_info(f"Удалён читатель {reader.full_name}")

    def clear_reader_form(self):
        self._readers_list.clearSelection()
        self._name_edit.clear()
        self._phone_edit.clear()

    def on_issue_book(self):
        book_id = self._loan_book_combo.current_id()
        reader_id = self._loan_reader_combo.current_id()
        if book_id is None or reader_id is None:
            MessageBox.error(self, "Выдача", "Выберите книгу и читателя")
            return
        try:
            loan = self._library.issue_book(book_id, reader_id)
        except LibraryError as error:
            MessageBox.error(self, "Книга не выдана", str(error))
            return
        self.refresh_all()
        self._status_bar.show_info(f"Выдано: {loan}")

    def on_return_book(self):
        loan_id = self._loans_table.selected_id()
        if loan_id is None:
            MessageBox.error(self, "Возврат", "Выберите выдачу в таблице")
            return
        try:
            loan = self._library.find_loan(loan_id)
            self._library.return_book(loan.book.id)
        except LibraryError as error:
            MessageBox.error(self, "Книга не возвращена", str(error))
            return
        self.refresh_all()
        self._status_bar.show_info(f"Возвращена книга {loan.book}")

    def show_about(self):
        MessageBox.info(self, "О программе",
                        "Учёт книг и читателей библиотеки.\n"
                        "Проект по дисциплине «Объектно-ориентированное программирование».\n"
                        "Python + PyQt5.")

    def save_report(self):
        if self._report_saved:
            return
        self._session.time_out = datetime.now()
        self._report_writer.save(self._session)
        self._report_saved = True

    def closeEvent(self, event):
        try:
            self.save_report()
        except OSError as error:
            MessageBox.error(self, "Отчёт не сохранён", f"Не удалось записать отчёт: {error}")
        event.accept()
