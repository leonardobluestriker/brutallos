"""Launch an actual project window at a reproducible position in the lab."""
from pathlib import Path
import sys
from PySide6.QtGui import QGuiApplication

app = QGuiApplication(sys.argv[:1])
if sys.argv[1] == "center":
    sys.path.insert(0, "/project/apps/brutall-center")
    from main import create_engine
    engine, backend = create_engine()
    window = engine.rootObjects()[0]
    window.setProperty("page", int(sys.argv[2]))
else:
    sys.path.insert(0, "/project/apps/brutall-welcome")
    from main import create_engine
    engine, backend = create_engine(app, Path("/home/tester/.config/brutallos"))
    window = engine.rootObjects()[0]
    window.setProperty("step", 2)
    window.setProperty("themeIndex", 2)
area = app.primaryScreen().availableGeometry()
window.resize(min(1120, area.width() - 80), min(760, area.height() - 60))
window.setPosition(area.x() + (area.width() - window.width()) // 2,
                   area.y() + (area.height() - window.height()) // 2)
window.requestActivate()
app.exec()
