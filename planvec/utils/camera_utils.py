import cv2 as cv2

from typing import List


def get_physical_camera_device_indices(maximum_index: int = 10) -> List[int]:
    index = 0
    arr = []
    i = maximum_index
    while i > 0:
        cap = cv2.VideoCapture(index)
        if cap.read()[0]:
            arr.append(index)
            cap.release()
        index += 1
        i -= 1
    return arr
