from .base import BaseModel
from typing import AsyncGenerator, Dict, Any, Union
from utils.audio_utils import get_audio_duration
import asyncio
import os
from swift.llm import (
    get_model_tokenizer, get_template, inference, ModelType,
    get_default_template_type, inference_stream
)
import torch

class QwenAudioBase(BaseModel):
    def __init__(self, model_id: str, device: str):
        self.model_type = ModelType.qwen_audio_chat
        self.template_type = get_default_template_type(self.model_type)
        self.model, self.tokenizer = get_model_tokenizer(
            self.model_type,
            torch.float16,
            model_kwargs={'device_map': 'auto'}
        )
        self.model.generation_config.max_new_tokens = 256
        self.template = get_template(self.template_type, self.tokenizer)

    async def transcribe(self, audio_file: Union[str, bytes], prompt: str = None, stream: bool = False) -> AsyncGenerator[Dict[str, Any], None]:
        query = f"Audio 1:<audio>{audio_file}</audio>\n{prompt or 'What did this speech say'}"
        
        if stream:
            gen = inference_stream(self.model, self.template, query)
            async for response, _ in gen:
                yield {"word": response}
        else:
            response, _ = await asyncio.to_thread(inference, self.model, self.template, query)
            yield {"transcription": response}

    async def live_transcribe(self, audio_chunk: bytes) -> Dict[str, Any]:

        query = f"Audio 1:<audio>{audio_chunk}</audio>\nWhat did this speech say"
        response, _ = await asyncio.to_thread(inference, self.model, self.template, query)
        return {"transcription": response}
