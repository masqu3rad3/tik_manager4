import sys
from pathlib import Path

_FROZEN = getattr(sys, 'frozen', False)
directory = Path(__file__).parent if not _FROZEN else Path(sys.executable).parents[2] / "defaults"
all = list(directory.glob("*.json"))
