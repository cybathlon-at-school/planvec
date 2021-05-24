from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QTimer, QEvent
from qt_material import apply_stylesheet, QtStyleTools

from planvec.gui.ui_generated.planvec_ui import Ui_planvec


class WrappedMainWindowWithStyle(QMainWindow, QtStyleTools):
    def __init__(self, q_app: QApplication) -> None:
        super().__init__()

        # PyQt5: Load Qt UI file
        self.ui = Ui_planvec()
        self.ui.setupUi(self)

        # Add classes to UI elements for css styling
        self.ui.appTitle.setProperty('class', 'app-title')
        self.ui.logo.setProperty('class', 'logo')
        self.ui.infoBox.setProperty('class', 'info-box')
        self.ui.settingsBox.setProperty('class', 'settings-box')
        self.ui.settingsAdvanced.setProperty('class', 'settings-box')
        self.ui.infoBoxInput.setProperty('class', 'info-box-input')

        q_app.installEventFilter(self)

        QTimer.singleShot(0, self.ui.settingsAdvanced.hide)  # hide the advanced setting module

        # TODO: Sind dies mouse tracking sachen wichtig?
        # self.main.setMouseTracking(1)
        self.ui.advancedOpenButton.setMouseTracking(1)
        self.ui.advancedCloseButton.setMouseTracking(1)
        # self.setMouseTracking(1)

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            if source == self.ui.advancedOpenButton:
                # print("Open Advanced")
                self.ui.settingsAdvanced.show()
                self.ui.settingsAdvanced.setGeometry(10, 296, 261, 449)

            if source == self.ui.advancedCloseButton:
                # print("Close Advanced")
                self.ui.settingsAdvanced.hide()

            # if source == self.main:
            #     print("Clicked elsewhere")
            #     self.main.settingsAdvanced.hide()

        return QMainWindow.eventFilter(self, source, event)
