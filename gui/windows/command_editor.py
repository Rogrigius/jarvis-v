"""
Visual Command Editor for JARVIS - Simple "No-Code" Version.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QListWidget, QComboBox,
                             QScrollArea, QFrame, QMessageBox, QStackedWidget)
from PyQt6.QtCore import Qt
from models.custom_command import CustomCommand, Action, ActionType
import json

class ActionWidget(QFrame):
    """
    Интерактивный виджет для настройки действия без ручного ввода JSON.
    """
    def __init__(self, action_type=None, params=None, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("background-color: rgba(0, 242, 255, 10); margin-bottom: 5px;")
        self.layout = QVBoxLayout(self)

        # Заголовок и выбор типа
        self.header = QHBoxLayout()
        self.type_combo = QComboBox()
        self.type_map = {
            ActionType.LAUNCH_APP: "Запустить программу",
            ActionType.OPEN_URL: "Открыть сайт",
            ActionType.TTS_RESPONSE: "Ответить голосом",
            ActionType.EXECUTE_SCRIPT: "Выполнить скрипт (Python)",
            ActionType.PLAY_AUDIO: "Проиграть звук"
        }
        for atype, label in self.type_map.items():
            self.type_combo.addItem(label, atype.value)

        self.remove_btn = QPushButton("✕")
        self.remove_btn.setObjectName("ActionRemoveBtn")
        self.remove_btn.setFixedWidth(40)
        self.remove_btn.clicked.connect(lambda: self.setParent(None))

        self.header.addWidget(QLabel("Действие:"))
        self.header.addWidget(self.type_combo, 1)
        self.header.addWidget(self.remove_btn)
        self.layout.addLayout(self.header)

        # Панель параметров (динамическая)
        self.param_stack = QStackedWidget()

        # 1. Поле для пути (LAUNCH_APP, PLAY_AUDIO)
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Введите полный путь к файлу или программе")

        # 2. Поле для URL (OPEN_URL)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Введите адрес сайта (https://...)")

        # 3. Поле для текста (TTS_RESPONSE)
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Что должен сказать ассистент?")

        # 4. Поле для скрипта (EXECUTE_SCRIPT)
        self.script_input = QLineEdit()
        self.script_input.setPlaceholderText("Python код...")

        self.param_stack.addWidget(self.path_input)   # Index 0
        self.param_stack.addWidget(self.url_input)    # Index 1
        self.param_stack.addWidget(self.text_input)   # Index 2
        self.param_stack.addWidget(self.script_input) # Index 3

        self.layout.addWidget(self.param_stack)

        self.type_combo.currentIndexChanged.connect(self.update_param_view)

        # Установка начальных значений
        if action_type:
            index = self.type_combo.findData(action_type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
            self.set_params(action_type, params)
        else:
            self.update_param_view()

    def update_param_view(self):
        atype = self.type_combo.currentData()
        if atype in [ActionType.LAUNCH_APP, ActionType.PLAY_AUDIO]:
            self.param_stack.setCurrentIndex(0)
        elif atype == ActionType.OPEN_URL:
            self.param_stack.setCurrentIndex(1)
        elif atype == ActionType.TTS_RESPONSE:
            self.param_stack.setCurrentIndex(2)
        elif atype == ActionType.EXECUTE_SCRIPT:
            self.param_stack.setCurrentIndex(3)

    def set_params(self, atype, params):
        if not params: return
        if atype in [ActionType.LAUNCH_APP, ActionType.PLAY_AUDIO]:
            self.path_input.setText(params.get("path", ""))
        elif atype == ActionType.OPEN_URL:
            self.url_input.setText(params.get("url", ""))
        elif atype == ActionType.TTS_RESPONSE:
            self.text_input.setText(params.get("text", ""))
        elif atype == ActionType.EXECUTE_SCRIPT:
            self.script_input.setText(params.get("script", ""))

    def get_data(self) -> dict:
        atype = self.type_combo.currentData()
        params = {}
        if atype in [ActionType.LAUNCH_APP, ActionType.PLAY_AUDIO]:
            params["path"] = self.path_input.text()
        elif atype == ActionType.OPEN_URL:
            params["url"] = self.url_input.text()
        elif atype == ActionType.TTS_RESPONSE:
            params["text"] = self.text_input.text()
        elif atype == ActionType.EXECUTE_SCRIPT:
            params["script"] = self.script_input.text()
        return {"type": atype, "params": params}

class CommandEditorWindow(QWidget):
    """
    GUI для простого создания и редактирования голосовых команд.
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

        # Левая панель
        self.left_panel = QVBoxLayout()
        self.cmd_list = QListWidget()
        self.cmd_list.itemClicked.connect(self.load_command)

        self.add_btn = QPushButton("+ НОВАЯ КОМАНДА")
        self.add_btn.clicked.connect(self.new_command)

        self.left_panel.addWidget(QLabel("ВАШИ КОМАНДЫ"))
        self.left_panel.addWidget(self.cmd_list)
        self.left_panel.addWidget(self.add_btn)

        # Правая панель
        self.editor_panel = QVBoxLayout()
        self.editor_card = QFrame()
        self.editor_card.setObjectName("EditorCard")
        self.card_layout = QVBoxLayout(self.editor_card)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Название команды")

        self.trigger_input = QLineEdit()
        self.trigger_input.setPlaceholderText("Слова-триггеры через запятую")

        self.actions_area = QScrollArea()
        self.actions_container = QWidget()
        self.actions_layout = QVBoxLayout(self.actions_container)
        self.actions_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.actions_area.setWidget(self.actions_container)
        self.actions_area.setWidgetResizable(True)

        self.add_action_btn = QPushButton("+ ДОБАВИТЬ ДЕЙСТВИЕ")
        self.add_action_btn.clicked.connect(lambda: self.add_action_ui())

        self.save_btn = QPushButton("СОХРАНИТЬ")
        self.save_btn.clicked.connect(self.save_command)

        self.card_layout.addWidget(QLabel("НАЗВАНИЕ"))
        self.card_layout.addWidget(self.name_input)
        self.card_layout.addWidget(QLabel("ФРАЗЫ (КАК ВЫ ГОВОРИТЕ)"))
        self.card_layout.addWidget(self.trigger_input)
        self.card_layout.addWidget(QLabel("ЧТО СДЕЛАТЬ (ПО ПОРЯДКУ)"))
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
        widget = ActionWidget(action_type, params)
        self.actions_layout.addWidget(widget)

    def clear_actions(self):
        for i in reversed(range(self.actions_layout.count())):
            item = self.actions_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

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
            QMessageBox.warning(self, "Ошибка", "Укажите название команды")
            return

        triggers = [t.strip() for t in self.trigger_input.text().split(",") if t.strip()]

        actions = []
        for i in range(self.actions_layout.count()):
            widget = self.actions_layout.itemAt(i).widget()
            if isinstance(widget, ActionWidget):
                actions.append(widget.get_data())

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
        QMessageBox.information(self, "Готово", "Команда сохранена")
