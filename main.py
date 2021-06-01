"""
This is the main Python executable for the planvec GUI 
running a PyQt5 Application.
"""
import os
import sys
from PyQt5.QtWidgets import QApplication
from qt_material import apply_stylesheet
from typing import List
from pathlib import Path

from planvec.gui.planvec_gui import PlanvecGui
from planvec.gui.RuntimeStyleSheets import WrappedMainWindowWithStyle
from config import planvec_config
from planvec.utils.path_utils import resource_path


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
    apply_stylesheet(app, theme=str(resource_path(Path('assets/planvec-theme.xml'))), extra=extra)
    stylesheet = app.styleSheet()
    with open(resource_path(Path('assets/custom.css'))) as file:
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
