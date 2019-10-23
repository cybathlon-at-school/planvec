import os
from PyQt5.QtGui import QImage

from planvec.common import DATA_DIR_PATH
from planvec.utils import date_utils

from typing import List

DATE_TAG = date_utils.get_date_tag()
DATE_TIME_TAG = date_utils.get_date_time_tag()
IMG_NAME_FORMAT = '{idx}_{team}_{date_tag}.jpeg'


class DataManager():
    def __init__(self, date_tag=DATE_TAG):
        self.date_tag = date_tag
        self.out_dir_path = os.path.join(DATA_DIR_PATH, DATE_TAG)
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

    def save_image(self, team_name: str, qt_img: QImage) -> None:
        assert self.team_dir_exists(team_name), 'Cannot save. Team directory \
                                                 does not exist.'

        img_name = IMG_NAME_FORMAT.format(idx=0,
                                          team=team_name,
                                          date_tag=self.date_tag)
        team_dir = os.path.join(self.out_dir_path, team_name)
        qt_img.save(os.path.join(team_dir, img_name))

    def load_team_img_names(self, team_name: str) -> List[str]:
        """Load all the img file names of a team."""
        if self.team_dir_exists(team_name):
            return os.listdir(os.path.join(self.out_dir_path, team_name))
        else:
            return []

    def load_all_team_names(self) -> List[str]:
        return os.listdir(self.out_dir_path)
