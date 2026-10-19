from pathlib import Path

from models.session import Session
from structures.base_container import BaseContainer


class ReportWriter(BaseContainer):
    """Пишет отчёт о сеансах работы приложения в текстовый файл в виде таблицы.

    Сам отчёт — контейнер сеансов: len(report), session in report, for session in report.
    """

    HEADERS = ("login", "time_in", "time_out")

    def __init__(self, path):
        self._path = Path(path)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = Path(value)

    def load(self):
        """Читает сеансы, которые уже записаны в файл."""
        if not self._path.exists():
            return []
        sessions = []
        for line in self._path.read_text(encoding="utf-8").splitlines():
            cells = ReportWriter.parse_line(line)
            if cells is None or cells == ReportWriter.HEADERS:
                continue
            try:
                sessions.append(Session.from_row(cells))
            except ValueError:
                continue  # испорченную строку просто пропускаем
        return sessions

    def save(self, session):
        """Добавляет сеанс к отчёту и перезаписывает файл."""
        sessions = self.load()
        sessions.append(session)
        self._path.write_text(ReportWriter.build_table(sorted(sessions)), encoding="utf-8")

    @staticmethod
    def parse_line(line):
        line = line.strip()
        if not line.startswith("|") or line.startswith("|-") or not line.endswith("|"):
            return None
        cells = tuple(cell.strip() for cell in line[1:-1].split("|"))
        return cells if len(cells) == len(ReportWriter.HEADERS) else None

    @staticmethod
    def format_row(cells, widths):
        return "| " + " | ".join(cell.ljust(width) for cell, width in zip(cells, widths)) + " |"

    @staticmethod
    def build_table(sessions):
        rows = [session.to_row() for session in sessions]
        widths = [len(header) for header in ReportWriter.HEADERS]
        for row in rows:
            for index, cell in enumerate(row):
                widths[index] = max(widths[index], len(cell))
        header = ReportWriter.format_row(ReportWriter.HEADERS, widths)
        border = "+" + "-" * (len(header) - 2) + "+"
        separator = "|" + "|".join("-" * (width + 2) for width in widths) + "|"
        lines = [border, header, separator]
        lines += [ReportWriter.format_row(row, widths) for row in rows]
        lines.append(border)
        return "\n".join(lines) + "\n"

    def clear(self):
        """Оставляет в файле пустую таблицу (только заголовок)."""
        self._path.write_text(ReportWriter.build_table([]), encoding="utf-8")

    def sort_key(self):
        return (str(self._path),)

    def __len__(self):
        return len(self.load())

    def __iter__(self):
        return iter(self.load())

    def __contains__(self, session):
        return session in self.load()

    def __eq__(self, other):
        if not isinstance(other, ReportWriter):
            return NotImplemented
        return self._path == other.path

    def __hash__(self):
        return hash(self._path)

    def __repr__(self):
        return f"ReportWriter(path={str(self._path)!r})"

    def __str__(self):
        return f"Отчёт {self._path.name}"
