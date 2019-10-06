import cv2 as cv
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import skimage

from planvec import img_proc


def plot_contours(contours, axis='off', **kwargs):
    setup_figure(**kwargs)
    plt.axis(axis)
    linewidth = kwargs.get('linewidth') if 'linewidth' in kwargs else 1
    for n, contour in enumerate(contours):
        if 'color' in kwargs:
            plt.plot(contour[:, 1], contour[:, 0], '-', c=kwargs.get('color'), linewidth=linewidth)
        else:
            plt.plot(contour[:, 1], contour[:, 0], '-', linewidth=linewidth)
    return plt.gcf()


def imshow(img, axis='off', img_space='RGB', **kwargs):
    setup_figure(**kwargs)
    plt.axis(axis)
    img_copy = img_proc.copy_img(img)
    if len(img_copy.shape) == 2:  # Only grey scale values
        plt.imshow(img_copy, cmap='gray')
    else:
        assert img_space in ['BGR', 'RGB'], 'Only RGB and BGR image spaces are allowed for this function.'
        if img_space == 'BGR':  # Needs conversion to RGB for matplotlib
            img_copy = cv.cvtColor(img_copy, cv.COLOR_BGR2RGB)
        plt.imshow(img_copy)


def plot_image_regions(labelled_image, regionprops, **kwargs):
    imshow(labelled_image, img_space='BGR', **kwargs)

    for region in regionprops:
        minr, minc, maxr, maxc = region.bbox
        rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr,
                                  fill=False, edgecolor='cyan', linewidth=1.5)
        plt.gca().add_patch(rect)


def setup_figure(**kwargs):
    if 'figsize' in kwargs:
        plt.figure(figsize=kwargs.get('figsize'))
    else:
        plt.figure()
    plt.axes().set_aspect('equal')