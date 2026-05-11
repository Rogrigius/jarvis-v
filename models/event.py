from dataclasses import dataclass
from typing import Any, Dict, Optional
from enum import Enum, auto

class EventType(Enum):
    VOICE_REQUEST = auto()
    VOICE_START = auto()
    VOICE_END = auto()
    COMMAND_DETECTED = auto()
    PLUGIN_LOADED = auto()
    SYSTEM_BOOT = auto()
    SHUTDOWN = auto()
    GUI_READY = auto()

@dataclass
class Event:
    type: EventType
    data: Optional[Dict[str, Any]] = None
    sender: str = "System"
