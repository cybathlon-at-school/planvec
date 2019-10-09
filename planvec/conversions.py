import cv2
import numpy as np
from PIL import Image
from PIL import ImageTk


def fig2data(fig):
    """Convert a Matplotlib figure to a 4D numpy array with RGBA channels and return it
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

    # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
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
    return Image.frombytes("RGBA", (w, h), buf.tostring())


def bgr2imgpil(bgr_img):
    image = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(image)


def rgb2imgpil(rgb_img):
    image = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR)
    return Image.fromarray(image)


def imgpil2imgtk(img_pil):
    return ImageTk.PhotoImage(img_pil)


def bgr2imgtk(bgr_img):
    image = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(image)
    return ImageTk.PhotoImage(image)


def np_ndarray2imgpil(np_ndarray):
    return Image.fromarray(np_ndarray)
