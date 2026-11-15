"""Location of the bundled picture files."""
import sys
from pathlib import Path

ASSETS = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / "assets"
