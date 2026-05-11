"""
Execution engine for custom JARVIS actions.
"""
import subprocess
import webbrowser
import os
import asyncio
from typing import List
from models.custom_command import Action, ActionType
from models.event import Event, EventType
from utils.logger import logger

class ActionEngine:
    """
    Executes various types of actions triggered by commands.
    """
    def __init__(self, event_bus):
        self.event_bus = event_bus

    async def execute_action(self, action: Action):
        """
        Executes a single action based on its type.
        """
        logger.info(f"Executing action: {action.type}")
        try:
            if action.type == ActionType.LAUNCH_APP:
                path = action.params.get("path")
                if path:
                    subprocess.Popen(path, shell=True)

            elif action.type == ActionType.OPEN_URL:
                url = action.params.get("url")
                if url:
                    webbrowser.open(url)

            elif action.type == ActionType.TTS_RESPONSE:
                text = action.params.get("text")
                if text:
                    await self.event_bus.emit(Event(
                        EventType.VOICE_REQUEST,
                        {"text": text},
                        "ActionEngine"
                    ))

            elif action.type == ActionType.EXECUTE_SCRIPT:
                script = action.params.get("script")
                if script:
                    # Caution: exec() is powerful and should be used carefully
                    exec(script)

            elif action.type == ActionType.PLAY_AUDIO:
                file_path = action.params.get("path")
                # Implementation would call an audio player utility
                pass

        except Exception as e:
            logger.error(f"Action execution error ({action.type}): {e}")

    async def execute_sequence(self, actions: List[Action]):
        """
        Executes a list of actions in order.
        """
        for action in actions:
            await self.execute_action(action)
            # Small delay between actions if needed
            await asyncio.sleep(0.1)
