"""
Utility to download Vosk STT models automatically.
"""
import os
import zipfile
import requests
from utils.logger import logger

def download_model(model_url: str, target_dir: str = "models"):
    """
    Downloads and extracts a Vosk model zip file.
    """
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    model_name = model_url.split("/")[-1]
    zip_path = os.path.join(target_dir, model_name)

    logger.info(f"Downloading model {model_name}...")
    response = requests.get(model_url, stream=True)
    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    logger.info("Extracting model...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(target_dir)

    os.remove(zip_path)
    logger.info(f"Model {model_name} ready.")

if __name__ == "__main__":
    # Example: Small Russian model
    RU_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip"
    download_model(RU_MODEL_URL)
