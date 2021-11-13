import os
from pathlib import Path
from PyQt5.QtGui import QImage
import matplotlib.pyplot as plt

from planvec.planvec_paths import DATA_REPOSITORY_DIR_PATH
from planvec.planvec_paths import DATA_DESKTOP_DIR_PATH
from planvec.utils import date_utils

from typing import List

date_utils.get_date_tag()
date_utils.get_date_time_tag()

IMG_NAME_FORMAT = '{idx}_{team}_{date_tag}{suffix}.{file_type}'


class DataManager:
    def __init__(self, output_location: str, date_tag: str = date_utils.get_date_tag()):
        self.date_tag = date_tag
        self.out_dir_path = str(self.output_root_dir_path_from_output_location(output_location) / date_tag)
        self.create_date_output_folder_if_not_exists()

    @staticmethod
    def output_root_dir_path_from_output_location(output_location: str) -> Path:
        if output_location == 'desktop':
            return DATA_DESKTOP_DIR_PATH
        elif output_location == 'repository':
            return DATA_REPOSITORY_DIR_PATH
        else:
            raise ValueError(f'output_location {output_location} not supported.')

    def create_date_output_folder_if_not_exists(self) -> None:
        if not os.path.exists(self.out_dir_path):
            os.makedirs(self.out_dir_path)

    def team_dir_exists(self, school_name: str, team_name: str) -> bool:
        assert os.path.exists(self.out_dir_path), 'Output folder for this \
                                                   date does not exist.'

        return os.path.exists(os.path.join(self.out_dir_path, school_name, team_name))

    def school_dir_exists(self, school_name: str) -> bool:
        return os.path.exists(os.path.join(self.out_dir_path, school_name))

    def create_team_folder(self, school_name, team_name: str) -> None:
        if not self.team_dir_exists(school_name, team_name):
            os.makedirs(os.path.join(self.out_dir_path, school_name, team_name))

    def _create_save_img_path(self, school_name: str, team_name: str, file_type: str, suffix: str = '',
                              idx: int = None) -> str:
        assert self.team_dir_exists(school_name, team_name), 'Cannot save. Team directory ' \
                                                             'does not exist.'
        if idx is None:
            idx = self.get_next_team_img_idx(school_name, team_name)
        img_name = IMG_NAME_FORMAT.format(idx=idx,
                                          team=team_name,
                                          date_tag=date_utils.get_date_time_tag(),
                                          suffix=suffix,
                                          file_type=file_type)
        team_dir = os.path.join(self.out_dir_path, school_name, team_name)
        return os.path.join(team_dir, img_name)

    def save_qt_image(self, school_name: str, team_name: str, qt_img: QImage, suffix: str = '', idx: int = None) -> None:
        file_path = self._create_save_img_path(school_name, team_name, 'jpeg', suffix, idx)
        qt_img.save(file_path)

    def save_pdf(self, school_name: str, team_name: str, fig: plt.Figure, suffix: str = '', idx: int = None) -> None:
        file_path = self._create_save_img_path(school_name, team_name, 'pdf', suffix, idx)
        save_output_fig(fig, file_path)

    def load_team_output_file_names(self, school_name, team_name: str, endswith: str) -> List[str]:
        """Load all the output file names of a team, e.g. .jpeg or .pdf files."""
        if self.team_dir_exists(school_name, team_name):
            all_files = os.listdir(os.path.join(self.out_dir_path, school_name, team_name))
            return [f for f in all_files if f.endswith(endswith)]
        else:
            return []

    def get_next_team_img_idx(self, school_name, team_name: str) -> int:
        team_img_names = self.load_team_output_file_names(school_name, team_name, endswith='jpeg')
        img_indices = sorted([int(name.split('_')[0]) for name in team_img_names])
        if len(img_indices) == 0:
            return 0
        return img_indices[-1] + 1

    def load_all_team_names(self, school_name: str) -> List[str]:
        if os.path.exists(os.path.join(self.out_dir_path, school_name)):
            items = os.listdir(os.path.join(self.out_dir_path, school_name))
            return [item for item in items
                    if os.path.isdir(os.path.join(self.out_dir_path, school_name, item))]
        else:
            return []

    def load_all_school_names(self) -> List[str]:
        return [item for item in os.listdir(self.out_dir_path) if os.path.isdir(os.path.join(self.out_dir_path, item))]

    def delete_all_team_images_and_pdfs(self, school_name, team_name: str):
        """Caution: This method deletes all output images stored for a team."""
        team_img_names = self.load_team_output_file_names(school_name, team_name, endswith='jpeg')
        team_pdf_names = self.load_team_output_file_names(school_name, team_name, endswith='pdf')
        for file_name in team_img_names + team_pdf_names:
            os.remove(os.path.join(os.path.join(self.out_dir_path, school_name, team_name, file_name)))


def save_output_fig(out_fig, path=os.path.join(DATA_REPOSITORY_DIR_PATH, 'default_out_name.pdf')):
    """Stores the output figure of the GUI processing without padding such that
    the resulting size on paper equals the size of the drawing canvas."""
    out_fig.tight_layout(pad=0)
    out_fig.savefig(path, bbox_inches='tight', pad_inches=0)
    print(f'Saved output figure at {path}')
