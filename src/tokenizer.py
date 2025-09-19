"""
Tokenization utilities for text-to-image generation
This module handles text processing and tokenization for the models.
"""

import torch
from transformers import CLIPTokenizer, AutoTokenizer
from config import TOKENIZER_CONFIG

class TextProcessor:
    """Class for processing and tokenizing text prompts"""
    
    def __init__(self, model_name="openai/clip-vit-base-patch32"):
        """
        Initialize the text processor
        
        Args:
            model_name (str): Name of the tokenizer model to use
        """
        self.model_name = model_name
        self.tokenizer = None
        self.load_tokenizer()
    
    def load_tokenizer(self):
        """Load the tokenizer"""
        try:
            print(f"📝 Loading tokenizer: {self.model_name}")
            self.tokenizer = CLIPTokenizer.from_pretrained(self.model_name)
            print("✅ Tokenizer loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading tokenizer: {e}")
            # Fallback to a basic tokenizer
            try:
                self.tokenizer = AutoTokenizer.from_pretrained("openai/clip-vit-base-patch32")
                print("✅ Fallback tokenizer loaded!")
            except:
                raise Exception("Failed to load any tokenizer")
    
    def preprocess_text(self, text):
        """
        Preprocess text prompt for better generation
        
        Args:
            text (str): Input text prompt
            
        Returns:
            str: Preprocessed text
        """
        # Basic text cleaning
        text = text.strip()
        
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Ensure text is not empty
        if not text:
            text = "a simple image"
        
        return text
    
    def tokenize_text(self, text, return_tensors="pt"):
        """
        Tokenize text for model input
        
        Args:
            text (str or list): Text prompt(s) to tokenize
            return_tensors (str): Format for returned tensors
            
        Returns:
            dict: Tokenized text ready for model input
        """
        if isinstance(text, str):
            text = self.preprocess_text(text)
        elif isinstance(text, list):
            text = [self.preprocess_text(t) for t in text]
        
        # Tokenize with the configured settings
        tokens = self.tokenizer(
            text,
            max_length=TOKENIZER_CONFIG["max_length"],
            padding=TOKENIZER_CONFIG["padding"],
            truncation=TOKENIZER_CONFIG["truncation"],
            return_tensors=return_tensors
        )
        
        return tokens
    
    def encode_prompt(self, prompt):
        """
        Encode a text prompt for generation
        
        Args:
            prompt (str): Text prompt to encode
            
        Returns:
            torch.Tensor: Encoded prompt
        """
        tokens = self.tokenize_text(prompt)
        return tokens["input_ids"]
    
    def decode_tokens(self, token_ids):
        """
        Decode token IDs back to text
        
        Args:
            token_ids (torch.Tensor): Token IDs to decode
            
        Returns:
            str: Decoded text
        """
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)
    
    def get_prompt_embeddings(self, prompts, text_encoder, device="cpu"):
        """
        Get text embeddings for prompts using a text encoder
        
        Args:
            prompts (list): List of text prompts
            text_encoder: Text encoder model
            device (str): Device to run on
            
        Returns:
            torch.Tensor: Text embeddings
        """
        # Tokenize prompts
        tokens = self.tokenize_text(prompts)
        input_ids = tokens["input_ids"].to(device)
        
        # Get embeddings
        with torch.no_grad():
            embeddings = text_encoder(input_ids)[0]
        
        return embeddings
    
    def create_prompt_variations(self, base_prompt, variations=None):
        """
        Create variations of a prompt for better generation
        
        Args:
            base_prompt (str): Base text prompt
            variations (list): List of variation patterns
            
        Returns:
            list: List of prompt variations
        """
        if variations is None:
            variations = [
                "high quality, detailed",
                "photorealistic, 8k resolution",
                "artistic, beautiful",
                "professional photography",
                "masterpiece, best quality"
            ]
        
        # Create variations by adding modifiers
        prompt_variations = [base_prompt]
        
        for variation in variations:
            prompt_variations.append(f"{base_prompt}, {variation}")
        
        return prompt_variations
    
    def extract_keywords(self, text):
        """
        Extract key terms from text for dataset categorization
        
        Args:
            text (str): Input text
            
        Returns:
            list: List of keywords
        """
        # Simple keyword extraction
        common_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "being"
        }
        
        words = text.lower().split()
        keywords = [word for word in words if word not in common_words and len(word) > 2]
        
        return list(set(keywords))  # Remove duplicates


def create_negative_prompt(style="general"):
    """
    Create negative prompts for better image quality
    
    Args:
        style (str): Style of negative prompt
        
    Returns:
        str: Negative prompt
    """
    negative_prompts = {
        "general": "blurry, low quality, distorted, deformed, bad anatomy, bad proportions",
        "portrait": "blurry, low quality, bad face, deformed face, extra limbs, bad anatomy",
        "landscape": "blurry, low quality, distorted horizon, bad composition, oversaturated",
        "object": "blurry, low quality, deformed, bad shape, unrealistic proportions"
    }
    
    return negative_prompts.get(style, negative_prompts["general"])


def enhance_prompt(prompt, style="realistic"):
    """
    Enhance a prompt with quality modifiers
    
    Args:
        prompt (str): Original prompt
        style (str): Style of enhancement
        
    Returns:
        str: Enhanced prompt
    """
    enhancements = {
        "realistic": "photorealistic, high quality, detailed, 8k resolution",
        "artistic": "artistic, beautiful, masterpiece, high quality",
        "professional": "professional photography, studio lighting, high quality",
        "cinematic": "cinematic lighting, dramatic, high quality, film photography"
    }
    
    enhancement = enhancements.get(style, enhancements["realistic"])
    return f"{prompt}, {enhancement}"


def main():
    """Test the text processor"""
    processor = TextProcessor()
    
    # Test prompts
    test_prompts = [
        "dog",
        "human",
        "a beautiful landscape",
        "portrait of a person"
    ]
    
    print("🧪 Testing text processor...")
    
    for prompt in test_prompts:
        print(f"\n📝 Original: '{prompt}'")
        
        # Preprocess
        preprocessed = processor.preprocess_text(prompt)
        print(f"🔄 Preprocessed: '{preprocessed}'")
        
        # Enhance
        enhanced = enhance_prompt(preprocessed)
        print(f"✨ Enhanced: '{enhanced}'")
        
        # Get negative prompt
        negative = create_negative_prompt()
        print(f"❌ Negative: '{negative}'")
        
        # Tokenize
        tokens = processor.tokenize_text(enhanced)
        print(f"🔢 Tokens shape: {tokens['input_ids'].shape}")


if __name__ == "__main__":
    main()