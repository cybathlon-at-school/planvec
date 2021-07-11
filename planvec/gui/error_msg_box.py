from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox, QLabel, QStackedLayout

from planvec.gui.datamanager import DataManager


class ErrorMsgBox(QMessageBox):
    def __init__(self, error_msg: str, parent=None) -> None:
        super(ErrorMsgBox, self).__init__(parent)
        self.error_msg = error_msg
        self.setup()

    def setup(self):
        self.setIcon(QMessageBox.Critical)
        self.setText(self.error_msg)
        self.setWindowTitle("Fehler")
        self.setStandardButtons(QMessageBox.Ok)

    def execute(self):
        self.exec_()
