from fastapi import HTTPException
from typing import Dict, Any

class GameError(HTTPException):
    def __init__(self, status_code: int, detail: str, error_code: str = None):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": False,
            "error": {
                "code": self.error_code,
                "message": self.detail,
                "status": self.status_code
            }
        }

class AudioProcessingError(GameError):
    def __init__(self, detail: str):
        super().__init__(
            status_code=400,
            detail=detail,
            error_code="AUDIO_PROCESSING_ERROR"
        )

class InvalidAudioFormat(GameError):
    def __init__(self):
        super().__init__(
            status_code=415,
            detail="Format audio tidak valid. Mohon gunakan format WAV.",
            error_code="INVALID_AUDIO_FORMAT"
        )

class AudioTooLong(GameError):
    def __init__(self):
        super().__init__(
            status_code=413,
            detail="Durasi rekaman terlalu panjang. Maksimal 5 detik.",
            error_code="AUDIO_TOO_LONG"
        )

class SpeechRecognitionError(GameError):
    def __init__(self, detail: str):
        super().__init__(
            status_code=422,
            detail=detail,
            error_code="SPEECH_RECOGNITION_ERROR"
        )

class RateLimitExceeded(GameError):
    def __init__(self):
        super().__init__(
            status_code=429,
            detail="Terlalu banyak permintaan. Silakan coba lagi nanti.",
            error_code="RATE_LIMIT_EXCEEDED"
        )
