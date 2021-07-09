import queue
import warnings

import cv2
import numpy as np
from PyQt5 import QtCore


CAM_MAP = {'BUILTIN': 0}


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
        self.capture_device = None

    def run(self) -> None:
        self.set_capture_device(self.video_config.camera)

        while True:
            if not self.stopped:
                ret, bgr_frame = self.capture_device.read()  # frame is BGR since OpenCV format
                if ret:
                    bgr_frame = np.fliplr(bgr_frame)  # slow but for builtin cam
                    self.frame_buffer.put(bgr_frame)

    def set_capture_device(self, camera_type: str) -> None:
        if camera_type == 'BUILTIN':
            capture_idx = CAM_MAP[camera_type]
        elif camera_type == 'USB':
            # loop through all possibilities until we find one working
            usb_cam_indices = []
            for cam_idx in range(1, 5):
                cap = cv2.VideoCapture(cam_idx)
                if cap.read()[0]:
                    usb_cam_indices.append(cam_idx)
                cap.release()

            if not len(usb_cam_indices) == 0:
                capture_idx = usb_cam_indices[0]  # simply take first one
            else:
                capture_idx = CAM_MAP['BUILTIN']  # fallback to builtin
        else:
            raise ValueError(f'Given camera type {camera_type} not available.')

        self.capture_device = cv2.VideoCapture(capture_idx)

        self.capture_device.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_config.max_input_width)
        self.capture_device.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_config.max_input_height)

    def toggle_stopped(self):
        self.stopped = not self.stopped
