import curses
import hashlib
import io
import json
import threading
import tempfile
import unittest
from contextlib import redirect_stdout
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen
from unittest.mock import patch

from command_guide import COMMAND_CARDS, command_cards
from content import LEVELS, MISSIONS, mission_by_id, missions_for_level
from game import Game
from lab.local_web import TrainingHandler
from mentor import build_user_message, redact_context
from progress import Progress, clean_answer


class ContentTests(unittest.TestCase):
    def test_curriculum_has_82_missions_across_thirteen_levels(self):
        self.assertEqual(len(LEVELS), 13)
        self.assertEqual(len(MISSIONS), 82)
        expected_counts = {
            0: 5, 1: 11, 2: 5, 3: 5, 4: 4, 5: 4, 6: 4, 7: 4,
            8: 8, 9: 8, 10: 8, 11: 8, 12: 8,
        }
        self.assertEqual(
            {level: len(missions_for_level(level)) for level in LEVELS},
            expected_counts,
        )

    def test_mission_ids_and_fixture_paths_are_unique_and_safe(self):
        ids = [mission.id for mission in MISSIONS]
        self.assertEqual(len(ids), len(set(ids)))
        for mission in MISSIONS:
            self.assertTrue(mission.files or mission.packet_capture)
            paths = {Path(name) for name in mission.files}
            for fixture_path, text in mission.files.items():
                path = Path(fixture_path)
                self.assertFalse(path.is_absolute())
                self.assertNotIn("..", path.parts)
                self.assertTrue(text)
                self.assertFalse(any(path in other.parents for other in paths if other != path))

    def test_search_course_teaches_names_sizes_and_content(self):
        lesson_ids = tuple(f"l1-m{number}" for number in range(6, 12))
        lessons = tuple(mission_by_id(mission_id) for mission_id in lesson_ids)
        self.assertTrue(all(lesson.level == 1 for lesson in lessons))
        self.assertEqual(tuple(lesson.id for lesson in missions_for_level(1)[-6:]), lesson_ids)
        self.assertEqual(len(mission_by_id("l1-m7").files["records/size-proof.bin"].encode()), 10)
        self.assertEqual(len(mission_by_id("l1-m7").files["records/near-miss.bin"].encode()), 11)
        self.assertEqual(set(mission_by_id("l1-m8").tools), {"find", "wc"})
        self.assertEqual(set(mission_by_id("l1-m9").tools), {"grep", "wc"})

    def test_command_cards_cover_find_and_grep_options(self):
        cards = {card.name: card for card in COMMAND_CARDS}
        self.assertEqual(len(cards), len(COMMAND_CARDS))
        self.assertTrue(
            {
                "pwd / cd", "mkdir / touch", "cp / mv / rm", "file / stat",
                "du / df", "cut", "awk", "sed", "chmod", "whoami / id",
                "ps / pgrep", "ip / ss", "curl", "sha256sum", "diff", "man / --help",
            }.issubset(cards)
        )
        find_options = dict(cards["find"].options)
        grep_options = dict(cards["grep"].options)
        self.assertIn("-size 20c", find_options)
        self.assertIn("-exec KOMENDA {} +", find_options)
        self.assertIn("-x", grep_options)
        self.assertIn("-r", grep_options)
        self.assertEqual(tuple(card.name for card in command_cards(("grep", "find"))), ("find", "grep"))
        self.assertEqual(tuple(card.name for card in command_cards(("file",))), ("file / stat",))
        self.assertEqual(tuple(card.name for card in command_cards(("head",))), ("head / tail",))

    def test_new_missions_list_tools_and_restrict_runtime_services(self):
        new_missions = [mission for mission in MISSIONS if mission.level >= 8]
        self.assertEqual(len(new_missions), 40)
        self.assertTrue(all(mission.tools for mission in new_missions))
        for mission in new_missions:
            self.assertLessEqual(set(mission.service_ports), {8080, 8081})
            if mission.service_ports:
                self.assertIn(mission.level, {9, 11})
            if mission.packet_capture:
                self.assertIn(mission.level, {10, 12})

    def test_fixture_hash_manifests_match_their_artifacts(self):
        cases = (
            ("l8-m2", "evidence/policy.txt", "evidence/SHA256SUMS"),
            ("l12-m2", "case/indicator.txt", "case/evidence.SHA256SUMS"),
        )
        for mission_id, artifact_path, manifest_path in cases:
            mission = mission_by_id(mission_id)
            digest = hashlib.sha256(mission.files[artifact_path].encode("utf-8")).hexdigest()
            self.assertTrue(mission.files[manifest_path].startswith(digest))

    def test_answers_are_normalized_without_changing_meaning(self):
        self.assertEqual(clean_answer("  DISABLED  "), "disabled")
        self.assertEqual(clean_answer("10.10.0.32"), "10.10.0.32")


class LocalDataTests(unittest.TestCase):
    def test_progress_persists_only_completion_and_hint_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "progress.json"
            progress = Progress(path)
            progress.completed.add("l0-m1")
            progress.hints["l0-m1"] = 2
            progress.save()

            stored = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(set(stored), {"completed", "hints"})
            self.assertNotIn("terminal", json.dumps(stored).lower())
            restored = Progress(path)
            self.assertEqual(restored.completed, {"l0-m1"})
            self.assertEqual(restored.hints["l0-m1"], 2)


class MissionMenuTests(unittest.TestCase):
    class FakeScreen:
        def __init__(self, keys, height=9, width=60):
            self.keys = iter(keys)
            self.height = height
            self.width = width
            self.lines = {}

        def keypad(self, enabled):
            pass

        def getmaxyx(self):
            return self.height, self.width

        def erase(self):
            self.lines = {}

        def addnstr(self, row, column, text, count, attribute=0):
            self.lines[row] = str(text)[:count]

        def refresh(self):
            pass

        def getch(self):
            return next(self.keys)

    def test_arrows_scroll_and_select_a_visible_mission(self):
        keys = [curses.KEY_DOWN] * 10 + [curses.KEY_UP, curses.KEY_ENTER]
        screen = self.FakeScreen(keys)
        with tempfile.TemporaryDirectory() as directory:
            game = Game.__new__(Game)
            game.progress = Progress(Path(directory) / "progress.json")
            game.test_mode = False
            with patch("game.curses.curs_set"):
                action, mission = game._mission_menu(screen)

        self.assertEqual(action, "mission")
        self.assertEqual(mission, MISSIONS[9])
        visible_lines = "\n".join(screen.lines.values())
        self.assertIn(mission.id, visible_lines)
        self.assertNotIn(MISSIONS[0].id, visible_lines)
        self.assertNotIn("\x1b", visible_lines)

    def test_test_mode_unlocks_without_completing_missions(self):
        with tempfile.TemporaryDirectory() as directory:
            game = Game.__new__(Game)
            game.test_mode = True
            game.progress = Progress(Path(directory) / "progress.json")

            self.assertTrue(game._level_unlocked(12))
            self.assertFalse(game.progress.completed)

    def test_command_guide_has_a_main_menu_shortcut(self):
        screen = self.FakeScreen([ord("c")])
        with tempfile.TemporaryDirectory() as directory:
            game = Game.__new__(Game)
            game.progress = Progress(Path(directory) / "progress.json")
            game.test_mode = False
            with patch("game.curses.curs_set"):
                action, mission = game._mission_menu(screen)
        self.assertEqual((action, mission), ("guide", None))

    def test_mission_command_guide_shows_contextual_card(self):
        output = io.StringIO()
        game = Game.__new__(Game)
        with patch("builtins.input", side_effect=["1", "", ""]), redirect_stdout(output):
            game.show_command_guide(("find",))
        self.assertIn("find . -type f -name '*.txt' -print", output.getvalue())
        self.assertIn("-size 20c", output.getvalue())

    def test_full_command_guide_paginates(self):
        output = io.StringIO()
        game = Game.__new__(Game)
        with patch("builtins.input", side_effect=["n", "1", "", ""]), redirect_stdout(output):
            game.show_command_guide()
        self.assertIn("Strona 2/3", output.getvalue())
        self.assertIn("pwd / cd", output.getvalue())
        self.assertIn("pwd    |    cd KATALOG", output.getvalue())


class LocalWebTests(unittest.TestCase):
    def test_training_server_serves_local_pages_with_review_headers(self):
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / "index.html"
            page.write_text("<title>Training Portal</title>\n", encoding="utf-8")
            handler = partial(TrainingHandler, directory=directory)
            server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                with urlopen(f"http://127.0.0.1:{server.server_port}/") as response:
                    body = response.read().decode("utf-8")
                    self.assertEqual(response.headers["X-Training-Mode"], "offline")
                    self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
                    self.assertIn("Training Portal", body)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)


class MentorPrivacyTests(unittest.TestCase):
    def test_common_secrets_are_redacted(self):
        sample = "Authorization: Bearer abc123\napi_key=sk-test\npassword: hello\n"
        result = redact_context(sample)
        self.assertNotIn("abc123", result)
        self.assertNotIn("sk-test", result)
        self.assertNotIn("hello", result)
        self.assertEqual(result.count("[REDACTED]"), 3)

    def test_preview_contains_exact_question_and_redacted_terminal(self):
        mission = MISSIONS[0]
        preview = build_user_message(mission, "Why is networking disabled?", "token=secret-value")
        self.assertIn("Why is networking disabled?", preview)
        self.assertIn(mission.task, preview)
        self.assertIn("[REDACTED]", preview)
        self.assertNotIn("secret-value", preview)


if __name__ == "__main__":
    unittest.main()
