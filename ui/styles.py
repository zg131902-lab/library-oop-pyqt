class Styles:
    MAIN = """
    QMainWindow, QDialog {
        background: #f4f6fb;
    }
    QGroupBox {
        border: 1px solid #c9cfdd;
        border-radius: 6px;
        margin-top: 14px;
        padding: 12px 10px 10px 10px;
        background: #ffffff;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 4px;
        color: #2f3b52;
    }
    QPushButton {
        background: #3d6fd9;
        color: #ffffff;
        border: none;
        border-radius: 4px;
        padding: 6px 14px;
    }
    QPushButton:hover {
        background: #2f5bbd;
    }
    QPushButton:pressed {
        background: #254a9c;
    }
    QPushButton#secondaryButton {
        background: #e3e8f4;
        color: #2f3b52;
    }
    QPushButton#secondaryButton:hover {
        background: #d3dbee;
    }
    QPushButton#dangerButton {
        background: #d9534f;
    }
    QPushButton#dangerButton:hover {
        background: #c13f3b;
    }
    QLineEdit, QComboBox, QSpinBox {
        min-height: 24px;
        padding: 2px 6px;
        border: 1px solid #c9cfdd;
        border-radius: 4px;
        background: #ffffff;
    }
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
        border: 1px solid #3d6fd9;
    }
    QTableWidget, QListWidget {
        background: #ffffff;
        border: 1px solid #c9cfdd;
        border-radius: 4px;
        selection-background-color: #3d6fd9;
        selection-color: #ffffff;
    }
    QHeaderView::section {
        background: #e3e8f4;
        padding: 4px;
        border: none;
        border-right: 1px solid #c9cfdd;
    }
    """
