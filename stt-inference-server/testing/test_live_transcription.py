import asyncio
import websockets
import json
import pyaudio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Audio recording parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 3

def list_audio_devices():
    p = pyaudio.PyAudio()
    print("Available audio input devices:")
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev.get('maxInputChannels') > 0:
            print(f"{i}: {dev.get('name')}")
    p.terminate()

def select_audio_device():
    list_audio_devices()
    while True:
        try:
            selection = int(input("Select the number of the input device you want to use: "))
            p = pyaudio.PyAudio()
            if 0 <= selection < p.get_device_count():
                dev = p.get_device_info_by_index(selection)
                if dev.get('maxInputChannels') > 0:
                    p.terminate()
                    return selection
            p.terminate()
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

async def mic_to_websocket():
    uri = "ws://localhost:8000/v1/live_transcription"
    
    device = select_audio_device()
    
    p = pyaudio.PyAudio()
    
    try:
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=device,
                        frames_per_buffer=CHUNK)

        async with websockets.connect(uri) as websocket:
            logger.info("WebSocket connection established")
            print("* Recording started")
            while True:
                try:
                    # Record audio
                    frames = []
                    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                        data = stream.read(CHUNK)
                        frames.append(data)
                    
                    # Convert to bytes
                    byte_data = b''.join(frames)
                    
                    # Send to server
                    await websocket.send(byte_data)
                    
                    # Receive and print response
                    response = await websocket.recv()
                    print(json.loads(response))
                except websockets.exceptions.ConnectionClosed:
                    logger.error("WebSocket connection closed unexpectedly")
                    break
                except Exception as e:
                    logger.error(f"Error during WebSocket communication: {str(e)}")
                    break
    except websockets.exceptions.InvalidStatusCode as e:
        logger.error(f"Failed to connect to WebSocket server: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        if 'stream' in locals():
            stream.stop_stream()
            stream.close()
        p.terminate()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(mic_to_websocket())