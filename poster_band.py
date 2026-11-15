"""Poster strip of the Explore page: one wide banner and one small card side by side. Each of them shows a random
picture from assets/posters and, every few seconds, fades over to another one."""
import random

from PySide6.QtCore import Qt, QRectF, QTimer, QVariantAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QPen, QColor, QPixmap
from PySide6.QtWidgets import QWidget

from panels_assets import ASSETS
from widgets import round_path, AA

GAP = 14
BANNER_RATIO = 4.6          # width / height of the banner box
CARD_RATIO = 1.48           # width / height of the card box (the card pictures are 1200 x 812)
RADIUS = 16
FADE_MS = 800


class _Slot:
    def __init__(self, kind, folder):
        self.kind = kind
        self.files = sorted(folder.glob(f"{kind}_*.jpg")) if folder.is_dir() else []
        self.bag = []
        self.cur = None            # file shown
        self.nxt = None            # file fading in
        self.t = 1.0               # fade progress (1 = finished)
        self.rect = QRectF()
        self.anim = None

    def pick(self):
        if not self.files:
            return None
        if not self.bag:
            self.bag = self.files[:]
            random.shuffle(self.bag)
            if len(self.bag) > 1 and self.bag[-1] == self.cur:          # never the same picture twice in a row
                self.bag.insert(0, self.bag.pop())
        return self.bag.pop()


class PosterBand(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        folder = ASSETS / "posters"
        self.banner = _Slot("banner", folder)
        self.card = _Slot("card", folder)
        self._raw = {}              # file -> QPixmap (a few kept)
        self._scaled = {}           # (file, w, h, dpr) -> QPixmap cropped to fill the box
        for s in (self.banner, self.card):
            s.cur = s.pick()
        self._timers = []
        for slot, every in ((self.banner, 7000), (self.card, 9000)):
            tm = QTimer(self)
            tm.setSingleShot(True)
            tm.timeout.connect(lambda s=slot, e=every: self._advance(s, e))
            self._timers.append((tm, every))
        self.has_posters = bool(self.banner.files or self.card.files)
        self.setVisible(self.has_posters)

    # -- timing ------------------------------------------------------------------------------------------
    def showEvent(self, e):
        for i, (tm, every) in enumerate(getattr(self, "_timers", ())):
            tm.start(every // 2 + i * 1800)
        super().showEvent(e)

    def hideEvent(self, e):
        for tm, _e in getattr(self, "_timers", ()):
            tm.stop()
        super().hideEvent(e)

    def _advance(self, slot, every):
        if not self.isVisible():
            return
        win = self.window()
        if win is not None and win.isMinimized():                     # nothing to show: try again later
            QTimer.singleShot(every, lambda: self._advance(slot, every))
            return
        nxt = slot.pick()
        if nxt is not None and nxt != slot.cur and self._raw_pm(nxt) is not None:
            slot.nxt, slot.t = nxt, 0.0
            if slot.anim is None:
                slot.anim = QVariantAnimation(self)
                slot.anim.setDuration(FADE_MS)
                slot.anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
                slot.anim.setStartValue(0.0)
                slot.anim.setEndValue(1.0)
                slot.anim.valueChanged.connect(lambda v, s=slot: self._on_fade(s, float(v)))
                slot.anim.finished.connect(lambda s=slot: self._fade_done(s))
            slot.anim.stop()
            slot.anim.start()
        for tm, ev in self._timers:
            if ev == every:
                tm.start(every)

    def _on_fade(self, slot, v):
        slot.t = v
        self.update(slot.rect.toAlignedRect())

    def _fade_done(self, slot):
        if slot.nxt is not None:
            slot.cur, slot.nxt = slot.nxt, None
        slot.t = 1.0
        self.update(slot.rect.toAlignedRect())

    # -- pictures ----------------------------------------------------------------------------------------
    def _raw_pm(self, f):
        if f is None:
            return None
        pm = self._raw.get(f)
        if pm is None:
            pm = QPixmap(str(f))
            if pm.isNull():
                return None
            if len(self._raw) >= 6:
                self._raw.pop(next(iter(self._raw)))
            self._raw[f] = pm
        return pm

    def _filled(self, f, rect):
        """The picture scaled to cover `rect` (the middle is kept), cached for this size."""
        dpr = self.devicePixelRatioF() or 1.0
        key = (f, int(rect.width()), int(rect.height()), dpr)
        pm = self._scaled.get(key)
        if pm is None:
            raw = self._raw_pm(f)
            if raw is None:
                return None
            tw, th = max(1, int(rect.width() * dpr)), max(1, int(rect.height() * dpr))
            sc = raw.scaled(tw, th, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            pm = sc.copy((sc.width() - tw) // 2, (sc.height() - th) // 2, tw, th)
            pm.setDevicePixelRatio(dpr)
            if len(self._scaled) >= 8:
                self._scaled.pop(next(iter(self._scaled)))
            self._scaled[key] = pm
        return pm

    # -- layout / painting ---------------------------------------------------------------------------------
    def resizeEvent(self, e):
        w = float(self.width())
        bw = max(200.0, (w - GAP) / (1.0 + 1.0 / BANNER_RATIO * CARD_RATIO))
        h = bw / BANNER_RATIO
        cw = h * CARD_RATIO
        self.banner.rect = QRectF(0, 0, bw, h)
        self.card.rect = QRectF(bw + GAP, 0, cw, h)
        self._scaled.clear()
        self.setFixedHeight(int(round(h)))
        super().resizeEvent(e)

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(AA)
        for slot in (self.banner, self.card):
            r = slot.rect
            if r.width() < 10 or slot.cur is None:
                continue
            p.save()
            p.setClipPath(round_path(r, RADIUS))
            base = self._filled(slot.cur, r)
            if base is not None:
                p.drawPixmap(r.topLeft(), base)
            if slot.nxt is not None and slot.t > 0.0:
                top = self._filled(slot.nxt, r)
                if top is not None:
                    p.setOpacity(slot.t)
                    p.drawPixmap(r.topLeft(), top)
                    p.setOpacity(1.0)
            p.restore()
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(QColor(255, 255, 255, 30), 1))
            p.drawPath(round_path(r.adjusted(0.5, 0.5, -0.5, -0.5), RADIUS))
        p.end()
