"""
This is the main Python executable for the planvec GUI 
running a PyQt5 Application.
"""

import sys
from PyQt5.QtWidgets import QApplication

from planvec.gui import PlanvecGui
from planvec.gui.gui_config import gui_config

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PlanvecGui.PlanvecGui(gui_config)
    sys.exit(app.exec_())
