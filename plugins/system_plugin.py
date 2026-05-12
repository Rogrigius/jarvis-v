import os
import subprocess
from models.command import Command
from models.event import Event, EventType
from utils.logger import logger

class SystemPlugin:
    def setup(self, event_bus, command_manager):
        self.event_bus = event_bus
        self.command_manager = command_manager

        # Command for shutdown
        shutdown_cmd = Command(
            name="Выключение",
            description="Выключить компьютер",
            keywords=["выключи компьютер", "выключение"],
            callback=self.shutdown_pc,
            is_async=True
        )

        # Command for restart
        restart_cmd = Command(
            name="Перезагрузка",
            description="Перезагрузить компьютер",
            keywords=["перезагрузи компьютер", "перезагрузка"],
            callback=self.restart_pc,
            is_async=True
        )

        self.command_manager.register_command(shutdown_cmd)
        self.command_manager.register_command(restart_cmd)
        logger.info("System Plugin initialized")

    async def shutdown_pc(self, text: str):
        await self.event_bus.emit(Event(
            EventType.VOICE_REQUEST,
            {"text": "Выключаю компьютер. До свидания!"},
            "SystemPlugin"
        ))
        logger.info("Shutdown command execution")
        if os.name == 'nt':
            subprocess.run(["shutdown", "/s", "/t", "1"])
        else:
            logger.warning("Shutdown not implemented for this OS")

    async def restart_pc(self, text: str):
        await self.event_bus.emit(Event(
            EventType.VOICE_REQUEST,
            {"text": "Перезагружаю систему."},
            "SystemPlugin"
        ))
        logger.info("Restart command execution")
        if os.name == 'nt':
            subprocess.run(["shutdown", "/r", "/t", "1"])
        else:
            logger.warning("Restart not implemented for this OS")
