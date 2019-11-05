import os
import subprocess
from pprint import pprint

from planvec.common import DATA_DIR_PATH
from planvec.gui.gui_io import DataManager
from typing import Dict, List


class PdfJammer:
    def __init__(self, data_manager: DataManager, out_dir: str):
        self.data_manager = data_manager
        self.out_dir = out_dir

    def jam_pdfs(self, pdfs, out_size=(50, 80)):
        """Main function to arrange all pdfs in the input list on one or more single-page pdfs."""
        print(pdfs)

    def accumulate_pdf_names(self) -> Dict[str, List[str]]:
        """Accumulates the .pdf output files for each team."""
        team_names = self.data_manager.load_all_team_names()
        teams_pdfs = {}
        for team in team_names:
            teams_pdfs[team] = self.data_manager.load_team_img_names(team,
                                                                     endswith='output.pdf')
        return teams_pdfs

    def accumulate_pdf_paths(self) -> Dict[str, List[str]]:
        """Accumulates the .pdf output file paths for each team."""
        teams_pdfs = self.accumulate_pdf_names()
        teams_pdfs_paths = {}
        for team, pdf_list in teams_pdfs.items():
            teams_pdfs_paths[team] = [os.path.join(DATA_DIR_PATH, f) for f in pdf_list]
        return teams_pdfs_paths

    @staticmethod
    def teams_pdfs_paths_to_list(teams_pdfs_paths):
        """Transform output from accumulate_pdf_paths to a single list of pdfs for all teams."""
        pdfs_list = []
        for pdfs in teams_pdfs_paths.values():
            pdfs_list += pdfs
        return pdfs_list
