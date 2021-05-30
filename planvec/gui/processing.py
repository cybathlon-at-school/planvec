from time import time
from queue import Queue
import cv2
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QImage
from matplotlib import pyplot as plt

import planvec.pipeline
from planvec import vizualization, conversions
from planvec.gui.video_stream import FrameBuffer


class FrameRateCounter:
    """Calculate the frame rate for a series of actions (processed images)."""
    def __init__(self, buffer_size=3) -> None:
        self.buffer_size = buffer_size
        self.block_start_time = time()
        self.event_count = 0
        self.frame_rate = 0

    def event_happened(self) -> None:
        self.event_count += 1
        if self.event_count % self.buffer_size == 0:
            self.frame_rate = self.event_count / (time() - self.block_start_time)
            self.event_count = 0
            self.block_start_time = time()

    def get_frame_rate(self) -> float:
        return self.frame_rate


class ImgProcessThread(QtCore.QThread):
    """Responsible to process frames from a frame buffer and sending the results back to the gui."""
    change_pixmap_signal = QtCore.pyqtSignal(QtGui.QImage, QtGui.QImage)
    frame_rate_signal = QtCore.pyqtSignal(str)

    def __init__(self, frame_buffer: FrameBuffer, parent=None):
        super().__init__(parent=parent)
        self.frame_buffer = frame_buffer
        self.out_fig, self.out_ax = vizualization.setup_figure()
        self.do_canny = True
        self.curr_qt_img_input = None
        self.curr_qt_img_out = None

    def get_curr_out(self) -> QImage:
        return self.curr_qt_img_out

    def get_curr_in(self) -> QImage:
        return self.curr_qt_img_input

    def get_curr_out_fig(self) -> plt.Figure:
        return self.out_fig

    @QtCore.pyqtSlot()
    def toggle_canny_slot(self) -> None:
        self.do_canny = not self.do_canny

    @staticmethod
    def process_frame(img, do_canny: bool, ax: plt.Axes) -> (plt.Axes, QImage):
        """Main function which takes the camera bgr_frame (bgr_frame since opencv) and
        processes it such that the resulting image (QImage format) can be displayed
        next to the input image."""
        ax.clear()
        if do_canny:
            rgb_img = conversions.bgr2rgb(img)
            gray_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2GRAY)
            edged = cv2.Canny(gray_img, 50, 100)
            qt_img_processed = conversions.gray2qt(edged)

        else:
            ax, qt_img_processed = planvec.pipeline.run_pipeline(img.copy(),
                                                                 ax=ax,
                                                                 verbose=False,
                                                                 visualize_steps=False)
        return ax, qt_img_processed

    def run(self) -> None:
        frame_rate_counter = FrameRateCounter(buffer_size=1)
        while True:
            bgr_frame = self.frame_buffer.get()
            self.out_ax, self.curr_qt_img_out = self.process_frame(bgr_frame, do_canny=self.do_canny, ax=self.out_ax)
            self.curr_qt_img_input = conversions.bgr2qt(bgr_frame)
            self.change_pixmap_signal.emit(self.curr_qt_img_input, self.curr_qt_img_out)
            frame_rate_counter.event_happened()
            self.frame_rate_signal.emit(f'Frame rate (last {frame_rate_counter.buffer_size} frames): '
                                        f'{round(frame_rate_counter.get_frame_rate(), 2)}')
