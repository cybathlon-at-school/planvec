"""
This is the main Python executable for the planvec GUI 
running a PyQt5 Application.
"""

import sys
from PyQt5.QtWidgets import QApplication

import planvec
from planvec.gui import gui
from config import planvec_config

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = gui.PlanvecGui(planvec_config)
    sys.exit(app.exec_())
