"""
TTS Model Integration Module

This module provides integration with lightweight Hugging Face TTS models
for converting text to high-quality speech audio.
"""

import torch
import numpy as np
from typing import Optional, Union, List, Dict, Any
from transformers import (
    SpeechT5Processor, 
    SpeechT5ForTextToSpeech,
    VitsModel,
    VitsTokenizer
)
from datasets import load_dataset
import logging
import warnings
import os

# Suppress some warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TTSModelManager:
    """
    Manages multiple TTS models and provides a unified interface for text-to-speech conversion.
    
    Supported models:
    - Microsoft SpeechT5 TTS
    - Facebook MMS TTS
    - VITS models
    """
    
    def __init__(self, model_name: str = "microsoft/speecht5_tts", device: Optional[str] = None):
        """
        Initialize the TTS model manager.
        
        Args:
            model_name: Name of the TTS model to use
            device: Device to run the model on ('cpu', 'cuda', or None for auto-detection)
        """
        self.model_name = model_name
        self.device = device or self._get_device()
        self.model = None
        self.processor = None
        self.tokenizer = None
        self.vocoder = None
        self.speaker_embeddings = None
        
        # Model configuration
        self.model_configs = {
            "microsoft/speecht5_tts": {
                "type": "speecht5",
                "requires_speaker_embedding": True,
                "sample_rate": 16000
            },
            "facebook/mms-tts-eng": {
                "type": "vits",
                "requires_speaker_embedding": False,
                "sample_rate": 22050
            },
            "facebook/fastspeech2-en-ljspeech": {
                "type": "fastspeech2",
                "requires_speaker_embedding": False,
                "sample_rate": 22050
            }
        }
        
        self._load_model()
    
    def _get_device(self) -> str:
        """Automatically detect the best available device."""
        if torch.cuda.is_available():
            device = "cuda"
            logger.info(f"Using GPU: {torch.cuda.get_device_name()}")
        else:
            device = "cpu"
            logger.info("Using CPU for inference")
        return device
    
    def _load_model(self):
        """Load the specified TTS model and processor."""
        try:
            logger.info(f"Loading model: {self.model_name}")
            
            if self.model_name.startswith("microsoft/speecht5"):
                self._load_speecht5_model()
            elif "mms-tts" in self.model_name or "vits" in self.model_name.lower():
                self._load_vits_model()
            else:
                # Try to load as SpeechT5 by default
                self._load_speecht5_model()
                
            logger.info(f"Successfully loaded {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            logger.info("Falling back to default model...")
            self.model_name = "microsoft/speecht5_tts"
            self._load_speecht5_model()
    
    def _load_speecht5_model(self):
        """Load Microsoft SpeechT5 TTS model."""
        self.processor = SpeechT5Processor.from_pretrained(self.model_name)
        self.model = SpeechT5ForTextToSpeech.from_pretrained(self.model_name)
        self.model.to(self.device)
        
        # Load default speaker embeddings
        self._load_speaker_embeddings()
    
    def _load_vits_model(self):
        """Load VITS-based TTS model."""
        self.model = VitsModel.from_pretrained(self.model_name)
        self.tokenizer = VitsTokenizer.from_pretrained(self.model_name)
        self.model.to(self.device)
    
    def _load_speaker_embeddings(self):
        """Load speaker embeddings for models that require them."""
        try:
            # Load speaker embeddings from CMU Arctic dataset
            embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
            self.speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)
            logger.info("Loaded default speaker embeddings")
        except Exception as e:
            logger.warning(f"Could not load speaker embeddings: {e}")
            # Create dummy speaker embeddings as fallback
            self.speaker_embeddings = torch.randn(1, 512)
    
    def synthesize_speech(
        self, 
        text: str, 
        speaker_id: Optional[int] = None,
        speed: float = 1.0,
        pitch: float = 1.0
    ) -> Optional[np.ndarray]:
        """
        Convert text to speech audio.
        
        Args:
            text: Input text to convert
            speaker_id: Speaker ID for multi-speaker models
            speed: Speech speed multiplier (1.0 = normal)
            pitch: Pitch multiplier (1.0 = normal)
            
        Returns:
            Audio array or None if synthesis failed
        """
        if not self.model:
            logger.error("No model loaded")
            return None
        
        if not text or not text.strip():
            logger.warning("Empty text provided")
            return None
        
        try:
            if self.model_name.startswith("microsoft/speecht5"):
                return self._synthesize_speecht5(text, speaker_id)
            elif "mms-tts" in self.model_name or "vits" in self.model_name.lower():
                return self._synthesize_vits(text)
            else:
                return self._synthesize_speecht5(text, speaker_id)
                
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            return None
    
    def _synthesize_speecht5(self, text: str, speaker_id: Optional[int] = None) -> Optional[np.ndarray]:
        """Synthesize speech using SpeechT5 model."""
        try:
            # Process text in smaller chunks for better quality
            if len(text) > 200:
                # Split into sentences for better audio quality
                sentences = text.replace('!', '.').replace('?', '.').split('.')
                sentences = [s.strip() for s in sentences if s.strip()]
                
                audio_chunks = []
                for sentence in sentences:
                    if len(sentence) > 5:  # Skip very short segments
                        chunk_audio = self._synthesize_single_chunk(sentence)
                        if chunk_audio is not None:
                            audio_chunks.append(chunk_audio)
                
                if audio_chunks:
                    # Add small pause between sentences
                    pause_samples = np.zeros(int(0.3 * 16000))  # 0.3 second pause
                    result = audio_chunks[0]
                    for chunk in audio_chunks[1:]:
                        result = np.concatenate([result, pause_samples, chunk])
                    return result
            
            return self._synthesize_single_chunk(text)
            
        except Exception as e:
            logger.error(f"SpeechT5 synthesis failed: {e}")
            return None
    
    def _synthesize_single_chunk(self, text: str) -> Optional[np.ndarray]:
        """Synthesize a single chunk of text."""
        try:
            # Tokenize input text
            inputs = self.processor(text=text, return_tensors="pt")
            input_ids = inputs["input_ids"].to(self.device)
            
            # Use speaker embeddings - ensure correct shape
            speaker_emb = self.speaker_embeddings.to(self.device)
            
            # Ensure speaker embedding has correct shape and select first speaker
            if len(speaker_emb.shape) > 1:
                speaker_emb = speaker_emb[0:1]  # Take first speaker embedding
            else:
                speaker_emb = speaker_emb.unsqueeze(0)
            
            # Generate speech
            with torch.no_grad():
                speech = self.model.generate_speech(input_ids, speaker_emb, vocoder=None)
            
            result = speech.cpu().numpy()
            
            # Ensure result is 1D and properly shaped
            if len(result.shape) > 1:
                result = result.flatten()
            
            # Add slight fade in/out for smoother audio
            if len(result) > 1000:
                fade_samples = min(500, len(result) // 10)
                fade_in = np.linspace(0, 1, fade_samples)
                fade_out = np.linspace(1, 0, fade_samples)
                result[:fade_samples] *= fade_in
                result[-fade_samples:] *= fade_out
            
            return result
            
        except Exception as e:
            logger.warning(f"Single chunk synthesis failed: {e}")
            return None
    
    def _synthesize_vits(self, text: str) -> Optional[np.ndarray]:
        """Synthesize speech using VITS model."""
        # Tokenize input text
        inputs = self.tokenizer(text, return_tensors="pt")
        input_ids = inputs["input_ids"].to(self.device)
        
        # Generate speech
        with torch.no_grad():
            output = self.model(input_ids)
            audio = output.waveform
        
        return audio.cpu().numpy().squeeze()
    
    def get_sample_rate(self) -> int:
        """Get the sample rate for the current model."""
        config = self.model_configs.get(self.model_name, {})
        return config.get("sample_rate", 16000)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        config = self.model_configs.get(self.model_name, {})
        
        info = {
            "model_name": self.model_name,
            "device": self.device,
            "model_type": config.get("type", "unknown"),
            "sample_rate": config.get("sample_rate", 16000),
            "requires_speaker_embedding": config.get("requires_speaker_embedding", False),
            "loaded": self.model is not None
        }
        
        return info
    
    def list_available_models(self) -> List[str]:
        """List all available TTS models."""
        return list(self.model_configs.keys())
    
    def switch_model(self, model_name: str) -> bool:
        """
        Switch to a different TTS model.
        
        Args:
            model_name: Name of the new model to load
            
        Returns:
            True if successful, False otherwise
        """
        if model_name == self.model_name:
            logger.info(f"Model {model_name} is already loaded")
            return True
        
        try:
            # Clear current model
            self.model = None
            self.processor = None
            self.tokenizer = None
            
            # Load new model
            self.model_name = model_name
            self._load_model()
            return True
            
        except Exception as e:
            logger.error(f"Failed to switch to model {model_name}: {e}")
            return False
    
    def batch_synthesize(self, texts: List[str]) -> List[Optional[np.ndarray]]:
        """
        Synthesize speech for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of audio arrays
        """
        results = []
        
        for i, text in enumerate(texts):
            logger.info(f"Processing text {i+1}/{len(texts)}")
            audio = self.synthesize_speech(text)
            results.append(audio)
        
        return results
    
    def estimate_duration(self, text: str) -> float:
        """
        Estimate the duration of synthesized speech for the given text.
        
        Args:
            text: Input text
            
        Returns:
            Estimated duration in seconds
        """
        # Rough estimation: average speaking rate is about 150-160 words per minute
        words = len(text.split())
        estimated_duration = (words / 150) * 60  # seconds
        
        return estimated_duration
    
    def cleanup(self):
        """Clean up model resources."""
        if self.model:
            del self.model
        if self.processor:
            del self.processor
        if self.tokenizer:
            del self.tokenizer
        
        # Clear GPU cache if using CUDA
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info("Model resources cleaned up")


def main():
    """Example usage of the TTSModelManager."""
    print("TTS Model Integration Example")
    print("=" * 40)
    
    # Initialize TTS model
    tts = TTSModelManager()
    
    # Get model info
    info = tts.get_model_info()
    print(f"Model Info: {info}")
    
    # Example texts
    sample_texts = [
        "Hello, this is a test of the text to speech system.",
        "The weather is beautiful today!",
        "How are you doing? I hope you're having a great day."
    ]
    
    print("\nSynthesizing sample texts...")
    
    for i, text in enumerate(sample_texts, 1):
        print(f"\nText {i}: {text}")
        
        # Estimate duration
        duration = tts.estimate_duration(text)
        print(f"Estimated duration: {duration:.2f} seconds")
        
        # Synthesize speech
        audio = tts.synthesize_speech(text)
        
        if audio is not None:
            print(f"Generated audio shape: {audio.shape}")
            print(f"Sample rate: {tts.get_sample_rate()} Hz")
        else:
            print("Failed to generate audio")
    
    # List available models
    available_models = tts.list_available_models()
    print(f"\nAvailable models: {available_models}")
    
    # Cleanup
    tts.cleanup()
    print("\nDone!")


if __name__ == "__main__":
    main()