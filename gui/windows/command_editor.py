"""
Visual Command Editor for JARVIS - Russian Localized and Enhanced.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QListWidget, QComboBox,
                             QScrollArea, QFrame, QMessageBox)
from PyQt6.QtCore import Qt
from models.custom_command import CustomCommand, Action, ActionType
import json

class CommandEditorWindow(QWidget):
    """
    GUI для создания и редактирования голосовых команд.
    """
    def __init__(self, db_manager, command_manager):
        super().__init__()
        self.db_manager = db_manager
        self.command_manager = command_manager
        self.init_ui()

    def init_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Левая панель: Список команд
        self.left_panel = QVBoxLayout()
        self.cmd_list = QListWidget()
        self.cmd_list.itemClicked.connect(self.load_command)

        self.add_btn = QPushButton("+ СОЗДАТЬ КОМАНДУ")
        self.add_btn.clicked.connect(self.new_command)

        self.left_panel.addWidget(QLabel("СПИСОК КОМАНД"))
        self.left_panel.addWidget(self.cmd_list)
        self.left_panel.addWidget(self.add_btn)

        # Правая панель: Редактор
        self.editor_panel = QVBoxLayout()
        self.editor_card = QFrame()
        self.editor_card.setObjectName("EditorCard")
        self.card_layout = QVBoxLayout(self.editor_card)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Название команды (например: Вечерний режим)")

        self.trigger_input = QLineEdit()
        self.trigger_input.setPlaceholderText("Фразы-триггеры (через запятую)")

        self.actions_area = QScrollArea()
        self.actions_container = QWidget()
        self.actions_layout = QVBoxLayout(self.actions_container)
        self.actions_area.setWidget(self.actions_container)
        self.actions_area.setWidgetResizable(True)
        self.actions_area.setMinimumHeight(300)

        self.add_action_btn = QPushButton("+ ДОБАВИТЬ ДЕЙСТВИЕ")
        self.add_action_btn.clicked.connect(self.add_action_ui)

        self.save_btn = QPushButton("СОХРАНИТЬ ИЗМЕНЕНИЯ")
        self.save_btn.clicked.connect(self.save_command)

        self.card_layout.addWidget(QLabel("РЕДАКТИРОВАНИЕ"))
        self.card_layout.addWidget(self.name_input)
        self.card_layout.addWidget(QLabel("ФРАЗЫ АКТИВАЦИИ"))
        self.card_layout.addWidget(self.trigger_input)
        self.card_layout.addWidget(QLabel("ЦЕПОЧКА ДЕЙСТВИЙ"))
        self.card_layout.addWidget(self.actions_area)
        self.card_layout.addWidget(self.add_action_btn)
        self.card_layout.addStretch()
        self.card_layout.addWidget(self.save_btn)

        self.editor_panel.addWidget(self.editor_card)

        self.layout.addLayout(self.left_panel, 1)
        self.layout.addLayout(self.editor_panel, 2)

        self.refresh_list()

    def refresh_list(self):
        self.cmd_list.clear()
        results = self.db_manager.execute("SELECT name FROM custom_commands")
        if results:
            for row in results:
                self.cmd_list.addItem(row[0])

    def new_command(self):
        self.name_input.clear()
        self.trigger_input.clear()
        self.clear_actions()
        self.current_cmd_id = None

    def add_action_ui(self, action_type=None, params=None):
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("background-color: rgba(0, 242, 255, 10); margin-bottom: 5px;")
        layout = QHBoxLayout(frame)

        type_combo = QComboBox()
        # Русские названия для типов действий
        type_map = {
            ActionType.LAUNCH_APP: "Запуск программы",
            ActionType.OPEN_URL: "Открыть сайт",
            ActionType.TTS_RESPONSE: "Ответ голосом",
            ActionType.EXECUTE_SCRIPT: "Выполнить скрипт",
            ActionType.PLAY_AUDIO: "Проиграть звук"
        }
        for atype, label in type_map.items():
            type_combo.addItem(label, atype.value)

        if action_type:
            index = type_combo.findData(action_type)
            if index >= 0:
                type_combo.setCurrentIndex(index)

        param_input = QLineEdit()
        if params:
            param_input.setText(json.dumps(params, ensure_ascii=False))
        param_input.setPlaceholderText("Параметры (JSON)")

        remove_btn = QPushButton("✕")
        remove_btn.setObjectName("ActionRemoveBtn")
        remove_btn.setFixedWidth(40)
        remove_btn.clicked.connect(lambda: frame.deleteLater())

        layout.addWidget(type_combo, 1)
        layout.addWidget(param_input, 2)
        layout.addWidget(remove_btn)

        self.actions_layout.insertWidget(self.actions_layout.count(), frame)

    def clear_actions(self):
        for i in reversed(range(self.actions_layout.count())):
            self.actions_layout.itemAt(i).widget().setParent(None)

    def load_command(self, item):
        name = item.text()
        result = self.db_manager.execute(
            "SELECT id, name, data FROM custom_commands WHERE name=?", (name,)
        )
        if result:
            id, name, data_str = result[0]
            data = json.loads(data_str)
            self.current_cmd_id = id
            self.name_input.setText(name)
            self.trigger_input.setText(", ".join(data.get("trigger_phrases", [])))

            self.clear_actions()
            for act in data.get("actions", []):
                self.add_action_ui(act["type"], act.get("params", {}))

    def save_command(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название команды")
            return

        triggers = [t.strip() for t in self.trigger_input.text().split(",") if t.strip()]

        actions = []
        for i in range(self.actions_layout.count()):
            widget = self.actions_layout.itemAt(i).widget()
            if not widget: continue

            type_combo = widget.findChild(QComboBox)
            param_input = widget.findChild(QLineEdit)

            try:
                params = json.loads(param_input.text()) if param_input.text() else {}
                actions.append({"type": type_combo.currentData(), "params": params})
            except:
                QMessageBox.warning(self, "Ошибка", f"Некорректный JSON в действии {i+1}")
                return

        data = {"trigger_phrases": triggers, "actions": actions}
        data_str = json.dumps(data, ensure_ascii=False)

        if hasattr(self, 'current_cmd_id') and self.current_cmd_id:
            self.db_manager.execute(
                "UPDATE custom_commands SET name=?, data=? WHERE id=?",
                (name, data_str, self.current_cmd_id)
            )
        else:
            self.db_manager.execute(
                "INSERT INTO custom_commands (name, category, data) VALUES (?, ?, ?)",
                (name, "Общие", data_str)
            )

        self.refresh_list()
        self.command_manager.reload()
        QMessageBox.information(self, "Успех", "Команда сохранена и готова к использованию")
