from functools import partial
from PyQt5.QtWidgets import (QMainWindow, QLabel, QPushButton,
                             QHBoxLayout, QVBoxLayout,
                             QGridLayout, QWidget, QMessageBox, QLineEdit, QShortcut)
from PyQt5 import QtCore, QtGui

from planvec.gui.gui_io import DataManager
from planvec.gui.processing import ImgProcessThread
from planvec.gui.video_stream import FrameBuffer, VideoStreamThread
from config import planvec_config
from dotmap import DotMap
from typing import Callable


class PlanvecGui(QMainWindow):
    """Main class for the PlanvecGui representing the main window and components."""

    toggle_canny_signal = QtCore.pyqtSignal()  # signal which toggles the image processing to canny edge detection

    def __init__(self, gui_config: DotMap) -> None:
        super().__init__()
        self.config = gui_config
        self.main_widget = QWidget()
        self.video_stream_thread = None
        self.frame_buffer = FrameBuffer()
        self.init_ui()
        self.data_manager = DataManager()
        self.save_msg_box = None
        QShortcut(QtGui.QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QtGui.QKeySequence("Esc"), self, self.close)

    def init_ui(self):
        # Setup Main window properties
        self.setWindowTitle(self.config.window.title)
        self.setGeometry(self.config.window.left, self.config.window.top,
                         self.config.window.width, self.config.window.height)
        # Status Bar the bottom
        self.statusBar().showMessage('Press "Esc" or "Ctrl+Q" to exit.')

        # Main Layout
        self.setCentralWidget(self.main_widget)
        self._create_main_layout()
        self.init_style_sheet()
        if self.config.window.full_screen:
            self.showFullScreen()
        else:
            self.show()

    def init_style_sheet(self):
        self.setStyleSheet(
            """
            QPushButton {
                color: #fff !important;
                text-transform: uppercase;
                padding: 20px;
            }
            """
        )

    def _create_main_layout(self):
        """This is the layout for them main widget by adding video and button widgets."""
        main_layout = QGridLayout()
        # Set relative stretch values, columns of equal size
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 1)
        # Relative stretch s.t. first row (for images) is ten times bottom row (for buttons)
        main_layout.setRowStretch(0, 10)
        main_layout.setRowStretch(1, 1)

        # Video widget for input and processed stream
        video_label, processed_label = self._start_video_stream_label()
        main_layout.addWidget(video_label, 0, 0,
                              alignment=QtCore.Qt.AlignCenter)

        main_layout.addWidget(processed_label, 0, 1,
                              alignment=QtCore.Qt.AlignCenter)

        # Buttons Widget
        main_layout.addLayout(self._create_btns_layout(), 1, 0, 1, 2,
                              alignment=QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        self.main_widget.setLayout(main_layout)

    def _start_video_stream_label(self):
        """Start a video VideoStreamThread, create original video and processed video QLabels and connect
        the VideoStreamThread QImage signal to the self.video_callback function which sets the pix maps
        of the video labels."""
        vid_label, proc_label = QLabel(self), QLabel(self)
        self.video_stream_thread = VideoStreamThread(frame_buffer=self.frame_buffer,
                                                     parent=self.main_widget,
                                                     video_config=self.config.video)
        self.video_stream_thread.start()
        self.proc_stream_thread = ImgProcessThread(frame_buffer=self.frame_buffer,
                                                   parent=self.main_widget)
        self.proc_stream_thread.change_pixmap_signal.connect(
            partial(self.video_callback, vid_label, proc_label)
        )
        self.proc_stream_thread.start()
        self.proc_stream_thread.frame_rate_signal.connect(self._status_msg_callback)
        print('Video stream started.')
        return vid_label, proc_label

    @QtCore.pyqtSlot(QtGui.QImage)
    def video_callback(self, video_label, proc_label, orig_image, final_image):
        # Resizing for display
        in_pixmap = QtGui.QPixmap.fromImage(orig_image)
        out_pixmap = QtGui.QPixmap.fromImage(final_image)

        # TODO: Choose aspect ratio of drawing area to match the initial input aspect to have equal size output
        in_pixmap = in_pixmap.scaled(self.config.video.display_width, self.config.video.display_height,
                                     QtCore.Qt.KeepAspectRatio)
        out_pixmap = out_pixmap.scaled(self.config.video.display_width, self.config.video.display_height,
                                       QtCore.Qt.KeepAspectRatio)

        video_label.setPixmap(in_pixmap)
        proc_label.setPixmap(out_pixmap)

    def _status_msg_callback(self, status_msg: str) -> None:
        # exit_msg = 'Press "Esc" or "Ctrl+Q" to exit.'
        self.statusBar().showMessage(f'{status_msg}')

    def _create_btns_layout(self) -> QHBoxLayout:
        """This is a box with holding various buttons."""
        btns_layout = QHBoxLayout()
        save_btn = QPushButton("Save!")
        save_btn.setStyleSheet("background-color: #5DADE2")
        save_btn.clicked.connect(self.save_img_dialog)
        dummy_btn = QPushButton("Toggle Canny!")
        dummy_btn.setStyleSheet("background-color: #E67E22")
        dummy_btn.clicked.connect(self.proc_stream_thread.toggle_canny_slot)
        btns_layout.addWidget(save_btn)
        btns_layout.addWidget(dummy_btn)
        return btns_layout

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
