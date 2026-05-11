import importlib
import inspect
from pathlib import Path
from typing import Dict, Any
from utils.logger import logger

class PluginManager:
    def __init__(self, plugin_dir: str = "plugins", event_bus=None, command_manager=None):
        self.plugin_dir = Path(plugin_dir)
        self.plugin_dir.mkdir(exist_ok=True)
        self.plugins: Dict[str, Any] = {}
        self.event_bus = event_bus
        self.command_manager = command_manager

    def load_plugins(self):
        logger.info("Loading plugins...")
        for plugin_file in self.plugin_dir.glob("*.py"):
            if plugin_file.name == "__init__.py":
                continue

            module_name = f"plugins.{plugin_file.stem}"
            try:
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and hasattr(obj, "setup"):
                        plugin_instance = obj()
                        plugin_instance.setup(self.event_bus, self.command_manager)
                        self.plugins[module_name] = plugin_instance
                        logger.info(f"Plugin loaded: {module_name}")
            except Exception as e:
                logger.error(f"Failed to load plugin {module_name}: {e}")

    def reload_plugins(self):
        self.plugins.clear()
        self.load_plugins()
