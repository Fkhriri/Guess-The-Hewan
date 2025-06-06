from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
from speech_service import SpeechService
from audio_processor import AudioProcessor
from errors import GameError, AudioProcessingError, InvalidAudioFormat, SpeechRecognitionError, RateLimitExceeded
from logger import RequestLoggingContext
import os
from typing import Dict, Any
import time
import sys
from collections import defaultdict
from datetime import datetime, timedelta

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        with RequestLoggingContext() as log_ctx:
            logger.info(f"Request started: {request.method} {request.url}")
            
            try:
                response = await call_next(request)
                process_time = time.time() - start_time
                logger.info(f"Request completed: {response.status_code} ({process_time:.2f}s)")
                return response
            except Exception as e:
                process_time = time.time() - start_time
                logger.error(f"Request failed: {str(e)} ({process_time:.2f}s)")
                raise

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = datetime.now()
        
        # Clean old requests
        client_request_counts[client_ip] = [
            timestamp for timestamp in client_request_counts[client_ip]
            if timestamp > now - timedelta(seconds=RATE_LIMIT_DURATION)
        ]
        
        # Check rate limit
        if len(client_request_counts[client_ip]) >= MAX_REQUESTS:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "status": "error",
                    "message": "Terlalu banyak permintaan. Silakan coba lagi nanti."
                }
            )
            
        # Add current request
        client_request_counts[client_ip].append(now)
        
        # Process request
        response = await call_next(request)
        return response

# Rate limiting configuration
RATE_LIMIT_DURATION = 60  # seconds
MAX_REQUESTS = 30  # requests per duration
client_request_counts = defaultdict(list)

app = FastAPI(
    title="Animal Guessing Game API",
    description="API for handling speech recognition in the Animal Guessing Game",
    version="1.0.0"
)

# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
    expose_headers=["Content-Disposition"]
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Create directories
os.makedirs("temp", exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("audio_logs", exist_ok=True)
os.makedirs("../static", exist_ok=True)

# Create required directories
os.makedirs("temp", exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("audio_logs", exist_ok=True)

# Ensure static directories exist
static_dirs = {
    "sounds": "../sounds",
    "images": "../images",
    "favicon": "../favicon",
    "static": "../static"
}

for dir_name, dir_path in static_dirs.items():
    os.makedirs(dir_path, exist_ok=True)

# Initialize services
speech_service = SpeechService()
audio_processor = AudioProcessor()

# Mount static files with proper error handling
for route, directory in static_dirs.items():
    try:
        app.mount(f"/{route}", StaticFiles(directory=directory), name=route)
        logger.info(f"Successfully mounted static directory: {route} -> {directory}")
    except Exception as e:
        logger.error(f"Failed to mount static directory {route}: {str(e)}")
        raise

# File serving routes with error handling
@app.get("/")
async def serve_root():
    """Serve the main HTML file"""
    try:
        return FileResponse(
            "../guess-game.html",
            media_type="text/html"
        )
    except Exception as e:
        logger.error(f"Failed to serve root HTML: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/style.css")
async def serve_css():
    """Serve the CSS file"""
    try:
        return FileResponse(
            "../style.css",
            media_type="text/css"
        )
    except Exception as e:
        logger.error(f"Failed to serve CSS: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/Guess-game.app.js")
async def serve_app_js():
    """Serve the main application JavaScript"""
    try:
        return FileResponse(
            "../Guess-game.app.js",
            media_type="application/javascript"
        )
    except Exception as e:
        logger.error(f"Failed to serve app.js: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/audio-converter.js")
async def serve_audio_converter():
    """Serve the audio converter JavaScript"""
    try:
        return FileResponse(
            "../audio-converter.js",
            media_type="application/javascript"
        )
    except Exception as e:
        logger.error(f"Failed to serve audio-converter.js: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors"""
    logger.warning(f"404 Not Found: {request.url}")
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": "Endpoint tidak ditemukan"}
        )
    return FileResponse("../guess-game.html")  # Redirect all other 404s to the main app

@app.post("/api/speech")
async def process_speech(file: UploadFile = File(...)):
    """
    Process speech from uploaded audio file
    """
    temp_path = f"temp/{int(time.time())}_{file.filename}"
    try:
        # Save uploaded file
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Validate and process audio
        audio_info = audio_processor.validate_and_normalize(temp_path)
        
        # Perform speech recognition
        result = speech_service.recognize_speech(temp_path)
        
        return {
            "status": "success",
            "text": result["text"],
            "confidence": result.get("confidence", 0.0),
            "language": result.get("language", "id-ID"),
            "duration": audio_info["duration"],
            "choice_type": result.get("choice_type"),
            "interpreted_value": result.get("interpreted_value")
        }
        
    except GameError as e:
        logger.error(f"Game error occurred: {e.error_code} - {e.detail}")
        return JSONResponse(
            status_code=e.status_code,
            content=e.to_dict()
        )
    except (AudioProcessingError, InvalidAudioFormat) as e:
        logger.error(f"Audio processing error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": str(e)}
        )
    except Exception as e:
        logger.exception("Unexpected error during speech processing")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": {"code": "INTERNAL_SERVER_ERROR", "message": "Terjadi kesalahan internal. Silakan coba lagi.", "status": 500}}
        )
    finally:
        # Cleanup temporary file
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                logger.debug(f"Cleaned up temporary file: {temp_path}")
            except Exception as e:
                logger.error(f"Failed to cleanup temporary file {temp_path}: {str(e)}")

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "timestamp": time.time()}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors
    """
    logger.warning(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"status": "error", "message": "Format permintaan tidak valid"}
    )
