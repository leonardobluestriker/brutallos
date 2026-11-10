import json
import os
from pathlib import Path
import unittest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QJSEngine
from test_top_panel import MOCK


class DockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QGuiApplication.instance() or QGuiApplication([])

    def setUp(self):
        self.js = QJSEngine()
        self.js.evaluate(MOCK + "\nknownWidgetTypes.push('org.kde.plasma.icontasks');")
        self.js.evaluate((Path(__file__).resolve().parents[1] / "plasma/layouts/top-panel.js").read_text())

    def value(self, source):
        result = self.js.evaluate("JSON.stringify(" + source + ")")
        self.assertFalse(result.isError(), result.toString())
        return json.loads(result.toString())

    def test_dock_geometry_grouping_and_rollback_leave_top_panel(self):
        self.js.evaluate("brutallTopPanel('apply', {screen:0,height:36,owner:'top'})")
        result = self.value("brutallTopPanel('apply', {screen:0,height:56,layout:'dock',owner:'dock',launchers:[]})")
        self.assertEqual(result["state"], "created")
        self.assertEqual(self.value("panels()[1].location"), "bottom")
        self.assertEqual(self.value("panels()[1].lengthMode"), "fit")
        self.assertEqual(self.value("panels()[1].widgets[0].config['General/groupedTaskVisualization']"), 3)
        self.assertEqual(self.value("brutallTopPanel('apply', {screen:0,height:56,layout:'dock',owner:'other'}).state"), "unchanged")
        self.value("brutallTopPanel('rollback', {layout:'dock',owner:'dock'})")
        self.assertEqual(self.value("panels().length"), 1)
        self.assertEqual(self.value("panels()[0].location"), "top")

    def test_existing_bottom_panel_blocks_without_removal(self):
        self.js.evaluate("new Panel();")
        self.assertFalse(self.value("brutallTopPanel('plan', {screen:0,layout:'dock'}).canApply"))
        error = self.js.evaluate("brutallTopPanel('apply', {screen:0,height:56,layout:'dock',owner:'dock'})")
        self.assertTrue(error.isError())
        self.assertEqual(self.value("panels().length"), 1)
