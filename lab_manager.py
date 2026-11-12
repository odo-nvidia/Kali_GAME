"""Manage isolated training containers and their tmux panes."""

import os
import shlex
import shutil
import subprocess
from pathlib import Path

from config import APP_DIR, CONTAINER_PREFIX, IMAGE_NAME, OWNER_LABEL
from content import Mission


class LabManager:
    """Run short-lived, network-isolated containers for synthetic fixtures."""

    def __init__(self, app_dir: Path = APP_DIR, no_tmux: bool = False):
        self.app_dir = app_dir
        self.no_tmux = no_tmux
        self.active: dict[str, tuple[str, str | None]] = {}

    @staticmethod
    def docker_prefix() -> list[str]:
        if os.environ.get("KALI_GAME_DOCKER_SUDO") == "1" and os.geteuid() != 0:
            return ["sudo", "docker"]
        return ["docker"]

    def _docker(self, *args: str, check: bool = True, capture: bool = False):
        return subprocess.run(
            [*self.docker_prefix(), *args],
            cwd=self.app_dir,
            check=check,
            text=True,
            capture_output=capture,
        )

    def _ensure_image(self) -> None:
        found = self._docker("image", "inspect", IMAGE_NAME, check=False, capture=True)
        if found.returncode == 0:
            return
        print("Pierwszy lab wymaga zbudowania lokalnego obrazu. To może pobrać bazowy obraz Debiana.")
        self._docker("build", "-f", "lab/Dockerfile", "-t", IMAGE_NAME, ".")

    def open_lab(self, mission: Mission) -> None:
        if self.no_tmux or not os.environ.get("TMUX"):
            raise RuntimeError("Lab wymaga sesji tmux. Uruchom grę normalnie, bez --no-tmux.")
        existing = self.active.get(mission.id)
        if existing:
            if self._pane_exists(existing[1]):
                subprocess.run(["tmux", "select-pane", "-t", existing[1]], check=False)
                print("Przełączono do otwartego panelu labu. Wróć skrótem tmux, aby kontynuować menu.")
                return
            self._docker("rm", "-f", existing[0], check=False, capture=True)
            self.active.pop(mission.id, None)

        self._ensure_image()
        container_name = f"{CONTAINER_PREFIX}-{mission.id}-{os.getpid()}"
        self._docker(
            "run", "--detach", "--name", container_name,
            "--label", f"com.kali-game.owner={OWNER_LABEL}",
            "--label", f"com.kali-game.mission={mission.id}",
            "--network", "none",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "--pids-limit", "128",
            "--memory", "512m",
            "--cpus", "1",
            "--read-only",
            "--tmpfs", "/tmp:rw,nosuid,nodev,size=32m",
            "--tmpfs", "/home/learner/workspace:rw,nosuid,nodev,uid=1000,gid=1000,mode=0750,size=64m",
            "--tmpfs", "/home/learner/.config:rw,nosuid,nodev,uid=1000,gid=1000,mode=0700,size=16m",
            "--tmpfs", "/home/learner/.cache:rw,nosuid,nodev,uid=1000,gid=1000,mode=0700,size=16m",
            "--env", f"KALI_GAME_MISSION={mission.id}",
            IMAGE_NAME,
            mission.id,
        )

        columns = shutil.get_terminal_size((100, 30)).columns
        direction = "-h" if columns >= 110 else "-v"
        shell = shlex.join(
            [
                *self.docker_prefix(), "exec", "-it", "-w", "/home/learner/workspace",
                "-e", "HISTFILE=/dev/null", container_name,
                "/bin/bash", "--noprofile", "--norc", "-i",
            ]
        )
        split = subprocess.run(
            ["tmux", "split-window", "-d", "-P", "-F", "#{pane_id}", "-l", "50%", direction, shell],
            check=False,
            text=True,
            capture_output=True,
        )
        if split.returncode != 0:
            self._docker("rm", "-f", container_name, check=False, capture=True)
            raise RuntimeError(split.stderr.strip() or "Nie udało się utworzyć panelu tmux.")
        pane_id = split.stdout.strip()
        self.active[mission.id] = (container_name, pane_id)
        subprocess.run(["tmux", "select-pane", "-t", pane_id], check=False)
        print("Lab działa w drugim panelu. Wróć do menu skrótem tmux: Ctrl-b, potem strzałka.")

    def _pane_exists(self, pane_id: str | None) -> bool:
        if not pane_id:
            return False
        result = subprocess.run(
            ["tmux", "display-message", "-p", "-t", pane_id, "#{pane_id}"],
            check=False,
            text=True,
            capture_output=True,
        )
        return result.returncode == 0

    def capture_lab(self, mission_id: str) -> str:
        active = self.active.get(mission_id)
        if not active or not self._pane_exists(active[1]):
            return ""
        result = subprocess.run(
            ["tmux", "capture-pane", "-p", "-S", "-24", "-t", active[1]],
            check=False,
            text=True,
            capture_output=True,
        )
        return result.stdout[-6000:] if result.returncode == 0 else ""

    def close_mission(self, mission_id: str) -> None:
        active = self.active.pop(mission_id, None)
        if not active:
            return
        container_name, pane_id = active
        if self._pane_exists(pane_id):
            subprocess.run(["tmux", "kill-pane", "-t", pane_id], check=False, capture_output=True)
        self._docker("rm", "-f", container_name, check=False, capture=True)

    def close_all(self) -> None:
        for mission_id in tuple(self.active):
            self.close_mission(mission_id)
