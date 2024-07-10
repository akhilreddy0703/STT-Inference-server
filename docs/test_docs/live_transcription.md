# Testing Live Transcription with Microphone Input

This guide will help you test the live transcription feature using real-time microphone input.

## Prerequisites

1. Ensure your server is running with the desired backend (faster_whisper or openai_whisper).

2. Install the required Python libraries:
   ```
   pip install websockets pyaudio
   ```
   Note: `pyaudio` might require additional system libraries. On Ubuntu/Debian, you might need to run:
   ```
   sudo apt-get install portaudio19-dev
   ```
   On macOS with Homebrew:
   ```
   brew install portaudio
   ```

3. Make sure you have a working microphone connected to your computer.

## Running the Test

1. Save the provided Python script to a file, e.g., `live_mic_transcription_test.py`.

2. Run the script:
   ```
   python live_mic_transcription_test.py
   ```

3. Start speaking into your microphone. The script will capture 3-second chunks of audio and send them to the server for transcription.

4. The transcription results will be printed to the console as they are received from the server.

5. To stop the recording and close the connection, press Ctrl+C.

## Notes

- The script records audio in 3-second chunks. You can adjust the `RECORD_SECONDS` variable to change this duration.
- The audio is recorded at 16kHz with 16-bit depth in mono. This should be compatible with most speech recognition models.
- A temporary WAV file is created for each chunk. In a production environment, you might want to optimize this to avoid file I/O.
- Handle any errors that may occur during recording or transmission gracefully in a production environment.
- Ensure you have permission to access the microphone on your system.

## Troubleshooting

- If you encounter issues with PyAudio, make sure you have the necessary system libraries installed.
- If the transcription seems delayed, you can try adjusting the `RECORD_SECONDS` value to find a balance between latency and accuracy.
- Ensure your microphone is properly configured and selected as the default input device on your system.

This setup allows for true live transcription, capturing audio from your microphone in real-time and sending it to the server for processing. It provides a more realistic testing scenario for your live transcription service.