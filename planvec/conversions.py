"""
Different libraries like OpenCV, Pillow, TKinter and PyQt use different
image formats and since they are needed throughout the system for different
tasks, we need conversion inbetween them.

  LIBRARY        IMAGE FORMAT
    OpenCV          Numpy   [BGR] !!!
    Pillow          Image   [RGB]
    TKinter         ImageTK [RGB]
    PyQt            QImage  [RGB]
"""

import io
import cv2
import numpy as np
from PIL import Image as ImagePil
from PIL import ImageTk
from PyQt5 import QtCore
from PyQt5.QtGui import QImage


#############################################################################
#                                                                           #
# Input: Matplotlib Figure                                                  #
#                                                                           #
#############################################################################

def fig2data(fig):
    """Convert a Matplotlib figure to a 4D numpy array with RGBA 
    channels and return it.
    Arguments
    ---------
        fig: a matplotlib figure
    Return
    ------
        buf: a numpy 3D array of RGBA values
    """
    # draw the renderer
    fig.canvas.draw()

    # Get the RGBA buffer from the figure
    w, h = fig.canvas.get_width_height()
    buf = np.frombuffer(fig.canvas.tostring_argb(), dtype=np.uint8)
    buf.shape = (w, h, 4)

    # canvas.tostring_argb give pixmap in ARGB mode.
    # Roll the ALPHA channel to have it in RGBA mode
    buf = np.roll(buf, 3, axis=2)
    return buf


def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image in RGBA format and return it
    Arguments
    ---------
        fig: a matplotlib figure
    Return
    ------
        a Python Imaging Library ( PIL ) image
    """
    # put the figure pixmap into a numpy array
    buf = fig2data(fig)
    w, h, d = buf.shape
    return ImagePil.frombytes("RGBA", (w, h), buf.tostring())


#############################################################################
#                                                                           #
# Input: Numpy ndarray.                                                     #
# Note: An rgb_img or bgr_img is assumed to be a numpy ndarray.             #
#                                                                           #
#############################################################################

def rgb2bgr(rgb_img) -> np.ndarray:
    return cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR)


def bgr2rgb(bgr_img) -> np.ndarray:
    return cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)


def bgr2imgpil(bgr_img) -> ImagePil:
    return ImagePil.fromarray(bgr2rgb(bgr_img))


def rgb2imgpil(rgb_img) -> ImagePil:
    return ImagePil.fromarray(rgb_img)


def np_ndarray2imgpil(np_ndarray) -> ImagePil:
    # TODO: Remove and update tk gui.
    return ImagePil.fromarray(np_ndarray)


# ----- Conversions to Tkinter ImageTk format. -----
def bgr2imgtk(bgr_img) -> ImageTk:
    image = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
    image = ImagePil.fromarray(image)

    return ImageTk.PhotoImage(image)


# ----- Conversions to PyQt QImage format. -----
def rgb2qt(rgb_img) -> QImage:
    height, width, n_channels = rgb_img.shape
    bytes_per_line = n_channels * width
    return QImage(rgb_img.data, width, height,
                  bytes_per_line,
                  QImage.Format_RGB888)


def bgr2qt(bgr_img):
    return rgb2qt(bgr2rgb(bgr_img))


def gray2qt(gray_img):
    rgb_img = np.asarray(
        np.dstack((gray_img, gray_img, gray_img)), dtype=np.uint8)
    return rgb2qt(rgb_img.copy())


#############################################################################
#                                                                           #
# Input: Pillow image.                                                      #
#                                                                           #
#############################################################################

def imgpil2imgtk(img_pil):
    return ImageTk.PhotoImage(img_pil)


#############################################################################
#                                                                           #
# Input: QtGui.QImage, PyQt image type.                                     #
#                                                                           #
#############################################################################


def qtimg2pilimg(qimage: QImage) -> ImagePil:
    """
    Convert qimage to PIL.Image

    Code adapted from SO:
    https://stackoverflow.com/a/1756587/7330813
    """
    qimage = qimage.copy()
    bio = io.BytesIO()
    bfr = QtCore.QBuffer()
    bfr.open(QtCore.QIODevice.ReadWrite)
    qimage.save(bfr, 'PNG')
    bytearr = bfr.data()
    bio.write(bytearr.data())
    bfr.close()
    bio.seek(0)
    img_pil = ImagePil.open(bio)
    return img_pil


def qtimg2bgr(qt_img):
    qt_img = qt_img.copy()
    qt_img = qt_img.convertToFormat(4)
    ptr = qt_img.bits()
    ptr.setsize(qt_img.byteCount())
    arr = np.array(ptr).reshape(qt_img.height(), qt_img.width(), 4)
    return arr


def qtimg2rgb(qt_img):
    return bgr2rgb(qtimg2bgr(qt_img))
