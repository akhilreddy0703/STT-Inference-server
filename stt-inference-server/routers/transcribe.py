from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from models.model_manager import model_manager
from server_metadata import server_metadata
from utils.logger import main_logger as logger
from utils.audio_utils import process_audio_file, get_audio_duration
import time
import json
import asyncio

router = APIRouter()

@router.post("/v1/transcribe")
async def transcribe(
    request: Request,
    file: UploadFile = File(...),
    stream: bool = Form(False)
):
    start_time = time.time()
    try:
        temp_audio_path, audio_content = await process_audio_file(file)
        audio_duration = get_audio_duration(audio_content)
        model = model_manager.get_model()

        if stream:
            logger.info("Invoke transcribe streaming")

            return StreamingResponse(
                generate_stream(request, model, temp_audio_path, start_time, audio_duration),
                media_type="text/event-stream"
            )
        else:
            logger.info("Invoke transcribe")

            return await generate_response(request, model, temp_audio_path, start_time, audio_duration)
    except Exception as e:
        logger.error(f"Error in transcribe endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
async def generate_stream(request, asr_model, audio_path, start_time, audio_duration):
    loop = asyncio.get_event_loop()
    try:
        transcribe_generator = await loop.run_in_executor(
            request.app.state.thread_pool,
            lambda: asr_model.transcribe(audio_path, stream=True)
        )
        
        async for word in transcribe_generator:
            yield f"data: {json.dumps(word)}\n\n"
        
        end_time = time.time()
        inference_time = end_time - start_time
        server_metadata.update_stats(audio_duration, inference_time)
        yield f"data: {{\"inference_time\": {inference_time}, \"audio_duration\": {audio_duration}}}\n\n"
    except Exception as e:
        logger.error(f"Error in stream generation: {str(e)}")
        yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

async def generate_response(request, asr_model, audio_path, start_time, audio_duration):
    loop = asyncio.get_event_loop()
    try:
        transcribe_generator = await loop.run_in_executor(
            request.app.state.thread_pool,
            lambda: asr_model.transcribe(audio_path, stream=False)
        )
        result = await anext(transcribe_generator)
        end_time = time.time()
        inference_time = end_time - start_time
        server_metadata.update_stats(audio_duration, inference_time)
        return JSONResponse({
            **result,
            "inference_time": inference_time,
            "audio_duration": audio_duration
        })    
    except Exception as e:
        logger.error(f"Error in response generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    