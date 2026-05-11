from dataclasses import dataclass
from typing import Callable, List, Optional

@dataclass
class Command:
    name: str
    description: str
    keywords: List[str]
    callback: Callable
    priority: int = 0
    is_async: bool = True
