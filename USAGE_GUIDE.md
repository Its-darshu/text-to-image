# 🎨 Text-to-Image Generation - Complete Usage Guide

This project provides a complete text-to-image generation system with fine-tuning capabilities. You can generate images from text prompts like "dog" → dog image, "human" → human image, etc.

## 🚀 Quick Start

### 1. Basic Setup
```bash
# Navigate to project directory
cd text-to-image

# Install all dependencies
python setup.py

# Create sample dataset
python create_dataset_simple.py
```

### 2. Demo Mode (Recommended for Testing)
```bash
# Run the demo interface (works without GPU)
python demo.py
```
This creates a web interface at `http://localhost:7860` with demo functionality.

### 3. Full Generation (Requires Model Download)
```bash
# For basic image generation
python main.py generate "a cute dog playing in a park"

# Launch full web interface
python main.py interface
```

## 📂 Project Structure

```
text-to-image/
├── main.py                 # Main CLI interface
├── demo.py                 # Demo interface (CPU-friendly)
├── setup.py                # Installation script
├── create_dataset_simple.py # Simple dataset creation
├── requirements.txt        # Dependencies
├── src/
│   ├── config.py          # Model configurations
│   ├── generator.py       # Image generation core
│   ├── tokenizer.py       # Text processing
│   ├── dataset.py         # Dataset handling
│   ├── fine_tuner.py      # Model fine-tuning
│   └── app.py             # Web interface
├── data/
│   ├── train/             # Training images and CSV
│   └── validation/        # Validation data
└── outputs/
    ├── generated/         # Generated images
    └── models/            # Fine-tuned models
```

## 🎯 Usage Examples

### Text Prompts
The system supports various types of prompts:

**Simple prompts:**
- `"dog"` → Generates a dog image
- `"human"` → Generates a human portrait
- `"car"` → Generates a car image
- `"landscape"` → Generates a landscape

**Detailed prompts:**
- `"a cute golden retriever playing in a sunny park"`
- `"a professional portrait of a smiling person"`
- `"a red sports car on a city street at sunset"`
- `"a beautiful mountain landscape with trees and a lake"`

### Command Line Usage

#### Generate Images
```bash
# Basic generation
python main.py generate "your prompt here"

# Advanced options
python main.py generate "a beautiful landscape" \
    --negative-prompt "blurry, low quality" \
    --num-images 2 \
    --seed 42
```

#### Create Training Dataset
```bash
# Create sample dataset
python main.py dataset

# Or use the simple version
python create_dataset_simple.py
```

#### Fine-tune Model
```bash
# Basic fine-tuning
python main.py finetune

# Custom settings
python main.py finetune \
    --epochs 5 \
    --learning-rate 1e-4 \
    --model small_stable_diffusion
```

### Web Interface Usage

#### Demo Interface (Recommended)
```bash
python demo.py
```
- Works without GPU
- Creates demo images with text overlay
- Good for testing and understanding the workflow

#### Full Interface
```bash
python main.py interface
```
- Requires model download (several GB)
- Real AI image generation
- Full fine-tuning capabilities

## 🔧 Configuration

### Model Selection
Edit `src/config.py` to choose models:

```python
# Available models
MODELS = {
    "flux_schnell": {          # Fast, high quality
        "name": "black-forest-labs/FLUX.1-schnell",
        "inference_steps": 4,
        "width": 1024,
        "height": 1024
    },
    "small_stable_diffusion": { # Good for fine-tuning
        "name": "OFA-Sys/small-stable-diffusion-v0",
        "inference_steps": 20,
        "width": 512,
        "height": 512
    },
    "cpu_compatible": {        # Works on CPU
        "name": "CompVis/stable-diffusion-v1-4",
        "inference_steps": 10,
        "width": 512,
        "height": 512
    }
}

# Change default model
DEFAULT_MODEL = "cpu_compatible"  # For CPU usage
```

### Fine-tuning Settings
```python
FINE_TUNE_CONFIG = {
    "learning_rate": 1e-4,
    "batch_size": 1,           # Keep small for memory
    "num_epochs": 10,
    "resolution": 512,
    "max_train_steps": 1000
}
```

## 📊 Dataset Format

### Training Data Structure
```
data/train/
├── dataset.csv           # Text-image mappings
├── sample_1.jpg         # Image files
├── sample_2.jpg
└── ...
```

### CSV Format
```csv
text,image_path,category
"a cute dog playing in the park",sample_1.jpg,animal
"a professional portrait of a human",sample_2.jpg,human
"a beautiful landscape with mountains",sample_3.jpg,landscape
```

### Adding Custom Data
1. Add images to `data/train/`
2. Update `data/train/dataset.csv`
3. Run fine-tuning: `python main.py finetune`

## 🖥️ Hardware Requirements

### Minimum (Demo Mode)
- CPU: Any modern processor
- RAM: 4GB
- Storage: 2GB free space
- Internet: For initial setup

### Recommended (Full Generation)
- CPU: Multi-core processor
- RAM: 8GB+ (16GB preferred)
- GPU: 6GB+ VRAM (optional but faster)
- Storage: 10GB+ free space

### GPU Setup (Optional)
For faster generation:
```bash
# Install CUDA-compatible PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Install xformers for memory efficiency
pip install xformers
```

## 🐛 Troubleshooting

### Common Issues

**1. xformers/CUDA Errors (Windows)**
```bash
# Solution: Use CPU-compatible mode
python demo.py  # Use demo instead
```

**2. Model Download Fails**
```bash
# Clear cache and retry
rm -rf ~/.cache/huggingface/
python setup.py
```

**3. Out of Memory**
- Use smaller models (`cpu_compatible`)
- Reduce batch size in config
- Use CPU mode instead of GPU

**4. Slow Generation**
- Use `flux_schnell` model (4 steps only)
- Reduce image resolution
- Use GPU if available

### Error Messages

**"DLL load failed"** → Use demo mode or CPU-compatible models
**"CUDA out of memory"** → Reduce batch size or use CPU
**"Model not found"** → Check internet connection and retry setup
**"Permission denied"** → Run with administrator privileges

## 📈 Performance Tips

### Speed Optimization
1. **Use fast models**: `flux_schnell` (4 steps)
2. **Reduce resolution**: 512x512 instead of 1024x1024
3. **GPU acceleration**: Install CUDA if you have NVIDIA GPU
4. **Batch processing**: Generate multiple images at once

### Quality Optimization
1. **Detailed prompts**: "a professional portrait of a smiling woman with natural lighting"
2. **Negative prompts**: "blurry, low quality, distorted"
3. **Style keywords**: "photorealistic, 8k, detailed, masterpiece"
4. **Fine-tuning**: Train on your specific style/content

### Memory Optimization
1. **Smaller batch sizes**: batch_size=1
2. **CPU offloading**: Enabled automatically
3. **Lower precision**: fp16 instead of fp32
4. **Model checkpointing**: Save progress frequently

## 🎓 Advanced Usage

### Custom Model Training
1. Collect 10-50 high-quality images per category
2. Create proper text descriptions
3. Use consistent naming and style
4. Start with few epochs (2-5) and adjust

### Prompt Engineering
**Good prompts:**
- "a cute golden retriever puppy playing in a sunny park, photorealistic, high quality"
- "professional headshot of a business person, studio lighting, sharp focus"

**Avoid:**
- Too short: "dog"
- Too complex: Multiple unrelated concepts
- Contradictory: "realistic cartoon"

### Batch Processing
```python
# Generate multiple variations
prompts = ["dog", "cat", "bird"]
for prompt in prompts:
    python main.py generate f"{prompt}, cute, photorealistic"
```

## 🔗 Integration

### Use in Other Projects
```python
from src.generator import TextToImageGenerator

# Initialize
generator = TextToImageGenerator()

# Generate
images, paths = generator.generate_and_save("your prompt")
```

### API Usage
The web interface can be extended with REST API endpoints for integration with other applications.

## 📚 Additional Resources

- **Models**: [Hugging Face Diffusers](https://huggingface.co/models?library=diffusers)
- **Prompting**: [Prompt Engineering Guide](https://www.promptingguide.ai/)
- **Fine-tuning**: [Diffusers Training](https://huggingface.co/docs/diffusers/training/overview)

---

**Need help?** Check the troubleshooting section or create an issue with your specific error message and system info.