"""Test table row synchronization, scene hints and binary searches without a game install."""
import os
import sys
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from add_out_of_table_lines import DE_SLOT, FR_SLOT, row, sync_rows  # noqa: E402
from apply_scene_hints import replace_in_bytes  # noqa: E402
from find_missing_keys import scan_binaries  # noqa: E402


class RowTests(unittest.TestCase):
    def test_key_comes_first(self):
        self.assertEqual(row("some_key", "Bonjour").split("|")[0], "some_key")

    def test_english_cell_stays_empty(self):
        # The project never invents English: nobody translating into a third language should read
        # our transcription as the official line.
        self.assertEqual(row("some_key", "Bonjour").split("|")[1], "")

    def test_french_goes_in_both_display_slots(self):
        fields = row("some_key", "Bonjour").split("|")
        self.assertEqual(fields[FR_SLOT], "Bonjour")
        self.assertEqual(fields[DE_SLOT], "Bonjour")

    def test_row_ends_with_the_end_marker(self):
        self.assertEqual(row("some_key", "Bonjour").split("|")[-1], "end")


class SyncRowsTests(unittest.TestCase):
    def setUp(self):
        self.lines = ["header", "a|1", "b|2", "", ""]

    def test_existing_rows_keep_their_index(self):
        # A game that resolves rows positionally must not be disturbed by the addition.
        out, added, updated = sync_rows(self.lines, {"c": "3"})
        self.assertEqual(out[:3], ["header", "a|1", "b|2"])

    def test_new_rows_land_before_the_trailing_empty_lines(self):
        out, added, updated = sync_rows(self.lines, {"c": "3"})
        self.assertEqual(out[3], row("c", "3"))
        self.assertEqual(out[-2:], ["", ""])

    def test_no_trailing_empty_line_appends_at_the_end(self):
        out, added, updated = sync_rows(["header", "a|1"], {"c": "3"})
        self.assertEqual(out, ["header", "a|1", row("c", "3")])

    def test_nothing_to_add_leaves_the_lines_alone(self):
        self.assertEqual(sync_rows(self.lines, {}), (self.lines, [], []))

    def test_updates_existing_translation_without_moving_the_row(self):
        lines = ["header", row("a", "Old"), "", ""]
        out, added, updated = sync_rows(lines, {"a": "New", "b": "Added"})
        self.assertEqual(out, ["header", row("a", "New"), row("b", "Added"), "", ""])
        self.assertEqual(added, [("b", "Added")])
        self.assertEqual(updated, [("a", "Old", "New")])

    def test_second_run_is_unchanged(self):
        lines = ["header", row("a", "New")]
        self.assertEqual(sync_rows(lines, {"a": "New"}), (lines, [], []))

    def test_updates_duplicate_rows_in_place(self):
        lines = ["header", row("a", "Old"), row("a", "Other")]
        out, added, updated = sync_rows(lines, {"a": "New"})
        self.assertEqual(out, ["header", row("a", "New"), row("a", "New")])
        self.assertEqual(added, [])
        self.assertEqual(len(updated), 2)


class BinaryScanTests(unittest.TestCase):
    def test_custom_directory_is_used_instead_of_default(self):
        with tempfile.TemporaryDirectory() as custom, tempfile.TemporaryDirectory() as default:
            Path(custom, "custom.assets").write_bytes(b"CUSTOM LABEL")
            Path(default, "default.assets").write_bytes(b"DEFAULT LABEL")
            with patch("find_missing_keys.DATA", default):
                found, count = scan_binaries(["CUSTOM LABEL", "DEFAULT LABEL"], data_dir=custom)
            self.assertEqual(count, 1)
            self.assertIn("CUSTOM LABEL", found)
            self.assertNotIn("DEFAULT LABEL", found)


class ReplaceInBytesTests(unittest.TestCase):
    # The pair must be the same BYTE length: that is the rule the tool enforces, and the reason
    # nothing else in the file moves. Real data pads the French with trailing spaces to get there.
    EN = "Open the door!"
    FR = "Ouvre la porte"

    @staticmethod
    def framed(text):
        """How the game stores a string: a 4-byte little-endian length, then the UTF-8 text."""
        return len(text.encode("utf-8")).to_bytes(4, "little") + text.encode("utf-8")

    def setUp(self):
        self.assertEqual(len(self.EN.encode("utf-8")), len(self.FR.encode("utf-8")),
                         "the fixture itself must obey the equal-length rule")

    def test_english_is_replaced_by_its_french_twin(self):
        raw = b"prefix" + self.framed(self.EN) + b"suffix"
        out, reps = replace_in_bytes(raw, {"door": {"en": self.EN, "fr": self.FR}})
        self.assertNotIn(self.EN.encode("utf-8"), out)
        self.assertIn(self.FR.encode("utf-8"), out)
        self.assertEqual(reps, [("door", 1)])

    def test_the_file_keeps_its_total_length(self):
        # The whole method rests on this: same byte length means no offset anywhere moves.
        raw = b"prefix" + self.framed(self.EN) + b"suffix"
        out, _ = replace_in_bytes(raw, {"door": {"en": self.EN, "fr": self.FR}})
        self.assertEqual(len(out), len(raw))

    def test_the_length_prefix_is_the_new_one(self):
        raw = self.framed(self.EN)
        out, _ = replace_in_bytes(raw, {"door": {"en": self.EN, "fr": self.FR}})
        self.assertEqual(int.from_bytes(out[:4], "little"), len(self.FR.encode("utf-8")))

    def test_absent_english_is_left_alone_and_reported(self):
        raw = b"nothing to see"
        out, reps = replace_in_bytes(raw, {"door": {"en": self.EN, "fr": self.FR}})
        self.assertEqual(out, raw)
        self.assertEqual(reps, [])


if __name__ == "__main__":
    unittest.main()
