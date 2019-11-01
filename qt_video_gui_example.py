"""This is a small example on how a PyQt5-based GUI would look like
which streams in the webcam camera and displays it inside a window."""

import sys
import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets


class Thread(QtCore.QThread):
    changePixmap = QtCore.pyqtSignal(QtGui.QImage)

    def run(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if ret:
                # https://stackoverflow.com/a/55468544/6622587
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgbImage = np.fliplr(rgbImage).copy()
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QtGui.QImage(rgbImage.data, w, h,
                                                 bytesPerLine,
                                                 QtGui.QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480,
                                             QtCore.Qt.KeepAspectRatio)
                self.changePixmap.emit(p)


class App(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 Video'
        self.left = 700
        self.top = 200
        self.width = 640
        self.height = 480
        self.init_ui()

    @QtCore.pyqtSlot(QtGui.QImage)
    def set_image(self, image):
        self.label.setPixmap(QtGui.QPixmap.fromImage(image))

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(660, 500)
        # create a label
        self.label = QtWidgets.QLabel(self)
        self.label.move(10, 10)
        self.label.resize(640, 480)
        th = Thread(self)
        th.changePixmap.connect(self.set_image)
        th.start()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
