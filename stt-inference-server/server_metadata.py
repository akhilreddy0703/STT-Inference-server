from pydantic import BaseModel, ConfigDict
from enum import Enum

class Backend(str, Enum):
    FASTER_WHISPER = "faster_whisper"
    OPENAI_WHISPER = "openai_whisper"
    PYTORCH = "pytorch"

class Device(str, Enum):
    CPU = "cpu"
    CUDA = "cuda"

class Quantization(str, Enum):
    FLOAT32 = "float32"
    FLOAT16 = "float16"
    INT8 = "int8"

class Stats(BaseModel):
    total_requests: int = 0
    total_audio_duration: float = 0
    total_inference_time: float = 0

    @property
    def average_inference_time(self):
        return self.total_inference_time / self.total_requests if self.total_requests > 0 else 0

    @property
    def real_time_factor(self):
        return self.total_inference_time / self.total_audio_duration if self.total_audio_duration > 0 else 0

class ServerMetadata(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    model_id: str = "base"
    backend: Backend = Backend.FASTER_WHISPER
    device: Device = Device.CPU
    quantization: Quantization = Quantization.INT8
    is_loaded: bool = False
    stats: Stats = Stats()

    def update(self, model_id: str, backend: Backend, device: Device, quantization: Quantization):
        self.model_id = model_id
        self.backend = backend
        self.device = device
        self.quantization = quantization

    def update_stats(self, audio_duration: float, inference_time: float):
        self.stats.total_requests += 1
        self.stats.total_audio_duration += audio_duration
        self.stats.total_inference_time += inference_time

server_metadata = ServerMetadata()