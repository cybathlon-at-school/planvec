import argparse
from pathlib import Path

from PyPDF2 import PdfFileReader


def main(parsed_args: argparse.Namespace):
    pdf = PdfFileReader(parsed_args.file.open('rb'))

    num_pages = pdf.getNumPages()
    for page_idx in range(num_pages):
        print(f"Page: {page_idx}")
        width_cm = round(float(pdf.getPage(page_idx).mediaBox.getWidth()) * 2.54 / 72.0)
        height_cm = round(float(pdf.getPage(page_idx).mediaBox.getHeight()) * 2.54 / 72.0)
        print(f"\tWidth: {width_cm}cm")
        print(f"\tHeight: {height_cm}cm")
        print("---")


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('--file',
                        type=Path,
                        required=True,
                        help='path to file')

    args = parser.parse_args()

    validate_args(args)

    return args


def validate_args(args: argparse.Namespace):
    path_to_file: Path = args.file
    if not path_to_file.exists():
        raise IOError(f'The specified path {path_to_file} does not exist. Exit.')


if __name__ == '__main__':
    main(parse_arguments())
