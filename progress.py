"""Local progress persistence for the campaign."""

import json
import os
import tempfile
from pathlib import Path

from config import PROGRESS_FILE
from content import MISSIONS


def clean_answer(value: str) -> str:
    return " ".join(value.strip().casefold().split())


class Progress:
    """Persist only completion and hint counts; never store shell output."""

    def __init__(self, path: Path = PROGRESS_FILE):
        self.path = path
        self.completed: set[str] = set()
        self.hints: dict[str, int] = {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            valid_ids = {mission.id for mission in MISSIONS}
            self.completed = set(data.get("completed", [])) & valid_ids
            self.hints = {
                key: max(0, int(value))
                for key, value in data.get("hints", {}).items()
                if key in valid_ids
            }
        except FileNotFoundError:
            pass
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            print("Uwaga: nie udało się odczytać zapisu; rozpoczęto nowy lokalny stan.")

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(
            {"completed": sorted(self.completed), "hints": self.hints},
            ensure_ascii=False,
            indent=2,
        )
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=self.path.parent, delete=False
        ) as temporary:
            temporary.write(payload)
            temp_path = Path(temporary.name)
        os.chmod(temp_path, 0o600)
        os.replace(temp_path, self.path)
