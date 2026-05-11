"""
Animation helpers for smooth UI transitions.
"""
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPoint

def fade_in(widget, duration=500):
    anim = QPropertyAnimation(widget, b"windowOpacity")
    anim.setDuration(duration)
    anim.setStartValue(0)
    anim.setEndValue(1)
    anim.start()
    return anim

def slide_widget(widget, start_pos, end_pos, duration=300):
    anim = QPropertyAnimation(widget, b"pos")
    anim.setDuration(duration)
    anim.setStartValue(start_pos)
    anim.setEndValue(end_pos)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start()
    return anim
