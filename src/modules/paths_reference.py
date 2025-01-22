# with pathlib create the path reference to the root of the project

from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent.parent

DATA_PATH = ROOT_PATH / "data"
NOTEBOOKS_PATH = ROOT_PATH / "notebooks"
SRC_PATH = ROOT_PATH / "src"