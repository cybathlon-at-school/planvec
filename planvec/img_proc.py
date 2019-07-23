import os
import tempfile
import skimage
import matplotlib.pyplot as plt
import cv2
import img2pdf
from PIL import Image


def read_img(dir_path, name):
    return plt.imread(os.path.join(dir_path, name))


def img_to_greyscale(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def add_gaussian_blur(img, std_x, std_y):
    return cv2.GaussianBlur(img, (std_x, std_y), 0)


def thresh_img(img, thresh_val, max_val, thresh_type=cv2.THRESH_BINARY):
    _, img = cv2.threshold(img, thresh_val, max_val, thresh_type)
    return img


def adaptive_thresh_img(img):
    # TODO: Remove hard coded stuff.
    return cv2.adaptiveThreshold(img, 100, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 101, 10)


def find_contours(img, value):
    contours = skimage.measure.find_contours(img, value)
    return contours


def plot_contours(contours, figsize=(10, 7)):
    plt.figure(figsize=figsize)
    plt.axis('off')
    for n, contour in enumerate(contours):
        plt.plot(contour[:, 1], contour[:, 0], linewidth=2)
    plt.show()


def imshow_grey(img, figsize=(13, 8)):
    plt.figure(figsize=figsize)
    plt.axis('off')
    plt.imshow(img, cmap='Greys_r')


def img_to_pdf(out_file_path, img):
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_img = Image.fromarray(img)
        tmp_img.save(os.path.join(tmp_dir, 'tmp_img.jpeg'))

        with open(out_file_path, "wb") as out_file:
            out_file.write(img2pdf.convert(os.path.join(tmp_dir, 'tmp_img.jpeg')))
        print(f'Stored image pdf at {out_file_path}.')
