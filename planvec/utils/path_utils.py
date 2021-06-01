import sys
from pathlib import Path

from main import PROJECT_ROOT_PATH


def resource_path(relative_path: Path) -> Path:
    """ Get the absolute path to the resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except Exception as e:
        base_path = PROJECT_ROOT_PATH
    return base_path / relative_path
