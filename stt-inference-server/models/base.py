from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, Union

class BaseModel(ABC):
    @abstractmethod
    async def transcribe(self, audio_file: Union[str, bytes], stream: bool = False) -> AsyncGenerator[Dict[str, Any], None]:
        pass

    @abstractmethod
    async def live_transcribe(self, audio_chunk: bytes) -> Dict[str, Any]:
        pass
