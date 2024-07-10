import uvicorn
import argparse
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routers import transcribe, live_transcription
from server_metadata import server_metadata, Backend, Device, Quantization
from utils.logger import main_logger as logger
from models.model_manager import model_manager
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

# Determine the number of worker threads
num_workers = multiprocessing.cpu_count() * 2 + 1

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Server starting up")
    logger.info(f"Server metadata: {server_metadata.model_dump()}")
    
    # Create ThreadPoolExecutor
    app.state.thread_pool = ThreadPoolExecutor(max_workers=num_workers)
    
    if not model_manager.is_loaded:
        logger.info("Loading model...")
        try:
            model_manager.load_model()
            logger.info(f"Model loaded successfully with server_metadata {server_metadata.model_dump()}.")
        except Exception as e:
            logger.error(f"Failed to load the model: {str(e)}")
    yield
    # Shutdown
    logger.info("Server shutting down")
    app.state.thread_pool.shutdown()

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(transcribe.router)
app.include_router(live_transcription.router)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the STT Inference Server"}

@app.get("/metadata")
async def get_metadata():
    try:
        logger.info("Metadata endpoint accessed")
        return server_metadata.model_dump()
    except Exception as e:
        logger.error(f"Error retrieving metadata: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/stats")
async def get_stats():
    try:
        logger.info("Stats endpoint accessed")
        return {
            "total_requests": server_metadata.stats.total_requests,
            "total_audio_duration": server_metadata.stats.total_audio_duration,
            "total_inference_time": server_metadata.stats.total_inference_time,
            "average_inference_time": server_metadata.stats.average_inference_time,
            "real_time_factor": server_metadata.stats.real_time_factor
        }
    except Exception as e:
        logger.error(f"Error retrieving stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

def main():
    parser = argparse.ArgumentParser(description="Run the STT Inference Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--model_id", type=str, default="base", help="Model ID or path to load")
    parser.add_argument("--backend", type=str, default="faster_whisper", choices=["faster_whisper", "openai_whisper", "pytorch"], help="Backend to use")
    parser.add_argument("--device", type=str, default="cpu", choices=["cpu", "cuda"], help="Device to run the model on")
    parser.add_argument("--dtype", type=str, default="int8", choices=["float32", "float16", "int8"], help="Quantization for model computations")
    args = parser.parse_args()

    try:
        # Update server metadata
        server_metadata.update(
            model_id=args.model_id,
            backend=Backend(args.backend),
            device=Device(args.device),
            quantization=Quantization(args.dtype)
        )

        # logger.info(f"Updated server metadata: {server_metadata.model_dump()}")

        # Run the server
        uvicorn.run("main:app", host=args.host, port=args.port, reload=False)
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        raise

if __name__ == "__main__":
    main()