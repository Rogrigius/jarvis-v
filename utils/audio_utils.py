"""
Utility for discovering audio input and output devices.
"""
import pyaudio
from typing import List, Dict

def get_audio_devices():
    """
    Returns a dictionary of input and output devices.
    """
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')

    inputs = []
    outputs = []

    for i in range(0, num_devices):
        dev_info = p.get_device_info_by_host_api_device_index(0, i)
        device = {
            "index": i,
            "name": dev_info.get('name'),
            "max_input_channels": dev_info.get('maxInputChannels'),
            "max_output_channels": dev_info.get('maxOutputChannels')
        }

        if dev_info.get('maxInputChannels') > 0:
            inputs.append(device)
        if dev_info.get('maxOutputChannels') > 0:
            outputs.append(device)

    p.terminate()
    return {"inputs": inputs, "outputs": outputs}
