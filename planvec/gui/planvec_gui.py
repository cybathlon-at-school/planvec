from functools import partial
from PyQt5.QtWidgets import (QMainWindow, QLabel, QPushButton,
                             QHBoxLayout, QVBoxLayout,
                             QGridLayout, QApplication, QMessageBox, QLineEdit, QShortcut, QWidget)
from PyQt5 import QtCore, QtGui

from planvec.gui.datamanager import DataManager
from planvec.gui.missing_school_or_team_name_msg_box import MissingSchoolOrTeamNameMsgBox
from planvec.gui.processing import ImgProcessThread
from planvec.gui.save_msg_box import SaveMsgBox
from planvec.gui.jam_msg_box import JamMsgBox
from planvec.gui.error_msg_box import ErrorMsgBox
from planvec.gui.team_dir_dialog import TeamDirDialog
from planvec.gui.ui_generated.planvec_ui import Ui_planvec
from planvec.gui.video_stream import FrameBuffer, VideoStreamThread
from planvec.pdf_jammer import PdfJammer

from dotmap import DotMap
from typing import Tuple


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
        self.ui.nameSaveButton_2.clicked.connect(self.jam_dialog)  # TODO: rename ui element in qt creator
        self.data_manager = DataManager(output_location=self.config.data.output_location)
        self.overwrite_output = False
        self.ui.outputWriteRadio.clicked.connect(self._toggle_overwrite_output)

        self.ui.captureDeviceName.currentTextChanged.connect(self._change_video_stream_capture_device)
        self.ui.cannyToggleButton.clicked.connect(self._toggle_canny_processing)

        self.ui.inputSizeWidth.returnPressed.connect(self._input_size_width_callback)
        self.ui.inputSizeHeight.returnPressed.connect(self._input_size_height_callback)
        self.ui.outputSizeWidth.returnPressed.connect(self._output_plate_size_width_callback)
        self.ui.outputSizeHeight.returnPressed.connect(self._output_plate_size_height_callback)

    def _start_video_stream_label(self):
        """Start a video VideoStreamThread, create original video and processed video QLabels and connect
        the VideoStreamThread QImage signal to the self.video_callback function which sets the pix maps
        of the video labels."""
        vid_label, proc_label = QLabel(self.ui.drawingContent), QLabel(self.ui.openGLWidget)

        self.video_stream_thread = VideoStreamThread(frame_buffer=self.frame_buffer,
                                                     video_config=self.config.video)
        self.video_stream_thread.start()
        self.proc_stream_thread = ImgProcessThread(frame_buffer=self.frame_buffer,
                                                   processing_config=self.config.processing,
                                                   color_ranges=self.config.color_range.toDict())
        self.proc_stream_thread.change_pixmap_signal.connect(
            partial(self.video_callback, vid_label, proc_label)
        )
        self.proc_stream_thread.start()
        print('Video stream started.')
        return vid_label, proc_label

    def _change_video_stream_capture_device(self, camera_type: str) -> None:
        self.video_stream_thread.set_capture_device(camera_type)

    def _toggle_canny_processing(self) -> None:
        self.proc_stream_thread.toggle_canny_slot()

    def _toggle_overwrite_output(self) -> None:
        self.overwrite_output = not self.overwrite_output

    def _parse_input_size(self, input_size_string: str) -> Tuple[int, int]:
        pass

    def _input_size_width_callback(self) -> None:
        self.proc_stream_thread.set_input_width(int(self.ui.inputSizeWidth.text()))

    def _input_size_height_callback(self) -> None:
        self.proc_stream_thread.set_input_height(int(self.ui.inputSizeHeight.text()))

    def _output_plate_size_width_callback(self) -> None:
        print(self.ui.outputSizeWidth.text())

    def _output_plate_size_height_callback(self) -> None:
        print(self.ui.outputSizeHeight.text())

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
        self.proc_stream_thread.toggle_stopped()
        school_name: str = self.ui.schoolName.text()
        team_name: str = self.ui.teamName.text()
        if not SaveMsgBox.validate_school_name(school_name) or not SaveMsgBox.validate_team_name(team_name):
            error_box = MissingSchoolOrTeamNameMsgBox(self.data_manager, school_name, team_name)
            error_box.execute()
        else:
            self.save_msg_box = SaveMsgBox(save_slot=self.save_img_btn,
                                           school_name=school_name,
                                           team_name=team_name,
                                           data_manager=self.data_manager)
            self.save_msg_box.execute()
        self.video_stream_thread.toggle_stopped()
        self.proc_stream_thread.toggle_stopped()

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
            school_name = self.ui.schoolName.text()
            if not self.data_manager.team_dir_exists(school_name, team_name):
                team_dir_dialog = TeamDirDialog(school_name, team_name, self.data_manager)
                team_dir_dialog.execute()
            if self.data_manager.team_dir_exists(school_name, team_name):  # dir created
                if self.overwrite_output:
                    self.data_manager.delete_all_team_images_and_pdfs(school_name, team_name)
                img_idx = self.data_manager.get_next_team_img_idx(school_name, team_name)
                self.data_manager.save_qt_image(school_name, team_name, curr_qt_img_in, '_original', idx=img_idx)
                self.data_manager.save_qt_image(school_name, team_name, curr_qt_img_out, '_output', idx=img_idx)
                self.data_manager.save_pdf(school_name, team_name, curr_out_fig, '_output', idx=img_idx)
                save_msg_box = QMessageBox()
                save_msg_box.setText(f'Bilder gespeichert für Gruppe: {team_name}')
                save_msg_box.exec_()
        elif button_return.text() == '&Cancel':
            pass
        else:
            raise ValueError('Cannot handle this button return.')

    def jam_dialog(self) -> None:
        """A QMessageBox pops up asking further details from the user."""
        self.video_stream_thread.toggle_stopped()
        self.proc_stream_thread.toggle_stopped()
        school_name: str = self.ui.schoolName_2.text()
        team_name: str = self.ui.teamName_2.text()
        if not JamMsgBox.validate_school_name(school_name):
            error_box = ErrorMsgBox(f'Bitte Schulnamen eingeben!')
            error_box.execute()
            return
        if not self.data_manager.school_dir_exists(school_name):
            error_box = ErrorMsgBox(f'Fehler: Kein Ordner für Schule {school_name} gefunden.')
            error_box.execute()
            return
        if team_name != '':
            if not self.data_manager.team_dir_exists(school_name, team_name):
                error_box = ErrorMsgBox(f'Fehler: Kein Team-Ordner {team_name} für Schule {school_name} gefunden.')
                error_box.execute()
                return

        self.jam_msg_box = JamMsgBox(jam_slot=self.jam_btn,
                                     school_name=school_name,
                                     team_name=None if team_name == '' else team_name,
                                     data_manager=self.data_manager)
        self.jam_msg_box.execute()
        self.video_stream_thread.toggle_stopped()
        self.proc_stream_thread.toggle_stopped()

    def jam_btn(self, button_return):
        # TODO: Typing!
        """This function gets called when the user presses the Create Output or Cancel
        buttons in the QMessageBox which pops up when the user presses Create Output
        in the main window."""
        if button_return.text() == '&OK':
            school_name = self.ui.schoolName_2.text()
            team_name = self.ui.teamName_2.text()
            if team_name == '':  # jam for all teams
                # TODO: invoke jammer
                save_msg_box = QMessageBox()
                # save_msg_box.setText(f'PDF Output generiert für alle Gruppe: ALLE')
                save_msg_box.setText(f'Funktionalität noch nicht umgesetzt. Coming soon...')
                save_msg_box.exec_()
            else:  # jam for specific team
                # TODO: invoke jammer
                save_msg_box = QMessageBox()
                #save_msg_box.setText(f'PDF Output generiert für Gruppe: {team_name}')
                save_msg_box.setText(f'Funktionalität noch nicht umgesetzt. Coming soon...')
                save_msg_box.exec_()

        elif button_return.text() == '&Cancel':
            pass
        else:
            raise ValueError('Cannot handle this button return.')
