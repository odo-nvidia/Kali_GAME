"""Command-line startup and environment checks."""

import argparse
import os
import platform
import shlex
import shutil
import subprocess
import sys

from config import APP_DIR, PROGRESS_FILE
from game import Game
from lab_manager import LabManager


def runtime_check() -> int:
    architecture = platform.machine()
    print("KALI GAME - kontrola środowiska")
    print(f"Architektura procesu: {architecture}")
    if architecture not in {"aarch64", "arm64"}:
        print("Uwaga: projekt jest przeznaczony dla Kali ARM64; wykryto inną architekturę.")
    for tool in ("python3", "tmux", "docker"):
        print(f"{tool}: {shutil.which(tool) or 'brak'}")
    docker = shutil.which("docker")
    if docker:
        result = subprocess.run(
            [*LabManager.docker_prefix(), "info", "--format", "{{.Architecture}}"],
            text=True,
            capture_output=True,
            check=False,
        )
        value = result.stdout.strip() if result.returncode == 0 else "niedostępny (sprawdź uprawnienia/usługę)"
        print(f"Docker Engine architektura: {value}")
    print(f"Katalog gry: {APP_DIR}")
    print(f"Plik postępu: {PROGRESS_FILE}")
    return 0


def attach_tmux(test_mode: bool = False) -> None:
    if os.environ.get("TMUX"):
        return
    if not shutil.which("tmux"):
        raise RuntimeError("Brak tmux. Zainstaluj go zgodnie z README i uruchom grę ponownie.")
    session = f"kali-game-{os.getpid()}"
    command_args = [sys.executable, str(APP_DIR / "kali_game.py"), "--inside-tmux"]
    if test_mode:
        command_args.append("--test-mode")
    command = shlex.join(command_args)
    os.execvp("tmux", ["tmux", "new-session", "-s", session, command])


def main() -> int:
    parser = argparse.ArgumentParser(description="Lokalna gra edukacyjna Kali Linux")
    parser.add_argument("--check", action="store_true", help="sprawdź wymagane narzędzia")
    parser.add_argument("--inside-tmux", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--no-tmux", action="store_true", help="uruchom samo menu bez panelu labu")
    parser.add_argument("--test-mode", action="store_true", help="odblokuj poziomy bez zmiany postępu")
    args = parser.parse_args()

    if args.check:
        return runtime_check()
    if not sys.stdin.isatty():
        print("Gra wymaga interaktywnego terminala.", file=sys.stderr)
        return 2
    try:
        if not args.no_tmux:
            attach_tmux(test_mode=args.test_mode)
    except (OSError, RuntimeError) as exc:
        print(f"Nie można uruchomić gry: {exc}", file=sys.stderr)
        return 2

    if os.geteuid() == 0:
        print("Uwaga: najlepiej uruchomić grę jako zwykły użytkownik, nie root.")
    return Game(no_tmux=args.no_tmux, test_mode=args.test_mode).run()
