import queue
import warnings

import cv2
import numpy as np
from PyQt5 import QtCore


CAM_MAP = {'USB': 1, 'BUILTIN': 0}


class FrameBuffer(queue.Queue):
    """Queue to hold frames. Gets filled up by a thread grabbing frames from the camera while processing functions
    might dequeue frames from the queue."""
    def __init__(self, max_size=1):
        super().__init__(maxsize=max_size)


class VideoStreamThread(QtCore.QThread):
    """Grab images from video stream thread and put them into the frame buffer queue."""
    def __init__(self, frame_buffer: FrameBuffer, video_config, parent=None):
        super().__init__(parent=parent)
        print(video_config)
        self.frame_buffer = frame_buffer
        self.video_config = video_config
        self.stopped = False

    def run(self) -> None:
        print(self.video_config.camera)
        capture = cv2.VideoCapture(CAM_MAP[self.video_config.camera])
        if not capture.isOpened():
            capture = cv2.VideoCapture(abs(1 - CAM_MAP[self.video_config.camera]))
            warnings.warn(f'Needed to switch camera choice!')
            if not capture.isOpened():
                raise RuntimeError(f'Couldn\'t connect to camera! Tried all of {list(CAM_MAP.keys())}')
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_config.max_input_width)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_config.max_input_height)
        while True:
            if not self.stopped:
                ret, bgr_frame = capture.read()  # frame is BGR since OpenCV format
                if ret:
                    bgr_frame = np.fliplr(bgr_frame)  # slow but for builtin cam
                    self.frame_buffer.put(bgr_frame)

    def toggle_stopped(self):
        self.stopped = not self.stopped
