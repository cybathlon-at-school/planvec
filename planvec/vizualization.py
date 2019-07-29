import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import skimage


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


def imshow(img, axis='off', **kwargs):
    setup_figure(**kwargs)
    plt.axis(axis)
    if len(img.shape) == 2:  # Only grey scale values
        plt.imshow(img, cmap='gray')
    else:
        plt.imshow(img)


def plot_image_regions(labelled_image, regionprops, **kwargs):
    setup_figure(**kwargs)
    plt.imshow(labelled_image)

    for region in regionprops:
        minr, minc, maxr, maxc = region.bbox
        rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr,
                                  fill=False, edgecolor='cyan', linewidth=1.5)
        plt.gca().add_patch(rect)

    plt.gca().set_axis_off()


def setup_figure(**kwargs):
    if 'figsize' in kwargs:
        plt.figure(figsize=kwargs.get('figsize'))
    else:
        plt.figure()
    plt.axes().set_aspect('equal')