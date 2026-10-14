from datetime import datetime

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QAbstractItemView, QComboBox, QFormLayout, QGroupBox, QHeaderView,
                             QLabel, QLineEdit, QListWidget, QListWidgetItem, QMenuBar,
                             QMessageBox, QPushButton, QSpinBox, QStatusBar, QTabWidget,
                             QTableWidget, QTableWidgetItem)

from models.book import Book


class AppButton(QPushButton):
    """Основная кнопка: одинаковая высота и курсор-рука."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(32)
        self.setCursor(Qt.PointingHandCursor)


class SecondaryButton(AppButton):
    """Второстепенная (серая) кнопка."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("secondaryButton")


class DangerButton(AppButton):
    """Красная кнопка для удаления."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("dangerButton")


class TitleLabel(QLabel):
    """Крупный жирный заголовок."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.setFont(font)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)


class InfoLabel(QLabel):
    """Подпись с переносом строк."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setStyleSheet("color: #55607a;")


class TextLineEdit(QLineEdit):
    """Поле ввода с подсказкой, ограничением длины и кнопкой очистки."""

    def __init__(self, placeholder="", max_length=100, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMaxLength(max_length)
        self.setClearButtonEnabled(True)

    def value(self):
        return self.text().strip()


class SearchLineEdit(TextLineEdit):
    """Поле поиска: Esc очищает строку."""

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.clear()
            return
        super().keyPressEvent(event)


class GenreComboBox(QComboBox):
    """Выбор жанра; может содержать первый пункт «Все жанры»."""

    ALL_GENRES = "Все жанры"

    def __init__(self, with_all=False, parent=None):
        super().__init__(parent)
        if with_all:
            self.addItem(GenreComboBox.ALL_GENRES)
        self.addItems(Book.GENRES)

    def current_genre(self):
        text = self.currentText()
        return None if text == GenreComboBox.ALL_GENRES else text

    def set_genre(self, genre):
        index = self.findText(genre)
        if index >= 0:
            self.setCurrentIndex(index)


class SortComboBox(QComboBox):
    """Выбор порядка сортировки. Сортировка идёт через сравнение объектов (__lt__)."""

    BY_ID = "По номеру"
    ASCENDING = "По алфавиту (А–Я)"
    DESCENDING = "По алфавиту (Я–А)"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.addItems((SortComboBox.BY_ID, SortComboBox.ASCENDING, SortComboBox.DESCENDING))

    def apply(self, items):
        mode = self.currentText()
        if mode == SortComboBox.ASCENDING:
            return sorted(items)
        if mode == SortComboBox.DESCENDING:
            return sorted(items, reverse=True)
        return sorted(items, key=SortComboBox.by_id)

    @staticmethod
    def by_id(item):
        return item.id


class EntityComboBox(QComboBox):
    """Выпадающий список объектов (книг или читателей), хранит их номера."""

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumContentsLength(25)
        self.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)

    def fill(self, entities):
        current = self.current_id()
        self.clear()
        for entity in entities:
            self.addItem(str(entity), entity.id)
        index = self.findData(current) if current is not None else -1
        self.setCurrentIndex(index if index >= 0 else (0 if self.count() else -1))

    def current_id(self):
        return self.currentData() if self.currentIndex() >= 0 else None


class YearSpinBox(QSpinBox):
    """Год издания. Колесо мыши меняет значение, только если поле в фокусе."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(Book.MIN_YEAR, datetime.now().year)
        self.setValue(2000)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAlignment(Qt.AlignRight)

    def wheelEvent(self, event):
        if not self.hasFocus():
            event.ignore()
            return
        super().wheelEvent(event)


class DataTable(QTableWidget):
    """Таблица только для чтения, выделение целыми строками. В первом столбце — номер."""

    def __init__(self, headers, stretch_column=1, parent=None):
        super().__init__(0, len(headers), parent)
        self.setHorizontalHeaderLabels(list(headers))
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(stretch_column, QHeaderView.Stretch)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    def fill(self, rows):
        self.clearSelection()
        self.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column, value in enumerate(row):
                item = QTableWidgetItem(value)
                item.setToolTip(value)
                alignment = Qt.AlignCenter if column == 0 else Qt.AlignLeft | Qt.AlignVCenter
                item.setTextAlignment(alignment)
                self.setItem(row_index, column, item)

    def selected_id(self):
        rows = self.selectionModel().selectedRows()
        if not rows:
            return None
        item = self.item(rows[0].row(), 0)
        return int(item.text()) if item is not None else None

    def select_by_id(self, entity_id):
        for row in range(self.rowCount()):
            item = self.item(row, 0)
            if item is not None and item.text() == str(entity_id):
                self.selectRow(row)
                return True
        return False


class TextList(QListWidget):
    """Список строк."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setWordWrap(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def fill_lines(self, lines):
        self.clear()
        self.addItems(list(lines))


class EntityList(TextList):
    """Список объектов, у каждой строки запомнен номер объекта."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

    def fill(self, entities):
        current = self.selected_id()
        self.clear()
        for entity in entities:
            item = QListWidgetItem(str(entity))
            item.setData(Qt.UserRole, entity.id)
            self.addItem(item)
            if entity.id == current:
                item.setSelected(True)
                self.setCurrentItem(item)

    def selected_id(self):
        items = self.selectedItems()
        return items[0].data(Qt.UserRole) if items else None


class FormGroupBox(QGroupBox):
    """Рамка с формой: подписи выровнены по правому краю, поля растягиваются."""

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        layout = QFormLayout(self)
        layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(8)

    def add_row(self, label, widget):
        self.layout().addRow(label, widget)

    def add_widget(self, widget):
        self.layout().addRow(widget)


class AppStatusBar(QStatusBar):
    """Строка состояния: временные сообщения слева, пользователь справа."""

    MESSAGE_TIMEOUT = 5000

    def __init__(self, parent=None):
        super().__init__(parent)
        self._user_label = QLabel()
        self.addPermanentWidget(self._user_label)

    @property
    def user_text(self):
        return self._user_label.text()

    @user_text.setter
    def user_text(self, value):
        self._user_label.setText(value)

    def show_info(self, text):
        self.showMessage(text, AppStatusBar.MESSAGE_TIMEOUT)


class AppMenuBar(QMenuBar):
    """Меню приложения. Наружу отдаёт сигналы, а не сами пункты меню."""

    exit_requested = pyqtSignal()
    about_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        file_menu = self.addMenu("Файл")
        exit_action = file_menu.addAction("Выход")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.exit_requested.emit)
        help_menu = self.addMenu("Справка")
        about_action = help_menu.addAction("О программе")
        about_action.triggered.connect(self.about_requested.emit)


class AppTabWidget(QTabWidget):
    """Вкладки главного окна."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDocumentMode(True)
        self.tabBar().setExpanding(False)


class MessageBox(QMessageBox):
    """Готовые диалоги сообщений."""

    @staticmethod
    def info(parent, title, text):
        QMessageBox.information(parent, title, text)

    @staticmethod
    def error(parent, title, text):
        QMessageBox.warning(parent, title, text)

    @staticmethod
    def confirm(parent, title, text):
        answer = QMessageBox.question(parent, title, text,
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return answer == QMessageBox.Yes
