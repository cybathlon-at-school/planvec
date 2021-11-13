"""
pdf_jammer

Command line tool to load output PDFs from a session and arrange them in a grid on a
larger PDF ready for laser cutting multiple Drawings.

The tool will grab the output from all teams from a certain session (date) and concatenate them to one or multiple
output PDFs, ready for laser cutting.
"""
import argparse
from pathlib import Path

from planvec.gui.datamanager import DataManager
from planvec.pdf_jammer import PdfJammer
from planvec.planvec_paths import DATA_DESKTOP_DIR_PATH


DEFAULT_OUT_DIR_PAR = Path.home() / 'Desktop'


def parse_arguments():
    parser = argparse.ArgumentParser(description='Arrange the single pdf outputs of a planvec session into '
                                                 'one or more laser-cutting ready pdfs.')
    parser.add_argument('-d', '--date-tag', required=True,
                        help='Specify the date of the session you want to process, e.g. "2019-31-05".')
    parser.add_argument('-o', '--out-dir', required=False, type=Path,
                        help='Absolute path - location to store created output pdf\'s. '
                             'Defaults to session folder given by --date-tag field.')
    args = parser.parse_args()
    return args


def main(parsed_args):
    equal_signs = 30 * '='
    print(f'{equal_signs} PDF JAMMER {equal_signs}\t')
    data_manager = DataManager(output_location='desktop', date_tag=parsed_args.date_tag)
    pdf_jammer = PdfJammer(data_manager=data_manager,
                           out_dir_path=parsed_args.out_dir if parsed_args.out_dir else DATA_DESKTOP_DIR_PATH / parsed_args.date_tag)
    pdfs_dict = pdf_jammer.accumulate_pdf_paths_all_schools_and_teams()
    pdf_paths_list = pdf_jammer.teams_pdfs_paths_to_list(pdfs_dict)
    pdf_jammer.run(pdf_paths_list)
    print(f'{equal_signs}==========={equal_signs}\t')


if __name__ == '__main__':
    main(parse_arguments())
