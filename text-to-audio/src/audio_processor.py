"""
Audio Processilogging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional pygame import for audio playback
PYGAME_AVAILABLE = False
pygame = None

try:
    import pygame
    PYGAME_AVAILABLE = True
    logger.debug("Pygame imported successfully")
except ImportError as e:
    PYGAME_AVAILABLE = False
    logger.warning(f"Pygame not available: {e}. Audio playback will be limited.")

This module handles audio output, file saving, format conversion, 
and playback functionality for the text-to-audio system.
"""

import numpy as np
import soundfile as sf
import librosa
from scipy import signal
from scipy.io import wavfile
import os
import tempfile
from typing import Optional, Union, List, Tuple, Dict, Any, TYPE_CHECKING
from pathlib import Path
import logging
from datetime import datetime

if TYPE_CHECKING:
    import pygame

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Try to import pygame for audio playback
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    logger.warning("Pygame not available. Audio playback will be limited.")


class AudioProcessor:
    """
    Comprehensive audio processing class for handling TTS output.
    
    Features:
    - Audio file I/O in multiple formats
    - Audio format conversion
    - Audio post-processing (normalization, filtering)
    - Playback functionality
    - Batch processing
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the audio processor.
        
        Args:
            output_dir: Directory to save output audio files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Supported audio formats
        self.supported_formats = {
            'wav': 'WAV',
            'mp3': 'MP3',
            'flac': 'FLAC',
            'ogg': 'OGG'
        }
        
        # Initialize pygame mixer for playback
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self.playback_available = True
                logger.info("Audio playback initialized")
            except Exception as e:
                logger.warning(f"Could not initialize audio playback: {e}")
                self.playback_available = False
        else:
            self.playback_available = False
    
    def save_audio(
        self,
        audio_data: np.ndarray,
        filename: str,
        sample_rate: int = 16000,
        format: str = 'wav',
        normalize: bool = True
    ) -> str:
        """
        Save audio data to file.
        
        Args:
            audio_data: Audio array to save
            filename: Output filename (without extension)
            sample_rate: Audio sample rate
            format: Output format ('wav', 'mp3', 'flac', 'ogg')
            normalize: Whether to normalize audio
            
        Returns:
            Path to saved file
        """
        if audio_data is None or len(audio_data) == 0:
            raise ValueError("No audio data provided")
        
        # Ensure audio data is in the right format
        audio_data = np.array(audio_data, dtype=np.float32)
        
        # Normalize audio if requested
        if normalize:
            audio_data = self.normalize_audio(audio_data)
        
        # Ensure filename has no extension
        filename = Path(filename).stem
        
        # Create full output path
        output_path = self.output_dir / f"{filename}.{format}"
        
        try:
            if format.lower() == 'wav':
                # Use soundfile for WAV
                sf.write(str(output_path), audio_data, sample_rate)
            else:
                # Use soundfile for other formats too
                sf.write(str(output_path), audio_data, sample_rate, format=format.upper())
            
            logger.info(f"Audio saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            raise
    
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """
        Load audio from file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        try:
            audio_data, sample_rate = sf.read(file_path, dtype=np.float32)
            logger.info(f"Loaded audio from: {file_path}")
            return audio_data, sample_rate
        except Exception as e:
            logger.error(f"Failed to load audio from {file_path}: {e}")
            raise
    
    def normalize_audio(self, audio_data: np.ndarray, target_level: float = -3.0) -> np.ndarray:
        """
        Normalize audio to target loudness level.
        
        Args:
            audio_data: Input audio array
            target_level: Target level in dB
            
        Returns:
            Normalized audio array
        """
        if len(audio_data) == 0:
            return audio_data
        
        # Calculate RMS
        rms = np.sqrt(np.mean(audio_data ** 2))
        
        if rms > 0:
            # Calculate normalization factor
            target_rms = 10 ** (target_level / 20)
            normalization_factor = target_rms / rms
            
            # Apply normalization
            normalized = audio_data * normalization_factor
            
            # Prevent clipping
            max_val = np.max(np.abs(normalized))
            if max_val > 1.0:
                normalized = normalized / max_val
            
            return normalized
        else:
            return audio_data
    
    def apply_fade(
        self, 
        audio_data: np.ndarray, 
        fade_in_ms: int = 50, 
        fade_out_ms: int = 50,
        sample_rate: int = 16000
    ) -> np.ndarray:
        """
        Apply fade-in and fade-out to audio.
        
        Args:
            audio_data: Input audio array
            fade_in_ms: Fade-in duration in milliseconds
            fade_out_ms: Fade-out duration in milliseconds
            sample_rate: Audio sample rate
            
        Returns:
            Audio with fades applied
        """
        if len(audio_data) == 0:
            return audio_data
        
        audio_copy = audio_data.copy()
        
        # Calculate fade lengths in samples
        fade_in_samples = int(fade_in_ms * sample_rate / 1000)
        fade_out_samples = int(fade_out_ms * sample_rate / 1000)
        
        # Apply fade-in
        if fade_in_samples > 0 and fade_in_samples < len(audio_copy):
            fade_in = np.linspace(0, 1, fade_in_samples)
            audio_copy[:fade_in_samples] *= fade_in
        
        # Apply fade-out
        if fade_out_samples > 0 and fade_out_samples < len(audio_copy):
            fade_out = np.linspace(1, 0, fade_out_samples)
            audio_copy[-fade_out_samples:] *= fade_out
        
        return audio_copy
    
    def resample_audio(
        self, 
        audio_data: np.ndarray, 
        original_rate: int, 
        target_rate: int
    ) -> np.ndarray:
        """
        Resample audio to target sample rate.
        
        Args:
            audio_data: Input audio array
            original_rate: Original sample rate
            target_rate: Target sample rate
            
        Returns:
            Resampled audio array
        """
        if original_rate == target_rate:
            return audio_data
        
        try:
            resampled = librosa.resample(
                audio_data, 
                orig_sr=original_rate, 
                target_sr=target_rate
            )
            logger.info(f"Resampled audio from {original_rate}Hz to {target_rate}Hz")
            return resampled
        except Exception as e:
            logger.error(f"Failed to resample audio: {e}")
            return audio_data
    
    def apply_noise_reduction(
        self, 
        audio_data: np.ndarray, 
        sample_rate: int,
        strength: float = 0.5
    ) -> np.ndarray:
        """
        Apply basic noise reduction using spectral subtraction.
        
        Args:
            audio_data: Input audio array
            sample_rate: Audio sample rate
            strength: Noise reduction strength (0.0 to 1.0)
            
        Returns:
            Noise-reduced audio array
        """
        if len(audio_data) == 0 or strength <= 0:
            return audio_data
        
        try:
            # Simple high-pass filter to reduce low-frequency noise
            nyquist = sample_rate / 2
            cutoff = 80  # Hz
            normalized_cutoff = cutoff / nyquist
            
            # Design high-pass filter
            b, a = signal.butter(4, normalized_cutoff, btype='high', analog=False)
            
            # Apply filter
            filtered_audio = signal.filtfilt(b, a, audio_data)
            
            # Blend with original based on strength
            result = (1 - strength) * audio_data + strength * filtered_audio
            
            return result.astype(np.float32)
            
        except Exception as e:
            logger.warning(f"Noise reduction failed: {e}")
            return audio_data
    
    def concatenate_audio(
        self, 
        audio_segments: List[np.ndarray], 
        gap_ms: int = 500,
        sample_rate: int = 16000
    ) -> np.ndarray:
        """
        Concatenate multiple audio segments with gaps.
        
        Args:
            audio_segments: List of audio arrays to concatenate
            gap_ms: Gap between segments in milliseconds
            sample_rate: Audio sample rate
            
        Returns:
            Concatenated audio array
        """
        if not audio_segments:
            return np.array([])
        
        if len(audio_segments) == 1:
            return audio_segments[0]
        
        # Calculate gap length in samples
        gap_samples = int(gap_ms * sample_rate / 1000)
        gap_audio = np.zeros(gap_samples, dtype=np.float32)
        
        # Concatenate with gaps
        result = audio_segments[0]
        
        for segment in audio_segments[1:]:
            result = np.concatenate([result, gap_audio, segment])
        
        return result
    
    def play_audio(self, audio_data: np.ndarray, sample_rate: int = 16000) -> bool:
        """
        Play audio using pygame.
        
        Args:
            audio_data: Audio array to play
            sample_rate: Audio sample rate
            
        Returns:
            True if playback started successfully, False otherwise
        """
        if not self.playback_available:
            logger.warning("Audio playback not available")
            return False
        
        try:
            # Handle different audio shapes
            if len(audio_data.shape) > 1:
                # If stereo or multi-channel, take first channel
                audio_data = audio_data[:, 0] if audio_data.shape[1] > 0 else audio_data.flatten()
            
            # Ensure audio is 1D
            audio_data = audio_data.flatten()
            
            # Normalize audio to prevent clipping
            if np.max(np.abs(audio_data)) > 0:
                audio_data = audio_data / np.max(np.abs(audio_data)) * 0.95
            
            # Convert to 16-bit integers
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                wavfile.write(temp_file.name, sample_rate, audio_int16)
                temp_path = temp_file.name
            
            # Reinitialize pygame mixer with correct settings
            try:
                pygame.mixer.quit()
                pygame.mixer.init(frequency=sample_rate, size=-16, channels=1, buffer=1024)
            except:
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=1024)
            
            # Play using pygame
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            
            logger.info("Audio playback started successfully")
            
            # Wait a moment for playback to start
            import time
            time.sleep(0.1)
            
            return True
            
        except Exception as e:
            logger.error(f"Audio playback failed: {e}")
            return False
    
    def get_audio_info(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """
        Get information about audio data.
        
        Args:
            audio_data: Audio array
            sample_rate: Audio sample rate
            
        Returns:
            Dictionary with audio information
        """
        if len(audio_data) == 0:
            return {"error": "No audio data"}
        
        duration = len(audio_data) / sample_rate
        rms = np.sqrt(np.mean(audio_data ** 2))
        peak = np.max(np.abs(audio_data))
        
        info = {
            "duration_seconds": duration,
            "sample_rate": sample_rate,
            "samples": len(audio_data),
            "channels": 1 if audio_data.ndim == 1 else audio_data.shape[1],
            "rms_level": rms,
            "peak_level": peak,
            "dynamic_range_db": 20 * np.log10(peak / rms) if rms > 0 else 0,
            "estimated_loudness_lufs": -23 + 20 * np.log10(rms) if rms > 0 else -np.inf
        }
        
        return info
    
    def batch_process_audio(
        self,
        audio_segments: List[np.ndarray],
        sample_rate: int,
        output_prefix: str = "audio",
        processing_options: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Process and save multiple audio segments.
        
        Args:
            audio_segments: List of audio arrays
            sample_rate: Audio sample rate
            output_prefix: Prefix for output filenames
            processing_options: Dictionary with processing options
            
        Returns:
            List of output file paths
        """
        options = processing_options or {}
        
        normalize = options.get('normalize', True)
        apply_fade = options.get('apply_fade', True)
        noise_reduction = options.get('noise_reduction', False)
        format = options.get('format', 'wav')
        
        output_paths = []
        
        for i, audio in enumerate(audio_segments):
            try:
                # Apply processing
                processed_audio = audio.copy()
                
                if noise_reduction:
                    processed_audio = self.apply_noise_reduction(
                        processed_audio, sample_rate, strength=0.3
                    )
                
                if apply_fade:
                    processed_audio = self.apply_fade(
                        processed_audio, sample_rate=sample_rate
                    )
                
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{output_prefix}_{i+1:03d}_{timestamp}"
                
                # Save audio
                output_path = self.save_audio(
                    processed_audio,
                    filename,
                    sample_rate,
                    format,
                    normalize
                )
                
                output_paths.append(output_path)
                
            except Exception as e:
                logger.error(f"Failed to process audio segment {i+1}: {e}")
                continue
        
        logger.info(f"Processed {len(output_paths)} audio segments")
        return output_paths
    
    def cleanup(self):
        """Clean up resources."""
        if PYGAME_AVAILABLE and pygame.mixer.get_init():
            pygame.mixer.quit()
        logger.info("Audio processor cleaned up")


def main():
    """Example usage of the AudioProcessor."""
    print("Audio Processing Example")
    print("=" * 30)
    
    # Initialize processor
    processor = AudioProcessor()
    
    # Generate sample audio (sine wave)
    sample_rate = 16000
    duration = 2.0  # seconds
    frequency = 440  # Hz (A4 note)
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    sample_audio = 0.3 * np.sin(2 * np.pi * frequency * t)
    
    print(f"Generated sample audio: {len(sample_audio)} samples at {sample_rate} Hz")
    
    # Get audio info
    info = processor.get_audio_info(sample_audio, sample_rate)
    print(f"Audio info: {info}")
    
    # Apply processing
    processed_audio = processor.apply_fade(sample_audio, sample_rate=sample_rate)
    processed_audio = processor.normalize_audio(processed_audio)
    
    # Save audio
    output_path = processor.save_audio(
        processed_audio, 
        "sample_audio", 
        sample_rate,
        format='wav'
    )
    
    print(f"Audio saved to: {output_path}")
    
    # Try to play audio
    if processor.playback_available:
        print("Playing audio...")
        processor.play_audio(processed_audio, sample_rate)
    else:
        print("Audio playback not available")
    
    # Cleanup
    processor.cleanup()
    print("Done!")


if __name__ == "__main__":
    main()