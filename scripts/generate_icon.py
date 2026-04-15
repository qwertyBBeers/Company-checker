from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QGuiApplication, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap, QColor


ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "assets"
ICON_PNG = ASSETS_DIR / "company_tracker.png"
ICON_ICO = ASSETS_DIR / "company_tracker.ico"


def rounded_path(rect: QRectF, radius: float) -> QPainterPath:
    path = QPainterPath()
    path.addRoundedRect(rect, radius, radius)
    return path


def render_icon(size: int = 256) -> QImage:
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)

    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    canvas = QRectF(10, 10, size - 20, size - 20)
    card = QRectF(24, 26, size - 48, size - 52)
    badge = QRectF(size - 92, 24, 52, 52)
    line1 = QRectF(42, 58, size - 120, 24)
    line2 = QRectF(42, 104, size - 76, 24)
    line3 = QRectF(42, 146, size - 108, 18)
    dot = QRectF(42, 188, 24, 24)
    timer = QRectF(82, 185, size - 120, 26)

    bg = QLinearGradient(0, 0, size, size)
    bg.setColorAt(0.0, QColor("#EEF2F8"))
    bg.setColorAt(1.0, QColor("#C8D4E4"))
    painter.fillPath(rounded_path(canvas, 56), bg)

    glass = QLinearGradient(card.topLeft(), card.bottomRight())
    glass.setColorAt(0.0, QColor(255, 255, 255, 196))
    glass.setColorAt(1.0, QColor(255, 255, 255, 118))
    painter.fillPath(rounded_path(card, 34), glass)
    painter.setPen(QPen(QColor(255, 255, 255, 190), 3))
    painter.drawPath(rounded_path(card, 34))

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#24344C"))
    painter.drawRoundedRect(line1, 10, 10)
    painter.drawRoundedRect(line2, 10, 10)
    painter.setBrush(QColor(36, 52, 76, 170))
    painter.drawRoundedRect(line3, 9, 9)

    accent = QLinearGradient(badge.topLeft(), badge.bottomRight())
    accent.setColorAt(0.0, QColor("#67B8FF"))
    accent.setColorAt(1.0, QColor("#2F80E7"))
    painter.setBrush(accent)
    painter.drawRoundedRect(badge, 18, 18)

    painter.setPen(QPen(QColor(255, 255, 255, 245), 5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    painter.drawLine(QPointF(badge.left() + 15, badge.center().y() + 2), QPointF(badge.left() + 24, badge.bottom() - 16))
    painter.drawLine(QPointF(badge.left() + 24, badge.bottom() - 16), QPointF(badge.right() - 12, badge.top() + 14))

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#3699FF"))
    painter.drawEllipse(dot)
    painter.drawRoundedRect(timer, 10, 10)

    painter.end()
    return image


def main() -> int:
    app = QGuiApplication(sys.argv)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    image = render_icon()
    png_ok = image.save(str(ICON_PNG))
    ico_ok = QPixmap.fromImage(image).save(str(ICON_ICO), "ICO")

    if not png_ok or not ico_ok:
        print("Failed to generate icon files.", file=sys.stderr)
        return 1

    print(f"Generated: {ICON_PNG}")
    print(f"Generated: {ICON_ICO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
