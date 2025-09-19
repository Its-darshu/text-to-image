"""
Text-to-Image Model Configuration
This module contains configuration settings for the lightweight text-to-image models.
"""

# Model configurations
MODELS = {
    "flux_schnell": {
        "name": "black-forest-labs/FLUX.1-schnell",
        "type": "diffusers",
        "description": "Fast and lightweight FLUX model for quick generation",
        "inference_steps": 4,  # Very fast
        "guidance_scale": 0.0,  # No guidance needed for schnell
        "width": 1024,
        "height": 1024
    },
    "small_stable_diffusion": {
        "name": "OFA-Sys/small-stable-diffusion-v0",
        "type": "diffusers", 
        "description": "Small version of Stable Diffusion for lightweight usage",
        "inference_steps": 20,
        "guidance_scale": 7.5,
        "width": 512,
        "height": 512
    },
    "cpu_compatible": {
        "name": "CompVis/stable-diffusion-v1-4",
        "type": "diffusers",
        "description": "CPU-compatible Stable Diffusion model",
        "inference_steps": 10,  # Reduced for CPU
        "guidance_scale": 7.5,
        "width": 512,
        "height": 512
    }
}

# Default model to use (CPU-compatible)
DEFAULT_MODEL = "cpu_compatible"

# Fine-tuning settings
FINE_TUNE_CONFIG = {
    "learning_rate": 1e-4,
    "batch_size": 1,
    "num_epochs": 10,
    "gradient_accumulation_steps": 4,
    "max_train_steps": 1000,
    "validation_steps": 100,
    "save_steps": 500,
    "resolution": 512,
    "center_crop": True,
    "random_flip": True
}

# Tokenizer settings
TOKENIZER_CONFIG = {
    "max_length": 77,
    "padding": "max_length",
    "truncation": True,
    "return_tensors": "pt"
}

# Output settings
OUTPUT_CONFIG = {
    "save_directory": "outputs/generated",
    "image_format": "PNG",
    "quality": 95
}