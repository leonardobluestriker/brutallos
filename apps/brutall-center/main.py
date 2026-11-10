#!/usr/bin/env python3
"""brutallOS launcher, settings entry points and read-only Striker monitoring."""
from pathlib import Path
import shutil
import subprocess
import sys

from PySide6.QtCore import QObject, Property, Signal, Slot, QTimer, QUrl, QProcess
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from services import applications, Metrics

ROOT = Path(__file__).resolve().parents[2]
MODULES = [("Tela", "kcm_kscreen"), ("Som", "kcm_pulseaudio"), ("Rede", "kcm_networkmanagement"),
           ("Energia", "kcm_powerdevilprofilesconfig"), ("Data e hora", "kcm_clock"),
           ("Teclado", "kcm_keyboard"), ("Bluetooth", "kcm_bluetooth")]


class Center(QObject):
    changed = Signal()
    appsChanged = Signal()
    metricsChanged = Signal()

    def __init__(self):
        super().__init__()
        self._message = ""
        self._apps = applications()
        self._visible_apps = self._apps
        self.gio = shutil.which("gio")
        self.settingsCommand = shutil.which("kcmshell6") or shutil.which("systemsettings")
        self.modules = set()
        if self.settingsCommand:
            try:
                listing = subprocess.run([self.settingsCommand, "--list"], capture_output=True, text=True, timeout=5, check=True)
                self.modules = {line.split()[0] for line in listing.stdout.splitlines() if line.strip()}
            except (OSError, subprocess.SubprocessError):
                pass
        self.reader = Metrics()
        self._metrics = self.reader.sample()
        self.timer = QTimer(self)
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.refreshMetrics)

    @Property(str, notify=changed)
    def message(self):
        return self._message

    @Property(bool, constant=True)
    def canLaunch(self):
        return bool(self.gio)

    @Property("QVariantList", notify=appsChanged)
    def apps(self):
        return self._visible_apps

    @Property("QVariantList", constant=True)
    def settings(self):
        return [dict(name=name, module=module, available=bool(self.settingsCommand and module in self.modules)) for name, module in MODULES]

    @Property("QVariantMap", notify=metricsChanged)
    def metrics(self):
        return self._metrics

    @Slot(str)
    def search(self, text):
        query = text.casefold().strip()
        self._visible_apps = [item for item in self._apps if query in (item["name"] + " " + item["description"] + " " + item["categories"]).casefold()]
        self.appsChanged.emit()

    def start(self, command, arguments):
        try:
            success, _ = QProcess.startDetached(command, arguments)
            self._message = "Solicitação enviada ao aplicativo." if success else "Não foi possível iniciar o aplicativo."
        except (OSError, TypeError) as error:
            self._message = str(error)
        self.changed.emit()

    @Slot(str)
    def launch(self, identifier):
        item = next((item for item in self._apps if item["id"] == identifier), None)
        if item and self.gio:
            self.start(self.gio, ["launch", item["path"]])

    @Slot(str)
    def openSettings(self, module):
        if module in {entry[1] for entry in MODULES} and module in self.modules and self.settingsCommand:
            self.start(self.settingsCommand, [module])

    @Slot()
    def openAppearance(self):
        self.start(sys.executable, [str(ROOT / "apps/brutall-welcome/main.py")])

    @Slot(bool)
    def setMonitoring(self, enabled):
        if enabled:
            self.refreshMetrics()
            self.timer.start()
        else:
            self.timer.stop()

    @Slot()
    def refreshMetrics(self):
        self._metrics = self.reader.sample()
        self.metricsChanged.emit()


def create_engine():
    backend = Center()
    engine = QQmlApplicationEngine()
    engine.setInitialProperties({"backend": backend})
    engine.load(QUrl.fromLocalFile(str(Path(__file__).parent / "Main.qml")))
    return engine, backend


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    app.setApplicationName("brutall-center")
    app.setOrganizationName("brutallOS")
    engine, backend = create_engine()
    sys.exit(app.exec() if engine.rootObjects() else 1)
