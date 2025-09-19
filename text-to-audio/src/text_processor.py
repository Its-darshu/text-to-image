"""
Text Processing Module for Text-to-Audio Conversion

This module provides comprehensive text preprocessing and tokenization
utilities for preparing text input for text-to-speech models.
"""

import re
import string
import nltk
from typing import List, Optional, Dict, Any
from transformers import AutoTokenizer
import logging

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextProcessor:
    """
    A comprehensive text processor for preparing text input for TTS models.
    
    Features:
    - Text cleaning and normalization
    - Tokenization
    - Sentence segmentation
    - Special character handling
    - Number and abbreviation expansion
    """
    
    def __init__(self, model_name: str = "microsoft/speecht5_tts"):
        """
        Initialize the text processor.
        
        Args:
            model_name: The name of the TTS model to use for tokenization
        """
        self.model_name = model_name
        self.tokenizer = None
        self._load_tokenizer()
        
        # Define text normalization patterns
        self.abbreviations = {
            "dr.": "doctor",
            "mr.": "mister", 
            "mrs.": "misses",
            "ms.": "miss",
            "prof.": "professor",
            "st.": "street",
            "ave.": "avenue",
            "blvd.": "boulevard",
            "etc.": "etcetera",
            "vs.": "versus",
            "e.g.": "for example",
            "i.e.": "that is",
        }
        
        # Number to word mapping for basic numbers
        self.numbers = {
            "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
            "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine",
            "10": "ten", "11": "eleven", "12": "twelve", "13": "thirteen",
            "14": "fourteen", "15": "fifteen", "16": "sixteen", "17": "seventeen",
            "18": "eighteen", "19": "nineteen", "20": "twenty"
        }
    
    def _load_tokenizer(self):
        """Load the tokenizer for the specified model."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            logger.info(f"Loaded tokenizer for {self.model_name}")
        except Exception as e:
            logger.warning(f"Could not load tokenizer for {self.model_name}: {e}")
            logger.info("Will proceed with basic text processing")
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text for TTS processing.
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned and normalized text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Expand abbreviations
        for abbr, expansion in self.abbreviations.items():
            text = text.replace(abbr, expansion)
        
        # Handle basic number expansion
        words = text.split()
        expanded_words = []
        
        for word in words:
            # Remove punctuation for checking
            clean_word = word.strip(string.punctuation)
            if clean_word in self.numbers:
                # Preserve surrounding punctuation
                prefix = word[:len(word) - len(word.lstrip(string.punctuation))]
                suffix = word[len(word.rstrip(string.punctuation)):]
                expanded_words.append(prefix + self.numbers[clean_word] + suffix)
            else:
                expanded_words.append(word)
        
        text = ' '.join(expanded_words)
        
        # Handle special characters
        text = self._handle_special_characters(text)
        
        # Final cleanup
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _handle_special_characters(self, text: str) -> str:
        """Handle special characters and symbols."""
        # Replace common symbols with words
        replacements = {
            '&': ' and ',
            '@': ' at ',
            '#': ' hash ',
            '$': ' dollar ',
            '%': ' percent ',
            '+': ' plus ',
            '=': ' equals ',
            '<': ' less than ',
            '>': ' greater than ',
            '|': ' or ',
        }
        
        for symbol, replacement in replacements.items():
            text = text.replace(symbol, replacement)
        
        # Remove remaining special characters that might cause issues
        text = re.sub(r'[^\w\s\.,!?\-\']', ' ', text)
        
        return text
    
    def segment_sentences(self, text: str) -> List[str]:
        """
        Segment text into sentences for better TTS processing.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        try:
            sentences = nltk.sent_tokenize(text)
            return [s.strip() for s in sentences if s.strip()]
        except Exception as e:
            logger.warning(f"NLTK sentence tokenization failed: {e}")
            # Fallback to simple sentence splitting
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]
    
    def tokenize_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Tokenize text using the model's tokenizer.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            Tokenization results or None if tokenizer not available
        """
        if not self.tokenizer:
            logger.warning("No tokenizer available")
            return None
        
        try:
            tokens = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )
            return tokens
        except Exception as e:
            logger.error(f"Tokenization failed: {e}")
            return None
    
    def preprocess_for_tts(self, text: str, max_length: int = 500) -> List[str]:
        """
        Complete preprocessing pipeline for TTS input.
        
        Args:
            text: Raw input text
            max_length: Maximum length for each text segment
            
        Returns:
            List of processed text segments ready for TTS
        """
        # Clean the text
        cleaned_text = self.clean_text(text)
        
        # Segment into sentences
        sentences = self.segment_sentences(cleaned_text)
        
        # Group sentences into chunks that don't exceed max_length
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + " " + sentence) <= max_length:
                current_chunk = (current_chunk + " " + sentence).strip()
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def validate_text(self, text: str) -> bool:
        """
        Validate that text is suitable for TTS processing.
        
        Args:
            text: Text to validate
            
        Returns:
            True if text is valid, False otherwise
        """
        if not text or not text.strip():
            return False
        
        # Check for minimum length
        if len(text.strip()) < 3:
            return False
        
        # Check for maximum length (reasonable for TTS)
        if len(text) > 5000:
            logger.warning("Text is very long, consider breaking it into smaller chunks")
        
        return True
    
    def get_text_stats(self, text: str) -> Dict[str, Any]:
        """
        Get statistics about the input text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with text statistics
        """
        cleaned_text = self.clean_text(text)
        sentences = self.segment_sentences(cleaned_text)
        words = cleaned_text.split()
        
        stats = {
            "original_length": len(text),
            "cleaned_length": len(cleaned_text),
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_words_per_sentence": len(words) / len(sentences) if sentences else 0,
            "has_numbers": bool(re.search(r'\d', text)),
            "has_special_chars": bool(re.search(r'[^\w\s]', text)),
        }
        
        return stats


def main():
    """Example usage of the TextProcessor."""
    processor = TextProcessor()
    
    # Example texts
    sample_texts = [
        "Hello! How are you today? I hope you're doing well.",
        "Dr. Smith lives on 123 Main St. He has 5 cats & 2 dogs.",
        "The temperature is 25°C. That's about 77°F.",
        "Please visit our website @ www.example.com for more info!"
    ]
    
    print("Text Processing Examples:")
    print("=" * 50)
    
    for i, text in enumerate(sample_texts, 1):
        print(f"\nExample {i}:")
        print(f"Original: {text}")
        
        # Clean text
        cleaned = processor.clean_text(text)
        print(f"Cleaned:  {cleaned}")
        
        # Get chunks for TTS
        chunks = processor.preprocess_for_tts(text)
        print(f"TTS Chunks: {chunks}")
        
        # Get statistics
        stats = processor.get_text_stats(text)
        print(f"Stats: {stats}")
        print("-" * 30)


if __name__ == "__main__":
    main()