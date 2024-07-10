# STT Inference Server API Documentation

## Endpoints

### 1. Transcribe Audio

**Endpoint:** `/v1/transcribe`
**Method:** POST
**Content-Type:** multipart/form-data

This endpoint transcribes an uploaded audio file.

**Parameters:**
- `file` (required): The audio file to transcribe
- `stream` (optional): Boolean flag to enable streaming response (default: false)
- `prompt` (optional): A text prompt to guide the transcription

**Response:**
- If `stream` is false:
  ```json
  {
    "transcription": "Transcribed text",
    "language": "Detected language",
    "language_probability": 0.99,
    "inference_time": 1.23,
    "audio_duration": 5.67
  }
  ```
- If `stream` is true:
  Server-Sent Events stream with partial transcriptions

### 2. Live Transcription

**Endpoint:** `/v1/live_transcription`
**Protocol:** WebSocket

This endpoint provides real-time transcription of audio streams.

**Input:**
- Binary audio data chunks

**Output:**
JSON messages with the following structure:
```json
{
  "words": [
    {"word": "Hello", "start": 0.0, "end": 0.5},
    {"word": "world", "start": 0.6, "end": 1.0}
  ],
  "language": "Detected language",
  "language_probability": 0.99,
  "inference_time": 0.05,
  "audio_duration": 1.0
}
```

### 3. Get Server Metadata

**Endpoint:** `/metadata`
**Method:** GET

Retrieves the current server metadata.

**Response:**
```json
{
  "model_id": "base",
  "backend": "faster_whisper",
  "device": "cpu",
  "quantization": "int8",
  "is_loaded": true,
  "stats": {
    "total_requests": 10,
    "total_audio_duration": 50.5,
    "total_inference_time": 25.3
  }
}
```

### 4. Get Server Statistics

**Endpoint:** `/stats`
**Method:** GET

Retrieves the current server statistics.

**Response:**
```json
{
  "total_requests": 10,
  "total_audio_duration": 50.5,
  "total_inference_time": 25.3,
  "average_inference_time": 2.53,
  "real_time_factor": 0.5
}
```