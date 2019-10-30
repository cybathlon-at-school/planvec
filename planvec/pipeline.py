import skimage
import matplotlib.pyplot as plt
from PIL.ImageQt import ImageQt

from planvec import img_proc
from planvec import color_range
from planvec import vizualization
from planvec import conversions

HELPER_COLOR_RANGES = [color_range.BLUE, color_range.RED_HIGH, color_range.RED_LOW, color_range.GREEN]
DEFAULT_FIG_SIZE = (13, 8)


def run_pipeline(img, visualize_steps=False, verbose=False, return_np_arr=True, return_fig=False):
    """Full processing pipeline for an incoming image producing end-to-end the final figure which then can be
    stored as a pdf."""
    if verbose:
        print(f'Input image shape: {img.shape}')

    if visualize_steps:
        vizualization.imshow(img, axis='off', figsize=DEFAULT_FIG_SIZE, img_space='BGR')
    # Process image, stretch to dots, and filter out helper colors
    img = img_proc.rectify_wrt_red_dots(img, (600, 350), show_plot=visualize_steps, verbose=verbose)
    img = img_proc.add_gaussian_blur(img, 3, 3)
    img = img_proc.filter_multi_hsv_ranges_to_white(img, HELPER_COLOR_RANGES)
    if visualize_steps:
        vizualization.imshow(img, axis='off', figsize=DEFAULT_FIG_SIZE, img_space='BGR')
    img = img_proc.img_to_greyscale(img)
    img = img_proc.thresh_img(img, 110, 255)
    if visualize_steps:
        vizualization.imshow(img, axis='off', figsize=DEFAULT_FIG_SIZE, img_space='BGR')

    # Labelling connected regions
    labelled_img, n = skimage.measure.label(img, background=0, return_num=True)
    regions = skimage.measure.regionprops(labelled_img)
    if verbose:
        print(f'Found {n} regions.')
    img_labelled_proc, filtered_regions = img_proc.filter_regions(labelled_img, regionprops=regions,
                                                                  area_threshold=5000, verbose=verbose)
    if verbose:
        print(f'After filtering, {len(filtered_regions)} are left.')
    if visualize_steps:
        vizualization.imshow(img_labelled_proc, axis='off', figsize=DEFAULT_FIG_SIZE, img_space='BGR')
        vizualization.plot_image_regions(img_labelled_proc, filtered_regions, figsize=DEFAULT_FIG_SIZE)

    # Find and filter contours of connected regions
    contours = img_proc.find_contours(img_labelled_proc != 0, 0)
    contours = img_proc.filter_contours_by_size(contours, n_points_thresh=100)

    # Approximate contours by polygons to smooth outline
    approx_contours = []
    for contour in contours:
        approx_contours.append(skimage.measure.approximate_polygon(contour.copy(), tolerance=1))

    output_fig = vizualization.plot_contours(approx_contours, axis='off', color='red', linewidth=0.5,
                                             figsize=DEFAULT_FIG_SIZE)
    output_fig.set_size_inches(6, 5)

    # Important: Close the figure, else a shitton of figures are staying open
    #            which will fill up memory.
    pil_img = conversions.fig2img(output_fig)
    if not return_fig:
        plt.close(output_fig)

        return ImageQt(pil_img)
    else:
        print(plt.get_fignums())
        # if return_np_arr:
        #    return conversions.fig2img(output_fig)
        #    plt.close('all')
        return output_fig
