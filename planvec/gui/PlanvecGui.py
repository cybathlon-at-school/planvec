import io
import os
import cv2
import time
from functools import partial
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QHBoxLayout, QGroupBox, QDialog, QVBoxLayout,
                             QGridLayout, QWidget)
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QImage
import numpy as np

from planvec import common
from planvec import conversions
import planvec.pipeline


class PlanvecGui(QMainWindow):
    """Main class for the PlanvecGui representing the
    main window and components."""

    toggle_canny_signal = QtCore.pyqtSignal()

    def __init__(self, gui_config):
        super().__init__()
        self.config = gui_config
        self.main_widget = QWidget()
        self.video_stream_thread = None
        self.initUI()

    def initUI(self):
        # Setup Main window properties
        self.setWindowTitle(self.config.window.title)
        self.setGeometry(self.config.window.left, self.config.window.top,
                         self.config.window.width, self.config.window.height)
        # Status Bar the bottom
        self.statusBar().showMessage('Systems charged, Master.')

        # Main Layout
        self.setCentralWidget(self.main_widget)
        self._create_main_layout()
        self.show()

    def _create_main_layout(self):
        """This is the layout for them main widget."""
        main_layout = QGridLayout()
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 1)
        main_layout.setRowStretch(0, 10)
        main_layout.setRowStretch(1, 1)

        # Video Widget
        video_label, processed_label = self._start_video_stream_label()
        main_layout.addWidget(
            video_label, 0, 0, alignment=QtCore.Qt.AlignCenter)

        # Processed image Widget
        # img_label = self._create_pixmap_label(file_path = os.path.join(common.PROJECT_ROOT_PATH, 'data/2019-10-09_16-21-38.jpg'))

        main_layout.addWidget(processed_label, 0, 1,
                              alignment=QtCore.Qt.AlignCenter)

        # Buttons Widget
        main_layout.addLayout(self._create_btns_layout(), 1, 0, 1, 2,
                              alignment=QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        self.main_widget.setLayout(main_layout)

    def _create_btns_layout(self):
        """This is a box with holding various buttons."""
        btns_layout = QHBoxLayout()
        save_btn = QPushButton("Save!")
        save_btn.setStyleSheet("background-color: #5DADE2")
        save_btn.clicked.connect(self.on_save_click)
        dummy_btn = QPushButton("Toggle Canny!")
        dummy_btn.setStyleSheet("background-color: #E67E22")
        dummy_btn.clicked.connect(self.video_stream_thread.toggle_canny_slot)
        btns_layout.addWidget(save_btn)
        btns_layout.addWidget(dummy_btn)
        return btns_layout

    def _start_video_stream_label(self):
        vid_label, proc_label = QLabel(self), QLabel(self)
        self.video_stream_thread = VideoStreamThread(self.main_widget)
        self.video_stream_thread.change_pixmap_signal.connect(partial(self.video_callback,
                                                vid_label, proc_label))
        self.video_stream_thread.start()
        print('Video stream started.')
        return vid_label, proc_label

    def _create_pixmap_label(self, file_path, width=None):
        label = QLabel(self)
        pixmap = QtGui.QPixmap(file_path)
        if width:
            pixmap = pixmap.scaledToWidth(width)
        label.setPixmap(pixmap)
        return label

    @QtCore.pyqtSlot()
    def on_save_click(self):
        print("Clicked save button.")

    @QtCore.pyqtSlot()
    def on_dummy_click(self):
        print("Clicked dummy button.")

    @QtCore.pyqtSlot(QtGui.QImage)
    def video_callback(self, video_label, proc_label, orig_image, final_image):
        video_label.setPixmap(QtGui.QPixmap.fromImage(orig_image))
        proc_label.setPixmap(QtGui.QPixmap.fromImage(final_image))


def process_frame(bgr_frame: np.ndarray, do_canny: bool) -> QImage:
    """Main function which takes the camera frame (bgr_frame since opencv) and
    processes it such that the resulting image (QImage format) can be displayed
    next to the input image."""
    if do_canny:
        rgb_img = conversions.bgr2rgb(bgr_frame)
        gray_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2GRAY)
        edged = cv2.Canny(gray_img, 50, 100)
        canny_qt_img = conversions.gray2qt(edged)
        return canny_qt_img

    qt_img_processed = planvec.pipeline.run_pipeline(
        bgr_frame.copy(), verbose=False, visualize_steps=False)
    return qt_img_processed


class VideoStreamThread(QtCore.QThread):
    change_pixmap_signal = QtCore.pyqtSignal(QtGui.QImage, QtGui.QImage)

    def __init__(self, parent=None, do_canny=True):
        super().__init__(parent=parent)
        self.do_canny = do_canny

    @QtCore.pyqtSlot()
    def toggle_canny_slot(self):
        self.do_canny = not self.do_canny

    def run(self):
        capture = cv2.VideoCapture(0)
        while True:
            ret, frame = capture.read()  # frame is BGR since OpenCV format
            if ret:
                frame = np.fliplr(frame)  # slower
                # frame = frame[:,::-1, :]  # flip img along vertical axis
                input_img_qt = conversions.bgr2qt(frame)
                output_img_qt = process_frame(frame, self.do_canny)
                self.change_pixmap_signal.emit(input_img_qt, output_img_qt)
                time.sleep(0.05)
