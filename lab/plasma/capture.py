"""Capture the entire X11 screen, including panels, desktop and windows."""
import sys
from PySide6.QtGui import QGuiApplication
app = QGuiApplication(sys.argv)
screen = app.primaryScreen()
if screen is None or not screen.grabWindow(0).save(sys.argv[1]):
    raise SystemExit("Full desktop capture failed")
print(screen.size().width(), screen.size().height(), sys.argv[1])
