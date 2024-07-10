from server_metadata import server_metadata, Backend
from utils.logger import model_logger as logger
from .faster_whisper_backend import FasterWhisperModel
from .openai_whisper_backend import OpenAIWhisperModel

class ModelManager:
    def __init__(self):
        self.model = None
        self.is_loaded = False

    def load_model(self):
        try:
            if server_metadata.backend == Backend.FASTER_WHISPER:
                self.model = FasterWhisperModel(
                    server_metadata.model_id,
                    server_metadata.device,
                    server_metadata.quantization
                )
            elif server_metadata.backend == Backend.OPENAI_WHISPER:
                self.model = OpenAIWhisperModel(
                    server_metadata.model_id,
                    server_metadata.device
                )
            else:
                raise ValueError(f"Unsupported backend: {server_metadata.backend}")

            self.is_loaded = True
            server_metadata.is_loaded = True
            logger.info(f"Loaded {server_metadata.backend} model {server_metadata.model_id} "
                        f"on {server_metadata.device} with {server_metadata.quantization}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self.is_loaded = False
            server_metadata.is_loaded = False
            raise

    def get_model(self):
        if not self.is_loaded or self.model is None:
            logger.error("Model not loaded. Please load a model first.")
            raise ValueError("Model not loaded. Please load a model first.")
        return self.model

model_manager = ModelManager()