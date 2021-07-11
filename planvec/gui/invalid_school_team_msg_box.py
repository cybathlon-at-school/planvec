from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox, QLabel, QStackedLayout

from planvec.gui.datamanager import DataManager


class InvalidSchoolTeamMsgBox(QMessageBox):
    def __init__(self, data_manager: DataManager, school_name: str, team_name: str, parent=None) -> None:
        super(InvalidSchoolTeamMsgBox, self).__init__(parent)
        self.data_manager = data_manager
        self.school_name = school_name
        self.team_name = team_name
        self.setup()

    def setup(self):
        self.setIcon(QMessageBox.Critical)
        self.setText("Bitte Schul- und Team-namen eingeben!")
        self.setWindowTitle("Fehler")
        self.setStandardButtons(QMessageBox.Ok)

    def execute(self):
        self.exec_()
