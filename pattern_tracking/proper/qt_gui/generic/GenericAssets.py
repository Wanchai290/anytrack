"""
A collection of functions used to represent generic information
"""
from PySide6.QtWidgets import QMessageBox, QWidget


class GenericAssets:

    @staticmethod
    def popup_message(title: str, message: str, is_error: bool, parent: QWidget = None):
        if is_error:
            icon = QMessageBox.Icon.Warning
        else:
            icon = QMessageBox.Icon.Information

        popup = QMessageBox(icon, title, message, parent=parent)
        popup.setFixedSize(240, 240)
        popup.exec()
