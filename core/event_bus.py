"""
Event bus implementation for decoupled communication.
"""
import asyncio
from typing import Dict, List, Callable, Any
from models.event import Event, EventType
from utils.logger import logger

class EventBus:
    """
    Asynchronous event bus that allows modules to communicate without direct dependencies.
    """
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = {}

    def subscribe(self, event_type: EventType, callback: Callable):
        """
        Subscribe a callback to a specific event type.

        Args:
            event_type: The type of event to listen for.
            callback: The function to call when the event is emitted.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed {callback.__name__} to {event_type.name}")

    async def emit(self, event: Event):
        """
        Emit an event to all interested subscribers.

        Args:
            event: The event instance to broadcast.
        """
        logger.debug(f"Emitting event {event.type.name} from {event.sender}")
        if event.type in self._subscribers:
            tasks = []
            for callback in self._subscribers[event.type]:
                if asyncio.iscoroutinefunction(callback):
                    tasks.append(callback(event))
                else:
                    callback(event)
            if tasks:
                await asyncio.gather(*tasks)

event_bus = EventBus()
