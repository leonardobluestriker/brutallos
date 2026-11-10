#!/usr/bin/env python3
"""brutallOS launcher, settings entry points and read-only Striker monitoring."""
from pathlib import Path
import shutil
import subprocess
import sys

from PySide6.QtCore import QObject, Property, Signal, Slot, QTimer, QUrl, QProcess, QTemporaryDir
from PySide6.QtGui import QGuiApplication, QIcon
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
    appearanceApplied = Signal(bool)

    def __init__(self):
        super().__init__()
        self._message = ""
        self._appearanceBackup = None
        self.appearanceProcess = QProcess(self)
        self.appearanceProcess.finished.connect(self.appearanceFinished)
        self.appearanceProcess.errorOccurred.connect(self.appearanceError)
        self._apps = applications()
        self._icons = QTemporaryDir()
        for index, item in enumerate(self._apps):
            icon_name = item.get("icon", "application-x-executable")
            icon = QIcon(icon_name) if Path(icon_name).is_absolute() else QIcon.fromTheme(icon_name)
            if icon.isNull():
                icon = QIcon.fromTheme("application-x-executable")
            item["iconUrl"] = ""
            if self._icons.isValid():
                path = Path(self._icons.path()) / (str(index) + ".png")
                item["iconUrl"] = QUrl.fromLocalFile(str(path)).toString() if icon.pixmap(56, 56).save(str(path)) else ""
        self._visible_apps = self._apps
        self._query = ""
        self._category = ""
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

    @Property(bool, constant=True)
    def systemDark(self):
        return QGuiApplication.palette().window().color().lightness() < 128

    @Property(bool, constant=True)
    def canApplyAppearance(self):
        return bool(shutil.which("kwriteconfig6") and shutil.which("plasma-apply-colorscheme"))

    @Property(bool, notify=changed)
    def appearanceBusy(self):
        return self.appearanceProcess.state() != QProcess.NotRunning

    @Property(bool, notify=changed)
    def canUndoAppearance(self):
        return self._appearanceBackup is not None

    @Property("QVariantList", constant=True)
    def themePreviews(self):
        return [dict(name=name, url=QUrl.fromLocalFile(str(ROOT / "assets/wallpapers" / filename)).toString())
                for name, filename in [("Bru", "BRU1.png"), ("Raio", "RAIO1.png"), ("Strikerzinho & Friends", "BLUESTRIKER.png")]]

    @Slot(str)
    def applyAppearance(self, mode):
        if mode not in {"light", "dark"} or self.appearanceBusy or not self.canApplyAppearance:
            return
        self._appearanceMode = mode
        self._pendingAppearancePreviousDark = QGuiApplication.palette().window().color().lightness() < 128
        self._message = "Aplicando Bru com backup…"
        self.appearanceProcess.start(sys.executable, [str(ROOT / "scripts/brutall-appearance"), "apply", "--mode", mode])
        self.changed.emit()

    def appearanceFinished(self, exit_code, status):
        output = bytes(self.appearanceProcess.readAllStandardOutput()).decode(errors="replace")
        errors = bytes(self.appearanceProcess.readAllStandardError()).decode(errors="replace")
        self._message = "Não foi possível concluir: " + (errors or output).strip()
        if exit_code != 0 and self._appearanceMode != "rollback":
            backup = next((line[8:].strip() for line in output.splitlines() if line.startswith("Backup: ")), None)
            if backup is not None:
                self._appearanceBackup = backup
                self._appearancePreviousDark = self._pendingAppearancePreviousDark
        if exit_code == 0:
            if self._appearanceMode == "rollback":
                self._appearanceBackup = None
                self._message = "Aparência anterior restaurada. Reabra outros apps para recarregar as cores."
                self.appearanceApplied.emit(self._appearancePreviousDark)
            else:
                self._appearancePreviousDark = self._pendingAppearancePreviousDark
                self._appearanceBackup = next((line[8:].strip() for line in output.splitlines() if line.startswith("Backup: ")), None)
                self._message = "Bru aplicado com backup. Você pode desfazer a última aplicação nesta tela."
                self.appearanceApplied.emit(self._appearanceMode == "dark")
        self.changed.emit()

    @Slot()
    def undoAppearance(self):
        if not self.canUndoAppearance or self.appearanceBusy:
            return
        self._appearanceMode = "rollback"
        self.appearanceProcess.start(sys.executable, [str(ROOT / "scripts/brutall-appearance"), "rollback", "--backup", self._appearanceBackup])
        self._message = "Restaurando a aparência anterior…"
        self.changed.emit()

    def appearanceError(self, error):
        self._message = "Falha ao executar a aplicação de tema: " + self.appearanceProcess.errorString()
        self.changed.emit()

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
        self._query = text.casefold().strip()
        self.filterApps()

    @Slot(str)
    def setCategory(self, category):
        if category not in {"", "Graphics", "AudioVideo", "Office", "Game", "Network", "Utility", "System"}:
            return
        self._category = category
        self.filterApps()

    def filterApps(self):
        self._visible_apps = [item for item in self._apps
                              if self._query in (item["name"] + " " + item["description"] + " " + item["categories"]).casefold()
                              and (not self._category or self._category in item["categories"].split(";"))]
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
    QGuiApplication.setWindowIcon(QIcon.fromTheme("preferences-system"))
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
