"""Caminhos do projeto (independentes do cwd)."""
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
ASSETS_IMAGES = ASSETS_DIR / "images"


def hamburger_png_path() -> Path:
    return ASSETS_IMAGES / "hamburger_menu.png"
