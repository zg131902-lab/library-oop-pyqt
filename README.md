# Библиотека — учёт книг и читателей (PyQt5)

Проект по дисциплине «Объектно-ориентированное программирование».

Настольное приложение для небольшой библиотеки: каталог книг, список читателей,
выдача и возврат книг, статистика по жанрам. При закрытии приложение сохраняет
отчёт о сеансе работы в файл `report.txt`.

## Запуск

Нужен Python 3.9 или новее.

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
python main.py
```

При запуске открывается окно входа: логин от 3 до 20 символов (латиница, цифры, `_`).
После закрытия главного окна рядом с `main.py` появляется `report.txt`:

```
+-------------------------------------------------+
| login   | time_in             | time_out            |
|---------|---------------------|---------------------|
| student | 14.10.2026 10:00:00 | 14.10.2026 10:05:00 |
+-------------------------------------------------+
```

Каждый новый сеанс добавляется в таблицу отдельной строкой. Формат времени `%d.%m.%Y %H:%M:%S`.

Тесты:

```bash
python -m unittest
```

## Возможности

- **Книги**: добавление, изменение, удаление, поиск по названию и автору, фильтр по жанру,
  сортировка по номеру и по алфавиту. Выданную книгу удалить нельзя, дубликат добавить нельзя.
- **Читатели**: добавление, изменение, удаление, поиск; видно, какие книги у читателя на руках.
  Телефон проверяется, один телефон — один читатель.
- **Выдача книг**: выдать свободную книгу читателю (не больше 3 книг на человека), вернуть книгу,
  статистика по жанрам.

## Структура проекта

```
main.py                    класс Application — точка входа
models/
    base.py                Comparable — абстрактный класс, сравнение объектов
    entity.py              Entity — абстрактная сущность с номером
    book.py                Book — книга
    reader.py              Reader — читатель
    loan.py                Loan — выдача книги
    session.py             Session — сеанс работы (для отчёта)
structures/
    base_container.py      BaseContainer — абстрактный контейнер
    pair.py                Pair — пара «ключ — значение»
    my_map.py              MyMap — своё отображение вместо dict
services/
    library.py             Library — логика библиотеки, LibraryError
    report.py              ReportWriter — отчёт report.txt
ui/
    styles.py              Styles — стили окна
    widgets.py             переопределённые компоненты окна
    login_dialog.py        LoginDialog — окно входа
    main_window.py         MainWindow — главное окно
tests/
    test_models.py         тесты (unittest)
```

## Выполнение требований

| Требование | Где выполнено |
|---|---|
| Все сущности описаны через классы | `models/`, `structures/`, `services/`, `ui/`; запуск тоже через класс `Application` |
| Переопределить не менее 10 компонентов окна | `ui/widgets.py`: `AppButton`, `SecondaryButton`, `DangerButton`, `TitleLabel`, `InfoLabel`, `TextLineEdit`, `SearchLineEdit`, `GenreComboBox`, `SortComboBox`, `EntityComboBox`, `YearSpinBox`, `DataTable`, `TextList`, `EntityList`, `FormGroupBox`, `AppStatusBar`, `AppMenuBar`, `AppTabWidget`, `MessageBox`; а также `LoginDialog` (QDialog) и `MainWindow` (QMainWindow, переопределён `closeEvent`) |
| Функциональность только через методы класса или объекта | вся логика в методах; служебные методы — `@staticmethod` (`Entity.check_text`, `Reader.only_digits`, `Session.from_row`, `ReportWriter.build_table`, `Library.create_demo` и др.) |
| Сущности наследуются от абстрактного класса | `Comparable(ABC)` → `Entity` → `Book`, `Reader`, `Loan`; `Comparable` → `Session`, `Pair`; `BaseContainer(ABC)` → `MyMap` |
| Не менее 3 специальных методов + `__eq__`, `__repr__`, `__str__` | во всех классах моделей есть `__eq__`, `__repr__`, `__str__`, `__hash__`, а от `Comparable` — `__lt__`, `__le__`, `__gt__`, `__ge__`; в `MyMap` ещё `__len__`, `__iter__`, `__contains__`, `__getitem__`, `__setitem__`, `__delitem__` |
| Классы сравнимы | `Comparable` задаёт сравнение по `sort_key()`; сортировка в интерфейсе делается обычным `sorted()` |
| Геттеры и сеттеры у атрибутов | `@property` с сеттерами и проверкой значений у всех атрибутов моделей, `Library`, `ReportWriter`, `LoginDialog`, `MainWindow` |
| Запрещён `dict` | словари нигде не используются; для «ключ — значение» сделан свой класс `MyMap` (выдачи книг, статистика по жанрам) |
| Не менее 5 UI-компонентов | кнопки, поля ввода, выпадающие списки, поле года, таблицы, списки, рамки форм, вкладки, меню, строка состояния, диалоги |
| Не менее 10 пользовательских объектов в коллекциях | при запуске создаются 12 книг, 10 читателей и 3 выдачи (`Library.create_demo`), хранятся в `list` |
| Все компоненты выровнены | только менеджеры компоновки (`QHBoxLayout`, `QVBoxLayout`, `QFormLayout`), подписи формы выровнены по правому краю |
| (*) Отчёт при закрытии | `MainWindow.closeEvent` → `ReportWriter.save` пишет таблицу `login / time_in / time_out` в `report.txt` |
