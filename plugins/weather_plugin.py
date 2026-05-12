from models.command import Command
from models.event import Event, EventType
from utils.logger import logger

class WeatherPlugin:
    def setup(self, event_bus, command_manager):
        self.event_bus = event_bus
        self.command_manager = command_manager

        # Регистрация команды
        weather_cmd = Command(
            name="Погода",
            description="Узнать текущую погоду",
            keywords=["погода", "температура", "прогноз"],
            callback=self.get_weather,
            is_async=True
        )
        self.command_manager.register_command(weather_cmd)
        logger.info("Weather Plugin initialized in Russian")

    async def get_weather(self, text: str):
        # В реальном плагине здесь был бы вызов API
        response = "Сегодня солнечно, температура около двадцати пяти градусов тепла."

        # Отправка события для озвучивания ответа
        logger.info(f"Weather Plugin Response: {response}")

        await self.event_bus.emit(Event(
            EventType.VOICE_REQUEST,
            {"text": response},
            "WeatherPlugin"
        ))
