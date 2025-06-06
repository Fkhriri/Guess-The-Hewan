import wave
import numpy as np
import time
import os
from loguru import logger
from typing import Dict, Any
from errors import AudioProcessingError, AudioTooLong, InvalidAudioFormat

class AudioProcessor:
    """
    Audio processing utilities for the speech recognition system
    """
    
    def __init__(self):
        self.sample_rate = 16000  # Standard sample rate for speech recognition
        self.channels = 1  # Mono audio
        self.sampwidth = 2  # 16-bit audio
        self.audio_dir = "./audio_logs"  # Directory for saving audio logs
        os.makedirs(self.audio_dir, exist_ok=True)  # Create directory if it doesn't exist
    
    def cleanup_old_files(self):
        """Clean up old temporary files"""
        try:
            current_time = time.time()
            # Clean up files older than 1 hour
            for root, dirs, files in os.walk(self.audio_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Skip if file doesn't exist (might have been deleted)
                    if not os.path.exists(file_path):
                        continue
                    # Get file creation time
                    creation_time = os.path.getctime(file_path)
                    if current_time - creation_time > 3600:  # 1 hour
                        try:
                            os.remove(file_path)
                            logger.debug(f"Cleaned up old file: {file_path}")
                        except Exception as e:
                            logger.error(f"Failed to clean up {file_path}: {str(e)}")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    def validate_and_normalize(self, audio_path: str) -> Dict[str, Any]:
        """
        Validate audio file and return its properties
        """
        try:
            # Clean up old files first
            self.cleanup_old_files()
            
            with wave.open(audio_path, 'rb') as wave_file:
                # Get audio properties
                params = wave_file.getparams()
                frames = wave_file.readframes(params.nframes)
                
                # Convert to numpy array
                audio_data = np.frombuffer(frames, dtype=np.int16)
                  # Calculate audio metrics
                total_duration = params.nframes / float(params.framerate)
                frame_cutoff = min(int(5.0 * params.framerate), params.nframes)  # Cut at 5 seconds
                
                # Trim audio data to 5 seconds if longer
                audio_data = audio_data[:frame_cutoff]
                duration = frame_cutoff / float(params.framerate)
                
                # Calculate metrics on trimmed audio
                max_amplitude = np.max(np.abs(audio_data))
                average_energy = np.mean(audio_data * audio_data)
                
                # Validate audio properties
                try:
                    # Check duration limits
                    if total_duration > 6.0:  # Allow recording up to 6 seconds
                        raise AudioTooLong()
                    
                    if duration < 0.1:
                        logger.warning(f"Audio too short: {duration:.2f}s")
                        raise AudioProcessingError("Rekaman terlalu pendek. Minimal 0.1 detik.")

                    # Check amplitude with exception suppression
                    try:
                        if max_amplitude < 100:
                            logger.warning(f"Audio amplitude too low: {max_amplitude}")
                            raise AudioProcessingError("Volume suara terlalu kecil. Mohon bicara lebih keras.")
                    except IndentationError:
                        pass  # Suppress any indentation errors here
                        
                    if average_energy < 1000:
                        logger.warning(f"Audio energy too low: {average_energy}")
                        raise AudioProcessingError("Suara tidak terdeteksi. Mohon bicara lebih jelas.")
                except AudioProcessingError as e:
                    raise e
                
                logger.info(f"Audio validation successful - Duration: {duration:.2f}s, Max amplitude: {max_amplitude}, Energy: {average_energy}")
                return {
                    "duration": duration,
                    "max_amplitude": max_amplitude,
                    "average_energy": average_energy,
                    "sample_rate": params.framerate,
                    "channels": params.nchannels,
                    "sample_width": params.sampwidth
                }
        except wave.Error as e:
            logger.error(f"Invalid audio format: {str(e)}")
            raise InvalidAudioFormat()
        except AudioTooLong as e:
            logger.warning(f"Audio too long: {str(e)}")
            raise e
        except AudioProcessingError as e:
            logger.error(f"Audio processing error: {str(e)}")
            raise e
        except Exception as e:
            logger.exception("Unexpected error during audio validation")
            raise AudioProcessingError(f"Gagal memproses audio: {str(e)}")
    
    def is_silence(self, audio_path: str, threshold: float = 500) -> bool:
        """
        Check if the audio file contains only silence
        """
        try:
            with wave.open(audio_path, 'rb') as wave_file:
                params = wave_file.getparams()
                frames = wave_file.readframes(params.nframes)
                audio_data = np.frombuffer(frames, dtype=np.int16)
                
                # Calculate RMS amplitude
                rms = np.sqrt(np.mean(audio_data * audio_data))
                
                logger.debug(f"Audio RMS: {rms}, Threshold: {threshold}")
                
                return rms < threshold
                
        except Exception as e:
            logger.error(f"Error checking silence: {str(e)}", exc_info=True)
            raise AudioProcessingError(f"Error checking audio quality: {str(e)}")
    
    def convert_to_optimal_format(self, audio_path: str, output_path: str) -> str:
        """
        Convert audio to optimal format for speech recognition
        """
        try:
            with wave.open(audio_path, 'rb') as wave_file:
                params = wave_file.getparams()
                frames = wave_file.readframes(params.nframes)
                
                # Convert to mono if needed
                if params.nchannels > 1:
                    audio_data = np.frombuffer(frames, dtype=np.int16)
                    audio_data = audio_data.reshape(-1, params.nchannels)
                    mono_data = np.mean(audio_data, axis=1, dtype=np.int16)
                    
                    with wave.open(output_path, 'wb') as out_file:
                        out_file.setnchannels(1)
                        out_file.setsampwidth(params.sampwidth)
                        out_file.setframerate(params.framerate)
                        out_file.writeframes(mono_data.tobytes())
                        
                    logger.info(f"Converted audio to mono: {output_path}")
                    return output_path
                
                return audio_path
                
        except Exception as e:
            logger.error(f"Error converting audio format: {str(e)}", exc_info=True)
            raise AudioProcessingError(f"Error optimizing audio: {str(e)}")
