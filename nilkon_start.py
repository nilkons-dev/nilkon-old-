"""Start-up file of the installed app: a small splash screen appears at once, then the player loads behind it."""
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen


def _splash():
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / "assets"
    pm = QPixmap(420, 240)
    pm.fill(QColor(11, 13, 19))
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    p.setPen(QColor(255, 255, 255, 30))
    p.drawRect(0, 0, 419, 239)
    for name in ("logo_app.png", "logo.png"):
        f = base / name
        if f.is_file():
            logo = QPixmap(str(f)).scaledToWidth(210, Qt.TransformationMode.SmoothTransformation)
            p.drawPixmap((420 - logo.width()) // 2, 36, logo)
            break
    p.setPen(QColor(255, 255, 255, 150))
    f = QFont()
    f.setPixelSize(12)
    p.setFont(f)
    p.drawText(pm.rect().adjusted(0, 0, 0, -22), Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom, "Starting…")
    p.end()
    return QSplashScreen(pm, Qt.WindowType.WindowStaysOnTopHint)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = _splash()
    splash.show()
    app.processEvents()
    import music_player                      # the heavy part - the splash is already on screen
    sys.exit(music_player.main(app, splash))
