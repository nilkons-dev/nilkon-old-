"""The animated NILKON logo (black cat, red flames, moon): flames flicker, ears twitch, whiskers sway, eyes blink.
Layers + keyframes come from assets/logo_anim (extracted from the supplied animated logo)."""
import json
import time
from pathlib import Path

from PySide6.QtCore import Qt, QRectF, QTimer
from PySide6.QtGui import QPainter, QPixmap, QTransform
from PySide6.QtWidgets import QWidget

from panels_assets import ASSETS

_SPEC = None


def _load_spec():
    global _SPEC
    if _SPEC is None:
        try:
            _SPEC = json.loads((ASSETS / "logo_anim" / "logo_anim.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _SPEC = {"size": [900, 947], "layers": [], "keyframes": {}}
    return _SPEC


def _ease(x):
    return x * x * (3.0 - 2.0 * x)           # close to CSS ease-in-out


def _value(frames, phase):
    """(rotation deg, scale, scaleY) at `phase` 0..1 of a keyframe list [[t, rot, scale, scaleY], ...]."""
    if not frames:
        return 0.0, 1.0, 1.0
    prev = frames[0]
    for cur in frames[1:]:
        if phase <= cur[0]:
            span = cur[0] - prev[0]
            k = _ease((phase - prev[0]) / span) if span > 1e-9 else 1.0
            return tuple(prev[i] + (cur[i] - prev[i]) * k for i in (1, 2, 3))
        prev = cur
    return prev[1], prev[2], prev[3]


class AnimatedLogo(QWidget):
    """Fixed-height logo widget. `reduced` (settings: reduced effects) shows it still."""

    def __init__(self, height=64, parent=None, animate=True):
        super().__init__(parent)
        spec = _load_spec()
        self._w, self._h = spec["size"]
        self._spec = spec
        self._animate = animate
        self._t0 = time.monotonic()
        self._pix = None            # (key, base, [layer pixmaps]) scaled for the current size
        self.setFixedSize(max(8, int(round(height * self._w / self._h))), height)
        self._timer = QTimer(self)
        self._timer.setInterval(33)
        self._timer.timeout.connect(self.update)
        self._src = {}

    def set_animated(self, on):
        self._animate = bool(on)
        if self.isVisible():
            self._timer.start() if on else self._timer.stop()
        self.update()

    def showEvent(self, e):
        if self._animate:
            self._timer.start()
        super().showEvent(e)

    def hideEvent(self, e):
        self._timer.stop()
        super().hideEvent(e)

    # -- pictures, scaled once for the widget's pixel size ---------------------------------------------------
    def _source(self, name):
        if name not in self._src:
            self._src[name] = QPixmap(str(ASSETS / "logo_anim" / f"{name}.png"))
        return self._src[name]

    def _scaled(self):
        dpr = self.devicePixelRatioF()
        key = (self.width(), self.height(), dpr)
        if self._pix and self._pix[0] == key:
            return self._pix
        W, H = self.width() * dpr, self.height() * dpr

        def fit(pm, w, h):
            if pm.isNull():
                return pm
            out = pm.scaled(max(1, int(round(w))), max(1, int(round(h))), Qt.AspectRatioMode.IgnoreAspectRatio,
                            Qt.TransformationMode.SmoothTransformation)
            out.setDevicePixelRatio(dpr)
            return out
        base = fit(self._source("base"), W, H)
        layers = []
        for lay in self._spec["layers"]:
            if lay["name"] == "base":
                continue
            bx, by, bw, bh = lay["box"]
            layers.append((lay, fit(self._source(lay["name"]), bw * W, bh * H)))
        self._pix = (key, base, layers)
        return self._pix

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        _key, base, layers = self._scaled()
        w, h = float(self.width()), float(self.height())
        p.drawPixmap(QRectF(0, 0, w, h).toRect(), base)
        t = time.monotonic() - self._t0 if self._animate else 0.0
        kfs = self._spec["keyframes"]
        for lay, pm in layers:
            bx, by, bw, bh = lay["box"]
            rect = QRectF(bx * w, by * h, bw * w, bh * h)
            rot, sc, scy = 0.0, 1.0, 1.0
            name = lay.get("kf")
            if name and self._animate and t >= lay.get("delay", 0.0):
                dur = lay.get("dur", 1.0)
                phase = ((t - lay.get("delay", 0.0)) % dur) / dur
                rot, sc, scy = _value(kfs.get(name), phase)
                if name == "blink":                       # eyelids: only scaleY matters
                    rot, sc = 0.0, 1.0
                else:
                    scy = 1.0
            elif name == "blink":
                scy = 0.0                                 # eyelid open
            if name == "blink" and scy <= 0.001:
                continue
            ox, oy = lay["origin"]
            pivot = (rect.left() + ox * rect.width(), rect.top() + oy * rect.height())
            tr = QTransform()
            tr.translate(*pivot)
            tr.rotate(rot)
            tr.scale(sc, scy if name == "blink" else sc)
            tr.translate(-pivot[0], -pivot[1])
            p.setTransform(tr)
            p.drawPixmap(rect.topLeft(), pm)
            p.resetTransform()
        p.end()


class LogoMark(AnimatedLogo):
    """Old name used by the main window and the settings page: LogoMark(engine, size)."""

    def __init__(self, engine=None, size=64, parent=None):
        super().__init__(size, parent)
        self.engine = engine

    def paintEvent(self, e):
        self._animate = not bool(getattr(self.engine, "reduced", False))
        super().paintEvent(e)
