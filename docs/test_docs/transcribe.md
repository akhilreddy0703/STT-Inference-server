# Testing the Transcribe Endpoint

This guide will help you test the `/v1/transcribe` endpoint of the STT Inference Server.

## Prerequisites

- The STT Inference Server is running and accessible (e.g., at `http://localhost:8000`)
- Python 3.6+ installed on your system
- `requests` library installed (`pip install requests`)

## Steps

1. Prepare an audio file for transcription (e.g., `test_audio.wav`).
2. Save the Python script provided below as `test_transcribe.py`.
3. Run the script: `python test_transcribe.py`
4. The script will send the audio file to the server and print the transcription result.

## Expected Output

You should see a JSON response containing the transcription, language information, and timing details.

Example:
```json
{
  "transcription": "This is a test audio file for transcription.",
  "language": "en",
  "language_probability": 0.98,
  "inference_time": 1.23,
  "audio_duration": 5.67
}
```

If you encounter any errors, check that your server is running and the audio file path is correct.