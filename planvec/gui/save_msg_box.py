from typing import Callable

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox, QLabel, QLineEdit, QVBoxLayout, QLayout

from planvec.gui.datamanager import DataManager
from planvec.utils.string_utils import is_empty_string


class SaveMsgBox(QMessageBox):
    def __init__(self, save_slot: Callable, data_manager: DataManager,
                 school_name: str, team_name: str, parent=None) -> None:
        super(SaveMsgBox, self).__init__(parent)
        self.save_slot = save_slot
        self.data_manager = data_manager
        self.school_name = school_name
        self.team_name = team_name
        self.line_edit = None
        self.setup()

    def setup(self) -> None:
        self.setIcon(QMessageBox.Question)
        self.setWindowTitle("Bild speichern")

        self.setText("Bild wirklich speichern?")
        self.setInformativeText(f"Schulname: {self.school_name} \nTeamname: {self.team_name}")
        team_names = self.data_manager.load_all_team_names(self.school_name)
        team_names_str = f'Folgende Gruppen existieren bereits für {self.school_name}:'
        if len(team_names) == 0:
            team_names_str = 'Es existieren noch keine Gruppen.'
        for team in team_names:
            # n_images = len(self.data_manager.load_team_img_names(team))
            team_names_str += f'\n    {team}'
        info_label = QLabel(team_names_str)

        team_layout = QVBoxLayout()
        team_layout.addWidget(info_label)

        self.layout().addLayout(team_layout, 3, 0, 1, 3,
                                QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.buttonClicked.connect(self.save_slot)

    @staticmethod
    def validate_school_name(school_name: str) -> bool:
        return not is_empty_string(school_name)

    @staticmethod
    def validate_team_name(team_name: str) -> bool:
        return not is_empty_string(team_name)

    def execute(self):
        self.exec_()
