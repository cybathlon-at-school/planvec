from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QMainWindow, QApplication, QShortcut
from PyQt5.QtCore import QTimer, QEvent
from qt_material import QtStyleTools

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
        self.ui.infoBoxOutput.setProperty('class', 'info-box-input')

        q_app.installEventFilter(self)

        QTimer.singleShot(0, self.ui.settingsAdvanced.hide)  # hide the advanced setting module

        self.ui.advancedOpenButton.setMouseTracking(1)
        self.ui.advancedCloseButton.setMouseTracking(1)

        self.quitShortcut = QShortcut(QKeySequence('Ctrl+Q'), self)
        self.quitShortcut.activated.connect(QApplication.instance().quit)

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            if source == self.ui.advancedOpenButton:
                self.ui.settingsAdvanced.show()
                self.ui.settingsAdvanced.setGeometry(10, 296, 261, 449)

            if source == self.ui.advancedCloseButton:
                self.ui.settingsAdvanced.hide()

        return QMainWindow.eventFilter(self, source, event)
