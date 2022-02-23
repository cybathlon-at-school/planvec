import queue

import cv2
from PyQt5 import QtCore
from dotmap import DotMap


class FrameBuffer(queue.Queue):
    """Queue to hold frames. Gets filled up by a thread grabbing frames from the camera while processing functions
    might dequeue frames from the queue."""

    def __init__(self, max_size=1):
        super().__init__(maxsize=max_size)


class VideoStreamThread(QtCore.QThread):
    """Grab images from video stream thread and put them into the frame buffer queue."""

    def __init__(self, frame_buffer: FrameBuffer, video_config: DotMap, camera_map: dict, parent=None):
        super().__init__(parent=parent)
        print(f"Initializing video stream with config: {video_config}")
        self.frame_buffer = frame_buffer
        self.video_config = video_config
        self.camera_map = camera_map
        self.stopped = False
        self.capture_device = None

    def run(self) -> None:
        camera_running_index_to_initialize_with = 1
        camera_device_index = self.camera_map[camera_running_index_to_initialize_with]
        print(f"Initializing to first camera {camera_running_index_to_initialize_with} "
              f"which has device index {camera_device_index}")
        self.set_capture_device(camera_device_index)

        while True:
            if not self.stopped:
                ret, bgr_frame = self.capture_device.read()  # frame is BGR since OpenCV format
                if ret:
                    self.frame_buffer.put(bgr_frame)

    def set_capture_device(self, camera_device_index: int) -> None:
        self.capture_device = cv2.VideoCapture(camera_device_index)
        self.capture_device.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_config.max_input_width)
        self.capture_device.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_config.max_input_height)

    def toggle_stopped(self):
        self.stopped = not self.stopped
