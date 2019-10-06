import os
import tempfile
import img2pdf
import cv2 as cv
from PIL import Image
import matplotlib.pyplot as plt


def read_img(dir_path, name, to_bgr=False):
    """Reads an image from file.
    Usual formats such as jpg, png, ... supported,
    see https://pillow.readthedocs.io/en/3.0.x/handbook/image-file-formats.html for comprehensive list.
    """
    rgb_img = plt.imread(os.path.join(dir_path, name))
    if to_bgr:
        return cv.cvtColor(rgb_img, cv.COLOR_RGB2BGR)
    else:
        return rgb_img


def write_img_to_pdf(out_file_path, img):
    """Writes an image to pdf using the img2pdf package (https://gitlab.mister-muffin.de/josch/img2pdf)/"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # First write the image to jpeg in temporary file
        tmp_img = Image.fromarray(img)
        tmp_img.save(os.path.join(tmp_dir, 'tmp_img.jpeg'))
        # Then read the jpg and let img2pdf convert it to a pdf
        with open(out_file_path, "wb") as out_file:
            out_file.write(img2pdf.convert(os.path.join(tmp_dir, 'tmp_img.jpeg')))
        print(f'Stored image pdf at {out_file_path}.')


def fig_to_pdf(out_dir_path, filename, fig):
    """Stores a matplotlib figure to file. out_file_path should be full path e.g. /path/to/dir/output.pdf."""
    assert filename.split('.')[-1] == 'pdf', 'File ending should be .pdf'

    # TODO: Scale stuff should happen here to ensure correct scaling of output pdf w.r.t. real images.
    fig.savefig(os.path.join(out_dir_path, filename))
