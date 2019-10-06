import numpy as np
import matplotlib.pyplot as plt
import skimage
import cv2 as cv
import planvec.vizualization
from planvec import color_range
from planvec.color_range import HSVColorRange

from typing import List


def copy_img(img):
    return np.copy(img)


def img_to_greyscale(img):
    return cv.cvtColor(img, cv.COLOR_BGR2GRAY)


def add_gaussian_blur(img, std_x, std_y):
    return cv.GaussianBlur(img, (std_x, std_y), sigmaX=0)


def thresh_img(img, thresh_val, max_val, thresh_type=cv.THRESH_BINARY):
    """Apply threshold to pixel values from an image. Refer to
    https://docs.opencv.org/2.4/doc/tutorials/imgproc/threshold/threshold.html for docs."""
    _, img = cv.threshold(img, thresh_val, max_val, thresh_type)
    return img


def invert_mask(mask):
    """Inverts an 8-bit mask (max value is 255)"""
    return 255 - mask


def create_hsv_range_mask(img, hsv_color_range: HSVColorRange):
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    return cv.inRange(hsv, np.array(hsv_color_range.start), np.array(hsv_color_range.end))


def filter_keep_by_hsv_range(img, hsv_color_range: HSVColorRange):
    """Returns an image where only pixels are kept with their values which fall into a HSV range between
    range_start, e.g. [0, 0, 0] and range_end, e.g. [179, 255, 255] or any values inbetween those bounds."""
    mask = create_hsv_range_mask(img, hsv_color_range)
    return cv.bitwise_and(img, img, mask=mask)


def filter_keep_multi_ranges(img, hsv_color_ranges: List[HSVColorRange]):
    masks = [create_hsv_range_mask(img, color_range) for color_range in hsv_color_ranges]
    final_mask = sum(masks)
    return cv.bitwise_and(img, img, mask=final_mask)


def filter_by_hsv_range_to_white(img, hsv_color_range: HSVColorRange):
    img = copy_img(img)
    mask = planvec.img_proc.create_hsv_range_mask(img, hsv_color_range)
    img[mask > 0] = 255
    return img


def filter_multi_hsv_ranges_to_white(img, hsv_color_ranges: List[HSVColorRange]):
    img = copy_img(img)
    for color_range in hsv_color_ranges:
        img = filter_by_hsv_range_to_white(img, color_range)
    return img


def white_pixels_to_black(img):
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(gray, 100, 255, cv.THRESH_BINARY)
    img[thresh == 255] = 0


def adaptive_thresh_img(img):
    # TODO: Remove hard coded stuff.
    return cv.adaptiveThreshold(img, 100, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 101, 10)


def find_contours(img, value):
    contours = skimage.measure.find_contours(img, value)
    return contours


def filter_contours_by_size(contours, n_points_thresh):
    return [cont for cont in contours if len(cont) > n_points_thresh]


def find_regions(img, area_threshold, intens_threshold):
    """Use skimage's region finding capabilities to find connected regions in an image.

    #TODO: specify args and returns
    """
    # Threshold processing
    img = planvec.img_proc.img_to_greyscale(img)
    img = planvec.img_proc.add_gaussian_blur(img, 5, 5)
    img_thresh = planvec.img_proc.thresh_img(img, thresh_val=intens_threshold, max_val=255, thresh_type=cv.THRESH_BINARY)
    labelled_img, n = skimage.measure.label(img_thresh, background=0, return_num=True)
    regions = skimage.measure.regionprops(labelled_img)
    # Filtering regions
    img_labelled_proc, filtered_regions = planvec.img_proc.filter_regions(labelled_img, regionprops=regions,
                                                                          area_threshold=area_threshold)
    return img_labelled_proc, filtered_regions


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
                print(f'Region {region.label} has area: {region.area} == (image size). Removed.')
            labelled_img[region_mask] = 0
            continue
        # Remove regions which are too small (basically noise)
        if region.area < area_threshold:
            if verbose:
                print(f'Region {region.label} has area: {region.area} < {area_threshold}. Too small. Removed.')
            labelled_img[region_mask] = 0
            continue
        filtered_regions.append(region)
    return labelled_img, filtered_regions


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
        plt.show()
    return warped_img


def rectify_wrt_red_dots(img, dst_shape, show_plot=False):
    """This function assumes we have four red dots in an image which represent the convex hull in a rectangular
    shape. When taking an image the camera is likely to take the picture a little bit from the side and distortion
    effects may take place. This function rectifies the image such that the four red dots form the outer boundary
    of the image.

    Arguments
    ---------
        img: input image
        dst_shape: tuple for size of final image, e.g. (600, 400) will give 600 pixels in x and 400 in y direction
        show_plot: if True, shows plot of before and after warping process
    Returns
    -------
        warped: a warped version of the input image in dst_shape
    """
    img_red = filter_keep_multi_ranges(img, [color_range.RED_LOW, color_range.RED_HIGH])
    img_labelled_proc, filtered_regions = planvec.img_proc.find_regions(img_red, 2, 10)
    corner_centroids = [[region.centroid[1], region.centroid[0]] for region in filtered_regions]
    new_corners = [[0, 0], [dst_shape[0], 0], [0, dst_shape[1]], [dst_shape[0], dst_shape[1]]]

    assert len(corner_centroids) == 4, f'Corner extraction failed. Extracted {len(corner_centroids)} but 4 expected.'
    warped = warp_image(img, corner_centroids, new_corners, dst_shape, show_plot=show_plot)
    return warped


def live_color_filter(use_camera=True, img=None):
    """Opens up a window for HSV color filtering based on camera input or an img. Let's you interactively adapt
    HSV threshold values to filter the image."""
    # Create a window
    cv.namedWindow('image')

    # create trackbars for color change
    # OpenCV HSV ranges: H -> 0-179, S -> 0-255, V -> 0-255
    def nothing(x):
        pass

    cv.createTrackbar('HMin', 'image', 0, 179, nothing)
    cv.createTrackbar('SMin', 'image', 0, 255, nothing)
    cv.createTrackbar('VMin', 'image', 0, 255, nothing)
    cv.createTrackbar('HMax', 'image', 0, 179, nothing)
    cv.createTrackbar('SMax', 'image', 0, 255, nothing)
    cv.createTrackbar('VMax', 'image', 0, 255, nothing)

    # Set default value for MAX HSV trackbars.
    cv.setTrackbarPos('HMax', 'image', 179)
    cv.setTrackbarPos('SMax', 'image', 255)
    cv.setTrackbarPos('VMax', 'image', 255)

    # Initialize to check if HSV min/max value changes
    hMin = sMin = vMin = hMax = sMax = vMax = 0
    phMin = psMin = pvMin = phMax = psMax = pvMax = 0

    # Output Image to display
    if use_camera:
        cap = cv.VideoCapture(0)
        # Wait longer to prevent freeze for videos.
        wait_time = 30
    else:
        assert img is not None, "img parameter needs to be given if camera not used"
        wait_time = 20

    while True:
        if use_camera:
            # Capture frame-by-frame
            ret, img = cap.read()

        # get current positions of all trackbars
        hMin = cv.getTrackbarPos('HMin', 'image')
        sMin = cv.getTrackbarPos('SMin', 'image')
        vMin = cv.getTrackbarPos('VMin', 'image')

        hMax = cv.getTrackbarPos('HMax', 'image')
        sMax = cv.getTrackbarPos('SMax', 'image')
        vMax = cv.getTrackbarPos('VMax', 'image')

        # Set minimum and max HSV values to display
        lower = np.array([hMin, sMin, vMin])
        upper = np.array([hMax, sMax, vMax])

        # Create HSV Image and threshold into a range.
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        mask = cv.inRange(hsv, lower, upper)
        output = cv.bitwise_and(img, img, mask=mask)

        # Print if there is a change in HSV value
        if ((phMin != hMin) | (psMin != sMin) | (pvMin != vMin) | (phMax != hMax) | (psMax != sMax) | (pvMax != vMax)):
            print("(hMin = %d , sMin = %d, vMin = %d), (hMax = %d , sMax = %d, vMax = %d)" % (
                hMin, sMin, vMin, hMax, sMax, vMax))
            phMin = hMin
            psMin = sMin
            pvMin = vMin
            phMax = hMax
            psMax = sMax
            pvMax = vMax

        # Display output image
        cv.imshow('image', output)

        # Wait longer to prevent freeze for videos.
        if cv.waitKey(wait_time) & 0xFF == ord('q'):
            break

    # Release resources
    if use_camera:
        cap.release()
    cv.destroyAllWindows()
