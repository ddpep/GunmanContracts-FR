import importlib
import sys
import types
import unittest

try:
    importlib.import_module("UnityPy")
except ModuleNotFoundError as error:
    if error.name != "UnityPy":
        raise
    sys.modules["UnityPy"] = types.ModuleType("UnityPy")

from apply_text import parse_args, translate_line, translate_lines


class TranslateLineTests(unittest.TestCase):
    def test_writes_french_without_touching_german(self):
        line = "mission|English text|Old German||Spanish|Polish|Chinese|Japanese|Russian"
        updated, changed = translate_line(line, {"mission": "Texte français"}, False)
        self.assertEqual(updated, "mission|English text|Old German|Texte français|Spanish|Polish|Chinese|Japanese|Russian")
        self.assertTrue(changed)

    def test_replaces_existing_french_on_second_run(self):
        line = "mission|English text|Existing German|Old French|Spanish"
        updated, changed = translate_line(line, {"mission": "New French"}, False)
        self.assertEqual(updated, "mission|English text|Existing German|New French|Spanish")
        self.assertTrue(changed)

    def test_overwrites_german_only_when_requested(self):
        line = "mission|English text|Existing German|Old French|Spanish"
        updated, changed = translate_line(line, {"mission": "New French"}, True)
        self.assertEqual(updated, "mission|English text|New French|New French|Spanish")
        self.assertTrue(changed)

    def test_second_run_with_same_translation_is_unchanged(self):
        line = "mission|English|German|French|Spanish"
        self.assertEqual(translate_line(line, {"mission": "French"}, False), (line, False))

    def test_unknown_and_short_rows_remain_unchanged(self):
        french = {"mission": "French"}
        for line in ("other|English|German|French", "mission|English|German"):
            with self.subTest(line=line):
                self.assertEqual(translate_line(line, french, True), (line, False))


class TranslateLinesTests(unittest.TestCase):
    def test_default_updates_french_without_touching_german(self):
        rows = ["key|EN|DE|FR", "a|A|German A|Old A", "b|B|German B|"]
        updated, changed, overwrite_de = translate_lines(rows, {"a": "New A", "b": "New B"})
        self.assertEqual(updated, ["key|EN|DE|FR", "a|A|German A|New A", "b|B|German B|New B"])
        self.assertEqual(changed, 2)
        self.assertFalse(overwrite_de)

    def test_explicit_de_overwrite_on_already_patched_asset_and_duplicate_keys(self):
        rows = ["key|EN|DE|FR", "a|First|Previous DE|Previous FR", "a|Alternate|German DE|Other FR"]
        updated, changed, overwrite_de = translate_lines(rows, {"a": "New FR"}, True)
        self.assertEqual(updated, ["key|EN|DE|FR", "a|First|New FR|New FR", "a|Alternate|New FR|New FR"])
        self.assertEqual(changed, 2)
        self.assertTrue(overwrite_de)

    def test_second_run_has_zero_changes(self):
        rows = ["key|EN|DE|FR", "a|A|German|French"]
        self.assertEqual(translate_lines(rows, {"a": "French"}), (rows, 0, False))


class CommandLineTests(unittest.TestCase):
    def test_default_preserves_de(self):
        args = parse_args([])
        self.assertFalse(args.overwrite_de)
        self.assertIn("GunmanContracts_Data", args.data)

    def test_explicit_flag_and_custom_path(self):
        args = parse_args(["--overwrite-de", "C:/Games/GunmanContracts_Data"])
        self.assertTrue(args.overwrite_de)
        self.assertEqual(args.data, "C:/Games/GunmanContracts_Data")


if __name__ == "__main__":
    unittest.main()
