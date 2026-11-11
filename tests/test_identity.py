import configparser
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/brutall-welcome"))
from catalog import THEMES
from identity import color, contrast, palette, settings, read_settings, color_scheme, rgb


class IdentityTests(unittest.TestCase):
    def test_theme_defaults_and_custom_colors_have_readable_selection_and_focus(self):
        tones = {v["accent"] for t in THEMES for v in t["variants"]} | {"#000", "#fff", "#cf0", "#777", "#00ffff"}
        self.assertEqual(THEMES[2]["variants"][2]["accent"], "#9333ea")
        for accent in tones:
            for dark in (True, False):
                for tinted in (True, False):
                    p = palette(accent, dark, tinted)
                    self.assertGreaterEqual(contrast(p["accentText"], p["accent"]), 4.5)
                    for background in (p["paper"], p["surface"]):
                        self.assertGreaterEqual(contrast(p["ink"], background), 4.5)
                        self.assertGreaterEqual(contrast(p["focus"], background), 3)
                        self.assertGreaterEqual(contrast(p["link"], background), 4.5)
        self.assertNotEqual(palette("#9333ea", True)["paper"], palette("#1557ff", True)["paper"])
        self.assertEqual(palette("#9333ea", True, False)["paper"], palette("#1557ff", True, False)["paper"])

    def test_custom_color_validation_and_persisted_override(self):
        self.assertEqual(color("#Cf0"), "#ccff00")
        for invalid in ("red", "#12345", "#12345678", "#ff00zz", "#fff\n[WM]", None):
            with self.assertRaises(ValueError): color(invalid)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "interface.json"
            expected = settings("friends", "purple", "#09b", False, "dark")
            path.write_text(json.dumps(expected))
            self.assertEqual(read_settings(path), expected)
            path.unlink()
            path.with_name("welcome.json").write_text(json.dumps({"theme": "friends", "variant": "purple"}))
            self.assertEqual(read_settings(path)["variant"], "purple")

    def test_generated_scheme_changes_surfaces_focus_and_selection_keeps_semantic_colors(self):
        identity = settings("friends", "purple", mode="dark")
        p = palette("#9333ea", True)
        config = configparser.ConfigParser()
        config.read_string(color_scheme((ROOT / "plasma/colors/BruDark.colors").read_text(), identity).decode())
        native = lambda value: ",".join(map(str, rgb(value)))
        self.assertEqual(config["Colors:Selection"]["BackgroundNormal"], native(p["accent"]))
        self.assertEqual(config["Colors:Selection"]["ForegroundNormal"], native(p["accentText"]))
        self.assertEqual(config["Colors:Window"]["BackgroundNormal"], native(p["paper"]))
        self.assertEqual(config["WM"]["activeBackground"], native(p["paper"]))
        self.assertEqual(config["Colors:Window"]["DecorationFocus"], native(p["focus"]))
        self.assertEqual(config["Colors:Window"]["ForegroundPositive"], "30,155,87")
