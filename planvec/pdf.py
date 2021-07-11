import os
import subprocess
import math

from dotmap import DotMap

from planvec.gui.datamanager import DataManager
from planvec.utils.date_utils import get_date_time_tag
from config import planvec_config
from typing import Dict, List


UNITE_FILE_TEMPL = 'unite_plate-{plate_idx}_{date_time_tag}.pdf'
JAMMED_FILE_TEMPL = 'jammed_plate-{plate_idx}_{date_time_tag}.pdf'


class PdfJammer:
    # TODO: Inject config into PdfJammer!
    def __init__(self, config: DotMap, data_manager: DataManager, out_dir: str, verbose: bool = True):
        self.config = config
        self.data_manager = data_manager
        self.out_dir = out_dir
        self.verbose = verbose

    def run(self, pdf_paths: List[str]) -> None:
        unite_commands, jam_commands = self.create_commands(pdf_paths)
        for unite_command, jam_command in zip(unite_commands, jam_commands):
            subprocess.call(unite_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.call(' '.join(jam_command), shell=True, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)  # pdfjam seems to work only with shell call
        print('Done.')

    def create_commands(self, pdfs) -> (List[List[str]], List[List[str]]):
        """Main function to arrange all pdfs in the input list on one or more single-page pdfs."""
        self.print_general_info(len(pdfs))
        n_grippers_per_plate = calc_max_n_pdfs_per_plate(PLATE_WIDTH, PLATE_HEIGHT, PDF_WIDTH, PDF_HEIGHT)
        unite_commands = []
        jam_commands = []
        for plate_idx, pdfs_chunk in enumerate(chunks(pdfs, n_grippers_per_plate)):
            unite_command, unite_file_path = self._create_unite_command(pdfs_chunk, plate_idx)
            jam_command = self._create_jam_command(unite_file_path, len(pdfs_chunk))
            # Step one: 'pdfunite' -> Merge all pdfs of this chunk into one pdf as pages
            unite_commands.append(unite_command)
            # Step two: 'pdfjam' -> Arrange all pages in the united pdf on a board given the dimensions of the
            #                       board and the individual pdfs.
            jam_commands.append(jam_command)
            self.print_plate_info(len(pdfs_chunk), plate_idx, jam_command[-1])
        return unite_commands, jam_commands

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
        command = ['pdfjam'] + [f'--nup {n_cols}x{n_rows}'] + [united_file_path] + [
            f"--papersize \'{{{width}cm, {height}cm}}\'"]
        command += [f'--outfile {out_file_path}']
        return command

    def _accumulate_pdf_names(self) -> Dict[str, List[str]]:
        """Accumulates the .pdf output files for each team."""
        team_names = self.data_manager.load_all_team_names()
        teams_pdfs = {}
        for team in team_names:
            teams_pdfs[team] = self.data_manager.load_team_output_file_names(team,
                                                                             endswith='output.pdf')
        return teams_pdfs

    def accumulate_pdf_paths(self) -> Dict[str, List[str]]:
        """Accumulates the .pdf output file paths for each team."""
        teams_pdfs = self._accumulate_pdf_names()
        teams_pdfs_paths = {}
        for team, pdf_list in teams_pdfs.items():
            teams_pdfs_paths[team] = [os.path.join(self.data_manager.out_dir_path, team, f) for f in pdf_list]
        return teams_pdfs_paths

    @staticmethod
    def teams_pdfs_paths_to_list(teams_pdfs_paths):
        """Transform output from accumulate_pdf_paths to a single list of pdfs for all teams."""
        pdfs_list = []
        for pdfs in teams_pdfs_paths.values():
            pdfs_list += pdfs
        return pdfs_list

    @staticmethod
    def print_pdf_paths(teams_pdf_dict: Dict[str, List[str]]) -> None:
        print(f'Arranging pdf\'s for the following teams...')
        for team, pdfs in teams_pdf_dict.items():
            print(f'  {team}')
            for path in pdfs:
                print(f'   {os.path.split(path)[1]}')

    def print_general_info(self, n_pdfs_total):
        max_pdfs_per_plate = calc_max_n_pdfs_per_plate(PLATE_WIDTH, PLATE_HEIGHT, PDF_WIDTH, PDF_HEIGHT)
        n_plates = calc_n_plates(max_pdfs_per_plate, n_pdfs_total)
        print(f'Collecting output from {self.data_manager.out_dir_path}...')
        print(f'Found {n_pdfs_total} pdf output files.')
        pdfs_dict = self.accumulate_pdf_paths()
        PdfJammer.print_pdf_paths(pdfs_dict)
        print(f'Given dimensions:')
        print(f' Plate width:\t {PLATE_WIDTH}')
        print(f' Plate height:\t {PLATE_HEIGHT}')
        print(f' PDF width:\t\t {PDF_WIDTH}')
        print(f' PDF width:\t\t {PDF_HEIGHT}')
        print(f' which means maximum {max_pdfs_per_plate} PDF\'s per plate and...')
        print(f' and in this case {n_plates} {"plates" if n_plates > 1 else "plate"} '
              f'for {n_pdfs_total} PDF\'s in total.')

    @staticmethod
    def print_plate_info(n_pdfs_on_plate, plate_idx, out_file_path):
        n_cols, n_rows = calc_n_cols_rows(n_pdfs_on_plate)
        final_width, final_height = calc_final_width_height(n_cols, n_rows)
        print(f'Plate {plate_idx + 1}: ')
        print(f'\t{n_pdfs_on_plate} PDF{"s" if n_pdfs_on_plate > 1 else ""} on this plate.')
        print(f'\tGrid dimensions {n_cols}{"cols" if n_cols > 1 else "col"} x '
              f'{n_rows}{"rows" if n_rows > 1 else "row"} with a total size of '
              f'{final_width}x{final_height} cm')
        print(f'\t{out_file_path}')


def calc_max_n_horizontal(plate_width, pdf_width):
    return plate_width // pdf_width


def calc_max_n_vertical(plate_height, pdf_height):
    return plate_height // pdf_height


def calc_max_n_pdfs_per_plate(plate_width, plate_height, pdf_width, pdf_height):
    """"Given the sizes of the gripper pdfs and laser cutter plate. How many grippers go on one plate?"""
    return calc_max_n_horizontal(plate_width, pdf_width) * calc_max_n_vertical(plate_height, pdf_height)


def calc_n_plates(max_pdfs_per_plate, n_pdfs):
    """Given the dimensions of a plate and the single pdfs, how many plates are needed?"""
    return math.ceil(n_pdfs / max_pdfs_per_plate)


def calc_n_cols_rows(n_pdfs):
    """Given the dimensions of the plate and single pdf and the number of pdfs, how many cols and rows are required."""
    n_max_cols = calc_max_n_horizontal(PLATE_WIDTH, PDF_WIDTH)
    n_cols = n_pdfs if n_pdfs < n_max_cols else n_max_cols
    n_rows = math.ceil(n_pdfs / n_cols)
    return n_cols, n_rows


def calc_final_width_height(n_cols, n_rows):
    width = n_cols * PDF_WIDTH
    height = n_rows * PDF_HEIGHT
    return width, height


def chunks(list_, chunk_size):
    """Yield successive (chunk_size)-sized chunks from list_."""
    for idx in range(0, len(list_), chunk_size):
        yield list_[idx:idx + chunk_size]
