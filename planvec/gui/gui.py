from functools import partial
from PyQt5.QtWidgets import (QMainWindow, QLabel, QPushButton,
                             QHBoxLayout, QVBoxLayout,
                             QGridLayout, QApplication, QMessageBox, QLineEdit, QShortcut, QWidget)
from PyQt5 import QtCore, QtGui

from planvec.gui.gui_io import DataManager
from planvec.gui.processing import ImgProcessThread
from planvec.gui.ui_generated.planvec_ui import Ui_planvec
from planvec.gui.video_stream import FrameBuffer, VideoStreamThread
from config import planvec_config
from dotmap import DotMap
from typing import Callable


class PlanvecGui:
    """Adds logic and behaviour to the ui elements."""

    toggle_canny_signal = QtCore.pyqtSignal()  # signal which toggles the image processing to canny edge detection

    def __init__(self, ui: Ui_planvec, main_window: QMainWindow, gui_config: DotMap) -> None:
        self.config = gui_config
        self.ui = ui
        self.main_window = main_window

        self.frame_buffer = FrameBuffer()
        self.video_stream_thread = None

        video_label, processed_label = self._start_video_stream_label()

        video_raw_layout = QGridLayout()
        video_raw_layout.addWidget(video_label, 0, 0,
                                   alignment=QtCore.Qt.AlignCenter)
        video_processed_layout = QGridLayout()
        video_processed_layout.addWidget(processed_label, 0, 0,
                                         alignment=QtCore.Qt.AlignCenter)

        self.ui.drawingContent.setLayout(video_processed_layout)
        self.ui.openGLWidget.setLayout(video_raw_layout)

        self.ui.nameSaveButton.clicked.connect(self.save_img_dialog)
        self.data_manager = DataManager()
        self.save_msg_box = None

    def _start_video_stream_label(self):
        """Start a video VideoStreamThread, create original video and processed video QLabels and connect
        the VideoStreamThread QImage signal to the self.video_callback function which sets the pix maps
        of the video labels."""
        vid_label, proc_label = QLabel(self.ui.drawingContent), QLabel(self.ui.openGLWidget)

        self.video_stream_thread = VideoStreamThread(frame_buffer=self.frame_buffer,
                                                     video_config=self.config.video)
        self.video_stream_thread.start()
        self.proc_stream_thread = ImgProcessThread(frame_buffer=self.frame_buffer)
        self.proc_stream_thread.change_pixmap_signal.connect(
            partial(self.video_callback, vid_label, proc_label)
        )
        self.proc_stream_thread.start()
        print('Video stream started.')
        return vid_label, proc_label

    @QtCore.pyqtSlot(QtGui.QImage)
    def video_callback(self, video_label, proc_label, orig_image, final_image):
        # Resizing for display
        in_pixmap = QtGui.QPixmap.fromImage(orig_image)
        out_pixmap = QtGui.QPixmap.fromImage(final_image)

        in_pixmap = in_pixmap.scaled(self.config.video.raw_display_width,
                                     self.config.video.raw_display_height,
                                     QtCore.Qt.KeepAspectRatio)
        out_pixmap = out_pixmap.scaled(self.config.video.processed_display_width,
                                       self.config.video.processed_display_height,
                                       QtCore.Qt.KeepAspectRatio)

        video_label.setPixmap(in_pixmap)
        proc_label.setPixmap(out_pixmap)

    def _create_pixmap_label(self, file_path: str, width: int = None) -> QLabel:
        label = QLabel(self)
        pixmap = QtGui.QPixmap(file_path)
        if width:
            pixmap = pixmap.scaledToWidth(width)
        label.setPixmap(pixmap)
        return label

    def save_img_dialog(self):
        """A QMessageBox pops up asking further details from the user."""
        self.video_stream_thread.toggle_stopped()
        self.save_msg_box = SaveMsgBox(save_slot=self.save_img_btn,
                                       data_manager=self.data_manager)
        self.save_msg_box.execute()
        self.video_stream_thread.toggle_stopped()

    def save_img_btn(self, button_return):
        # TODO: Typing!
        """This function gets called when the user presses the Save or Cancel
        buttons in the QMessageBox which pops up when the user presses Save
        in the main window."""
        curr_qt_img_out = self.proc_stream_thread.get_curr_out()
        curr_qt_img_in = self.proc_stream_thread.get_curr_in()
        curr_out_fig = self.proc_stream_thread.get_curr_out_fig()
        if button_return.text() == '&OK':
            team_name = self.save_msg_box.get_team_name()
            if not self.data_manager.team_dir_exists(team_name):
                team_dir_dialog = TeamDirDialog(team_name, self.data_manager)
                team_dir_dialog.execute()
            if self.data_manager.team_dir_exists(team_name):  # dir created
                if planvec_config.data.overwrite_output:
                    self.data_manager.delete_all_team_imgs(team_name)
                img_idx = self.data_manager.get_next_team_img_idx(team_name)
                self.data_manager.save_qt_image(team_name, curr_qt_img_in, '_original', idx=img_idx)
                self.data_manager.save_qt_image(team_name, curr_qt_img_out, '_output', idx=img_idx)
                self.data_manager.save_pdf(team_name, curr_out_fig, '_output', idx=img_idx)
                save_msg_box = QMessageBox()
                save_msg_box.setText(f'Bilder gespeichert für Gruppe: {team_name}')
                save_msg_box.exec_()
        elif button_return.text() == '&Cancel':
            pass
        else:
            raise ValueError('Cannot handle this button return.')


class SaveMsgBox(QMessageBox):
    def __init__(self, save_slot: Callable, data_manager: DataManager, parent=None) -> None:
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
            # n_images = len(self.data_manager.load_team_img_names(team))
            team_names_str += f'\n    {team}'
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
    def __init__(self, team_name: str, data_manager: DataManager, parent=None) -> None:
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
