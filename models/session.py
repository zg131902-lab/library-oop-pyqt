import re
from datetime import datetime

from models.base import Comparable


class Session(Comparable):
    TIME_FORMAT = "%d.%m.%Y %H:%M:%S"
    LOGIN_PATTERN = re.compile(r"^[A-Za-z0-9_]{3,20}$")
    EMPTY_TIME = "-"

    def __init__(self, login, time_in, time_out=None):
        self._login = ""
        self._time_in = None
        self._time_out = None
        self.login = login
        self.time_in = time_in
        self.time_out = time_out

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, value):
        self._login = Session.check_login(value)

    @property
    def time_in(self):
        return self._time_in

    @time_in.setter
    def time_in(self, value):
        if not isinstance(value, datetime):
            raise ValueError("Время входа должно быть датой")
        if self._time_out is not None and value > self._time_out:
            raise ValueError("Время входа не может быть позже времени выхода")
        self._time_in = value

    @property
    def time_out(self):
        return self._time_out

    @time_out.setter
    def time_out(self, value):
        if value is not None:
            if not isinstance(value, datetime):
                raise ValueError("Время выхода должно быть датой")
            if value < self._time_in:
                raise ValueError("Время выхода не может быть раньше времени входа")
        self._time_out = value

    @staticmethod
    def check_login(value):
        if not isinstance(value, str) or not Session.LOGIN_PATTERN.match(value.strip()):
            raise ValueError("Логин: от 3 до 20 символов, только латинские буквы, цифры и _")
        return value.strip()

    @staticmethod
    def format_time(value):
        return Session.EMPTY_TIME if value is None else value.strftime(Session.TIME_FORMAT)

    @staticmethod
    def from_row(cells):
        login, time_in, time_out = cells
        time_out_value = None
        if time_out != Session.EMPTY_TIME:
            time_out_value = datetime.strptime(time_out, Session.TIME_FORMAT)
        return Session(login, datetime.strptime(time_in, Session.TIME_FORMAT), time_out_value)

    def sort_key(self):
        return (self._time_in, self._login)

    def to_row(self):
        return (self._login, Session.format_time(self._time_in), Session.format_time(self._time_out))

    def __eq__(self, other):
        if not isinstance(other, Session):
            return NotImplemented
        return self.to_row() == other.to_row()

    def __hash__(self):
        return hash(self.to_row())

    def __repr__(self):
        return f"Session(login={self._login!r}, time_in={self._time_in!r}, time_out={self._time_out!r})"

    def __str__(self):
        login, time_in, time_out = self.to_row()
        return f"{login}: {time_in} — {time_out}"
