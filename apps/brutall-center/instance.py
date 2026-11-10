"""One launcher window per user/runtime; activate it on subsequent requests."""
from pathlib import Path
import hashlib
import os
from PySide6.QtCore import QLockFile, QStandardPaths
from PySide6.QtGui import QGuiApplication
from PySide6.QtNetwork import QLocalServer, QLocalSocket


class LauncherInstance:
    def __init__(self, name=None):
        runtime = QStandardPaths.writableLocation(QStandardPaths.RuntimeLocation)
        display = os.environ.get("WAYLAND_DISPLAY", "wayland-0") if QGuiApplication.platformName().startswith("wayland") else os.environ.get("DISPLAY", "headless")
        tag = hashlib.sha256((QGuiApplication.platformName() + display).encode()).hexdigest()[:12]
        self.name = name or str(Path(runtime) / ("brutallos-launcher-" + tag + ".sock"))
        self.lock = QLockFile(self.name + ".lock")
        self.server = QLocalServer()
        self.server.setSocketOptions(QLocalServer.UserAccessOption)

    def acquire(self):
        if not self.lock.tryLock(0):
            client = QLocalSocket()
            client.connectToServer(self.name)
            if not client.waitForConnected(1500):
                raise RuntimeError("O launcher está iniciando. Tente novamente.")
            client.write(b"activate")
            client.waitForBytesWritten(500)
            client.disconnectFromServer()
            return False
        QLocalServer.removeServer(self.name)  # lock proves no live owner remains
        if not self.server.listen(self.name):
            raise RuntimeError(self.server.errorString())
        return True

    def bind(self, window):
        def activate():
            while self.server.hasPendingConnections():
                client = self.server.nextPendingConnection()
                client.disconnectFromServer()
                client.deleteLater()
            window.showNormal()
            window.raise_()
            window.requestActivate()
        self.server.newConnection.connect(activate)

    def close(self):
        self.server.close()
        self.lock.unlock()
