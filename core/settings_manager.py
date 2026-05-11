"""
Settings manager for JARVIS with persistence and profiles.
"""
import json
from typing import Any, Dict, Optional
from utils.logger import logger
from models.config import AppConfig

class SettingsManager:
    """
    Manages application settings, profiles, and automatic persistence to the database.
    """
    def __init__(self, db_manager, config: AppConfig):
        self.db_manager = db_manager
        self.config = config
        self.load_settings()

    def load_settings(self):
        """Loads all settings from the database and updates the config object."""
        logger.info("Loading settings from database...")
        results = self.db_manager.execute("SELECT key, value FROM settings")
        if results:
            for key, value in results:
                try:
                    typed_value = json.loads(value)
                    if hasattr(self.config, key):
                        setattr(self.config, key, typed_value)
                except Exception as e:
                    logger.error(f"Failed to load setting {key}: {e}")

    def set(self, key: str, value: Any):
        """Sets a setting and persists it immediately."""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            json_value = json.dumps(value)
            self.db_manager.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, json_value)
            )
            logger.info(f"Setting updated: {key} = {value}")

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self.config, key, default)
