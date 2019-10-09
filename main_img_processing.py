import os
import argparse
import planvec.pipeline
import planvec.io
import planvec.vizualization

ASSETS_DIR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test', 'assets')
DEFAULT_FILE_PATH = os.path.join(ASSETS_DIR_PATH, 'solid_lines.jpg')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file-path', default=DEFAULT_FILE_PATH)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    input_img = planvec.io.read_img_full_path(args.file_path, to_bgr=True)
    output_img = planvec.pipeline.run_pipeline(input_img, visualize_steps=False, verbose=False)
    #planvec.vizualization.imshow(output_img, axis='off', img_space='BGR')
