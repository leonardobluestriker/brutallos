"""Public Plasma scripting behavior in Qt's JS engine + backup orchestration.

The mocked Plasma objects are not an integration test of a live Plasma session.
"""
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QJSEngine

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("top_panel_runner", str(ROOT / "scripts/brutall-top-panel"))
spec = importlib.util.spec_from_loader(loader.name, loader)
runner = importlib.util.module_from_spec(spec)
loader.exec_module(runner)

MOCK = """
var locked = false;
var screenCount = 2;
var knownWidgetTypes = ["org.kde.plasma.kickoff", "org.kde.plasma.appmenu",
 "org.kde.plasma.panelspacer", "org.kde.plasma.systemtray", "org.kde.plasma.digitalclock",
 "org.kde.plasma.networkmanagement", "org.kde.plasma.volume", "org.kde.plasma.battery"];
var instances = [];
var failPlugin = "";
function configObject() {
    return {currentConfigGroup: [], config: {},
        readConfig: function(key, fallback) {
            var name = this.currentConfigGroup.join("/") + "/" + key;
            return name in this.config ? this.config[name] : fallback;
        },
        writeConfig: function(key, value) {
            this.config[this.currentConfigGroup.join("/") + "/" + key] = value;
        }};
}
function Panel() {
    var self = configObject();
    self.id = instances.length + 10;
    self.screen = 0;
    self.location = "bottom";
    self.removed = false;
    self.widgets = [];
    self.addWidget = function(plugin) {
        if (plugin === failPlugin) throw new Error("widget failed");
        var widget = configObject();
        widget.plugin = plugin;
        this.widgets.push(widget);
        return widget;
    };
    self.remove = function() {this.removed = true;};
    instances.push(self);
    return self;
}
function panels() {return instances.filter(function(p) {return !p.removed;});}
"""


class LayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QGuiApplication.instance() or QGuiApplication([])

    def setUp(self):
        self.js = QJSEngine()
        self.assertFalse(self.js.evaluate(MOCK).isError())
        self.assertFalse(self.js.evaluate(runner.SCRIPT.read_text()).isError())

    def value(self, code):
        result = self.js.evaluate("JSON.stringify(" + code + ")")
        self.assertFalse(result.isError(), result.toString())
        return json.loads(result.toString())

    def call(self, action, **options):
        return self.value("brutallTopPanel(" + json.dumps(action) + "," + json.dumps(dict(screen=0, height=36, owner="test-owner", **options)) + ")")

    def test_plan_does_not_change_existing_panels(self):
        self.js.evaluate("new Panel();")
        self.assertTrue(self.call("plan")["canApply"])
        self.assertEqual(self.value("panels().length"), 1)
        self.assertEqual(self.value("panels()[0].widgets.length"), 0)

    def test_create_reapply_and_rollback_preserve_original_panel(self):
        self.js.evaluate("new Panel();")
        created = self.call("apply")
        self.assertEqual(created["state"], "created")
        self.assertEqual(self.value("panels()[1].location"), "top")
        self.assertEqual(self.value("panels()[1].widgets.map(function(w) {return w.plugin;})"), [
            "org.kde.plasma.kickoff", "org.kde.plasma.appmenu", "org.kde.plasma.panelspacer",
            "org.kde.plasma.systemtray", "org.kde.plasma.digitalclock"])
        self.assertEqual(self.value("panels()[1].widgets[0].config['General/menuLabel']"), "brutallOS")
        self.assertEqual(self.call("apply")["state"], "unchanged")
        self.assertEqual(self.value("panels().length"), 2)
        self.assertEqual(self.call("rollback")["removed"], [created["id"]])
        self.assertEqual(self.value("panels()[0].id"), 10)
        self.assertEqual(self.call("rollback")["state"], "absent")

    def test_top_panel_conflict_and_missing_required_widget_do_not_mutate(self):
        self.js.evaluate("var existing = new Panel(); existing.location = 'top';")
        self.assertFalse(self.call("plan")["canApply"])
        failure = self.js.evaluate("brutallTopPanel('apply', {screen:0,height:36,owner:'x'})")
        self.assertTrue(failure.isError())
        self.assertEqual(self.value("panels().length"), 1)
        self.js.evaluate("existing.location = 'bottom'; knownWidgetTypes = [];")
        self.assertFalse(self.call("plan")["canApply"])
        self.assertTrue(self.js.evaluate("brutallTopPanel('apply', {screen:0,height:36,owner:'x'})").isError())
        self.assertEqual(self.value("panels().length"), 1)

    def test_absent_global_menu_is_omitted(self):
        self.js.evaluate("knownWidgetTypes.splice(1, 1);")
        self.assertEqual(self.call("apply")["state"], "created")
        plugins = self.value("panels()[0].widgets.map(function(w) {return w.plugin;})")
        self.assertNotIn("org.kde.plasma.appmenu", plugins)

    def test_failed_widget_creation_removes_only_new_panel(self):
        self.js.evaluate("new Panel(); failPlugin = 'org.kde.plasma.systemtray';")
        self.assertTrue(self.js.evaluate("brutallTopPanel('apply', {screen:0,height:36,owner:'x'})").isError())
        self.assertEqual(self.value("panels().length"), 1)
        self.assertEqual(self.value("panels()[0].id"), 10)

    def test_rollback_uses_owner_even_after_move_or_disconnect(self):
        self.call("apply")
        self.js.evaluate("panels()[0].screen = -1; panels()[0].location = 'bottom'; screenCount = 0;")
        self.assertEqual(self.call("rollback")["state"], "removed")

    def test_foreign_owner_never_removed(self):
        self.call("apply")
        result = self.value("brutallTopPanel('rollback', {owner:'different-owner'})")
        self.assertEqual(result["removed"], [])
        self.assertEqual(self.value("panels().length"), 1)

    def test_locked_session_and_invalid_screen_are_rejected(self):
        self.js.evaluate("locked = true;")
        self.assertFalse(self.call("plan")["canApply"])
        self.assertTrue(self.js.evaluate("brutallTopPanel('apply', {screen:0,height:36,owner:'x'})").isError())
        self.assertTrue(self.js.evaluate("brutallTopPanel('plan', {screen:9})").isError())
        self.assertEqual(self.value("panels().length"), 0)


class FakePlasma:
    version = "plasmashell 6.3.6"

    def __init__(self, state, failure=False):
        self.state = state
        self.failure = failure
        self.actions = []

    def evaluate(self, action, options):
        self.actions.append(action)
        if action == "plan":
            return {"existing": [], "canApply": True}
        if action == "apply":
            manifests = list(self.state.glob("backups/*/manifest.json"))
            assert len(manifests) == 1, "Remote changes cannot precede the backup"
            manifest = json.loads(manifests[0].read_text())
            assert manifest["phase"] == "prepared"
            assert manifest["owner"] == options["owner"]
            if self.failure:
                raise subprocess.TimeoutExpired("qdbus", 45)
            return {"state": "created", "id": 123}
        return {"state": "removed", "removed": [123]}


class BackupTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.config = self.root / "config"
        self.config.mkdir()
        self.state = self.root / "state"
        self.options = {"screen": 0, "height": 36}

    def test_backup_precedes_mutation_and_preserves_original_bytes(self):
        original = b"[Containments][1]\nplugin=org.kde.panel\n"
        source = self.config / runner.CONFIG_FILES[0]
        source.write_bytes(original)
        plasma = FakePlasma(self.state)
        result = runner.apply(plasma, self.state, self.config, self.options)
        directory = Path(result["backup"])
        self.assertEqual((directory / source.name).read_bytes(), original)
        self.assertEqual(source.read_bytes(), original)
        manifest = json.loads((directory / "manifest.json").read_text())
        self.assertFalse(manifest["files"]["plasmashellrc"]["existed"])
        self.assertEqual(manifest["phase"], "created")
        self.assertEqual(runner.rollback(plasma, self.state, directory)["state"], "removed")
        self.assertEqual(json.loads((directory / "manifest.json").read_text())["phase"], "reverted")

    def test_backup_failure_prevents_remote_mutation(self):
        plasma = FakePlasma(self.state)
        with patch.object(runner, "backup", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                runner.apply(plasma, self.state, self.config, self.options)
        self.assertEqual(plasma.actions, ["plan"])

    def test_transport_timeout_retains_recovery_journal(self):
        plasma = FakePlasma(self.state, failure=True)
        with self.assertRaisesRegex(ValueError, "Resultado não confirmado"):
            runner.apply(plasma, self.state, self.config, self.options)
        manifest_path = next(self.state.glob("backups/*/manifest.json"))
        self.assertEqual(json.loads(manifest_path.read_text())["phase"], "uncertain")
        self.assertEqual(runner.rollback(plasma, self.state, manifest_path.parent)["state"], "removed")

    def test_dbus_error_reports_reason_without_dumping_layout_source(self):
        plasma = runner.Plasma.__new__(runner.Plasma)
        plasma.command = "/mock/qdbus6"
        reply = subprocess.CompletedProcess([], 1, "", "Widgets are locked")
        with patch.object(runner.subprocess, "run", return_value=reply):
            with self.assertRaisesRegex(ValueError, "Widgets are locked") as caught:
                plasma.evaluate("plan", self.options)
        self.assertNotIn("function brutallTopPanel", str(caught.exception))

    def test_offline_plan_does_not_create_state_or_require_plasma(self):
        environment = dict(os.environ, XDG_STATE_HOME=str(self.state), XDG_CONFIG_HOME=str(self.config))
        process = subprocess.run([str(ROOT / "scripts/brutall-top-panel"), "plan", "--offline"],
                                 env=environment, text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(process.stdout)["mode"], "offline")
        self.assertFalse(self.state.exists())


if __name__ == "__main__":
    unittest.main()
