import io
import tempfile
import soundfile as sf
from typing import Union, Tuple
from fastapi import UploadFile
import numpy as np

async def process_audio_file(file: UploadFile) -> Tuple[str, bytes]:
    """
    Process an uploaded audio file and return its path and content.
    
    :param file: UploadFile object containing the audio file
    :return: Tuple containing the path to the temporary file and its content in bytes
    """
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            content = await file.read()
            temp_audio.write(content)
            temp_audio_path = temp_audio.name
        return temp_audio_path, content
    except Exception as e:
        raise ValueError(f"Error processing audio file: {str(e)}")


def get_audio_duration(audio_input: Union[str, bytes]) -> float:
    try:
        if isinstance(audio_input, str):
            with sf.SoundFile(audio_input) as audio_file:
                return len(audio_file) / audio_file.samplerate
        elif isinstance(audio_input, bytes):
            with sf.SoundFile(io.BytesIO(audio_input)) as audio_file:
                return len(audio_file) / audio_file.samplerate
        else:
            raise ValueError(f"Unsupported audio input type: {type(audio_input)}")
    except Exception as e:
        raise ValueError(f"Error processing audio: {str(e)}")

def audio_processor(audio_data: Union[str, bytes], is_file: bool = False, sample_rate: int = 16000) -> bytes:
    try:
        if is_file:
            if isinstance(audio_data, str):
                with open(audio_data, 'rb') as f:
                    audio_data = f.read()
            elif not isinstance(audio_data, bytes):
                raise ValueError("Invalid input for is_file=True. Expected string (filepath) or bytes.")
        
        # Convert to numpy array
        audio = np.frombuffer(audio_data, dtype=np.int16)
        
        # Convert to mono if stereo
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)

        # Resample to 16kHz if necessary
        if sample_rate != 16000:
            audio = sf.resample(audio, 16000, sample_rate)

        # Ensure audio is in int16 format
        audio = (audio * 32767).astype(np.int16)

        # Write to bytes buffer
        buffer = io.BytesIO()
        sf.write(buffer, audio, 16000, format='WAV', subtype='PCM_16')
        buffer.seek(0)
        processed_audio = buffer.read()

        return processed_audio
    except Exception as e:
        raise ValueError(f"Error processing audio: {str(e)}")

class AudioBuffer:
    def __init__(self, buffer_duration: float = 30.0, sample_rate: int = 16000):
        self.buffer_duration = buffer_duration
        self.sample_rate = sample_rate
        self.buffer_size = int(buffer_duration * sample_rate)
        self.buffer = np.zeros(self.buffer_size, dtype=np.int16)
        self.write_pos = 0

    def add_audio(self, audio_chunk: bytes) -> np.ndarray:
        chunk = np.frombuffer(audio_chunk, dtype=np.int16)
        chunk_size = len(chunk)

        # If chunk is larger than buffer, only keep the latest buffer_size samples
        if chunk_size >= self.buffer_size:
            self.buffer = chunk[-self.buffer_size:]
            self.write_pos = 0
        else:
            # Compute the number of samples to copy
            samples_to_copy = min(chunk_size, self.buffer_size - self.write_pos)
            
            # Copy samples to buffer
            self.buffer[self.write_pos:self.write_pos + samples_to_copy] = chunk[:samples_to_copy]
            
            # If there are remaining samples, copy them to the beginning of the buffer
            if samples_to_copy < chunk_size:
                remaining_samples = chunk_size - samples_to_copy
                self.buffer[:remaining_samples] = chunk[samples_to_copy:]
            
            # Update write position
            self.write_pos = (self.write_pos + chunk_size) % self.buffer_size

        return self.buffer