"""
Command management system for JARVIS.
"""
from typing import Dict, List, Optional
from models.command import Command
from utils.logger import logger

class CommandManager:
    """
    Registers and dispatches commands to their respective callbacks.
    """
    def __init__(self):
        self._commands: Dict[str, Command] = {}

    def register_command(self, command: Command):
        """
        Register a new command with the system.

        Args:
            command: The command object containing metadata and callback.
        """
        self._commands[command.name.lower()] = command
        logger.info(f"Command registered: {command.name}")

    def find_command(self, text: str) -> Optional[Command]:
        """
        Attempt to find a command that matches the provided text.

        Args:
            text: The input string from the user.

        Returns:
            The matching Command object or None if no match is found.
        """
        text = text.lower()
        # Basic keyword matching. In production, this might use NLP.
        for cmd in self._commands.values():
            if cmd.name.lower() in text or any(kw.lower() in text for kw in cmd.keywords):
                return cmd
        return None

    async def execute_command(self, text: str):
        """
        Find and execute a command based on input text.

        Args:
            text: The raw input text.
        """
        cmd = self.find_command(text)
        if cmd:
            logger.info(f"Executing command: {cmd.name}")
            try:
                if cmd.is_async:
                    await cmd.callback(text)
                else:
                    cmd.callback(text)
            except Exception as e:
                logger.error(f"Error executing command {cmd.name}: {e}")
        else:
            logger.warning(f"No command found for: {text}")

    def get_all_commands(self) -> List[Command]:
        """Returns a list of all registered commands."""
        return list(self._commands.values())
