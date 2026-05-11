"""
Custom widgets for the JARVIS HUD interface.
"""
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtProperty, QEasingCurve, QRect, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient

class VoiceVisualizer(QWidget):
    """
    A circular HUD-style voice visualizer that pulses.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self._pulse_radius = 0
        self._is_active = False

        self.animation = QPropertyAnimation(self, b"pulse_radius")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(100)
        self.animation.setLoopCount(-1)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    @pyqtProperty(int)
    def pulse_radius(self):
        return self._pulse_radius

    @pulse_radius.setter
    def pulse_radius(self, value):
        self._pulse_radius = value
        self.update()

    def set_active(self, active: bool):
        self._is_active = active
        if active:
            self.animation.start()
        else:
            self.animation.stop()
            self._pulse_radius = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center = self.rect().center()

        # Draw background ring
        pen = QPen(QColor(0, 242, 255, 50))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawEllipse(center, 50, 50)

        # Draw pulsing outer ring
        if self._is_active:
            alpha = 150 - (self._pulse_radius * 1.5)
            pen.setColor(QColor(0, 242, 255, int(alpha)))
            painter.setPen(pen)
            radius = 50 + int(self._pulse_radius / 2)
            painter.drawEllipse(center, radius, radius)

            # Glow effect
            gradient = QRadialGradient(QPointF(center), 80.0)
            gradient.setColorAt(0, QColor(0, 242, 255, 50))
            gradient.setColorAt(1, QColor(0, 242, 255, 0))
            painter.setBrush(gradient)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center, 80, 80)

class HUDPanel(QFrame):
    """
    A styled panel for the HUD interface.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HUDPanel")
