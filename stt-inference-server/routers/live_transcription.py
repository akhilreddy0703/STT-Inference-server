from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from models.model_manager import model_manager
from server_metadata import server_metadata
from utils.logger import main_logger as logger, transcription_logger
from utils.audio_utils import get_audio_duration, audio_processor, AudioBuffer
import time


router = APIRouter()

@router.websocket("/v1/live_transcription")
async def live_transcription(websocket: WebSocket):
    try:
        await websocket.accept()
        logger.info("WebSocket connection accepted")
        audio_buffer = AudioBuffer()
        
        if not model_manager.is_loaded:
            logger.error("Model not loaded")
            await websocket.close(code=1011, reason="Model not loaded")
            return
        
        model = model_manager.get_model()
        while True:
            try:
                audio_chunk = await websocket.receive_bytes()
                start_time = time.time()
                
                # Add the new chunk to the buffer and get the entire buffer
                buffer_data = audio_buffer.add_audio(audio_chunk)
                
                # Process the audio buffer
                processed_audio = audio_processor(buffer_data.tobytes(), is_file=False, sample_rate=16000)
                
                # Transcribe the processed audio
                result = model.live_transcribe(processed_audio)
                end_time = time.time()

                inference_time = end_time - start_time
                audio_duration = get_audio_duration(processed_audio)
                server_metadata.update_stats(audio_duration, inference_time)
                response = {
                    **result,
                    "inference_time": inference_time,
                    "audio_duration": audio_duration
                }
                transcription_logger.info(response)
                await websocket.send_json(response)
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected")
                break
            except Exception as e:
                logger.error(f"Error in live transcription: {str(e)}")
                await websocket.send_json({"error": str(e)})
    except Exception as e:
        logger.error(f"Unexpected error in live transcription: {str(e)}")
    finally:
        await websocket.close()
        logger.info("WebSocket connection closed")