"""
Visual Command Editor for JARVIS.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QListWidget, QComboBox,
                             QScrollArea, QFrame, QMessageBox)
from PyQt6.QtCore import Qt
from models.custom_command import CustomCommand, Action, ActionType
import json

class CommandEditorWindow(QWidget):
    """
    GUI for creating and editing voice commands and their action chains.
    """
    def __init__(self, db_manager, command_manager):
        super().__init__()
        self.db_manager = db_manager
        self.command_manager = command_manager
        self.init_ui()

    def init_ui(self):
        self.layout = QHBoxLayout(self)

        # Left Side: Command List
        self.left_panel = QVBoxLayout()
        self.cmd_list = QListWidget()
        self.cmd_list.itemClicked.connect(self.load_command)

        self.add_btn = QPushButton("NEW COMMAND")
        self.add_btn.clicked.connect(self.new_command)

        self.left_panel.addWidget(QLabel("COMMANDS"))
        self.left_panel.addWidget(self.cmd_list)
        self.left_panel.addWidget(self.add_btn)

        # Right Side: Editor
        self.editor_panel = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Command Name")

        self.trigger_input = QLineEdit()
        self.trigger_input.setPlaceholderText("Trigger Phrases (comma separated)")

        self.actions_area = QScrollArea()
        self.actions_container = QWidget()
        self.actions_layout = QVBoxLayout(self.actions_container)
        self.actions_area.setWidget(self.actions_container)
        self.actions_area.setWidgetResizable(True)

        self.add_action_btn = QPushButton("ADD ACTION")
        self.add_action_btn.clicked.connect(self.add_action_ui)

        self.save_btn = QPushButton("SAVE COMMAND")
        self.save_btn.clicked.connect(self.save_command)

        self.editor_panel.addWidget(QLabel("EDIT COMMAND"))
        self.editor_panel.addWidget(self.name_input)
        self.editor_panel.addWidget(self.trigger_input)
        self.editor_panel.addWidget(QLabel("ACTIONS"))
        self.editor_panel.addWidget(self.actions_area)
        self.editor_panel.addWidget(self.add_action_btn)
        self.editor_panel.addWidget(self.save_btn)

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
        layout = QHBoxLayout(frame)

        type_combo = QComboBox()
        type_combo.addItems([t.value for t in ActionType])
        if action_type:
            type_combo.setCurrentText(action_type)

        param_input = QLineEdit()
        if params:
            param_input.setText(json.dumps(params))
        param_input.setPlaceholderText("Parameters (JSON)")

        remove_btn = QPushButton("X")
        remove_btn.setFixedWidth(30)
        remove_btn.clicked.connect(lambda: frame.deleteLater())

        layout.addWidget(type_combo)
        layout.addWidget(param_input)
        layout.addWidget(remove_btn)

        self.actions_layout.addWidget(frame)

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
        name = self.name_input.text()
        triggers = [t.strip() for t in self.trigger_input.text().split(",")]

        actions = []
        for i in range(self.actions_layout.count()):
            frame = self.actions_layout.itemAt(i).widget()
            type_combo = frame.findChild(QComboBox)
            param_input = frame.findChild(QLineEdit)

            try:
                params = json.loads(param_input.text()) if param_input.text() else {}
                actions.append({"type": type_combo.currentText(), "params": params})
            except:
                QMessageBox.warning(self, "Error", f"Invalid JSON in action {i+1}")
                return

        data = {"trigger_phrases": triggers, "actions": actions}
        data_str = json.dumps(data)

        if hasattr(self, 'current_cmd_id') and self.current_cmd_id:
            self.db_manager.execute(
                "UPDATE custom_commands SET name=?, data=? WHERE id=?",
                (name, data_str, self.current_cmd_id)
            )
        else:
            self.db_manager.execute(
                "INSERT INTO custom_commands (name, category, data) VALUES (?, ?, ?)",
                (name, "General", data_str)
            )

        self.refresh_list()
        self.command_manager.reload()
        QMessageBox.information(self, "Success", "Command saved and reloaded")
