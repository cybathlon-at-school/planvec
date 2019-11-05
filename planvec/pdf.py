import os
import subprocess
from pprint import pprint
import math

from planvec.common import DATA_DIR_PATH
from planvec.gui.gui_io import DataManager
from planvec.utils.date_utils import get_date_time_tag
from typing import Dict, List

# In cm
# TODO: Maybe put inside config?
PDF_WIDTH = 20
PDF_HEIGHT = 14
PLATE_WIDTH = 80
PLATE_HEIGHT = 50
UNITE_FILE_TEMPL = 'unite_plate-{plate_idx}_{date_time_tag}.pdf'
JAMMED_FILE_TEMPL = 'jammed_plate-{plate_idx}_{date_time_tag}.pdf'


class PdfJammer:
    def __init__(self, data_manager: DataManager, out_dir: str):
        self.data_manager = data_manager
        self.out_dir = out_dir

    def jam_pdfs(self, pdfs):
        """Main function to arrange all pdfs in the input list on one or more single-page pdfs."""
        n_grippers_per_plate = calc_max_n_pdfs_per_plate(PLATE_WIDTH, PLATE_HEIGHT, PDF_WIDTH, PDF_HEIGHT)

        for plate_idx, pdfs_chunk in enumerate(chunks(pdfs, n_grippers_per_plate)):
            unite_command, unite_file_path = self._create_unite_command(pdfs_chunk, plate_idx)
            jam_command = self._create_jam_command(unite_file_path, len(pdfs_chunk))
            # Step one: 'pdfunite' -> Merge all pdfs of this chunk into one pdf as pages
            subprocess.call(unite_command)
            # Step two: 'pdfjam' -> Arrange all pages in the united pdf on a board given the dimensions of the
            #                       board and the individual pdfs.
            subprocess.call(' '.join(jam_command), shell=True)  # pdfjam seems to work only with shell call

    def _create_unite_command(self, pdfs, plate_idx):
        """Creates the subprocess command to merge multiple pdfs to one pdf with multiple pages."""
        n_grippers_per_plate = calc_max_n_pdfs_per_plate(PLATE_WIDTH, PLATE_HEIGHT, PDF_HEIGHT, PDF_HEIGHT)
        if len(pdfs) > n_grippers_per_plate:
            raise ValueError(f'Cannot have more than {n_grippers_per_plate} on one plate! Given: {len(pdfs)}.')
        out_file_name = UNITE_FILE_TEMPL.format(plate_idx=plate_idx,
                                                date_time_tag=get_date_time_tag())
        out_file_path = os.path.join(self.data_manager.out_dir_path, out_file_name)
        command = ['pdfunite'] + pdfs + [out_file_path]
        return command, out_file_path

    def _create_jam_command(self, united_file_path, n_pdfs):
        """Creates a list of strings representing the subprocess command to jam them ."""
        out_dir_path, united_file_name = os.path.split(united_file_path)
        jam_file_name = '_'.join(['jammed', united_file_name.split('_', 1)[1]])
        out_file_path = os.path.join(self.data_manager.out_dir_path, jam_file_name)

        max_pdfs_per_plate = calc_max_n_pdfs_per_plate(PLATE_WIDTH, PLATE_HEIGHT, PDF_WIDTH, PDF_HEIGHT)
        n_max_cols = calc_max_n_horizontal(PLATE_WIDTH, PDF_WIDTH)
        n_max_rows = calc_max_n_vertical(PLATE_HEIGHT, PDF_HEIGHT)
        n_cols = n_pdfs if n_pdfs < n_max_cols else n_max_cols
        n_rows = math.ceil(n_pdfs / n_cols)
        assert n_rows <= n_max_rows, f'n_rows ({n_rows}) cannot be larger than n_max_rows ({n_max_rows}).'
        width = n_cols * PDF_WIDTH
        height = n_rows * PDF_HEIGHT
        command = ['pdfjam'] + [f'--nup {n_cols}x{n_rows}'] + [united_file_path] + [f"--papersize \'{{{width}cm, {height}cm}}\'"]
        command += [f'--outfile {out_file_path}']
        return command

    def _accumulate_pdf_names(self) -> Dict[str, List[str]]:
        """Accumulates the .pdf output files for each team."""
        team_names = self.data_manager.load_all_team_names()
        teams_pdfs = {}
        for team in team_names:
            teams_pdfs[team] = self.data_manager.load_team_img_names(team,
                                                                     endswith='output.pdf')
        return teams_pdfs

    def _accumulate_pdf_paths(self) -> Dict[str, List[str]]:
        """Accumulates the .pdf output file paths for each team."""
        teams_pdfs = self._accumulate_pdf_names()
        teams_pdfs_paths = {}
        for team, pdf_list in teams_pdfs.items():
            teams_pdfs_paths[team] = [os.path.join(self.data_manager.out_dir_path, team, f) for f in pdf_list]
        return teams_pdfs_paths

    @staticmethod
    def _teams_pdfs_paths_to_list(teams_pdfs_paths):
        """Transform output from accumulate_pdf_paths to a single list of pdfs for all teams."""
        pdfs_list = []
        for pdfs in teams_pdfs_paths.values():
            pdfs_list += pdfs
        return pdfs_list


def calc_max_n_horizontal(plate_width, pdf_width):
    return plate_width // pdf_width


def calc_max_n_vertical(plate_height, pdf_height):
    return plate_height // pdf_height


def calc_max_n_pdfs_per_plate(plate_width, plate_height, pdf_width, pdf_height):
    """"Given the sizes of the gripper pdfs and laser cutter plate. How many grippers go on one plate?"""
    return calc_max_n_horizontal(plate_width, pdf_width) * calc_max_n_vertical(plate_height, pdf_height)


def calc_n_plates(n_pdfs_per_plate, n_pdfs):
    """Given the dimensions of a plate and the single pdfs, how many plates are needed?"""
    return math.ceil(n_pdfs / n_pdfs_per_plate)


def chunks(list_, chunk_size):
    """Yield successive (chunk_size)-sized chunks from list_."""
    for idx in range(0, len(list_), chunk_size):
        yield list_[idx:idx + chunk_size]
