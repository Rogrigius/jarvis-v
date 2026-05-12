import asyncio
import sys
import threading
from PyQt6.QtWidgets import QApplication
from core.event_bus import event_bus
from core.config_manager import ConfigManager
from core.database_manager import DatabaseManager
from core.enhanced_command_manager import EnhancedCommandManager
from core.settings_manager import SettingsManager
from core.action_engine import ActionEngine
from core.hotkey_manager import HotkeyManager
from core.plugin_manager import PluginManager
from core.voice_manager import VoiceManager
from core.stt.voice_listener import VoiceListener
from gui.windows.main_window import FuturisticMainWindow
from models.event import Event, EventType
from utils.logger import logger

class JarvisApp:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.db_manager = DatabaseManager(self.config_manager.get("db_path"))
        self.settings_manager = SettingsManager(self.db_manager, self.config_manager.config)
        self.action_engine = ActionEngine(event_bus)
        self.command_manager = EnhancedCommandManager(self.db_manager, self.action_engine)
        self.event_bus = event_bus
        self.hotkey_manager = HotkeyManager(self.event_bus)
        self.voice_manager = VoiceManager(
            self.event_bus,
            self.config_manager.get("voice_name"),
            self.config_manager.get("output_device_name")
        )
        self.voice_listener = VoiceListener(self.event_bus, self.config_manager.config)
        self.voice_listener.main_loop = None # Will be set in run_async_tasks
        self.plugin_manager = PluginManager(
            self.config_manager.get("plugin_dir"),
            self.event_bus,
            self.command_manager
        )

        self.qt_app = QApplication(sys.argv)
        self.window = FuturisticMainWindow(
            self.event_bus,
            self.db_manager,
            self.command_manager,
            self.settings_manager
        )

        self._setup_event_handlers()

    def _setup_event_handlers(self):
        self.event_bus.subscribe(EventType.VOICE_REQUEST, self._on_voice_request)
        self.event_bus.subscribe(EventType.VOICE_START, self._on_voice_start)
        self.event_bus.subscribe(EventType.VOICE_END, self._on_voice_end)
        self.event_bus.subscribe(EventType.COMMAND_DETECTED, self._on_command_detected)

    async def _on_voice_start(self, event: Event):
        self.window.signals.status_changed.emit("ГОВОРИТ")
        self.window.signals.listening_started.emit()
        self.window.signals.update_log.emit(f"ДЖАРВИС: {event.data.get('text')}")

    async def _on_voice_end(self, event: Event):
        self.window.signals.status_changed.emit("ОЖИДАНИЕ")
        self.window.signals.listening_stopped.emit()

    async def _on_voice_request(self, event: Event):
        text = event.data.get("text")
        if text:
            await self.voice_manager.speak(text)

    async def _on_command_detected(self, event: Event):
        command_text = event.data.get("text")
        self.window.signals.update_log.emit(f"Пользователь: {command_text}")
        await self.command_manager.execute_command(command_text)

    async def run_async_tasks(self):
        # Provide the running loop to managers
        loop = asyncio.get_running_loop()
        self.voice_listener.main_loop = loop

        # Initialize hotkeys
        self.hotkey_manager.setup_hotkeys(
            self.settings_manager.get("hotkeys", {}),
            loop
        )

        # Load plugins
        self.plugin_manager.load_plugins()

        # Initial greeting
        await self.voice_manager.speak("Система инициализирована. Я готов к работе.")

        # Start voice listening
        self.voice_listener.start()

        # Keep the async loop running
        while True:
            await asyncio.sleep(1)

    def start(self):
        # Run asyncio loop in a separate thread
        def run_asyncio_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.run_async_tasks())

        self.loop = asyncio.new_event_loop()
        self.async_thread = threading.Thread(target=run_asyncio_loop, args=(self.loop,), daemon=True)
        self.async_thread.start()

        # Run GUI in the main thread
        self.window.show()
        sys.exit(self.qt_app.exec())

if __name__ == "__main__":
    app = JarvisApp()
    app.start()
