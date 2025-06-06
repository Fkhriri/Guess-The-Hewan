import speech_recognition as sr
from loguru import logger
import wave
from errors import AudioProcessingError, SpeechRecognitionError, InvalidAudioFormat, AudioTooLong
from typing import Dict, Any

class SpeechService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Adjust recognition parameters
        self.recognizer.energy_threshold = 300  # Minimum audio energy to consider
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8  # Seconds of non-speaking audio before phrase completion
        
        # Define letter mappings (including common variations)
        self.letter_mappings = {
            'a': ['a', 'ah', 'ay', 'ei'],
            'b': ['b', 'be', 'bee', 'bi'],
            'c': ['c', 'ce', 'see', 'si'],
            # Add more letters if needed
        }
        
        # Common word variations to normalize
        self.word_variations = {
            'satu': ['1', 'one', 'first', 'pertama'],
            'dua': ['2', 'two', 'second', 'kedua'],
            'tiga': ['3', 'three', 'third', 'ketiga'],
            # Add more numbers/words if needed
        }
        
        # Morphological corrections
        self.common_corrections = {
            # Number variations
            'wan': 'one', 'von': 'one',
            'tu': 'two', 'to': 'two',
            'tree': 'three', 'tri': 'three',
            
            # Indonesian number variations
            'satoe': 'satu', 'siji': 'satu',
            'loro': 'dua', 'roro': 'dua',
            'telu': 'tiga', 'tigo': 'tiga',
            
            # Letter variations
            'hey': 'a', 'eh': 'a',
            'bee': 'b', 'beh': 'b',
            'sie': 'c', 'shi': 'c',
            
            # Common misspellings
            'ya': 'iya', 'yah': 'iya',
            'nga': 'tidak', 'ngga': 'tidak',
            'gak': 'tidak', 'nggak': 'tidak'
        }
        
    def normalize_input(self, text: str) -> str:
        """Normalize input text to handle variations in speech recognition"""
        text = text.lower().strip()
        
        # Check for letter matches
        for letter, variations in self.letter_mappings.items():
            if text in variations:
                return letter.upper()
                
        # Check for word/number variations
        for word, variations in self.word_variations.items():
            if text in variations:
                return word
                
        return text
        
    def interpret_choice(self, text: str) -> Dict[str, Any]:
        """
        Interpret the recognized text as either an alphabet choice or content choice
        Returns a dictionary with the type of choice and the interpreted value
        """
        normalized = self.normalize_input(text)
        
        # Check if it's a single letter
        if len(normalized) == 1 and normalized.isalpha():
            return {
                "type": "alphabet",
                "value": normalized.upper(),
                "original": text
            }
            
        # Otherwise treat it as a content choice
        return {
            "type": "content",
            "value": normalized,
            "original": text
        }
        
    def validate_audio_file(self, audio_path: str) -> None:
        """Validate the audio file format and duration"""
        try:
            with wave.open(audio_path, 'rb') as wave_file:
                # Check duration
                frames = wave_file.getnframes()
                rate = wave_file.getframerate()
                duration = frames / float(rate)
                
                if duration > 5.5:  # Allow slight buffer over 5 seconds
                    raise AudioTooLong()
                
        except wave.Error:
            raise InvalidAudioFormat()
        
    def apply_morphological_corrections(self, text: str) -> str:
        """Apply morphological corrections to the text"""
        words = text.lower().split()
        corrected_words = []
        
        for word in words:
            # Apply corrections if available
            word = self.common_corrections.get(word, word)
            corrected_words.append(word)
            
        return ' '.join(corrected_words)
        
    def recognize_speech(self, audio_path: str) -> Dict[str, Any]:
        """
        Recognize speech from audio file using Google Speech Recognition
        Returns a standardized response dictionary with interpretation
        """
        max_retries = 2
        retry_count = 0
        
        try:
            # Validate audio file first
            self.validate_audio_file(audio_path)
            
            while retry_count <= max_retries:
                try:
                    with sr.AudioFile(audio_path) as source:
                        # Record audio for processing
                        audio = self.recognizer.record(source)
                        
                        # First try Indonesian
                        try:
                            text = self.recognizer.recognize_google(audio, language="id-ID")
                            text = self.apply_morphological_corrections(text)  # Apply corrections
                            choice = self.interpret_choice(text)
                            return {
                                "text": text,
                                "language": "id-ID",
                                "confidence": 0.8,  # Estimated confidence
                                "retries": retry_count,
                                "choice_type": choice["type"],
                                "interpreted_value": choice["value"]
                            }
                        except sr.UnknownValueError:
                            # Fallback to English
                            try:
                                text = self.recognizer.recognize_google(audio, language="en-US")
                                text = self.apply_morphological_corrections(text)  # Apply corrections
                                choice = self.interpret_choice(text)
                                return {
                                    "text": text,
                                    "language": "en-US",
                                    "confidence": 0.6,  # Lower confidence for fallback
                                    "retries": retry_count,
                                    "choice_type": choice["type"],
                                    "interpreted_value": choice["value"]
                                }
                            except sr.UnknownValueError:
                                if retry_count < max_retries:
                                    logger.warning(f"Speech not recognized, attempt {retry_count + 1}/{max_retries}")
                                    retry_count += 1
                                    continue
                                raise SpeechRecognitionError("Maaf, suara tidak dapat dikenali. Mohon coba lagi.")
                            
                except sr.RequestError as e:
                    if retry_count < max_retries:
                        logger.warning(f"API request failed, attempt {retry_count + 1}/{max_retries}: {str(e)}")
                        retry_count += 1
                        continue
                    raise SpeechRecognitionError("Layanan pengenalan suara sedang bermasalah. Mohon coba lagi nanti.")
                    
        except Exception as e:
            logger.exception("Unexpected error in speech recognition")
            raise SpeechRecognitionError(f"Terjadi kesalahan: {str(e)}")
            
        raise SpeechRecognitionError("Maaf, suara tidak dapat dikenali setelah beberapa percobaan.")
