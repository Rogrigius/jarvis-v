"""
Comprehensive Settings Window for JARVIS - Russian Localized.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QComboBox, QSlider,
                             QScrollArea, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt

class SettingsWindow(QWidget):
    """
    GUI для управления всеми настройками ассистента ДЖАРВИС.
    """
    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        form = QFormLayout(container)
        form.setSpacing(15)

        # Настройки голоса
        voice_group = QGroupBox("ГОЛОС И СИНТЕЗ РЕЧИ (TTS)")
        voice_form = QFormLayout()
        self.voice_name = QLineEdit(self.settings_manager.get("voice_name"))
        voice_form.addRow("Имя голоса (Edge-TTS):", self.voice_name)
        voice_group.setLayout(voice_form)
        form.addRow(voice_group)

        # Настройки распознавания
        stt_group = QGroupBox("РАСПОЗНАВАНИЕ РЕЧИ (STT)")
        stt_form = QFormLayout()
        self.wake_words = QLineEdit(", ".join(self.settings_manager.get("stt_wake_words")))
        stt_form.addRow("Слова активации:", self.wake_words)
        self.model_path = QLineEdit(self.settings_manager.get("stt_model_path"))
        stt_form.addRow("Путь к модели (Vosk):", self.model_path)
        stt_group.setLayout(stt_form)
        form.addRow(stt_group)

        # Общие системные настройки
        gen_group = QGroupBox("ОБЩИЕ СИСТЕМНЫЕ НАСТРОЙКИ")
        gen_form = QFormLayout()
        self.app_name = QLineEdit(self.settings_manager.get("name"))
        gen_form.addRow("Имя ассистента:", self.app_name)
        gen_group.setLayout(gen_form)
        form.addRow(gen_group)

        scroll.setWidget(container)
        self.layout.addWidget(scroll)

        self.save_btn = QPushButton("ПРИМЕНИТЬ НАСТРОЙКИ")
        self.save_btn.setFixedHeight(50)
        self.save_btn.clicked.connect(self.save_settings)
        self.layout.addWidget(self.save_btn)

    def save_settings(self):
        self.settings_manager.set("voice_name", self.voice_name.text().strip())
        self.settings_manager.set("stt_wake_words", [w.strip() for w in self.wake_words.text().split(",") if w.strip()])
        self.settings_manager.set("stt_model_path", self.model_path.text().strip())
        self.settings_manager.set("name", self.app_name.text().strip())

        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Успех", "Настройки сохранены и применены.")
