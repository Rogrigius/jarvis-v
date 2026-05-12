"""
Advanced HUD Main Window for JARVIS.
"""
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QStackedWidget, QTextEdit,
                             QSystemTrayIcon, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QAction
from gui.widgets.hud_widgets import VoiceVisualizer, HUDPanel
from gui.windows.command_editor import CommandEditorWindow
from gui.windows.settings_window import SettingsWindow
from utils.logger import logger

class GuiSignals(QObject):
    update_log = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    listening_started = pyqtSignal()
    listening_stopped = pyqtSignal()

class FuturisticMainWindow(QMainWindow):
    def __init__(self, event_bus, db_manager, command_manager, settings_manager):
        super().__init__()
        self.event_bus = event_bus
        self.db_manager = db_manager
        self.command_manager = command_manager
        self.settings_manager = settings_manager
        self.signals = GuiSignals()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.init_ui()
        self.setup_tray()
        self.load_styles()
        self.connect_signals()

    def init_ui(self):
        self.resize(1000, 700)

        # Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.home_btn = self.create_nav_button("ГЛАВНАЯ", True)
        self.editor_btn = self.create_nav_button("КОМАНДЫ")
        self.logs_btn = self.create_nav_button("ЛОГИ")
        self.settings_btn = self.create_nav_button("НАСТРОЙКИ")

        self.sidebar_layout.addWidget(self.home_btn)
        self.sidebar_layout.addWidget(self.editor_btn)
        self.sidebar_layout.addWidget(self.logs_btn)
        self.sidebar_layout.addWidget(self.settings_btn)

        self.main_layout.addWidget(self.sidebar)

        # Content Area
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("ContentArea")

        # HUD Page
        self.hud_page = QWidget()
        self.hud_layout = QVBoxLayout(self.hud_page)

        self.status_label = QLabel("СИСТЕМА ГОТОВА")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.visualizer = VoiceVisualizer()

        self.hud_layout.addStretch()
        self.hud_layout.addWidget(self.status_label)
        self.hud_layout.addWidget(self.visualizer, alignment=Qt.AlignmentFlag.AlignCenter)
        self.hud_layout.addStretch()

        # Logs Page
        self.logs_page = QWidget()
        self.logs_layout = QVBoxLayout(self.logs_page)
        self.log_view = QTextEdit()
        self.log_view.setObjectName("LogView")
        self.log_view.setReadOnly(True)
        self.logs_layout.addWidget(QLabel("СИСТЕМНЫЙ ЖУРНАЛ"))
        self.logs_layout.addWidget(self.log_view)

        # Editor Page
        self.editor_page = CommandEditorWindow(self.db_manager, self.command_manager)

        # Settings Page
        self.settings_page = SettingsWindow(self.settings_manager)

        self.content_stack.addWidget(self.hud_page)
        self.content_stack.addWidget(self.editor_page)
        self.content_stack.addWidget(self.logs_page)
        self.content_stack.addWidget(self.settings_page)

        self.main_layout.addWidget(self.content_stack)

    def create_nav_button(self, text, active=False):
        btn = QPushButton(text)
        btn.setObjectName("SidebarButton")
        btn.setProperty("active", active)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self.handle_nav(btn))
        return btn

    def handle_nav(self, active_btn):
        buttons = [self.home_btn, self.editor_btn, self.logs_btn, self.settings_btn]
        for btn in buttons:
            btn.setProperty("active", btn == active_btn)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        index = buttons.index(active_btn)
        self.content_stack.setCurrentIndex(index)

    def load_styles(self):
        try:
            with open("gui/styles/theme.qss", "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            logger.error(f"Failed to load stylesheet: {e}")

    def connect_signals(self):
        self.signals.update_log.connect(self.log_view.append)
        self.signals.status_changed.connect(self.status_label.setText)
        self.signals.listening_started.connect(lambda: self.visualizer.set_active(True))
        self.signals.listening_stopped.connect(lambda: self.visualizer.set_active(False))

    def show_notification(self, title, message):
        self.tray_icon.showMessage(
            title,
            message,
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        # self.tray_icon.setIcon(QIcon("gui/resources/jarvis.png"))

        tray_menu = QMenu()
        show_action = QAction("ОТКРЫТЬ ИНТЕРФЕЙС", self)
        quit_action = QAction("ЗАВЕРШИТЬ РАБОТУ", self)

        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(sys.exit)

        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()
