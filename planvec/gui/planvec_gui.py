from functools import partial
from PyQt5.QtWidgets import (QMainWindow, QLabel, QPushButton,
                             QHBoxLayout, QVBoxLayout,
                             QGridLayout, QApplication, QMessageBox, QLineEdit, QShortcut, QWidget)
from PyQt5 import QtCore, QtGui

from planvec.gui.datamanager import DataManager
from planvec.gui.invalid_school_team_msg_box import InvalidSchoolTeamMsgBox
from planvec.gui.processing import ImgProcessThread
from planvec.gui.save_msg_box import SaveMsgBox
from planvec.gui.team_dir_dialog import TeamDirDialog
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
    def video_callback(self, video_raw_label, video_out_label, orig_image, final_image):
        # Resizing for display
        in_pixmap = QtGui.QPixmap.fromImage(orig_image)
        out_pixmap = QtGui.QPixmap.fromImage(final_image)

        in_pixmap = in_pixmap.scaled(self.config.video.raw_display_width,
                                     self.config.video.raw_display_height,
                                     QtCore.Qt.KeepAspectRatio)
        out_pixmap = out_pixmap.scaled(self.config.video.processed_display_width,
                                       self.config.video.processed_display_height,
                                       QtCore.Qt.KeepAspectRatio)

        video_raw_label.setPixmap(in_pixmap)
        video_out_label.setPixmap(out_pixmap)

    def save_img_dialog(self):
        """A QMessageBox pops up asking further details from the user."""
        self.video_stream_thread.toggle_stopped()
        school_name: str = self.ui.schoolName.text()
        team_name: str = self.ui.teamName.text()
        if not SaveMsgBox.validate_school_name(school_name) or not SaveMsgBox.validate_team_name(team_name):
            error_box = InvalidSchoolTeamMsgBox(self.data_manager, school_name, team_name)
            error_box.execute()
        else:
            self.save_msg_box = SaveMsgBox(save_slot=self.save_img_btn,
                                           school_name=school_name,
                                           team_name=team_name,
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
            team_name = self.ui.teamName.text()
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
