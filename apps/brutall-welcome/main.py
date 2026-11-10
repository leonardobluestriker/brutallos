#!/usr/bin/env python3
"""brutall-welcome — Qt 6 / QML onboarding, without Plasma configuration writes."""
import argparse
import os
from pathlib import Path
import sys

from PySide6.QtCore import QObject, Property, Signal, Slot, QUrl, QTranslator, QLocale, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from catalog import THEMES, PRESETS, ARTCRAFT, defaults
from preferences import Preferences

ROOT = Path(__file__).resolve().parents[2]


class WelcomeBackend(QObject):
    changed = Signal()
    messageChanged = Signal()
    systemAppearanceChanged = Signal()

    def __init__(self, directory):
        super().__init__()
        self.store = Preferences(directory)
        self._message = ""
        QGuiApplication.styleHints().colorSchemeChanged.connect(self.systemAppearanceChanged.emit)
        try:
            self._preferences = self.store.read()
        except (OSError, ValueError, TypeError, KeyError) as error:
            self._preferences = defaults()
            self._message = "Não foi possível ler as preferências. O arquivo será preservado no backup ao salvar. " + str(error)

    @Property("QVariantList", constant=True)
    def themes(self):
        return THEMES

    @Property(bool, notify=systemAppearanceChanged)
    def systemDark(self):
        return QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark

    @Property("QVariantList", constant=True)
    def presets(self):
        return PRESETS

    @Property("QStringList", constant=True)
    def artcraft(self):
        return ARTCRAFT

    @Property("QVariantMap", notify=changed)
    def preferences(self):
        return self._preferences

    @Property(str, notify=messageChanged)
    def message(self):
        return self._message

    @Property(bool, notify=changed)
    def canRestore(self):
        return self.store.backup.exists()

    @Slot(str, result=str)
    def asset(self, filename):
        allowed = {v["file"] for t in THEMES for v in t["variants"]}
        if filename not in allowed:
            return ""
        return QUrl.fromLocalFile(str(ROOT / "assets" / "wallpapers" / filename)).toString()

    @Slot(str, str, str, str, bool, bool, result=bool)
    def save(self, theme, variant, preset, appearance, contrast, reduced):
        data = dict(schemaVersion=1, theme=theme, variant=variant, preset=preset,
                    appearance=appearance, highContrast=contrast, reducedMotion=reduced, completed=True)
        try:
            self.store.save(data)
            self._preferences = data
            self._message = "Preferências salvas. Você pode desfazer a última gravação."
            success = True
        except (OSError, ValueError) as error:
            self._message = "Não foi possível salvar: " + str(error)
            success = False
        self.changed.emit()
        self.messageChanged.emit()
        return success

    @Slot(result=bool)
    def restore(self):
        try:
            self.store.restore()
            try:
                self._preferences = self.store.read()
                self._message = "Última gravação desfeita."
            except (OSError, ValueError, TypeError, KeyError):
                self._preferences = defaults()
                self._message = "Arquivo anterior restaurado; seu conteúdo não é uma preferência válida."
            success = True
        except (OSError, ValueError, KeyError, TypeError) as error:
            self._message = "Não foi possível desfazer: " + str(error)
            success = False
        self.changed.emit()
        self.messageChanged.emit()
        return success


def create_engine(app, directory):
    backend = WelcomeBackend(directory)
    engine = QQmlApplicationEngine()
    engine.setInitialProperties({"backend": backend})
    engine.load(QUrl.fromLocalFile(str(Path(__file__).parent / "qml" / "Main.qml")))
    return engine, backend


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-dir", type=Path, help="Diretório isolado para testes")
    parser.add_argument("--restore", action="store_true", help="Desfaz a última gravação e encerra")
    args = parser.parse_args()
    directory = args.config_dir or Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "brutallos"
    if args.restore:
        try:
            Preferences(directory).restore()
        except (OSError, ValueError, KeyError, TypeError) as error:
            print(error, file=sys.stderr)
            return 1
        print("Última gravação desfeita.")
        return 0
    QGuiApplication.setApplicationName("brutall-welcome")
    QGuiApplication.setOrganizationName("brutallOS")
    app = QGuiApplication(sys.argv[:1])
    translator = QTranslator(app)
    translator.load(QLocale(), "welcome", "_", str(Path(__file__).parent / "translations"))
    app.installTranslator(translator)
    engine, backend = create_engine(app, directory)
    if not engine.rootObjects():
        return 1
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
