"""
This is the main Python executable for the planvec GUI 
running a PyQt5 Application.
"""

import sys
from PyQt5.QtWidgets import QApplication

from planvec.gui import PlanvecGui
from config import CONFIG

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PlanvecGui.PlanvecGui(CONFIG)
    sys.exit(app.exec_())
