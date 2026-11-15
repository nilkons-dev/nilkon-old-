"""Header of a playlist / collection page (Spotify style): big cover, name, size, big play button, extra buttons.
Playlists can carry a picture of the user's own; without one the first song covers form a 2 x 2 mosaic."""
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QPainter, QFont, QFontMetrics, QPen, QColor, QLinearGradient, QBrush, QPainterPath
from PySide6.QtWidgets import QWidget, QLineEdit

from icons import draw_icon, qicon
from theme import T, alpha, ink, hsv, hue_for
from widgets import ui_font, round_path, NOPEN, NOBRUSH, AA

HERO_H = 232
COVER = 176
PAD = 24


class CollectionHero(QWidget):
    playClicked = Signal()
    shuffleClicked = Signal()
    coverClicked = Signal()
    shareClicked = Signal()
    menuClicked = Signal()
    sortClicked = Signal(object)
    renameClicked = Signal()
    searchChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(HERO_H)
        self.setMouseTracking(True)
        self.kind = "all"
        self.title = ""
        self.meta = ""
        self.custom = None
        self.mosaic = []
        self.can_edit = False
        self.can_play = False
        self.tint = None
        self.sort_label = ""
        self._hover = ""
        self.f_eye = ui_font(11, QFont.Weight.Bold)
        self.f_meta = ui_font(13, QFont.Weight.Normal)
        self._search_open = False
        self.field = QLineEdit(self)
        self.field.setPlaceholderText("Search in this list")
        self.field.setClearButtonEnabled(True)
        self.field.hide()
        self.field.textChanged.connect(self.searchChanged)
        self.field.editingFinished.connect(self._field_done)
        self._field_action = None
        self._style_field()

    # -- inline search (like Spotify: a magnifier next to the sort button opens a small field) ---------------
    def _style_field(self):
        self.field.setStyleSheet(
            "QLineEdit { background: %s; border: 1px solid %s; border-radius: 18px; padding: 0 12px 0 4px; "
            "color: %s; font-size: 13px; selection-background-color: %s; }"
            "QLineEdit:focus { border: 1px solid %s; }" % (
                ink(0.08).name(QColor.NameFormat.HexArgb), ink(0.16).name(QColor.NameFormat.HexArgb),
                ink(0.95).name(QColor.NameFormat.HexArgb), alpha(T.c1, 0.5).name(QColor.NameFormat.HexArgb),
                alpha(T.c1, 0.8).name(QColor.NameFormat.HexArgb)))
        if self._field_action is not None:
            self.field.removeAction(self._field_action)
        self._field_action = self.field.addAction(qicon("search", ink(0.6), 16), QLineEdit.ActionPosition.LeadingPosition)

    def _field_done(self):
        if not self.field.text().strip():
            self.close_search()

    def open_search(self):
        self._search_open = True
        self._place_field()
        self.field.show()
        self.field.setFocus()
        self.update()

    def close_search(self):
        if not self._search_open:
            return
        self._search_open = False
        if self.field.text():
            self.field.blockSignals(True)
            self.field.clear()
            self.field.blockSignals(False)
            self.searchChanged.emit("")
        self.field.hide()
        self.update()

    def set_search_text(self, text):
        """Shows `text` in the field without announcing it (used when the page changes)."""
        self.field.blockSignals(True)
        self.field.setText(text)
        self.field.blockSignals(False)
        if text:
            self._search_open = True
            self._place_field()
            self.field.show()
        elif self._search_open:
            self._search_open = False
            self.field.hide()
        self.update()

    def _place_field(self):
        b = self._buttons()
        right = b["sort"].left() - 8 if "sort" in b else float(self.width()) - PAD
        y = (b["sort"].top() if "sort" in b else self.cover_rect().bottom() - 46)
        wd = max(120.0, min(260.0, right - (self.cover_rect().right() + 28 + 56 + 14 + 40 * 3 + 40)))
        self.field.setGeometry(int(right - wd), int(y), int(wd), 36)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self._search_open:
            self._place_field()

    def refresh_theme(self):
        self._style_field()

    # -- data ---------------------------------------------------------------------------------------------
    def set_content(self, kind, title, meta, custom=None, mosaic=(), can_edit=False, can_play=True, tint=None, sort_label=""):
        self.kind, self.title, self.meta = kind, title, meta
        self.custom, self.mosaic = custom, [m for m in mosaic if m is not None and not m.isNull()][:4]
        self.can_edit, self.can_play, self.tint = can_edit, can_play, tint
        self.sort_label = sort_label
        if self._search_open:
            self._place_field()
        self.update()

    # -- geometry -----------------------------------------------------------------------------------------
    def cover_rect(self):
        return QRectF(PAD, (HERO_H - COVER) / 2.0 + 4, COVER, COVER)

    def _buttons(self):
        c = self.cover_rect()
        x = c.right() + 28
        y = c.bottom() - 56
        out = {"play": QRectF(x, y, 56, 56)}
        x += 56 + 14
        out["shuffle"] = QRectF(x, y + 8, 40, 40)
        x += 40 + 6
        if self.can_edit:
            out["cover"] = QRectF(x, y + 8, 40, 40)
            x += 40 + 6
            out["rename"] = QRectF(x, y + 8, 40, 40)
            x += 40 + 6
            out["share"] = QRectF(x, y + 8, 40, 40)
            x += 40 + 6
        right = float(self.width()) - PAD
        if self.sort_label:
            fm = QFontMetrics(self.f_meta)
            wd = fm.horizontalAdvance(self.sort_label) + 44
            out["sort"] = QRectF(right - wd, y + 10, wd, 36)
            right -= wd + 6
        if not self._search_open:
            out["search"] = QRectF(right - 36, y + 10, 36, 36)
        return out

    def _zone(self, pos):
        for k, r in self._buttons().items():
            if r.contains(pos):
                return k
        if self.can_edit and self.cover_rect().contains(pos):
            return "cover"
        return ""

    # -- mouse --------------------------------------------------------------------------------------------
    def mouseMoveEvent(self, e):
        z = self._zone(e.position())
        if z != self._hover:
            self._hover = z
            self.setCursor(Qt.CursorShape.PointingHandCursor if z else Qt.CursorShape.ArrowCursor)
            self.update()

    def leaveEvent(self, e):
        self._hover = ""
        self.unsetCursor()
        self.update()

    def mousePressEvent(self, e):
        if e.button() != Qt.MouseButton.LeftButton:
            return
        z = self._zone(e.position())
        if z == "play" and self.can_play:
            self.playClicked.emit()
        elif z == "shuffle" and self.can_play:
            self.shuffleClicked.emit()
        elif z == "cover":
            self.coverClicked.emit()
        elif z == "share":
            self.shareClicked.emit()
        elif z == "rename":
            self.renameClicked.emit()
        elif z == "search":
            self.open_search()
        elif z == "sort":
            r = self._buttons()["sort"]
            self.sortClicked.emit(self.mapToGlobal(QPointF(r.right(), r.bottom()).toPoint()))

    # -- painting -----------------------------------------------------------------------------------------
    def _placeholder(self, p, r):
        if self.kind == "liked":
            g = QLinearGradient(r.topLeft(), r.bottomRight())
            g.setColorAt(0.0, T.c1.lighter(120))
            g.setColorAt(1.0, T.c1.darker(170))
            p.fillRect(r, QBrush(g))
            icon = "heart-fill"
        else:
            h = hue_for(self.title or "x")
            g = QLinearGradient(r.topLeft(), r.bottomRight())
            g.setColorAt(0.0, hsv(h, 0.62, 0.70 if T.dark else 0.90))
            g.setColorAt(1.0, hsv(h + 0.07, 0.75, 0.30 if T.dark else 0.68))
            p.fillRect(r, QBrush(g))
            icon = {"recent": "history", "all": "library"}.get(self.kind, "list-music")
        isz = r.width() * 0.34
        draw_icon(p, icon, QRectF(r.center().x() - isz / 2, r.center().y() - isz / 2, isz, isz), QColor(255, 255, 255, 215))

    @staticmethod
    def _draw_square(p, pm, r):
        s = min(pm.width(), pm.height())
        src = QRectF((pm.width() - s) / 2.0, (pm.height() - s) / 2.0, s, s)
        p.drawPixmap(r, pm, src)

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(AA)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        w, h = float(self.width()), float(self.height())
        # soft colour wash that fades out downwards
        base = self.tint or T.c1
        g = QLinearGradient(0, 0, 0, h)
        g.setColorAt(0.0, alpha(base, 0.42 if T.dark else 0.30))
        g.setColorAt(1.0, alpha(base, 0.0))
        p.setPen(NOPEN)
        p.setBrush(QBrush(g))
        p.drawPath(round_path(QRectF(0, 0, w, h), 20))
        # cover with a soft shadow
        c = self.cover_rect()
        for i in range(6, 0, -1):
            p.setBrush(QColor(0, 0, 0, 12))
            p.drawPath(round_path(c.adjusted(-i * 1.5, -i * 0.5, i * 1.5, i * 2.5), 16 + i))
        clip = round_path(c, 14)
        p.save()
        p.setClipPath(clip)
        if self.custom is not None and not self.custom.isNull():
            self._draw_square(p, self.custom, c)
        elif len(self.mosaic) >= 4:
            half = c.width() / 2.0
            for i, pm in enumerate(self.mosaic[:4]):
                self._draw_square(p, pm, QRectF(c.left() + (i % 2) * half, c.top() + (i // 2) * half, half, half))
        elif self.mosaic:
            self._draw_square(p, self.mosaic[0], c)
        else:
            self._placeholder(p, c)
        if self.can_edit and self._hover == "cover":
            p.fillRect(c, QColor(0, 0, 0, 150))
            draw_icon(p, "image", QRectF(c.center().x() - 16, c.center().y() - 26, 32, 32), QColor(255, 255, 255))
            p.setFont(ui_font(12, QFont.Weight.DemiBold))
            p.setPen(QColor(255, 255, 255))
            p.drawText(QRectF(c.left(), c.center().y() + 12, c.width(), 22), Qt.AlignmentFlag.AlignHCenter, "Choose photo")
        p.restore()
        p.setBrush(NOBRUSH)
        p.setPen(QPen(QColor(255, 255, 255, 40) if T.dark else QColor(12, 20, 44, 40), 1))
        p.drawPath(round_path(c.adjusted(0.5, 0.5, -0.5, -0.5), 14))
        # texts
        x = c.right() + 28
        tw = max(40.0, w - x - PAD)
        p.setFont(self.f_eye)
        f = QFont(self.f_eye)
        f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2.0)
        p.setFont(f)
        p.setPen(ink(0.62))
        label = {"playlist": "PLAYLIST", "liked": "PLAYLIST", "recent": "HISTORY", "all": "LIBRARY"}.get(self.kind, "PLAYLIST")
        p.drawText(QPointF(x, c.top() + 20), label)
        size = 46
        while size > 24:
            tf = ui_font(size, QFont.Weight.Black)
            if QFontMetrics(tf).horizontalAdvance(self.title) <= tw:
                break
            size -= 2
        tf = ui_font(size, QFont.Weight.Black)
        fm = QFontMetrics(tf)
        p.setFont(tf)
        p.setPen(ink(0.98))
        p.drawText(QPointF(x, c.top() + 24 + fm.ascent() + 4), fm.elidedText(self.title, Qt.TextElideMode.ElideRight, int(tw)))
        p.setFont(self.f_meta)
        p.setPen(ink(0.62))
        fm2 = QFontMetrics(self.f_meta)
        p.drawText(QPointF(x, c.top() + 24 + fm.height() + 24), fm2.elidedText(self.meta, Qt.TextElideMode.ElideRight, int(tw)))
        # buttons
        for key, r in self._buttons().items():
            hov = self._hover == key
            dis = key in ("play", "shuffle") and not self.can_play
            if key == "play":
                p.setPen(NOPEN)
                p.setBrush(alpha(T.c1, 0.35) if dis else T.c1.lighter(112 if hov else 100))
                rr = r.adjusted(-2, -2, 2, 2) if hov and not dis else r
                p.drawEllipse(rr)
                draw_icon(p, "play", QRectF(r.center().x() - 12 + 2, r.center().y() - 12, 24, 24), T.on_accent)
            elif key == "sort":
                if hov:
                    p.setPen(NOPEN)
                    p.setBrush(ink(0.08))
                    p.drawRoundedRect(r, 18, 18)
                p.setFont(self.f_meta)
                p.setPen(ink(0.95 if hov else 0.72))
                fm3 = QFontMetrics(self.f_meta)
                p.drawText(QPointF(r.left() + 16, r.center().y() + (fm3.ascent() - fm3.descent()) / 2.0), self.sort_label)
                tx = r.right() - 20
                p.setBrush(ink(0.72))
                p.setPen(NOPEN)
                tri = QPainterPath()
                tri.moveTo(tx - 4, r.center().y() - 2)
                tri.lineTo(tx + 4, r.center().y() - 2)
                tri.lineTo(tx, r.center().y() + 3)
                tri.closeSubpath()
                p.drawPath(tri)
            else:
                if hov and not dis:
                    p.setPen(NOPEN)
                    p.setBrush(ink(0.10))
                    p.drawEllipse(r)
                icon = {"shuffle": "shuffle", "cover": "image", "share": "link", "rename": "pen", "search": "search"}[key]
                draw_icon(p, icon, QRectF(r.center().x() - 12, r.center().y() - 12, 24, 24),
                          ink(0.28 if dis else (1.0 if hov else 0.72)))
        p.end()
