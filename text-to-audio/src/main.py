"""
Main Text-to-Audio Conversion Application

This is the main application that combines text processing, TTS model integration,
and audio output to provide a complete text-to-speech solution.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import logging
from datetime import datetime

# Add src directory to path
sys.path.append(str(Path(__file__).parent))

from text_processor import TextProcessor
from tts_model import TTSModelManager
from audio_processor import AudioProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextToAudioConverter:
    """
    Complete text-to-audio conversion system.
    
    This class provides a high-level interface for converting text to audio
    using the best available TTS models and processing techniques.
    """
    
    def __init__(
        self,
        model_name: str = "microsoft/speecht5_tts",
        output_dir: str = "output",
        device: Optional[str] = None
    ):
        """
        Initialize the text-to-audio converter.
        
        Args:
            model_name: Name of the TTS model to use
            output_dir: Directory for output audio files
            device: Device to run models on ('cpu', 'cuda', or None for auto)
        """
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.device = device
        
        # Initialize components
        self.text_processor = None
        self.tts_model = None
        self.audio_processor = None
        
        # Configuration
        self.config = {
            "max_text_length": 500,
            "audio_format": "wav",
            "normalize_audio": True,
            "apply_fade": True,
            "noise_reduction": False,
            "concatenate_segments": True,
            "segment_gap_ms": 500
        }
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all processing components."""
        try:
            logger.info("Initializing text-to-audio converter...")
            
            # Initialize text processor
            self.text_processor = TextProcessor(self.model_name)
            logger.info("Text processor initialized")
            
            # Initialize TTS model
            self.tts_model = TTSModelManager(self.model_name, self.device)
            logger.info("TTS model initialized")
            
            # Initialize audio processor
            self.audio_processor = AudioProcessor(str(self.output_dir))
            logger.info("Audio processor initialized")
            
            logger.info("Text-to-audio converter ready!")
            
        except Exception as e:
            logger.error(f"Failed to initialize converter: {e}")
            raise
    
    def convert_text(
        self,
        text: str,
        output_filename: Optional[str] = None,
        **kwargs
    ) -> Optional[str]:
        """
        Convert text to audio file.
        
        Args:
            text: Input text to convert
            output_filename: Custom output filename (optional)
            **kwargs: Additional processing options
            
        Returns:
            Path to generated audio file or None if failed
        """
        if not text or not text.strip():
            logger.error("No text provided for conversion")
            return None
        
        try:
            logger.info(f"Converting text to audio: '{text[:50]}...'")
            
            # Validate text
            if not self.text_processor.validate_text(text):
                logger.error("Text validation failed")
                return None
            
            # Process text
            processed_chunks = self.text_processor.preprocess_for_tts(
                text, 
                max_length=self.config["max_text_length"]
            )
            
            if not processed_chunks:
                logger.error("Text processing produced no output")
                return None
            
            logger.info(f"Text processed into {len(processed_chunks)} chunks")
            
            # Generate audio for each chunk
            audio_segments = []
            sample_rate = self.tts_model.get_sample_rate()
            
            for i, chunk in enumerate(processed_chunks):
                logger.info(f"Synthesizing chunk {i+1}/{len(processed_chunks)}")
                
                audio = self.tts_model.synthesize_speech(chunk)
                
                if audio is not None:
                    audio_segments.append(audio)
                else:
                    logger.warning(f"Failed to synthesize chunk {i+1}")
            
            if not audio_segments:
                logger.error("No audio generated from any text chunks")
                return None
            
            # Combine audio segments
            if len(audio_segments) > 1 and self.config["concatenate_segments"]:
                logger.info("Concatenating audio segments")
                combined_audio = self.audio_processor.concatenate_audio(
                    audio_segments,
                    gap_ms=self.config["segment_gap_ms"],
                    sample_rate=sample_rate
                )
            else:
                combined_audio = audio_segments[0]
            
            # Apply post-processing
            processed_audio = self._post_process_audio(combined_audio, sample_rate)
            
            # Generate output filename
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                word_count = len(text.split())
                output_filename = f"tts_output_{word_count}words_{timestamp}"
            
            # Save audio
            output_path = self.audio_processor.save_audio(
                processed_audio,
                output_filename,
                sample_rate,
                format=self.config["audio_format"],
                normalize=self.config["normalize_audio"]
            )
            
            logger.info(f"Text-to-audio conversion completed: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Text-to-audio conversion failed: {e}")
            return None
    
    def _post_process_audio(self, audio_data, sample_rate):
        """Apply post-processing to audio data."""
        processed_audio = audio_data.copy()
        
        # Apply noise reduction if enabled
        if self.config["noise_reduction"]:
            processed_audio = self.audio_processor.apply_noise_reduction(
                processed_audio, sample_rate, strength=0.3
            )
        
        # Apply fade in/out if enabled
        if self.config["apply_fade"]:
            processed_audio = self.audio_processor.apply_fade(
                processed_audio, sample_rate=sample_rate
            )
        
        return processed_audio
    
    def convert_batch(
        self,
        texts: List[str],
        output_prefix: str = "batch"
    ) -> List[str]:
        """
        Convert multiple texts to audio files.
        
        Args:
            texts: List of input texts
            output_prefix: Prefix for output filenames
            
        Returns:
            List of paths to generated audio files
        """
        output_paths = []
        
        for i, text in enumerate(texts):
            try:
                filename = f"{output_prefix}_{i+1:03d}"
                output_path = self.convert_text(text, filename)
                
                if output_path:
                    output_paths.append(output_path)
                    logger.info(f"Batch item {i+1}/{len(texts)} completed")
                else:
                    logger.warning(f"Batch item {i+1}/{len(texts)} failed")
                    
            except Exception as e:
                logger.error(f"Batch item {i+1} failed: {e}")
                continue
        
        logger.info(f"Batch conversion completed: {len(output_paths)}/{len(texts)} successful")
        return output_paths
    
    def convert_questions_and_answers(
        self,
        qa_pairs: List[Dict[str, str]],
        include_questions: bool = True
    ) -> List[str]:
        """
        Convert question-answer pairs to audio.
        
        Args:
            qa_pairs: List of dicts with 'question' and 'answer' keys
            include_questions: Whether to include questions in audio
            
        Returns:
            List of paths to generated audio files
        """
        output_paths = []
        
        for i, qa_pair in enumerate(qa_pairs):
            try:
                question = qa_pair.get('question', '')
                answer = qa_pair.get('answer', '')
                
                if include_questions and question:
                    full_text = f"Question: {question}. Answer: {answer}"
                else:
                    full_text = answer
                
                filename = f"qa_{i+1:03d}"
                output_path = self.convert_text(full_text, filename)
                
                if output_path:
                    output_paths.append(output_path)
                    logger.info(f"Q&A pair {i+1}/{len(qa_pairs)} completed")
                
            except Exception as e:
                logger.error(f"Q&A pair {i+1} failed: {e}")
                continue
        
        return output_paths
    
    def play_audio_file(self, file_path: str) -> bool:
        """
        Play an audio file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            True if playback started successfully
        """
        try:
            audio_data, sample_rate = self.audio_processor.load_audio(file_path)
            return self.audio_processor.play_audio(audio_data, sample_rate)
        except Exception as e:
            logger.error(f"Failed to play audio file {file_path}: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get information about the current system configuration."""
        tts_info = self.tts_model.get_model_info() if self.tts_model else {}
        
        info = {
            "model_name": self.model_name,
            "output_dir": str(self.output_dir),
            "device": self.device,
            "config": self.config.copy(),
            "tts_model_info": tts_info,
            "components_initialized": {
                "text_processor": self.text_processor is not None,
                "tts_model": self.tts_model is not None,
                "audio_processor": self.audio_processor is not None
            }
        }
        
        return info
    
    def update_config(self, **kwargs):
        """Update configuration parameters."""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                logger.info(f"Updated config: {key} = {value}")
            else:
                logger.warning(f"Unknown config parameter: {key}")
    
    def switch_model(self, model_name: str) -> bool:
        """
        Switch to a different TTS model.
        
        Args:
            model_name: Name of the new model
            
        Returns:
            True if successful
        """
        try:
            success = self.tts_model.switch_model(model_name)
            if success:
                self.model_name = model_name
                # Reinitialize text processor with new model
                self.text_processor = TextProcessor(model_name)
            return success
        except Exception as e:
            logger.error(f"Failed to switch model: {e}")
            return False
    
    def cleanup(self):
        """Clean up all resources."""
        if self.tts_model:
            self.tts_model.cleanup()
        if self.audio_processor:
            self.audio_processor.cleanup()
        logger.info("Text-to-audio converter cleaned up")


def main():
    """Example usage of the TextToAudioConverter."""
    print("Text-to-Audio Converter Demo")
    print("=" * 40)
    
    # Initialize converter
    converter = TextToAudioConverter()
    
    # Get system info
    info = converter.get_system_info()
    print(f"System Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    print()
    
    # Example 1: Simple text conversion
    print("Example 1: Simple text conversion")
    text1 = "Hello! Welcome to our text-to-speech demonstration. This system can convert any text into high-quality audio."
    
    output_path1 = converter.convert_text(text1, "demo_simple")
    if output_path1:
        print(f"✓ Audio saved to: {output_path1}")
    else:
        print("✗ Conversion failed")
    
    # Example 2: Question and answer format
    print("\nExample 2: Question and Answer conversion")
    qa_pairs = [
        {
            "question": "What is artificial intelligence?",
            "answer": "Artificial intelligence is the simulation of human intelligence in machines that are programmed to think and learn like humans."
        },
        {
            "question": "How does text-to-speech work?",
            "answer": "Text-to-speech systems analyze written text and convert it into spoken words using linguistic rules and audio synthesis techniques."
        }
    ]
    
    qa_outputs = converter.convert_questions_and_answers(qa_pairs)
    print(f"✓ Generated {len(qa_outputs)} Q&A audio files")
    
    # Example 3: Batch conversion
    print("\nExample 3: Batch text conversion")
    batch_texts = [
        "Good morning! Today is a beautiful day.",
        "Technology is advancing rapidly in the 21st century.",
        "Thank you for using our text-to-speech system!"
    ]
    
    batch_outputs = converter.convert_batch(batch_texts, "batch_demo")
    print(f"✓ Generated {len(batch_outputs)} batch audio files")
    
    # Example 4: Configuration update
    print("\nExample 4: Configuration update and long text")
    converter.update_config(
        audio_format="wav",
        apply_fade=True,
        noise_reduction=True
    )
    
    long_text = """
    This is a longer text example to demonstrate how the system handles extended content.
    The text-to-speech system will automatically break this into smaller chunks for better processing.
    Each chunk will be processed separately and then combined into a single audio file.
    This approach ensures high-quality output even for lengthy documents.
    """
    
    output_long = converter.convert_text(long_text.strip(), "demo_long")
    if output_long:
        print(f"✓ Long text audio saved to: {output_long}")
    
    # List all generated files
    print(f"\nGenerated files in {converter.output_dir}:")
    if converter.output_dir.exists():
        for file_path in converter.output_dir.glob("*.wav"):
            print(f"  - {file_path.name}")
    
    # Cleanup
    converter.cleanup()
    print("\nDemo completed!")


if __name__ == "__main__":
    main()