import requests
import json

# Server URL
URL = "http://localhost:8000/v1/transcribe"

# Path to your audio file
AUDIO_FILE_PATH = "path/to/your/audio/file.wav"

def test_transcribe():
    # Prepare the file for upload
    files = {
        'file': ('audio.wav', open(AUDIO_FILE_PATH, 'rb'), 'audio/wav')
    }

    # Additional parameters (optional)
    data = {
        'stream': 'false'  # Set to 'true' if you want to test streaming
    }

    try:
        # Send POST request to the server
        response = requests.post(URL, files=files, data=data)

        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            print("Transcription successful:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: Received status code {response.status_code}")
            print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")

    except json.JSONDecodeError:
        print("Error: Received invalid JSON response")
        print(response.text)

if __name__ == "__main__":
    test_transcribe()