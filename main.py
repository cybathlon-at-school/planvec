"""
This is the main Python executable for the planvec GUI 
running a PyQt5 Application.
"""
import os
import sys
from PyQt5.QtWidgets import QApplication
from qt_material import apply_stylesheet
from typing import List

import planvec
from planvec.gui.gui import PlanvecGui
from planvec.gui.ui_generated.RuntimeStyleSheets import WrappedMainWindowWithStyle
from planvec.common import UI_GENERATED_PATH
from config import planvec_config


def setup_application(argv: List[str]) -> QApplication:
    app = QApplication(argv)
    # Extra stylesheets
    extra = {
        # Button colors
        'danger': '#dc3545',
        'warning': '#ffc107',
        'success': '#17a2b8',
        # Font
        'font_family': 'Roboto',
    }
    apply_stylesheet(app, theme=str(UI_GENERATED_PATH / 'planvec-theme.xml'), extra=extra)
    stylesheet = app.styleSheet()
    with open(UI_GENERATED_PATH / 'custom.css') as file:
        app.setStyleSheet(stylesheet + file.read().format(**os.environ))
    return app


def main() -> None:
    app = setup_application(sys.argv)
    window = WrappedMainWindowWithStyle(app)
    gui = PlanvecGui(window.ui, window, planvec_config)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
