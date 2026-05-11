"""
Serializable action and command models for the JARVIS editor.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from enum import Enum, auto

class ActionType(str, Enum):
    LAUNCH_APP = "launch_app"
    OPEN_URL = "open_url"
    EXECUTE_SCRIPT = "execute_script"
    PRESS_KEYS = "press_keys"
    TTS_RESPONSE = "tts_response"
    PLAY_AUDIO = "play_audio"
    SEQUENCE = "sequence"

@dataclass
class Action:
    type: ActionType
    params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)

@dataclass
class CustomCommand:
    id: Optional[int] = None
    name: str = ""
    trigger_phrases: List[str] = field(default_factory=list)
    actions: List[Action] = field(default_factory=list)
    enabled: bool = True
    category: str = "General"

    def to_dict(self):
        return asdict(self)
