from models.command import Command
from models.event import Event, EventType
from utils.logger import logger

class WeatherPlugin:
    def setup(self, event_bus, command_manager):
        self.event_bus = event_bus
        self.command_manager = command_manager

        # Register a command
        weather_cmd = Command(
            name="Weather",
            description="Get the current weather",
            keywords=["weather", "temperature", "forecast"],
            callback=self.get_weather,
            is_async=True
        )
        self.command_manager.register_command(weather_cmd)
        logger.info("Weather Plugin initialized")

    async def get_weather(self, text: str):
        # In a real plugin, you'd call an API here
        response = "The weather today is sunny with a high of 75 degrees."

        # Emit a voice event to speak the result
        # Note: In a real app, you might want to access VoiceManager via event_bus or a registry
        # For simplicity in this demo, we can just log or emit a specific event
        logger.info(f"Weather Plugin Response: {response}")

        # We can emit an event that VoiceManager or MainApp handles
        await self.event_bus.emit(Event(
            EventType.VOICE_START,
            {"text": response},
            "WeatherPlugin"
        ))
