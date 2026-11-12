"""Interactive menus, mission flow, and mentor integration."""

import curses
import getpass
import os
import subprocess
import sys

from command_guide import command_cards
from config import PROGRESS_FILE
from content import LEVELS, MISSIONS, Mission, missions_for_level
from lab_manager import LabManager
from mentor import MODEL, ask_mentor, build_user_message
from progress import Progress, clean_answer


class Game:
    def __init__(self, no_tmux: bool = False, test_mode: bool = False):
        self.progress = Progress()
        self.labs = LabManager(no_tmux=no_tmux)
        self.no_tmux = no_tmux
        self.test_mode = test_mode
        self.started: set[str] = set()
        self.api_key: str | None = None

    @staticmethod
    def _clear() -> None:
        if sys.stdout.isatty():
            print("\033[2J\033[H", end="")

    def _level_unlocked(self, level: int) -> bool:
        if self.test_mode:
            return True
        return all(
            mission.id in self.progress.completed
            for previous in range(level)
            for mission in missions_for_level(previous)
        )

    def _print_header(self) -> None:
        print("KALI GAME v0.1 | Kampania lokalna | ARM64")
        print("Polecenia wykonuj wyłącznie w panelu labu.")
        print("=" * 66)

    @staticmethod
    def _menu_window(selected: int, total: int, visible: int) -> tuple[int, int]:
        visible = min(max(visible, 1), total)
        start = max(0, min(selected - visible // 2, total - visible))
        return start, start + visible

    def _mission_menu(self, screen) -> tuple[str, Mission | None]:
        screen.keypad(True)
        try:
            curses.curs_set(0)
        except curses.error:
            pass

        selected = 0
        while True:
            height, width = screen.getmaxyx()
            draw_width = max(1, width - 1)
            screen.erase()
            screen.addnstr(0, 0, "KALI GAME v0.1 | Kampania lokalna | ARM64", draw_width)
            screen.addnstr(1, 0, "Wybierz misję: ↑/↓ lub j/k, Enter otwiera", draw_width)
            notice = "TRYB TESTOWY: poziomy odblokowane bez zmiany zapisu." if self.test_mode else ""
            screen.addnstr(2, 0, notice, draw_width)

            list_top = 3
            visible = max(1, height - list_top - 1)
            start, end = self._menu_window(selected, len(MISSIONS), visible)
            for row, index in enumerate(range(start, end), start=list_top):
                mission = MISSIONS[index]
                marker = "[x]" if mission.id in self.progress.completed else "[ ]"
                locked = " [ZABLOKOWANA]" if not self._level_unlocked(mission.level) else ""
                prefix = ">" if index == selected else " "
                line = f"{prefix} {marker} L{mission.level} {mission.id}  {mission.title}{locked}"
                attribute = curses.A_REVERSE if index == selected else curses.A_NORMAL
                screen.addnstr(row, 0, line, draw_width, attribute)

            footer = (
                f"Misje {start + 1}-{end}/{len(MISSIONS)} | Enter: wybierz | "
                "c: komendy | p: postęp | i: wpisz ID | q: wyjście"
            )
            screen.addnstr(height - 1, 0, footer, draw_width)
            screen.refresh()

            key = screen.getch()
            if key in (curses.KEY_UP, ord("k")):
                selected = max(0, selected - 1)
            elif key in (curses.KEY_DOWN, ord("j")):
                selected = min(len(MISSIONS) - 1, selected + 1)
            elif key == curses.KEY_PPAGE:
                selected = max(0, selected - visible)
            elif key == curses.KEY_NPAGE:
                selected = min(len(MISSIONS) - 1, selected + visible)
            elif key == curses.KEY_HOME:
                selected = 0
            elif key == curses.KEY_END:
                selected = len(MISSIONS) - 1
            elif key in (10, 13, curses.KEY_ENTER):
                return "mission", MISSIONS[selected]
            elif key in (ord("p"), ord("P")):
                return "progress", None
            elif key in (ord("c"), ord("C")):
                return "guide", None
            elif key in (ord("i"), ord("I")):
                return "id", None
            elif key in (ord("q"), ord("Q")):
                return "quit", None

    def show_progress(self) -> None:
        total = len(MISSIONS)
        done = len(self.progress.completed)
        print(f"\nPostęp kampanii: {done}/{total} misji.")
        print(f"Zapis lokalny: {PROGRESS_FILE}")
        input("Enter, aby wrócić...")

    def mission_screen(self, mission: Mission) -> None:
        if not self._level_unlocked(mission.level):
            print("Najpierw ukończ poprzednie poziomy.")
            input("Enter, aby wrócić...")
            return

        while True:
            self._clear()
            self._print_header()
            print(f"POZIOM {mission.level}: {LEVELS[mission.level]}")
            print(f"MISJA {mission.id}: {mission.title}\n")
            if mission.tools:
                print(f"NARZĘDZIA: {', '.join(mission.tools)}\n")
            print(f"CEL: {mission.goal}\n")
            print(mission.lesson)
            print(f"\nZADANIE: {mission.task}")
            done = "ZALICZONA" if mission.id in self.progress.completed else "W TOKU"
            print(f"\nStatus: {done}")
            print("\n1 - Otwórz lab w drugim panelu")
            print("2 - Pokaż następną lokalną wskazówkę")
            print("3 - Zapytaj mentora (wysyłka dopiero po podglądzie i zgodzie)")
            print("4 - Sprawdź odpowiedź")
            print("5 - Otwórz karty komend")
            print("0 - Wróć do menu")
            choice = input("\nWybór: ").strip().lower()
            if choice == "1":
                self.start_lab(mission)
            elif choice == "2":
                self.show_hint(mission)
            elif choice == "3":
                self.mentor(mission)
            elif choice == "4":
                self.check_answer(mission)
            elif choice == "5":
                self.show_command_guide(mission.tools)
            elif choice == "0":
                self.labs.close_mission(mission.id)
                return

    def show_command_guide(self, names: tuple[str, ...] | None = None) -> None:
        cards = command_cards(names)
        if not cards:
            cards = command_cards()
        page_size = 8
        page = 0
        while True:
            start = page * page_size
            visible_cards = cards[start : start + page_size]
            page_count = (len(cards) + page_size - 1) // page_size
            self._clear()
            print("KARTY KOMEND | składnia, opcje i przykłady")
            print("=" * 66)
            if page_count > 1:
                print(f"Strona {page + 1}/{page_count} | n: następna | p: poprzednia\n")
            for index, card in enumerate(visible_cards, 1):
                print(f"{index} - {card.name}: {card.purpose}")
            choice = input("\nNumer karty, n/p: zmień stronę, Enter: wróć: ").strip().lower()
            if not choice:
                return
            if choice in {"n", "next"} and page + 1 < page_count:
                page += 1
                continue
            if choice in {"p", "prev"} and page > 0:
                page -= 1
                continue
            try:
                index = int(choice) - 1
                if index < 0 or index >= len(visible_cards):
                    raise ValueError
                card = visible_cards[index]
            except (ValueError, IndexError):
                print("Nie ma takiej karty.")
                input("Enter, aby kontynuować...")
                continue

            self._clear()
            print(f"{card.name}: {card.purpose}\n")
            print(f"SKŁADNIA: {card.syntax}\n")
            print("OPCJE:")
            for option, explanation in card.options:
                print(f"  {option}: {explanation}")
            print("\nPRZYKŁADY:")
            for example in card.examples:
                print(f"  {example}")
            if card.notes:
                print("\nWARTO WIEDZIEĆ:")
                for note in card.notes:
                    print(f"  {note}")
            input("\nEnter, aby wrócić do kart...")

    def start_lab(self, mission: Mission) -> None:
        try:
            self.labs.open_lab(mission)
            self.started.add(mission.id)
        except (OSError, subprocess.CalledProcessError, RuntimeError) as exc:
            print(f"\nNie udało się uruchomić labu: {exc}")
            print("Sprawdź Docker, uprawnienia i README. Zapis postępu pozostał bez zmian.")
            input("Enter, aby wrócić...")

    def show_hint(self, mission: Mission) -> None:
        index = self.progress.hints.get(mission.id, 0)
        if index >= len(mission.hints):
            print("Wykorzystano już wszystkie lokalne wskazówki. Możesz zapytać mentora.")
        else:
            print(f"\nWskazówka {index + 1}/{len(mission.hints)}: {mission.hints[index]}")
            self.progress.hints[mission.id] = index + 1
            self.progress.save()
        input("Enter, aby wrócić...")

    def check_answer(self, mission: Mission) -> None:
        if mission.id not in self.started:
            print("Najpierw otwórz lab i spróbuj samodzielnie wykonać zadanie.")
            input("Enter, aby wrócić...")
            return
        answer = input(f"\n{mission.question} ")
        if clean_answer(answer) == clean_answer(mission.answer):
            first_pass = mission.id not in self.progress.completed
            self.progress.completed.add(mission.id)
            self.progress.save()
            print("\nDobrze. Wynik zapisano lokalnie.")
            if first_pass and all(
                item.id in self.progress.completed for item in missions_for_level(mission.level)
            ):
                print(f"Odblokowano następny poziom: {LEVELS.get(mission.level + 1, 'kampania ukończona')}.")
            print("Wniosek: zachowuj dowody, sprawdzaj zakres i nie wyciągaj wniosków poza dane.")
        else:
            print("\nJeszcze nie. Wróć do plików, sprawdź źródło danych i spróbuj ponownie.")
        input("Enter, aby wrócić...")

    def mentor(self, mission: Mission) -> None:
        question = input("\nCo chcesz lepiej zrozumieć? ").strip()
        snapshot = self.labs.capture_lab(mission.id)
        payload = build_user_message(mission, question, snapshot)
        print("\nDokładny podgląd treści wysyłanej do OpenRouter:")
        print("-" * 66)
        print(payload)
        print("-" * 66)
        print("\nTo zapytanie opuści Kali i trafi przez OpenRouter do usługi modelu.")
        if input("Wysłać teraz? [t/N]: ").strip().casefold() not in {"t", "tak", "y", "yes"}:
            print("Nie wysłano żadnych danych.")
            input("Enter, aby wrócić...")
            return

        if not self.api_key:
            self.api_key = getpass.getpass("Klucz OpenRouter (nie będzie wyświetlony ani zapisany): ").strip()
        if not self.api_key:
            print("Brak klucza. Misja działa dalej bez mentora.")
            input("Enter, aby wrócić...")
            return

        try:
            model = os.environ.get("OPENROUTER_MODEL", MODEL)
            answer = ask_mentor(self.api_key, mission, question, snapshot, model=model)
            print(f"\nMENTOR ({model}):\n{answer}")
        except RuntimeError as exc:
            print(f"\nMentor jest chwilowo niedostępny: {exc}")
            print(f"Lokalna wskazówka: {mission.hints[0]}")
        input("\nEnter, aby wrócić...")

    def run(self) -> int:
        try:
            while True:
                action, mission = curses.wrapper(self._mission_menu)
                if action == "quit":
                    return 0
                if action == "progress":
                    self.show_progress()
                    continue
                if action == "guide":
                    self.show_command_guide()
                    continue
                if action == "id":
                    mission_id = input("Wpisz ID misji (np. l0-m1): ").strip().lower()
                    mission = next((item for item in MISSIONS if item.id == mission_id), None)
                    if mission is None:
                        print("Nieznane ID misji.")
                        input("Enter, aby kontynuować...")
                        continue
                if mission is None:
                    continue
                self.mission_screen(mission)
        except (KeyboardInterrupt, EOFError):
            print("\nZamykanie gry...")
            return 130
        finally:
            self.labs.close_all()
