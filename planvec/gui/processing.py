from time import time
from queue import Queue
import cv2
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QImage
from dotmap import DotMap
from matplotlib import pyplot as plt
from typing import Tuple

import planvec.pipeline
from planvec import vizualization, conversions
from planvec.gui.video_stream import FrameBuffer
from planvec.utils.units_conversion import cm_to_inches


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

    def __init__(self, frame_buffer: FrameBuffer, processing_config: DotMap, color_ranges: dict, parent=None):
        super().__init__(parent=parent)
        self.frame_buffer = frame_buffer
        self.processing_config = processing_config
        self.color_ranges = color_ranges
        self.out_fig, self.out_ax = vizualization.setup_figure()
        self.do_canny = False
        self.curr_qt_img_input = None
        self.curr_qt_img_out = None
        self.stopped = False

    def get_curr_out(self) -> QImage:
        return self.curr_qt_img_out

    def get_curr_in(self) -> QImage:
        return self.curr_qt_img_input

    def get_curr_out_fig(self) -> plt.Figure:
        return self.out_fig

    def toggle_stopped(self):
        self.stopped = not self.stopped

    def set_input_width(self, width) -> None:
        _, current_height_inches = self.processing_config.out_size_inches
        new_width_in_inches = cm_to_inches(width)
        self.processing_config.out_size_inches = (new_width_in_inches, current_height_inches)
        self.processing_config.rectify_shape = self._calculate_display_shape_in_pixels(new_width_in_inches,
                                                                                       current_height_inches)

    def set_input_height(self, height) -> None:
        current_width_inches, _ = self.processing_config.out_size_inches
        new_height_in_inches = cm_to_inches(height)
        self.processing_config.out_size_inches = (current_width_inches, new_height_in_inches)
        self.processing_config.rectify_shape = self._calculate_display_shape_in_pixels(current_width_inches,
                                                                                       new_height_in_inches)

    @staticmethod
    def _calculate_height_to_width_ratio(height: float, width: float) -> float:
        return height / width

    @staticmethod
    def _calculate_display_shape_in_pixels(width_in_inches: float, height_in_inches: float) -> Tuple[float, float]:
        height_to_width_ratio = ImgProcessThread._calculate_height_to_width_ratio(height_in_inches, width_in_inches)

        max_pixels_value = 1920
        if width_in_inches >= height_in_inches:
            return max_pixels_value, int(max_pixels_value * height_to_width_ratio)
        else:
            return int(max_pixels_value / height_to_width_ratio), max_pixels_value

    @QtCore.pyqtSlot()
    def toggle_canny_slot(self) -> None:
        self.do_canny = not self.do_canny

    @staticmethod
    def process_frame(img, processing_config: DotMap, color_ranges: dict, do_canny: bool, ax: plt.Axes) -> (plt.Axes, QImage):
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
                                                                 config=processing_config,
                                                                 color_ranges=color_ranges,
                                                                 verbose=False,
                                                                 visualize_steps=False)
        return ax, qt_img_processed

    def run(self) -> None:
        frame_rate_counter = FrameRateCounter(buffer_size=1)
        while True:
            if not self.stopped:
                bgr_frame = self.frame_buffer.get()
                self.out_ax, self.curr_qt_img_out = self.process_frame(bgr_frame,
                                                                       processing_config=self.processing_config,
                                                                       color_ranges=self.color_ranges,
                                                                       do_canny=self.do_canny,
                                                                       ax=self.out_ax)
                self.curr_qt_img_input = conversions.bgr2qt(bgr_frame)
                self.change_pixmap_signal.emit(self.curr_qt_img_input, self.curr_qt_img_out)
                frame_rate_counter.event_happened()
                self.frame_rate_signal.emit(f'Frame rate (last {frame_rate_counter.buffer_size} frames): '
                                            f'{round(frame_rate_counter.get_frame_rate(), 2)}')
