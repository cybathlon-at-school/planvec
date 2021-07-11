from PyQt5.QtWidgets import QMessageBox

from planvec.gui.datamanager import DataManager


class TeamDirDialog(QMessageBox):
    def __init__(self, school_name: str, team_name: str, data_manager: DataManager, parent=None) -> None:
        super(TeamDirDialog, self).__init__(parent)
        self.school_name = school_name
        self.team_name = team_name
        self.data_manager = data_manager
        self.setup()

    def setup(self):
        text = 'Die Gruppe {} existiert noch nicht.\n' \
               'Neuen Ordner anlegen?'.format(self.team_name)
        self.setIcon(QMessageBox.Question)
        self.setText(text)
        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.buttonClicked.connect(self.ok_btn_slot)

    def execute(self):
        self.exec_()

    def ok_btn_slot(self, button_return):
        if button_return.text() == '&OK':
            self.data_manager.create_team_folder(self.school_name, self.team_name)
