import json
from pathlib import Path
from typing import Any
from models.config import AppConfig
from utils.logger import logger

class ConfigManager:
    def __init__(self, config_path: str = "config/config.json"):
        self.config_path = Path(config_path)
        self.config = AppConfig()
        self.load_config()

    def load_config(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self.config, key):
                            setattr(self.config, key, value)
                logger.info("Configuration loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        else:
            self.save_config()

    def save_config(self):
        self.config_path.parent.mkdir(exist_ok=True)
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config.__dict__, f, indent=4)
            logger.info("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self.config, key, default)
