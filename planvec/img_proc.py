import numpy as np
import skimage
import cv2
import planvec.vizualization


def copy_img(img):
    return np.copy(img)


def img_to_greyscale(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def add_gaussian_blur(img, std_x, std_y):
    return cv2.GaussianBlur(img, (std_x, std_y), 0)


def thresh_img(img, thresh_val, max_val, thresh_type=cv2.THRESH_BINARY):
    _, img = cv2.threshold(img, thresh_val, max_val, thresh_type)
    return img


def filter_by_hsv_range(img, range_start, range_end):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, np.array(range_start), np.array(range_end))
    filtered_img = cv2.bitwise_and(img, img, mask=mask)
    planvec.vizualization.imshow(mask)
    return filtered_img


def adaptive_thresh_img(img):
    # TODO: Remove hard coded stuff.
    return cv2.adaptiveThreshold(img, 100, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 101, 10)


def find_contours(img, value):
    contours = skimage.measure.find_contours(img, value)
    return contours


def filter_contours_by_size(contours, n_points_thresh):
    return [cont for cont in contours if len(cont) > n_points_thresh]


def filter_regions(labelled_img, regionprops, area_threshold):
    filtered_regions = []
    for region in regionprops:
        region_mask = labelled_img == region.label
        # Remove regions which have image size since they represent the boundary
        if region.bbox_area == np.prod(np.array(labelled_img.size)):
            print(f'Region {region.label} has area: {region.area} == (image size). Removed.')
            labelled_img[region_mask] = 0
            continue
        # Remove regions which are too small (basically noise)
        if region.area < area_threshold:
            print(f'Region {region.label} has area: {region.area} < {area_threshold}. Too small. Removed.')
            labelled_img[region_mask] = 0
            continue
        filtered_regions.append(region)
    return labelled_img, filtered_regions
