"""
Enhanced Command Manager with dynamic database-backed commands.
"""
import json
from typing import Dict, List, Optional
from models.command import Command
from models.custom_command import CustomCommand, Action
from utils.logger import logger

class EnhancedCommandManager:
    """
    Manages both hardcoded and user-defined custom commands.
    """
    def __init__(self, db_manager, action_engine):
        self.db_manager = db_manager
        self.action_engine = action_engine
        self._hardcoded_commands: Dict[str, Command] = {}
        self._custom_commands: List[CustomCommand] = []
        self.load_custom_commands()

    def register_command(self, command: Command):
        """Compatibility method for the original CommandManager interface."""
        self.register_hardcoded_command(command)

    def register_hardcoded_command(self, command: Command):
        self._hardcoded_commands[command.name.lower()] = command
        logger.info(f"Hardcoded command registered: {command.name}")

    def load_custom_commands(self):
        """Loads user-defined commands from the database."""
        logger.info("Loading custom commands from database...")
        self._custom_commands = []
        results = self.db_manager.execute("SELECT id, name, category, data, enabled FROM custom_commands")
        if results:
            for row in results:
                id, name, category, data_str, enabled = row
                data = json.loads(data_str)

                # Convert dict data back to CustomCommand object
                cmd = CustomCommand(
                    id=id,
                    name=name,
                    category=category,
                    trigger_phrases=data.get("trigger_phrases", []),
                    enabled=bool(enabled)
                )
                for act_data in data.get("actions", []):
                    cmd.actions.append(Action(type=act_data["type"], params=act_data.get("params", {})))

                self._custom_commands.append(cmd)
        logger.info(f"Loaded {len(self._custom_commands)} custom commands")

    async def execute_command(self, text: str):
        text = text.lower()

        # 1. Check hardcoded commands first
        for cmd in self._hardcoded_commands.values():
            if cmd.name.lower() in text or any(kw.lower() in text for kw in cmd.keywords):
                logger.info(f"Executing hardcoded command: {cmd.name}")
                if cmd.is_async:
                    await cmd.callback(text)
                else:
                    cmd.callback(text)
                return

        # 2. Check custom commands
        for cmd in self._custom_commands:
            if not cmd.enabled:
                continue

            for phrase in cmd.trigger_phrases:
                if phrase.lower() in text:
                    logger.info(f"Executing custom command: {cmd.name}")
                    await self.action_engine.execute_sequence(cmd.actions)
                    return

        logger.warning(f"No command found for: {text}")

    def reload(self):
        """Hot-reloads custom commands."""
        self.load_custom_commands()
