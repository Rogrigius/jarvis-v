"""
Global hotkey management for JARVIS.
"""
import keyboard
import asyncio
from typing import Dict, Callable
from utils.logger import logger
from models.event import Event, EventType

class HotkeyManager:
    """
    Handles registration and execution of global system hotkeys.
    """
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self._hotkeys: Dict[str, str] = {}
        self.main_loop = None

    def setup_hotkeys(self, hotkeys: Dict[str, str], main_loop):
        """
        Registers hotkeys from configuration.
        """
        self._hotkeys = hotkeys
        self.main_loop = main_loop

        try:
            keyboard.unhook_all()
            for action, shortcut in self._hotkeys.items():
                if shortcut:
                    keyboard.add_hotkey(shortcut, lambda a=action: self._handle_hotkey(a))
                    logger.info(f"Hotkey registered: {shortcut} -> {action}")
        except Exception as e:
            logger.error(f"Failed to setup hotkeys: {e}")

    def _handle_hotkey(self, action: str):
        """
        Internal handler that translates hotkey presses to system events.
        """
        logger.info(f"Hotkey triggered: {action}")
        if not self.main_loop:
            return

        if action == "activate":
            # Example: Trigger listening
            pass
        elif action == "stop_tts":
            # Emit event to stop current speech
            asyncio.run_coroutine_threadsafe(
                self.event_bus.emit(Event(EventType.VOICE_END, sender="HotkeyManager")),
                self.main_loop
            )
