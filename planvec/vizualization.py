import cv2 as cv
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import skimage

from planvec import img_proc
from planvec.utils.timing import timeit
from config import planvec_config


@timeit
def plot_contours(contours, ax=None, axis='off', reverse_y_axis=True, **kwargs):
    if axis == 'off':
        ax.set_axis_off()
    linewidth = kwargs.get('linewidth') if 'linewidth' in kwargs else 1
    for n, contour in enumerate(contours):
        if 'color' in kwargs:
            ax.plot(contour[:, 1], contour[:, 0], '-', c=kwargs.get('color'), linewidth=linewidth)
        else:
            ax.plot(contour[:, 1], contour[:, 0], '-', linewidth=linewidth)
    # Set correct ratio
    xlim, ylim = planvec_config.processing.rectify_shape
    ax.set_xlim([0, xlim])
    ax.set_ylim([0, ylim])
    if reverse_y_axis:
        ax.invert_yaxis()
    return ax


@timeit
def imshow(img, axis='on', img_space='RGB', **kwargs):
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


@timeit
def plot_image_regions(labelled_image, regionprops, **kwargs):
    imshow(labelled_image, img_space='BGR', **kwargs)

    for region in regionprops:
        minr, minc, maxr, maxc = region.bbox
        rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr,
                                  fill=False, edgecolor='cyan', linewidth=1.5)
        plt.gca().add_patch(rect)


@timeit
def setup_figure(**kwargs):
    if 'figsize' in kwargs:
        fig = plt.figure(figsize=kwargs.get('figsize'))
    else:
        fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    if 'title' in kwargs:
        ax.set_title(kwargs.get('title'))
    ax.set_aspect('equal')
    return fig, ax
