from typing import Callable

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox, QLabel, QLineEdit, QVBoxLayout, QLayout

from planvec.gui.datamanager import DataManager
from planvec.utils.string_utils import is_empty_string
from planvec.utils.date_utils import get_date_tag


class JamMsgBox(QMessageBox):
    def __init__(self, jam_slot: Callable, data_manager: DataManager,
                 school_name: str, team_name: str = None, parent=None) -> None:
        super(JamMsgBox, self).__init__(parent)
        self.jam_slot = jam_slot
        self.data_manager = data_manager
        self.school_name = school_name
        self.team_name = team_name
        self.line_edit = None
        self.setup()

    def setup(self) -> None:
        self.setIcon(QMessageBox.Question)
        self.setWindowTitle("PDF output generieren")

        self.setText(f"Output wirklich generieren (für {get_date_tag()} Ordner)?")
        self.setInformativeText(f"Schulname: {self.school_name}\n"
                                f"Teamname: {self.team_name if self.team_name else 'ALLE'}")
        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.buttonClicked.connect(self.jam_slot)

    @staticmethod
    def validate_school_name(school_name: str) -> bool:
        return not is_empty_string(school_name)

    @staticmethod
    def validate_team_name(team_name: str) -> bool:
        return not is_empty_string(team_name)

    def execute(self):
        self.exec_()
