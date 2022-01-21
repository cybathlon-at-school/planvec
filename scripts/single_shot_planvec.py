import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import cv2

from context import planvec
from planvec import vizualization
from planvec.pipeline import run_pipeline
from planvec.utils.date_utils import get_date_time_tag
from config import planvec_config


def main(parsed_args: argparse.Namespace):
    cap = cv2.VideoCapture(parsed_args.camera)
    ret, input_img = cap.read()

    # Show input image
    planvec.vizualization.imshow(input_img, axis='on', figsize=(18, 12), img_space='BGR')

    # Setup output final output figure and run complete pipeline
    fig, ax = vizualization.setup_figure()
    _, output_img = run_pipeline(input_img, ax,
                                 visualize_steps=False,
                                 verbose=False,
                                 config=planvec_config.processing,
                                 color_ranges=planvec_config.color_range.toDict())

    if parsed_args.display:
        plt.show()

    if not parsed_args.skip_save:
        fig.tight_layout(pad=0)
        fig.savefig(parsed_args.out_dir / get_date_time_tag(), bbox_inches='tight', pad_inches=0)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Single-image (from webcam) end-to-end processing pipeline '
                                                 'to process a single input and generate a pdf output. '
                                                 'To run this script, simply activate the pipenv environment '
                                                 '(pipenv shell), go to the "scripts" folder and run '
                                                 '"python single_shot_planvec.py". Display help with --help.')
    parser.add_argument('-c', '--camera',
                        type=int,
                        default=4,
                        help='Which camera to use. Depends on the actual machine this command is run on. '
                             'Usually something like 1 works, you might want to try values between 0 and 4.')
    parser.add_argument('-o', '--out-dir',
                        type=Path,
                        default=Path.home() / 'Desktop',
                        help='Absolute, full-specified path - location (directory) to store created output pdf. '
                             'Defaults to Desktop if not specified. If specified, directory needs to exist. '
                             'Example: /home/cybathlon/planvec/output_images')
    parser.add_argument('--input-width',
                        type=float,
                        help='The width of the input drawing in centimeters.')
    parser.add_argument('--input-height',
                        type=float,
                        help='The height of the input drawing in centimeters.')
    parser.add_argument('--output-width',
                        type=float,
                        help='The width of the output plate in centimeters.')
    parser.add_argument('--output-height',
                        type=float,
                        help='The height of the output plate in centimeters.')
    parser.add_argument('-d', '--display',
                        action='store_true',
                        help='Specify this flag without any value if you want to '
                             'see/display the input and output image. '
                             'As of default, they are not shown. In case you chose to save the image, this happens '
                             'only after you closed the display windows.')
    parser.add_argument('-s', '--skip-save',
                        action='store_true',
                        help='Specify this flag without any value if you do NOT want to save the output. '
                             'As of default, the output is being stored in the specified output directory.')
    args = parser.parse_args()

    validate_args(args)

    return args


def validate_args(args: argparse.Namespace):
    path_to_output_directory: Path = args.out_dir
    if not path_to_output_directory.exists():
        raise IOError(f'The specified path {path_to_output_directory} does not exist. Exit.')
    for value in [args.input_width, args.input_height, args.output_width, args.output_height]:
        if value <= 0:
            raise ValueError(f'Input and output sizes need to be > 0. Exit.')
    if args.output_width < args.input_width:
        raise ValueError(f'The output width of the plate needs to be greater or equal to the input drawing width.')
    if args.output_height < args.input_height:
        raise ValueError(f'The output height of the plate needs to be greater or equal to the input drawing height.')


if __name__ == '__main__':
    main(parse_arguments())
