import os
from PyQt5.QtGui import QImage
import matplotlib.pyplot as plt

from planvec.common import DATA_DIR_PATH
from planvec.utils import date_utils

from typing import List

date_utils.get_date_tag()
date_utils.get_date_time_tag()
IMG_NAME_FORMAT = '{idx}_{team}_{date_tag}{suffix}.{file_type}'


class DataManager:
    def __init__(self, date_tag=date_utils.get_date_tag()):
        self.date_tag = date_tag
        self.out_dir_path = os.path.join(DATA_DIR_PATH, date_tag)
        self.try_create_date_output_folder()

    def try_create_date_output_folder(self) -> None:
        if not os.path.exists(self.out_dir_path):
            os.makedirs(self.out_dir_path)

    def team_dir_exists(self, team_name: str) -> bool:
        assert os.path.exists(self.out_dir_path), 'Output folder for this \
                                                   date does not exist.'

        return os.path.exists(os.path.join(self.out_dir_path, team_name))

    def create_team_folder(self, team_name: str) -> None:
        if not self.team_dir_exists(team_name):
            os.makedirs(os.path.join(self.out_dir_path, team_name))

    def _create_save_img_path(self, team_name: str, file_type: str, suffix: str = '', idx: int = None) -> str:
        assert self.team_dir_exists(team_name), 'Cannot save. Team directory ' \
                                                'does not exist.'
        if idx is None:
            idx = self.get_next_team_img_idx(team_name)
        img_name = IMG_NAME_FORMAT.format(idx=idx,
                                          team=team_name,
                                          date_tag=date_utils.get_date_time_tag(),
                                          suffix=suffix,
                                          file_type=file_type)
        team_dir = os.path.join(self.out_dir_path, team_name)
        return os.path.join(team_dir, img_name)

    def save_qt_image(self, team_name: str, qt_img: QImage, suffix: str = '', idx: int = None) -> None:
        file_path = self._create_save_img_path(team_name, 'jpeg', suffix, idx)
        qt_img.save(file_path)

    def save_pdf(self, team_name: str, fig: plt.Figure, suffix: str = '', idx: int = None) -> None:
        file_path = self._create_save_img_path(team_name, 'pdf', suffix, idx)
        save_output_fig(fig, file_path)

    def load_team_img_names(self, team_name: str) -> List[str]:
        """Load all the img file names of a team."""
        if self.team_dir_exists(team_name):
            return os.listdir(os.path.join(self.out_dir_path, team_name))
        else:
            return []

    def get_next_team_img_idx(self, team_name: str) -> int:
        team_img_names = self.load_team_img_names(team_name)
        img_indices = sorted([int(name.split('_')[0]) for name in team_img_names])
        if len(img_indices) == 0:
            return 0
        return img_indices[-1] + 1

    def load_all_team_names(self) -> List[str]:
        items = os.listdir(self.out_dir_path)
        return [item for item in items
                if os.path.isdir(os.path.join(self.out_dir_path, item))]

    def delete_all_team_imgs(self, team_name: str):
        """Caution: This method deletes all output images stored for a team."""
        team_img_names = self.load_team_img_names(team_name)
        for img in team_img_names:
            os.remove(os.path.join(os.path.join(self.out_dir_path, team_name, img)))


def save_output_fig(out_fig, path=os.path.join(DATA_DIR_PATH, 'default_out_name.pdf')):
    """Stores the output figure of the GUI processing without padding such that
    the resulting size on paper equals the size of the drawing canvas."""
    out_fig.tight_layout(pad=0)
    out_fig.savefig(path, bbox_inches='tight', pad_inches=0)
    print(f'Saved output figure at {path}')
