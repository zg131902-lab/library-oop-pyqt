from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QRegularExpressionValidator
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout

from models.session import Session
from ui.styles import Styles
from ui.widgets import AppButton, InfoLabel, MessageBox, SecondaryButton, TextLineEdit, TitleLabel


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._login = ""
        self.setWindowTitle("Вход")
        self.setModal(True)
        self.setFixedWidth(360)
        self.setStyleSheet(Styles.MAIN)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(TitleLabel("Библиотека"))
        layout.addWidget(InfoLabel("Введите логин: от 3 до 20 символов, латинские буквы, цифры и _"))

        self._login_edit = TextLineEdit("Логин", 20)
        self._login_edit.setValidator(
            QRegularExpressionValidator(QRegularExpression("[A-Za-z0-9_]{0,20}"), self))
        layout.addWidget(self._login_edit)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel_button = SecondaryButton("Отмена")
        ok_button = AppButton("Войти")
        ok_button.setDefault(True)
        buttons.addWidget(cancel_button)
        buttons.addWidget(ok_button)
        layout.addLayout(buttons)

        cancel_button.clicked.connect(self.reject)
        ok_button.clicked.connect(self.try_accept)

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, value):
        self._login = Session.check_login(value)
        self._login_edit.setText(self._login)

    def try_accept(self):
        try:
            self.login = self._login_edit.value()
        except ValueError as error:
            MessageBox.error(self, "Ошибка входа", str(error))
            return
        self.accept()
