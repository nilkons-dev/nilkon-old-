"""Start-up window: the animated NILKON logo, the name under it and a loading bar. Light on purpose - it is on screen
before the heavy parts of the program are loaded."""
import sys
import time
from pathlib import Path

from PySide6.QtCore import QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QGuiApplication, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap, QRadialGradient
from PySide6.QtWidgets import QWidget

from logo_widget import AnimatedLogo
from theme import load_fonts, FONT_FAMILIES

W, H = 460, 440
LOGO_H = 218
ACCENT = QColor(240, 40, 60)
ACCENT2 = QColor(255, 92, 77)


class Splash(QWidget):
    def __init__(self):
        super().__init__(None, Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint
                         | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowTransparentForInput)
        load_fonts()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(W, H)
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / "assets"
        self._word = QPixmap(str(base / "wordmark.png"))
        self._target = 0.04
        self._shown = 0.0
        self._text = "Starting…"
        self._phase = 0.0
        self.logo = AnimatedLogo(LOGO_H, self)
        self.logo.move((W - self.logo.width()) // 2, 34)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        scr = QGuiApplication.primaryScreen()
        if scr is not None:
            g = scr.availableGeometry()
            self.move(g.center().x() - W // 2, g.center().y() - H // 2)

    def showEvent(self, e):
        self.timer.start(16)
        super().showEvent(e)

    def set_progress(self, value, text=None):
        self._target = max(self._target, min(1.0, float(value)))
        if text:
            self._text = text
        self.update()

    def _tick(self):
        self._phase = (time.monotonic() * 0.9) % 1.0
        # the bar glides towards the real progress and keeps creeping a little, so it never looks frozen
        self._shown += (self._target - self._shown) * 0.12
        if self._shown < self._target + 0.04:
            self._shown += 0.0009
        self._shown = min(self._shown, 0.985 if self._target < 1.0 else 1.0)
        self.update()

    def finish(self, _window=None):
        self.timer.stop()
        self.close()

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        r = QRectF(0.5, 0.5, W - 1, H - 1)
        path = QPainterPath()
        path.addRoundedRect(r, 18, 18)
        p.fillPath(path, QColor(10, 10, 14))
        glow = QRadialGradient(W / 2.0, 150, 240)
        glow.setColorAt(0.0, QColor(200, 25, 45, 70))
        glow.setColorAt(1.0, QColor(200, 25, 45, 0))
        p.setClipPath(path)
        p.fillRect(self.rect(), glow)
        p.setClipping(False)
        p.setPen(QPen(QColor(255, 255, 255, 26), 1))
        p.drawPath(path)
        # name under the logo
        y = 34 + LOGO_H + 8
        if not self._word.isNull():
            wm = self._word.scaledToWidth(210, Qt.TransformationMode.SmoothTransformation)
            p.drawPixmap((W - wm.width()) // 2, y, wm)
            y += wm.height()
        # loading bar
        bw, bh = 250.0, 5.0
        bx, by = (W - bw) / 2.0, float(H - 62)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(255, 255, 255, 24))
        p.drawRoundedRect(QRectF(bx, by, bw, bh), bh / 2, bh / 2)
        fw = max(bh, bw * self._shown)
        g = QLinearGradient(bx, 0, bx + bw, 0)
        g.setColorAt(0.0, ACCENT)
        g.setColorAt(1.0, ACCENT2)
        p.setBrush(g)
        p.drawRoundedRect(QRectF(bx, by, fw, bh), bh / 2, bh / 2)
        # soft moving highlight on the bar
        hx = bx + (bw - 60) * self._phase
        hl = QLinearGradient(hx, 0, hx + 60, 0)
        hl.setColorAt(0.0, QColor(255, 255, 255, 0))
        hl.setColorAt(0.5, QColor(255, 255, 255, 70))
        hl.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setClipRect(QRectF(bx, by, fw, bh))
        p.setBrush(hl)
        p.drawRoundedRect(QRectF(hx, by, 60, bh), bh / 2, bh / 2)
        p.setClipping(False)
        f = QFont()
        f.setFamilies(FONT_FAMILIES)
        f.setPixelSize(13)
        p.setFont(f)
        p.setPen(QColor(255, 255, 255, 120))
        p.drawText(QRectF(0, by + 12, W, 20), Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, self._text)
        p.end()
