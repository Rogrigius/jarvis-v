import sys
from PyQt6.QtWidgets import (QMainWindow, QSystemTrayIcon, QMenu,
                             QVBoxLayout, QWidget, QTextEdit, QLabel)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import pyqtSignal, QObject
from models.event import Event, EventType
from utils.logger import logger

class GuiSignals(QObject):
    update_log = pyqtSignal(str)
    status_changed = pyqtSignal(str)

class MainWindow(QMainWindow):
    def __init__(self, event_bus):
        super().__init__()
        self.event_bus = event_bus
        self.signals = GuiSignals()

        self.init_ui()
        self.setup_tray()

        self.signals.update_log.connect(self.append_log)
        self.signals.status_changed.connect(self.update_status)

    def init_ui(self):
        self.setWindowTitle("JARVIS Assistant")
        self.resize(600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.status_label = QLabel("Status: Idle")
        layout.addWidget(self.status_label)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view)

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        # In a real app, you'd use a proper icon file from assets/
        # self.tray_icon.setIcon(QIcon("assets/icon.png"))

        tray_menu = QMenu()
        show_action = QAction("Show", self)
        quit_action = QAction("Quit", self)

        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(self.close_app)

        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def append_log(self, text: str):
        self.log_view.append(text)

    def update_status(self, status: str):
        self.status_label.setText(f"Status: {status}")

    def close_app(self):
        # Trigger shutdown event
        # self.event_bus.emit(Event(EventType.SHUTDOWN))
        sys.exit()

    def closeEvent(self, event):
        # Minimize to tray instead of closing
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "JARVIS",
            "Application minimized to tray",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
