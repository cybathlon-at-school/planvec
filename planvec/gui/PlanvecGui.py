import io
import os
import cv2
import time
from functools import partial
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QHBoxLayout, QGroupBox, QDialog, QVBoxLayout,
                             QGridLayout, QWidget, QMessageBox, QLineEdit)
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QImage
import numpy as np

from planvec import common
from planvec import conversions
from planvec.gui.gui_io import DataManager
import planvec.pipeline

CAMERA = 1  # 0 is built-in camera, 1 is USB camera


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
        self.data_manager = DataManager()
        self.save_msg_box = None

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
        main_layout.addWidget(video_label,
                              0,
                              0,
                              alignment=QtCore.Qt.AlignCenter)

        # Processed image Widget
        # img_label = self._create_pixmap_label(file_path = os.path.join(common.PROJECT_ROOT_PATH, 'data/2019-10-09_16-21-38.jpg'))

        main_layout.addWidget(processed_label,
                              0,
                              1,
                              alignment=QtCore.Qt.AlignCenter)

        # Buttons Widget
        main_layout.addLayout(self._create_btns_layout(),
                              1,
                              0,
                              1,
                              2,
                              alignment=QtCore.Qt.AlignCenter
                              | QtCore.Qt.AlignTop)
        self.main_widget.setLayout(main_layout)

    def _create_btns_layout(self):
        """This is a box with holding various buttons."""
        btns_layout = QHBoxLayout()
        save_btn = QPushButton("Save!")
        save_btn.setStyleSheet("background-color: #5DADE2")
        save_btn.clicked.connect(self.save_img_dialog)
        dummy_btn = QPushButton("Toggle Canny!")
        dummy_btn.setStyleSheet("background-color: #E67E22")
        dummy_btn.clicked.connect(self.video_stream_thread.toggle_canny_slot)
        btns_layout.addWidget(save_btn)
        btns_layout.addWidget(dummy_btn)
        return btns_layout

    def _start_video_stream_label(self):
        vid_label, proc_label = QLabel(self), QLabel(self)
        self.video_stream_thread = VideoStreamThread(self.main_widget)
        self.video_stream_thread.change_pixmap_signal.connect(
            partial(self.video_callback, vid_label, proc_label))
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

    @QtCore.pyqtSlot(QtGui.QImage)
    def video_callback(self, video_label, proc_label, orig_image, final_image):
        video_label.setPixmap(QtGui.QPixmap.fromImage(orig_image))
        proc_label.setPixmap(QtGui.QPixmap.fromImage(final_image))

    def save_img_dialog(self):
        """A QMessageBox pops up asking further details from the user."""
        self.video_stream_thread.toggle_stopped()
        self.save_msg_box = SaveMsgBox(save_slot=self.save_img_btn,
                                       data_manager=self.data_manager)
        self.save_msg_box.execute()
        self.video_stream_thread.toggle_stopped()

    def save_img_btn(self, button_return):
        """This function gets called when the user presses the Save or Cancel
        buttons in the QMessageBox which pops up when the user presses Save
        in the main window."""
        curr_qt_img_out = self.video_stream_thread.get_curr_out()
        curr_qt_img_in = self.video_stream_thread.get_curr_in()
        if button_return.text() == '&OK':
            team_name = self.save_msg_box.get_team_name()
            if not self.data_manager.team_dir_exists(team_name):
                team_dir_dialog = TeamDirDialog(team_name, self.data_manager)
                team_dir_dialog.execute()
            if self.data_manager.team_dir_exists(team_name):  # dir created
                img_idx = self.data_manager.get_next_team_img_idx(team_name)
                self.data_manager.save_image(team_name, curr_qt_img_in,
                                            '_original', idx=img_idx)
                self.data_manager.save_image(team_name, curr_qt_img_out,
                                            '_output', idx=img_idx)
                save_msg_box = QMessageBox()
                save_msg_box.setText(f'Bilder gespeichert für Gruppe: {team_name}')
                save_msg_box.exec_()
        elif button_return.text() == '&Cancel':
            pass
        else:
            raise ValueError('Cannot handle this button return.')


def process_frame(bgr_frame: np.ndarray, do_canny: bool) -> QImage:
    """Main function which takes the camera bgr_frame (bgr_frame since opencv) and
    processes it such that the resulting image (QImage format) can be displayed
    next to the input image."""
    if do_canny:
        rgb_img = conversions.bgr2rgb(bgr_frame)
        gray_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2GRAY)
        edged = cv2.Canny(gray_img, 50, 100)
        canny_qt_img = conversions.gray2qt(edged)
        return canny_qt_img

    qt_img_processed = planvec.pipeline.run_pipeline(bgr_frame.copy(),
                                                     verbose=False,
                                                     visualize_steps=False)
    return qt_img_processed


class VideoStreamThread(QtCore.QThread):
    change_pixmap_signal = QtCore.pyqtSignal(QtGui.QImage, QtGui.QImage)

    def __init__(self, parent=None, do_canny=True):
        super().__init__(parent=parent)
        self.do_canny = do_canny
        self.curr_qt_img_input = None
        self.curr_qt_img_out = None
        self.stopped = False

    @QtCore.pyqtSlot()
    def toggle_canny_slot(self) -> None:
        self.do_canny = not self.do_canny

    def get_curr_out(self) -> QImage:
        return self.curr_qt_img_out

    def get_curr_in(self) -> QImage:
        return self.curr_qt_img_input

    def run(self) -> None:
        capture = cv2.VideoCapture(CAMERA)
        while True:
            if not self.stopped:
                ret, bgr_frame = capture.read()  # frame is BGR since OpenCV format
                if ret:
                    # bgr_frame = np.fliplr(bgr_frame)  # slow but for builtin cam
                    self.curr_qt_img_input = conversions.bgr2qt(bgr_frame)
                    self.curr_qt_img_out = process_frame(bgr_frame, self.do_canny)

                    self.change_pixmap_signal.emit(self.curr_qt_img_input,
                                                   self.curr_qt_img_out)
                time.sleep(0.05)

    def toggle_stopped(self):
        self.stopped = not self.stopped
        print('Toggled stop. Now: ', self.stopped)


class SaveMsgBox(QMessageBox):
    def __init__(self, save_slot, data_manager, parent=None):
        super(SaveMsgBox, self).__init__(parent)
        self.save_slot = save_slot
        self.data_manager = data_manager
        self.line_edit = None
        self.setup()
        
    def setup(self):
        self.setIcon(QMessageBox.Question)
        self.setText("Bild wirklich speichern?")
        self.setInformativeText("Hier kommt Bild Infos rein...")
        self.setWindowTitle("Bild speichern")
        question_label = QLabel("Gruppennamen eingeben:")
        team_names = self.data_manager.load_all_team_names()
        team_names_str = 'Folgende Gruppen existieren bereits:'
        if len(team_names) == 0:
            team_names_str = 'Es existieren noch keine Gruppen.'
        for team in team_names:
            n_images = len(self.data_manager.load_team_img_names(team))
            team_names_str += f'\n   {team}\t\t {n_images} Bilder.'
        
        info_label = QLabel(team_names_str)
        self.line_edit = QLineEdit()
        team_layout = QVBoxLayout()
        team_layout.addWidget(question_label)
        team_layout.addWidget(self.line_edit)
        team_layout.addWidget(info_label)

        self.layout().addLayout(team_layout, 3, 0, 1, 3,
                                QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.buttonClicked.connect(self.save_slot)

    def get_team_name(self):
        return self.line_edit.text()

    def execute(self):
        self.exec_()


class TeamDirDialog(QMessageBox):
    def __init__(self, team_name, data_manager, parent=None):
        super(TeamDirDialog, self).__init__(parent)
        self.team_name = team_name
        self.data_manager = data_manager
        self.setup()

    def setup(self):
        text = 'Die Gruppe {} existiert noch nicht. ' \
                'Neuen Ordner anlegen?'.format(self.team_name)
        self.setIcon(QMessageBox.Question)
        self.setText(text)
        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.buttonClicked.connect(self.ok_btn_slot)

    def execute(self):
        self.exec_()

    def ok_btn_slot(self, button_return):
        if button_return.text() == '&OK':
            self.data_manager.create_team_folder(self.team_name)
