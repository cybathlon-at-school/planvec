import os
from pathlib import Path

PROJECT_ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
DATA_REPOSITORY_DIR_PATH = os.path.join(PROJECT_ROOT_PATH, 'data')
DATA_DESKTOP_DIR_PATH = Path.home() / 'Desktop' / 'planvec'
UI_GENERATED_PATH = Path(PROJECT_ROOT_PATH) / 'planvec/gui/ui_generated'
