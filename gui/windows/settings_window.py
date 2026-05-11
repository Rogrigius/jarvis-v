"""
Comprehensive Settings Window for JARVIS.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QComboBox, QSlider,
                             QScrollArea, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt

class SettingsWindow(QWidget):
    """
    GUI for managing all JARVIS application settings.
    """
    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        scroll = QScrollArea()
        container = QWidget()
        form = QFormLayout(container)

        # Voice Settings
        voice_group = QGroupBox("VOICE & TTS")
        voice_form = QFormLayout()
        self.voice_name = QLineEdit(self.settings_manager.get("voice_name"))
        voice_form.addRow("Voice Name:", self.voice_name)
        voice_group.setLayout(voice_form)
        form.addRow(voice_group)

        # STT Settings
        stt_group = QGroupBox("SPEECH RECOGNITION")
        stt_form = QFormLayout()
        self.wake_words = QLineEdit(", ".join(self.settings_manager.get("stt_wake_words")))
        stt_form.addRow("Wake Words:", self.wake_words)
        self.model_path = QLineEdit(self.settings_manager.get("stt_model_path"))
        stt_form.addRow("Model Path:", self.model_path)
        stt_group.setLayout(stt_form)
        form.addRow(stt_group)

        # General Settings
        gen_group = QGroupBox("SYSTEM")
        gen_form = QFormLayout()
        self.app_name = QLineEdit(self.settings_manager.get("name"))
        gen_form.addRow("Assistant Name:", self.app_name)
        gen_group.setLayout(gen_form)
        form.addRow(gen_group)

        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        self.layout.addWidget(scroll)

        self.save_btn = QPushButton("APPLY SETTINGS")
        self.save_btn.clicked.connect(self.save_settings)
        self.layout.addWidget(self.save_btn)

    def save_settings(self):
        self.settings_manager.set("voice_name", self.voice_name.text())
        self.settings_manager.set("stt_wake_words", [w.strip() for w in self.wake_words.text().split(",")])
        self.settings_manager.set("stt_model_path", self.model_path.text())
        self.settings_manager.set("name", self.app_name.text())

        # Notifications could be shown here
        print("Settings saved and applied")
