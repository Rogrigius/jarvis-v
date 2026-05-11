# JARVIS - Modular Voice Assistant

This project implements a clean, modular architecture for a voice assistant named JARVIS, designed for Windows using Python 3.12+.

## Architecture Overview

The assistant follows a **Decoupled Event-Driven Architecture**:

- **Core**: Contains the central orchestration logic, including the Event Bus, Plugin Manager, and Command Manager.
- **GUI**: A PyQt6-based interface that communicates with the core through signals and events.
- **Models**: Unified data structures using `dataclasses` for commands, events, and configuration.
- **Plugins**: Independent modules that can be added to extend functionality without modifying the core.
- **Utilities**: Shared resources like the logging system.

### Key Components

1.  **Event Bus (`core/event_bus.py`)**: The central nervous system. All modules communicate by emitting and subscribing to events, ensuring low coupling.
2.  **Plugin Manager (`core/plugin_manager.py`)**: Dynamically loads Python modules from the `plugins/` directory. Each plugin can register commands and subscribe to events.
3.  **Command Manager (`core/command_manager.py`)**: Matches user input (text or transcribed voice) against registered commands using keyword mapping.
4.  **Voice Manager (`core/voice_manager.py`)**: Handles TTS (via Edge-TTS) and provides a structure for STT (Vosk/Whisper).
5.  **Multi-threading**: The GUI runs on the main thread (required by PyQt), while the core logic and voice processing run on an `asyncio` event loop in a background thread.

## Operational Workflow

1.  **Initialization**: `main.py` starts the `JarvisApp`, which initializes core managers, the GUI, and the background event loop.
2.  **Plugin Loading**: The `PluginManager` scans the `plugins/` folder and calls the `setup()` method on found classes.
3.  **Listening**: The `VoiceManager` (STT) listens for audio. When speech is detected, it's transcribed to text.
4.  **Event Emission**: An `EventType.COMMAND_DETECTED` event is emitted with the transcribed text.
5.  **Command Execution**: The `CommandManager` catches the event, finds a matching command (e.g., from a plugin), and executes its callback.
6.  **Response**: The command callback may emit a `EventType.VOICE_START` event, which the `VoiceManager` (TTS) picks up to speak the response.

## Extensibility

### Adding a New Command
Commands can be registered via plugins. Simply define a callback and add it to the `CommandManager` during plugin setup.

### Creating a Plugin
1. Create a new `.py` file in the `plugins/` directory.
2. Define a class with a `setup(self, event_bus, command_manager)` method.
3. Use the provided managers to hook into the system.

Example (see `plugins/weather_plugin.py`):
```python
class MyPlugin:
    def setup(self, event_bus, command_manager):
        command_manager.register_command(Command(
            name="Hello",
            keywords=["hi", "hello"],
            callback=self.say_hello
        ))

    async def say_hello(self, text):
        await event_bus.emit(Event(EventType.VOICE_START, {"text": "Hello there!"}))
```

## Setup and Requirements

- Python 3.12+
- PyQt6
- edge-tts
- pygame (for audio playback)
- vosk
- pyaudio
- sqlite3 (built-in)

### Automated Setup (Recommended for Windows)

1.  Double-click `install.bat`. This will create a virtual environment and install all dependencies.
2.  Double-click `run.bat` to launch the application.

### Manual Setup

```bash
# Create venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### Note on STT Models
JARVIS requires a Vosk model to be present in the `models/` directory. By default, it looks for `vosk-model-small-ru-0.22`.
You can download models from [alphacephei.com/vosk/models](https://alphacephei.com/vosk/models).
