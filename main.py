import sys
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QDialog

from models.session import Session
from services.library import Library
from services.report import ReportWriter
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow


class Application:
    REPORT_FILE = Path(__file__).resolve().parent / "report.txt"

    @staticmethod
    def run():
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        login_dialog = LoginDialog()
        if login_dialog.exec_() != QDialog.Accepted:
            return 0
        session = Session(login_dialog.login, datetime.now())
        window = MainWindow(Library.create_demo(), session, ReportWriter(Application.REPORT_FILE))
        window.show()
        return app.exec_()


if __name__ == "__main__":
    sys.exit(Application.run())
