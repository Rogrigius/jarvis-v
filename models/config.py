"""
Configuration model for the JARVIS application.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class AppConfig:
    """
    Data class representing the application configuration.

    Attributes:
        name: Name of the assistant.
        version: Application version.
        language: Preferred language.
        voice_name: Edge-TTS voice identifier.
        stt_model_path: Path to the STT model (Vosk/Whisper).
        db_path: Path to the SQLite database.
        plugin_dir: Directory where plugins are stored.
        command_prefix: Prefix for text-based commands.
        settings: Additional dynamic settings.
    """
    name: str = "JARVIS"
    version: str = "1.0.0"
    language: str = "en-US"
    voice_name: str = "en-US-GuyNeural"
    stt_model_path: str = "models/vosk-model-small-ru-0.22"
    stt_sample_rate: int = 16000
    stt_chunk_size: int = 4000
    stt_wake_words: List[str] = field(default_factory=lambda: ["джарвис", "jarvis"])
    db_path: str = "database/jarvis.db"
    plugin_dir: str = "plugins"
    command_prefix: str = "/"
    settings: Dict[str, Any] = field(default_factory=dict)
