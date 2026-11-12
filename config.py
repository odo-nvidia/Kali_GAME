"""Shared paths and versioned runtime identifiers."""

from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
IMAGE_NAME = "kali-game-lab:0.1"
CONTAINER_PREFIX = "kgv04"
OWNER_LABEL = "Kali_game_v04"
DATA_DIR = Path.home() / ".local" / "share" / "Kali_GAME"
PROGRESS_FILE = DATA_DIR / "progress.json"
