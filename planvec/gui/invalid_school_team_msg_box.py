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
        self.setText("Bitte nicht-leere Schul- und Teamnamen eingeben!")
        self.setWindowTitle("Fehler")
        team_names = self.data_manager.load_all_team_names()
        team_names_str = 'Folgende Gruppen existieren bereits:'
        for team in team_names:
            # n_images = len(self.data_manager.load_team_img_names(team))
            team_names_str += f'\n    {team}'
        info_label = QLabel(team_names_str)
        team_layout = QStackedLayout()
        team_layout.addWidget(info_label)

        self.layout().addLayout(team_layout, 1, 0, QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)

        self.setStandardButtons(QMessageBox.Ok)

    def execute(self):
        self.exec_()
