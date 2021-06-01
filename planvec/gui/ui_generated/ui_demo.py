import os
# PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, QEvent
from PyQt5 import uic

from qt_material import apply_stylesheet, QtStyleTools

# Extra stylesheets
extra = {

    # Button colors
    'danger': '#dc3545',
    'warning': '#ffc107',
    'success': '#17a2b8',

    # Font
    'font_family': 'Roboto',
}


########################################################################
class RuntimeStylesheets(QMainWindow, QtStyleTools):

    def __init__(self):
        """"""
        super().__init__()

        # PyQt5: Load Qt UI file
        self.main = uic.loadUi('planvec.ui', self)

        # Add classes to UI elements for css stylingf
        self.main.appTitle.setProperty('class', 'app-title')
        self.main.logo.setProperty('class', 'logo')
        self.main.infoBox.setProperty('class', 'info-box')
        self.main.settingsBox.setProperty('class', 'settings-box')
        self.main.settingsAdvanced.setProperty('class', 'settings-box')
        self.main.infoBoxInput.setProperty('class', 'info-box-input')

        qApp.installEventFilter(self)

        QTimer.singleShot(0, self.main.settingsAdvanced.hide)  # hide the advanced setting module

        self.main.setMouseTracking(1)
        self.main.advancedOpenButton.setMouseTracking(1)
        self.main.advancedCloseButton.setMouseTracking(1)
        self.setMouseTracking(1)
        self.main.setMouseTracking(1)

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            if source == self.main.advancedOpenButton:
                # print("Open Advanced")
                self.main.settingsAdvanced.show()
                self.main.settingsAdvanced.setGeometry(10, 296, 261, 449)

            if source == self.main.advancedCloseButton:
                # print("Close Advanced")
                self.main.settingsAdvanced.hide()

            # if source == self.main:
            #     print("Clicked elsewhere")
            #     self.main.settingsAdvanced.hide()

        return QMainWindow.eventFilter(self, source, event)


if __name__ == "__main__":
    app = QApplication([])

    # Local file
    # QFontDatabase.addApplicationFont('Raleway-Regular.ttf')

    # # Set theme on in itialization
    # apply_stylesheet(app, theme + '.xml',
    #                  invert_secondary=(
    #                      'light' in theme and 'dark' not in theme),
    #                  extra=extra)

    apply_stylesheet(app, theme='planvec-theme.xml', extra=extra)  # load custom qt_material Theme

    # Load custom stylesheet
    stylesheet = app.styleSheet()
    with open('custom.css') as file:
        app.setStyleSheet(stylesheet + file.read().format(**os.environ))

    frame = RuntimeStylesheets()
    frame.main.show()
    app.exec_()
