from pathlib import Path


# ------------------------------------------------------------------
# Project Directories
# ------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

OUTPUT_DIR = PROJECT_ROOT / "output"

TEMPLATES_DIR = PROJECT_ROOT / "src" / "templates"