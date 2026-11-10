from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps/brutall-welcome"))
from catalog import defaults
from preferences import Preferences


class PreferencesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Preferences(Path(self.temp.name) / "brutallos")

    def test_read_is_side_effect_free_and_first_save_can_be_removed(self):
        self.assertEqual(self.store.read(), defaults())
        self.assertFalse(self.store.directory.exists())
        self.store.save(defaults())
        self.assertEqual(self.store.read(), defaults())
        self.store.restore()
        self.assertFalse(self.store.path.exists())

    def test_restores_exact_original_bytes_even_if_invalid(self):
        self.store.directory.mkdir()
        original = b'not valid json\n'
        self.store.path.write_bytes(original)
        self.store.save(defaults())
        self.store.restore()
        self.assertEqual(self.store.path.read_bytes(), original)

    def test_external_change_blocks_restore(self):
        self.store.save(defaults())
        external = b'{"external": true}\n'
        self.store.path.write_bytes(external)
        with self.assertRaisesRegex(ValueError, "alteradas"):
            self.store.restore()
        self.assertEqual(self.store.path.read_bytes(), external)
        self.assertTrue(self.store.backup.exists())

    def test_second_save_can_be_reverted(self):
        self.store.save(defaults())
        original = self.store.path.read_bytes()
        updated = dict(defaults(), theme="friends", variant="purple", completed=True)
        self.store.save(updated)
        self.assertEqual(self.store.read(), updated)
        self.store.restore()
        self.assertEqual(self.store.path.read_bytes(), original)

    def test_invalid_selection_never_writes(self):
        with self.assertRaises(ValueError):
            self.store.save(dict(defaults(), theme="../../etc", variant="x"))
        self.assertFalse(self.store.directory.exists())

    def test_non_object_json_is_rejected(self):
        self.store.directory.mkdir()
        self.store.path.write_text("[]")
        with self.assertRaises(ValueError):
            self.store.read()


if __name__ == "__main__":
    unittest.main()
