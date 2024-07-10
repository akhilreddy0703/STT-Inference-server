from .base import BaseModel
from faster_whisper import WhisperModel
from typing import AsyncGenerator, Dict, Any, Union
import numpy as np

class FasterWhisperModel(BaseModel):
    def __init__(self, model_id: str, device: str, compute_type: str):
        self.model = WhisperModel(model_id, device=device, compute_type=compute_type)

    async def transcribe(self, audio_file: Union[str, bytes], stream: bool = False) -> AsyncGenerator[Dict[str, Any], None]:
        segments, info = self.model.transcribe(audio_file, beam_size=5, word_timestamps=stream)
        
        if stream:
            async for word in self._stream_words(segments):
                yield word
        else:
            yield {
                "transcription": " ".join([segment.text for segment in list(segments)]),
                "language": info.language,
                "language_probability": info.language_probability
            }

    def live_transcribe(self, audio_chunk: bytes) -> Dict[str, Any]:
        # Convert bytes to numpy array
        audio_np = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
        
        segments, info = self.model.transcribe(audio_np, beam_size=5, word_timestamps=True)
        words = [{"word": word.word, "start": word.start, "end": word.end} 
                for segment in segments for word in segment.words]
        
        return {
            "words": words,
            "language": info.language,
            "language_probability": info.language_probability
        }
    
    @staticmethod
    async def _stream_words(segments) -> AsyncGenerator[Dict[str, Any], None]:
        for segment in segments:
            for word in segment.words:
                yield {
                    "word": word.word,
                    "start": word.start,
                    "end": word.end
                }