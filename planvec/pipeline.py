import skimage
from PIL.ImageQt import ImageQt

from planvec import img_proc
from planvec import vizualization
from planvec import conversions
from config import planvec_config

DEFAULT_FIG_SIZE = (13, 8)
COLOR_RANGES = planvec_config.color_range.toDict()  # convert DotMap to Dict
RED_COLOR_RANGES = [color_range for key, color_range in COLOR_RANGES.items() if 'red' in key]


def run_pipeline(img, ax, visualize_steps=False, verbose=False, return_np_arr=True, return_fig=False, save_pdf_path=None):
    """Full processing pipeline for an incoming image producing end-to-end the final figure which then can be
    stored as a pdf."""

    if visualize_steps:
        vizualization.imshow(img, figsize=DEFAULT_FIG_SIZE, img_space='BGR', title='Input image')
    # ----- Process image, stretch to dots -----

    img, warped_ok = img_proc.rectify_wrt_red_dots(img, planvec_config.processing.rectify_shape, RED_COLOR_RANGES,
                                                   show_plot=visualize_steps, verbose=verbose)
    if not warped_ok:
        return ax, conversions.bgr2qt(img)
    # ----- Add Gaussian Blur before filtering colors -----
    img = img_proc.add_gaussian_blur(img, *planvec_config.processing.gaussian_blur)

    # ----- Filter out (make white) color ranges -----
    img = img_proc.filter_multi_hsv_ranges_to_white(img, list(COLOR_RANGES.values()))
    if visualize_steps:
        vizualization.imshow(img, figsize=DEFAULT_FIG_SIZE, img_space='BGR', title='Filtered out colors')

    # ----- Convert to greyscale -----
    img = img_proc.img_to_greyscale(img)
    if visualize_steps:
        vizualization.imshow(img, figsize=DEFAULT_FIG_SIZE, img_space='BGR', title='Grey scale')

    # ----- Threshold image -----
    img = img_proc.thresh_img(img, *planvec_config.processing.img_threshold)
    if visualize_steps:
        vizualization.imshow(img, figsize=DEFAULT_FIG_SIZE, img_space='BGR', title='Grey thresholded')

    # ----- Labelling connected regions -----
    labelled_img, n = skimage.measure.label(img, background=0, return_num=True)
    regions = skimage.measure.regionprops(labelled_img)
    # TODO(matt): Clear stuff up and use find / filter regions functions properly.

    if visualize_steps:
        vizualization.imshow(labelled_img, figsize=DEFAULT_FIG_SIZE, img_space='BGR',
                             title='Regions before filter')

    # ----- Filter regions by size -----
    img_labelled_proc, filtered_regions = img_proc.filter_regions(labelled_img, regionprops=regions,
                                                                  area_threshold=planvec_config.processing.area_threshold,
                                                                  verbose=verbose)
    if visualize_steps:
        vizualization.imshow(img_labelled_proc, figsize=DEFAULT_FIG_SIZE, img_space='BGR',
                             title='Regions after filter')
        vizualization.plot_image_regions(img_labelled_proc, filtered_regions, figsize=DEFAULT_FIG_SIZE,
                                         title='Image regions filtered with boxes')

    # ----- Find and filter contours of connected regions -----
    contours = img_proc.find_contours(img_labelled_proc != 0, level=0)
    contours = img_proc.filter_contours_by_size(contours, n_points_thresh=planvec_config.processing.contours_size_threshold)

    # ----- Approximate contours by polygons to smooth outline ------
    approx_contours = []
    for contour in contours:
        approx_contours.append(skimage.measure.approximate_polygon(contour.copy(), tolerance=0.7))

    # ----- Creating the final output figure of the contours ------
    ax = vizualization.plot_contours(approx_contours, ax=ax, color='red',
                                     linewidth=planvec_config.processing.line_width, axis='off')
    ax.figure.set_size_inches(*planvec_config.processing.out_size_inches)

    pil_img = conversions.fig2img(ax.figure)
    return ax, ImageQt(pil_img)
