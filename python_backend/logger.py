from loguru import logger
import os
import sys
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)
os.makedirs("logs/audio", exist_ok=True)

# Remove default logger
logger.remove()

# Add stdout logging with custom format
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# Add file logger for all logs
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="500 MB",
    retention="30 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    level="DEBUG",
    backtrace=True,
    diagnose=True
)

# Add separate logger for audio processing
logger.add(
    "logs/audio/processing_{time:YYYY-MM-DD}.log",
    rotation="100 MB",
    retention="7 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[request_id]} | {message}",
    filter=lambda record: "audio" in record["extra"],
    level="DEBUG"
)

# Create a context manager for request logging
class RequestLoggingContext:
    def __init__(self):
        self.request_id = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        
    def __enter__(self):
        logger.configure(extra={"request_id": self.request_id})
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.configure(extra={"request_id": None})
