# STT Inference Server

This project implements a Speech-to-Text (STT) Inference Server using FastAPI. It supports multiple backends, including Faster Whisper and OpenAI Whisper, and provides both batch and real-time transcription capabilities.

## Features

- Support for multiple STT backends (Faster Whisper, OpenAI Whisper)
- Batch audio file transcription
- Real-time audio stream transcription via WebSocket
- Configurable model parameters (device, quantization)
- Server metadata and statistics endpoints

## Prerequisites

- Python 3.8+
- FastAPI
- uvicorn
- faster-whisper
- openai-whisper
- PyAudio (for client-side audio capture)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/stt-inference-server.git
   cd stt-inference-server
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Start the server:
   ```
   python main.py --backend faster_whisper --model_id base --device cpu --dtype int8
   ```

2. The server will start on `http://localhost:8000` by default.

3. Use the provided API endpoints to transcribe audio files or connect via WebSocket for real-time transcription.

## API Documentation

Refer to the [API Documentation](docs/api.md) for detailed information on available endpoints and their usage.

## TODO

- `[ ]` Add backend for QwenAudio models
- `[ ]` Optimize the server for batch inference
- `[ ]` Alternative implementation for the live_transcription

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
