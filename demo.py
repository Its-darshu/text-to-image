"""
Simple Text-to-Image Demo using Hugging Face API
This script demonstrates basic functionality without complex model loading.
"""

import os
import sys
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_huggingface_generation():
    """Test image generation using Hugging Face's hosted API"""
    try:
        # Test the HuggingFace MCP integration for image generation
        from mcp_huggingface_gr1_flux1_schnell_infer import mcp_huggingface_gr1_flux1_schnell_infer
        
        print("🎨 Testing image generation with Hugging Face API...")
        
        # Test prompts
        test_prompts = [
            "a cute dog playing in a sunny park",
            "a professional portrait of a human",
            "a beautiful landscape with mountains",
            "a modern car on a city street"
        ]
        
        for prompt in test_prompts:
            print(f"\\n📝 Generating: '{prompt}'")
            
            try:
                # This will use the MCP HuggingFace integration
                result = mcp_huggingface_gr1_flux1_schnell_infer(
                    prompt=prompt,
                    width=512,
                    height=512,
                    num_inference_steps=4
                )
                
                if result:
                    print(f"✅ Generated image for: '{prompt}'")
                else:
                    print(f"❌ Failed to generate image for: '{prompt}'")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except ImportError:
        print("⚠️  Hugging Face MCP not available, creating demo functionality...")
        create_demo_functionality()

def create_demo_functionality():
    """Create demo functionality without complex model loading"""
    print("🎯 Creating Text-to-Image Demo...")
    
    # Test dataset creation
    try:
        # Import our simple dataset creation
        exec(open('create_dataset_simple.py').read())
        print("✅ Dataset creation works!")
    except Exception as e:
        print(f"❌ Dataset creation error: {e}")
    
    # Test text processing
    try:
        from tokenizer import TextProcessor, enhance_prompt, create_negative_prompt
        
        processor = TextProcessor()
        
        test_prompts = ["dog", "human", "car", "landscape"]
        
        print("\\n🔤 Testing text processing...")
        for prompt in test_prompts:
            enhanced = enhance_prompt(prompt)
            negative = create_negative_prompt()
            print(f"Original: '{prompt}'")
            print(f"Enhanced: '{enhanced}'")
            print(f"Negative: '{negative}'")
            print("-" * 40)
            
        print("✅ Text processing works!")
        
    except Exception as e:
        print(f"❌ Text processing error: {e}")
    
    # Create a simple web interface demo
    create_simple_interface()

def create_simple_interface():
    """Create a simple interface demo"""
    print("\\n🌐 Creating simple web interface demo...")
    
    try:
        import gradio as gr
        
        def demo_generate(prompt, num_images=1):
            """Demo generation function"""
            if not prompt.strip():
                return [], "❌ Please enter a text prompt"
            
            # Create demo images (colored rectangles with text)
            from PIL import Image, ImageDraw, ImageFont
            
            images = []
            for i in range(num_images):
                # Create a colored image with the prompt text
                img = Image.new('RGB', (512, 512), (100 + i*50, 150, 200))
                draw = ImageDraw.Draw(img)
                
                try:
                    font = ImageFont.truetype("arial.ttf", 30)
                except:
                    font = ImageFont.load_default()
                
                # Split text into lines for better display
                lines = prompt.split()
                line_height = 40
                y = 200
                
                for j in range(0, len(lines), 3):  # 3 words per line
                    line = " ".join(lines[j:j+3])
                    try:
                        bbox = draw.textbbox((0, 0), line, font=font)
                        text_width = bbox[2] - bbox[0]
                    except:
                        text_width = len(line) * 15  # Fallback
                    
                    x = (512 - text_width) // 2
                    draw.text((x, y), line, fill=(255, 255, 255), font=font)
                    y += line_height
                
                # Add demo label
                draw.text((10, 10), f"DEMO IMAGE {i+1}", fill=(255, 255, 0), font=font)
                
                images.append(img)
            
            # Save images
            os.makedirs("outputs/generated", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            saved_paths = []
            
            for i, img in enumerate(images):
                filename = f"demo_{timestamp}_{i+1}.png"
                filepath = os.path.join("outputs/generated", filename)
                img.save(filepath)
                saved_paths.append(filepath)
            
            status = f"✅ Generated {len(images)} demo image(s)!\\nSaved to: {', '.join(saved_paths)}"
            return images, status
        
        # Create Gradio interface
        with gr.Blocks(title="Text-to-Image Demo") as demo:
            gr.HTML('<h1 style="text-align: center;">🎨 Text-to-Image Demo</h1>')
            gr.HTML('<p style="text-align: center;">This is a demo version. Real AI generation requires model setup.</p>')
            
            with gr.Row():
                with gr.Column():
                    prompt_input = gr.Textbox(
                        label="Text Prompt",
                        placeholder="Enter your text description (e.g., 'a cute dog')",
                        lines=3
                    )
                    
                    num_images_slider = gr.Slider(
                        minimum=1, maximum=4, value=1, step=1,
                        label="Number of Images"
                    )
                    
                    generate_btn = gr.Button("🎨 Generate Demo Images", variant="primary")
                
                with gr.Column():
                    output_gallery = gr.Gallery(
                        label="Generated Demo Images",
                        columns=2,
                        rows=2,
                        height="auto"
                    )
                    
                    status_output = gr.Textbox(
                        label="Status",
                        lines=3,
                        interactive=False
                    )
            
            gr.HTML('''
            <h3>📖 How to Setup Real AI Generation</h3>
            <ol>
                <li>Install compatible models (see README.md)</li>
                <li>For GPU: Install CUDA-compatible PyTorch and xformers</li>
                <li>For CPU: Use smaller models with fewer inference steps</li>
                <li>Run: <code>python main.py interface</code></li>
            </ol>
            ''')
            
            generate_btn.click(
                fn=demo_generate,
                inputs=[prompt_input, num_images_slider],
                outputs=[output_gallery, status_output]
            )
        
        print("✅ Demo interface created successfully!")
        print("🚀 Launching demo interface...")
        
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True
        )
        
    except Exception as e:
        print(f"❌ Interface creation error: {e}")
        print("\\n📝 You can still use the command line functions:")
        print("- Dataset creation: python create_dataset_simple.py")
        print("- Text processing test: python -c \"from src.tokenizer import *; print('Text processing works!')\"")

def main():
    """Main demo function"""
    print("🚀 Starting Text-to-Image Project Demo...")
    print("=" * 50)
    
    # Test environment
    print("🔍 Checking environment...")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Create directories if they don't exist
    os.makedirs("outputs/generated", exist_ok=True)
    os.makedirs("data/train", exist_ok=True)
    os.makedirs("data/validation", exist_ok=True)
    
    print("✅ Environment check completed!")
    
    # Try different approaches
    try:
        test_huggingface_generation()
    except Exception as e:
        print(f"⚠️  API generation not available: {e}")
        create_demo_functionality()

if __name__ == "__main__":
    main()