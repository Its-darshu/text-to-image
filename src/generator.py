"""
Text-to-Image Generator using lightweight models
This module provides functionality to generate images from text prompts.
"""

import torch
import os
from PIL import Image
from datetime import datetime
from diffusers import DiffusionPipeline
from transformers import CLIPTokenizer
import warnings

from config import MODELS, DEFAULT_MODEL, OUTPUT_CONFIG, TOKENIZER_CONFIG

warnings.filterwarnings("ignore")

class TextToImageGenerator:
    """Main class for text-to-image generation"""
    
    def __init__(self, model_name=None, device=None):
        """
        Initialize the text-to-image generator
        
        Args:
            model_name (str): Name of the model to use (from config)
            device (str): Device to run the model on ('cuda', 'cpu', 'mps')
        """
        self.model_name = model_name or DEFAULT_MODEL
        self.device = device or self._get_best_device()
        self.model_config = MODELS[self.model_name]
        self.pipeline = None
        self.tokenizer = None
        
        print(f"🚀 Initializing Text-to-Image Generator")
        print(f"📱 Model: {self.model_config['name']}")
        print(f"🖥️  Device: {self.device}")
        
    def _get_best_device(self):
        """Automatically detect the best available device"""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    
    def load_model(self):
        """Load the diffusion model and tokenizer"""
        try:
            print("📥 Loading model...")
            
            # Load the diffusion pipeline
            self.pipeline = DiffusionPipeline.from_pretrained(
                self.model_config["name"],
                torch_dtype=torch.float16 if self.device != "cpu" else torch.float32,
                trust_remote_code=True
            )
            
            # Move to device
            self.pipeline = self.pipeline.to(self.device)
            
            # Enable memory efficient attention if available
            try:
                if hasattr(self.pipeline, "enable_xformers_memory_efficient_attention"):
                    self.pipeline.enable_xformers_memory_efficient_attention()
            except Exception as e:
                print(f"⚠️  xformers not available (CPU mode): {e}")
                pass
            
            # Enable CPU offload for memory efficiency
            try:
                if self.device == "cuda":
                    self.pipeline.enable_sequential_cpu_offload()
            except Exception as e:
                print(f"⚠️  CPU offload not available: {e}")
                pass
            
            print("✅ Model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def generate_image(self, prompt, negative_prompt=None, num_images=1, seed=None):
        """
        Generate images from text prompt
        
        Args:
            prompt (str): Text description of the image to generate
            negative_prompt (str): Text describing what to avoid in the image
            num_images (int): Number of images to generate
            seed (int): Random seed for reproducible results
            
        Returns:
            list: List of PIL Image objects
        """
        if self.pipeline is None:
            self.load_model()
        
        # Set random seed if provided
        if seed is not None:
            torch.manual_seed(seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed(seed)
        
        print(f"🎨 Generating image for: '{prompt}'")
        
        try:
            # Prepare generation parameters
            generation_kwargs = {
                "prompt": prompt,
                "num_images_per_prompt": num_images,
                "num_inference_steps": self.model_config["inference_steps"],
                "width": self.model_config["width"],
                "height": self.model_config["height"]
            }
            
            # Add guidance scale if supported by the model
            if self.model_config["guidance_scale"] > 0:
                generation_kwargs["guidance_scale"] = self.model_config["guidance_scale"]
            
            # Add negative prompt if provided and supported
            if negative_prompt and "guidance_scale" in generation_kwargs:
                generation_kwargs["negative_prompt"] = negative_prompt
            
            # Generate images
            with torch.autocast(self.device):
                result = self.pipeline(**generation_kwargs)
            
            images = result.images
            print(f"✅ Generated {len(images)} image(s)!")
            
            return images
            
        except Exception as e:
            print(f"❌ Error generating image: {e}")
            raise
    
    def save_images(self, images, prompt, output_dir=None):
        """
        Save generated images to disk
        
        Args:
            images (list): List of PIL Image objects
            prompt (str): Original prompt used for generation
            output_dir (str): Directory to save images
            
        Returns:
            list: List of saved file paths
        """
        if output_dir is None:
            output_dir = OUTPUT_CONFIG["save_directory"]
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a safe filename from the prompt
        safe_prompt = "".join(c for c in prompt if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_prompt = safe_prompt[:50]  # Limit length
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        saved_paths = []
        
        for i, image in enumerate(images):
            filename = f"{safe_prompt}_{timestamp}_{i+1}.{OUTPUT_CONFIG['image_format'].lower()}"
            filepath = os.path.join(output_dir, filename)
            
            image.save(filepath, format=OUTPUT_CONFIG['image_format'], quality=OUTPUT_CONFIG['quality'])
            saved_paths.append(filepath)
            print(f"💾 Saved: {filepath}")
        
        return saved_paths
    
    def generate_and_save(self, prompt, negative_prompt=None, num_images=1, seed=None, output_dir=None):
        """
        Generate images and save them to disk
        
        Args:
            prompt (str): Text description of the image to generate
            negative_prompt (str): Text describing what to avoid in the image
            num_images (int): Number of images to generate
            seed (int): Random seed for reproducible results
            output_dir (str): Directory to save images
            
        Returns:
            tuple: (list of PIL Images, list of saved file paths)
        """
        images = self.generate_image(prompt, negative_prompt, num_images, seed)
        saved_paths = self.save_images(images, prompt, output_dir)
        return images, saved_paths


def main():
    """Example usage of the TextToImageGenerator"""
    # Create generator
    generator = TextToImageGenerator()
    
    # Example prompts
    test_prompts = [
        "a cute dog playing in a sunny park",
        "a professional portrait of a human smiling", 
        "a beautiful landscape with mountains and trees",
        "a modern car on a city street"
    ]
    
    print("🎯 Testing the generator with example prompts...")
    
    for prompt in test_prompts:
        try:
            images, paths = generator.generate_and_save(
                prompt=prompt,
                num_images=1,
                seed=42  # For reproducible results
            )
            print(f"✅ Successfully generated image for: '{prompt}'")
            print(f"📁 Saved to: {paths[0]}")
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Failed to generate image for '{prompt}': {e}")
            print("-" * 50)


if __name__ == "__main__":
    main()