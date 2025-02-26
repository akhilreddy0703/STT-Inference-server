from .base import BaseModel
import whisper
from typing import AsyncGenerator, Dict, Any, Union
import numpy as np

class OpenAIWhisperModel(BaseModel):
    def __init__(self, model_id: str, device: str):
        self.model = whisper.load_model(model_id, device=device)

    async def transcribe(self, audio_file: Union[str, bytes], stream: bool = False) -> AsyncGenerator[Dict[str, Any], None]:
        result = self.model.transcribe(audio_file, word_timestamps=stream)
        segments = result["segments"]
        if stream:
            async for word in self._stream_words(segments):
                yield word
        else:
            yield {
                "transcription": result["text"],
                "language": result["language"],
                "segments": result["segments"]
            }

    def live_transcribe(self, audio_chunk: bytes) -> Dict[str, Any]:
        # Convert bytes to numpy array
        audio_np = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
        
        result = self.model.transcribe(audio_np, word_timestamps=True)
        words = [{"word": word["word"], "start": word["start"], "end": word["end"]} 
                for segment in result["segments"] for word in segment["words"]]
        
        return {
            "words": words,
            "language": result["language"]
        }

    @staticmethod
    async def _stream_words(segments) -> AsyncGenerator[Dict[str, Any], None]:
        for segment in segments:
                for word in segment["words"]:
                    yield {
                        "word": word["word"],
                        "start": word["start"],
                        "end": word["end"]
                    }