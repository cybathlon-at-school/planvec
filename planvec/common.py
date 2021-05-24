import os
from pathlib import Path

PROJECT_ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
DATA_DIR_PATH = os.path.join(PROJECT_ROOT_PATH, 'data')
UI_GENERATED_PATH = Path(PROJECT_ROOT_PATH) / 'planvec/gui/ui_generated'
