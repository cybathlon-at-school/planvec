import numpy as np
import matplotlib.pyplot as plt
import skimage
import skimage.measure
import cv2 as cv
from functools import reduce
import operator
import math
from time import time

import planvec.vizualization
from planvec.utils.timing import timeit
from planvec.color_range import HSVColorRange

from typing import List

DEBUG_BARS = 5 * '-'


@timeit
def copy_img(img):
    return np.copy(img)


@timeit
def img_to_greyscale(img):
    return cv.cvtColor(img, cv.COLOR_BGR2GRAY)


@timeit
def add_gaussian_blur(img, std_x, std_y):
    return cv.GaussianBlur(img, (std_x, std_y), sigmaX=0)


@timeit
def thresh_img(img, thresh_val, max_val, thresh_type=cv.THRESH_BINARY):
    """Apply threshold to pixel values from an image. Refer to
    https://docs.opencv.org/2.4/doc/tutorials/imgproc/threshold/threshold.html for docs."""
    _, img = cv.threshold(img, thresh_val, max_val, thresh_type)
    return img


@timeit
def invert_mask(mask):
    """Inverts an 8-bit mask (max value is 255)"""
    return 255 - mask


@timeit
def create_hsv_range_mask(img, hsv_color_range: HSVColorRange):
    """Based on a HSVColorRange, create a mask for which pixels in an input image are in this range."""
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    return cv.inRange(hsv, np.array(hsv_color_range.start), np.array(hsv_color_range.end))


@timeit
def filter_keep_by_hsv_range(img, hsv_color_range: HSVColorRange):
    """Returns an image where only pixels are kept with their values which fall into a HSV range between
    range_start, e.g. [0, 0, 0] and range_end, e.g. [179, 255, 255] or any values in-between those bounds."""
    mask = create_hsv_range_mask(img, hsv_color_range)
    return cv.bitwise_and(img, img, mask=mask)


@timeit
def filter_keep_multi_ranges(img, hsv_color_ranges: List[HSVColorRange]):
    """Same as filter_keep_by_hsv_range but for multiple hsv color ranges."""
    masks = [create_hsv_range_mask(img, hsv_color_range) for hsv_color_range in hsv_color_ranges]
    final_mask = sum(masks)
    return cv.bitwise_and(img, img, mask=final_mask)


@timeit
def filter_by_hsv_range_to_white(img, hsv_color_range: HSVColorRange):
    """Pixels of the input image will be set to white is they are within the hsv color range."""
    img = copy_img(img)
    mask = planvec.img_proc.create_hsv_range_mask(img, hsv_color_range)
    img[mask > 0] = 255
    return img


@timeit
def filter_multi_hsv_ranges_to_white(img, hsv_color_ranges: List[HSVColorRange]):
    """Same as filter_by_hsv_range_to_white but for multiple hsv color ranges."""
    img = copy_img(img)
    for hsv_color_range in hsv_color_ranges:
        img = filter_by_hsv_range_to_white(img, hsv_color_range)
    return img


@timeit
def white_pixels_to_black(img):
    """#TODO: Add docstring."""
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(gray, 100, 255, cv.THRESH_BINARY)
    img[thresh == 255] = 0


@timeit
def adaptive_thresh_img(img):
    # TODO: Remove hard coded stuff.
    return cv.adaptiveThreshold(img, 100, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 101, 10)


@timeit
def find_contours(img, level):
    contours = skimage.measure.find_contours(img, level=level)
    return contours


@timeit
def filter_contours_by_size(contours, n_points_thresh):
    return [cont for cont in contours if len(cont) > n_points_thresh]


@timeit
def find_regions(img, area_threshold, intens_threshold):
    """Use skimage's region finding capabilities to find connected regions in an image.

    #TODO: specify args and returns
    """
    # Threshold processing
    img = planvec.img_proc.img_to_greyscale(img)
    img = planvec.img_proc.add_gaussian_blur(img, std_x=3, std_y=3)
    img_thresh = planvec.img_proc.thresh_img(img, thresh_val=intens_threshold, max_val=255, thresh_type=cv.THRESH_BINARY)
    labelled_img, n = skimage.measure.label(img_thresh, background=0, return_num=True)
    regions = skimage.measure.regionprops(labelled_img)
    # Filtering regions
    img_labelled_proc, filtered_regions = planvec.img_proc.filter_regions(labelled_img, regionprops=regions,
                                                                          area_threshold=area_threshold)
    return img_labelled_proc, filtered_regions


@timeit
def filter_regions(labelled_img, regionprops, area_threshold, verbose=False):
    """After regions are found we need to filter those to get rid of too small regions as well as the region which
    is the bbox of the whole image.

    #TODO: specify args and returns
    """
    filtered_regions = []
    for region in regionprops:
        region_mask = labelled_img == region.label
        # Remove regions which have image size since they represent the boundary
        if region.bbox_area == np.prod(np.array(labelled_img.size)):
            if verbose:
                # print(f'Region {region.label} has area: {region.area} == (image size). Removed.')
                pass
            labelled_img[region_mask] = 0
            continue
        # Remove regions which are too small (basically noise)
        if region.area < area_threshold:
            if verbose:
                # print(f'Region {region.label} has area: {region.area} < {area_threshold}. Too small. Removed.')
                pass
            labelled_img[region_mask] = 0
            continue
        filtered_regions.append(region)
    if verbose:
        # print(f'{len(filtered_regions)} regions left, sizes: {[region.area for region in filtered_regions]}')
        pass
    return labelled_img, filtered_regions


@timeit
def warp_image(img, src_points, dst_points, final_size, show_plot=False):
    """Warps an image such that src_points will be mapped to dst_points from the original img to a new image of
    size final_size.

    Arguments
    ---------
        img: an numpy nd-array
        src_points: list of four points, a point is a list or tuple of length two (x, y), x is horizontal
        dst_points: same shape as src_points, coordinates to map the src_points to
        final_size: shape of the final image (x, y)
        show_plot: plots original and warped image
    Returns
    -------
        warped_img: a warped version of the input image in shape of final_size
    """
    src_points = np.float32(src_points)
    dst_points = np.float32(dst_points)
    assert len(src_points) == len(dst_points), f'src and dst point arrays have to be of same length, ' \
                                               f'given: {len(dst_points)} and {len(src_points)}'

    transformation = cv.getPerspectiveTransform(src_points, dst_points)
    warped_img = cv.warpPerspective(img, transformation, final_size)
    if show_plot:
        plt.subplots(figsize=(15, 9))
        plt.subplot(121), plt.imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB)), plt.title('Input')
        plt.subplot(122), plt.imshow(cv.cvtColor(warped_img, cv.COLOR_BGR2RGB)), plt.title('Output')
    return warped_img


@timeit
def rectify_wrt_red_dots(img, dst_shape, red_color_ranges, n_dots=4, show_plot=False, verbose=False):
    """This function assumes we have four red dots in an image which represent the convex hull in a rectangular
    shape. When taking an image the camera is likely to take the picture a little bit from the side and distortion
    effects may take place. This function rectifies the image such that the four red dots form the outer boundary
    of the image.

    Arguments
    ---------
        img: input image
        red_color_ranges: list of HSVCOlorRange's for red low and red high filter ranges
        dst_shape: tuple for size of final image, e.g. (600, 400) will give 600 pixels in x and 400 in y direction
        show_plot: if True, shows plot of before and after warping process
    Returns
    -------
        (warped, success): a warped version of the input image in dst_shape and a boolean whether warping worked
    """
    img_red = filter_keep_multi_ranges(img, red_color_ranges)
    img_labelled_proc, filtered_regions = planvec.img_proc.find_regions(img_red, area_threshold=2, intens_threshold=10)
    if len(filtered_regions) != 4:
        # Rectification only works if we find 4 corners, else we return the original image and signal no success
        return img, False
    filtered_regions = sorted(filtered_regions, key=lambda region: region.area, reverse=True)
    """
    We need to sort corner_centroids such that they map correctly to the new corners.
    1 - 3
    |   |
    2 - 4
    Therefore we first sort by lateral x-direction and then by vertical y-direction.
    """
    @timeit
    def sort_points_clockwise(coords):
        center = tuple(map(operator.truediv, reduce(lambda x, y: map(operator.add, x, y), coords), [len(coords)] * 2))
        return sorted(coords, key=lambda coord: (-135 - math.degrees(math.atan2(*tuple(map(operator.sub, coord, center))[::-1]))) % 360)
    corner_centroids = sort_points_clockwise([(region.centroid[1], region.centroid[0]) for region in filtered_regions])
    new_corners = [[0, 0], [0, dst_shape[1]], [dst_shape[0], dst_shape[1]], [dst_shape[0], 0]]
    warped = warp_image(img, corner_centroids, new_corners, dst_shape, show_plot=show_plot)
    if verbose:
        print(DEBUG_BARS)
        print(f'Warping image wrt corners. Found {len(corner_centroids)} corners at positions\n'
              f'{np.array(corner_centroids).round(decimals=2)}\nMapped to \n{np.array(new_corners)}.\nNew image size: {dst_shape}.')
    return warped, True

