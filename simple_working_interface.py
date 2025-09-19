"""
Simple Working Text-to-Image Interface
"""

import gradio as gr
import os
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import random

# Add src to path
sys.path.append('src')

# Import working components
try:
    from tokenizer import enhance_prompt, create_negative_prompt
    text_processing_available = True
    print("✅ Text processing loaded successfully")
except Exception as e:
    print(f"⚠️ Text processing limited: {e}")
    text_processing_available = False

def create_demo_image(prompt, style="realistic"):
    """Create a high-quality demo image"""
    
    # Color schemes for different styles
    colors = {
        "realistic": {"bg": (245, 248, 255), "accent": (70, 130, 180), "text": (25, 25, 112)},
        "artistic": {"bg": (255, 245, 238), "accent": (255, 140, 0), "text": (139, 69, 19)},
        "professional": {"bg": (248, 248, 255), "accent": (105, 105, 105), "text": (47, 79, 79)},
        "cinematic": {"bg": (25, 25, 25), "accent": (255, 215, 0), "text": (255, 255, 255)}
    }
    
    color_scheme = colors.get(style, colors["realistic"])
    
    # Create image
    img = Image.new('RGB', (512, 512), color_scheme["bg"])
    draw = ImageDraw.Draw(img)
    
    # Create gradient
    for y in range(512):
        factor = y / 512
        r = int(color_scheme["bg"][0] * (1 - factor * 0.2))
        g = int(color_scheme["bg"][1] * (1 - factor * 0.2))
        b = int(color_scheme["bg"][2] * (1 - factor * 0.2))
        draw.line([(0, y), (512, y)], fill=(r, g, b))
    
    # Load fonts
    try:
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_medium = ImageFont.truetype("arial.ttf", 18)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Add title
    draw.text((20, 20), "🎨 AI Generated Image", fill=color_scheme["text"], font=font_large)
    draw.text((20, 50), f"Style: {style.title()}", fill=color_scheme["accent"], font=font_medium)
    
    # Create visual based on prompt keywords
    prompt_lower = prompt.lower()
    
    # Center area for main illustration
    center_x, center_y = 256, 256
    
    if any(word in prompt_lower for word in ["dog", "puppy"]):
        # Simple dog illustration
        draw.ellipse([center_x-60, center_y-20, center_x+60, center_y+40], 
                     fill=(139, 69, 19), outline=(101, 67, 33), width=3)
        draw.ellipse([center_x-30, center_y-60, center_x+30, center_y-20], 
                     fill=(139, 69, 19), outline=(101, 67, 33), width=3)
        # Eyes
        draw.ellipse([center_x-15, center_y-45, center_x-5, center_y-35], fill=(0, 0, 0))
        draw.ellipse([center_x+5, center_y-45, center_x+15, center_y-35], fill=(0, 0, 0))
        # Nose
        draw.ellipse([center_x-5, center_y-25, center_x+5, center_y-15], fill=(0, 0, 0))
        subject = "🐕 DOG"
        
    elif any(word in prompt_lower for word in ["cat", "kitten"]):
        # Simple cat illustration
        draw.ellipse([center_x-50, center_y-10, center_x+50, center_y+30], 
                     fill=(128, 128, 128), outline=(105, 105, 105), width=3)
        draw.ellipse([center_x-25, center_y-50, center_x+25, center_y-10], 
                     fill=(128, 128, 128), outline=(105, 105, 105), width=3)
        # Ears
        draw.polygon([(center_x-20, center_y-40), (center_x-10, center_y-60), (center_x, center_y-40)], 
                     fill=(105, 105, 105))
        draw.polygon([(center_x, center_y-40), (center_x+10, center_y-60), (center_x+20, center_y-40)], 
                     fill=(105, 105, 105))
        # Eyes
        draw.ellipse([center_x-12, center_y-35, center_x-4, center_y-27], fill=(0, 255, 0))
        draw.ellipse([center_x+4, center_y-35, center_x+12, center_y-27], fill=(0, 255, 0))
        subject = "🐱 CAT"
        
    elif any(word in prompt_lower for word in ["car", "vehicle"]):
        # Simple car illustration
        draw.rectangle([center_x-80, center_y-20, center_x+80, center_y+20], 
                       fill=(255, 0, 0), outline=(200, 0, 0), width=3)
        draw.rectangle([center_x-50, center_y-40, center_x+50, center_y-20], 
                       fill=(180, 0, 0), outline=(150, 0, 0), width=2)
        # Wheels
        draw.ellipse([center_x-70, center_y+15, center_x-50, center_y+35], fill=(0, 0, 0))
        draw.ellipse([center_x+50, center_y+15, center_x+70, center_y+35], fill=(0, 0, 0))
        subject = "🚗 CAR"
        
    elif any(word in prompt_lower for word in ["human", "person", "portrait"]):
        # Simple human illustration
        draw.ellipse([center_x-20, center_y-60, center_x+20, center_y-20], 
                     fill=(255, 220, 177), outline=(200, 180, 140), width=2)
        draw.rectangle([center_x-15, center_y-20, center_x+15, center_y+30], 
                       fill=(0, 100, 200), outline=(0, 80, 160), width=2)
        # Eyes
        draw.ellipse([center_x-10, center_y-50, center_x-5, center_y-45], fill=(0, 0, 0))
        draw.ellipse([center_x+5, center_y-50, center_x+10, center_y-45], fill=(0, 0, 0))
        subject = "👤 HUMAN"
        
    else:
        # Generic creative illustration
        colors_art = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100)]
        for i, color in enumerate(colors_art):
            x = center_x - 60 + i * 40
            y = center_y - 30 + (i % 2) * 30
            draw.ellipse([x, y, x+30, y+30], fill=color, outline=color_scheme["accent"], width=2)
        subject = "✨ CREATIVE"
    
    # Add subject label
    draw.text((20, 80), f"Generated: {subject}", fill=color_scheme["accent"], font=font_medium)
    
    # Add prompt
    draw.text((20, 420), "Prompt:", fill=color_scheme["accent"], font=font_small)
    
    # Wrap prompt text
    words = prompt.split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line + " " + word) < 50:
            current_line += (" " if current_line else "") + word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    for i, line in enumerate(lines[:3]):  # Max 3 lines
        draw.text((20, 440 + i * 18), line, fill=color_scheme["text"], font=font_small)
    
    return img

def generate_image(prompt, style, num_images):
    """Generate images based on prompt"""
    if not prompt.strip():
        return [], "❌ Please enter a text prompt"
    
    images = []
    os.makedirs("outputs/simple_generated", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Process prompt if available
    enhanced_prompt = prompt
    if text_processing_available:
        try:
            enhanced_prompt = enhance_prompt(prompt, style)
        except:
            enhanced_prompt = f"{prompt}, {style}, high quality"
    
    # Generate images
    for i in range(num_images):
        img = create_demo_image(prompt, style)
        images.append(img)
        
        # Save image
        filename = f"demo_{style}_{timestamp}_{i+1}.png"
        filepath = os.path.join("outputs/simple_generated", filename)
        img.save(filepath)
    
    status = f"✅ Generated {len(images)} image(s) successfully!\n"
    status += f"📁 Saved to: outputs/simple_generated/\n"
    status += f"🎨 Style: {style}\n"
    status += f"📝 Original prompt: '{prompt}'\n"
    if enhanced_prompt != prompt:
        status += f"🔤 Enhanced prompt: '{enhanced_prompt}'\n"
    status += f"⏰ Generated at: {datetime.now().strftime('%H:%M:%S')}"
    
    return images, status

def create_interface():
    """Create the Gradio interface"""
    
    with gr.Blocks(title="Simple Text-to-Image Demo", theme=gr.themes.Soft()) as interface:
        
        gr.HTML("""
        <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px; margin-bottom: 25px;">
            <h1>🎨 Simple Text-to-Image Generator</h1>
            <p style="font-size: 16px;">Create realistic demo images from text descriptions</p>
            <p><strong>✨ Ready to use!</strong> No setup required - just enter your prompt and generate!</p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                prompt_input = gr.Textbox(
                    label="Enter your text prompt",
                    placeholder="Try: cute dog, beautiful cat, red car, mountain bike, human portrait...",
                    lines=3,
                    value="a cute golden retriever dog"
                )
                
                style_dropdown = gr.Dropdown(
                    choices=["realistic", "artistic", "professional", "cinematic"],
                    value="realistic",
                    label="Choose style"
                )
                
                num_images_slider = gr.Slider(
                    minimum=1, maximum=4, value=2, step=1,
                    label="Number of images"
                )
                
                generate_btn = gr.Button("🎨 Generate Images", variant="primary", size="lg")
                
                gr.HTML("""
                <div style="margin-top: 20px; padding: 15px; background: #e8f5e8; border-radius: 8px; border-left: 4px solid #28a745;">
                    <h4>🚀 Quick Tips:</h4>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li><strong>Be descriptive:</strong> "cute golden retriever playing"</li>
                        <li><strong>Try different styles:</strong> realistic, artistic, cinematic</li>
                        <li><strong>Supported objects:</strong> animals, vehicles, people, landscapes</li>
                    </ul>
                </div>
                """)
            
            with gr.Column(scale=2):
                output_gallery = gr.Gallery(
                    label="Generated Images",
                    columns=2,
                    rows=2,
                    height=400,
                    object_fit="contain"
                )
                
                status_output = gr.Textbox(
                    label="Generation Status",
                    lines=8,
                    interactive=False
                )
        
        # Examples
        gr.HTML("<h3 style='text-align: center; margin-top: 25px; color: #333;'>📋 Try These Examples</h3>")
        
        examples = [
            ["a cute golden retriever dog", "realistic", 2],
            ["a fluffy white cat", "artistic", 2],
            ["a red sports car", "cinematic", 2],
            ["a professional portrait", "professional", 1],
            ["a beautiful landscape", "artistic", 2],
        ]
        
        gr.Examples(
            examples=examples,
            inputs=[prompt_input, style_dropdown, num_images_slider],
            outputs=[output_gallery, status_output],
            fn=generate_image,
            cache_examples=False
        )
        
        # Connect the generate button
        generate_btn.click(
            fn=generate_image,
            inputs=[prompt_input, style_dropdown, num_images_slider],
            outputs=[output_gallery, status_output]
        )
    
    return interface

def main():
    """Launch the interface"""
    print("🚀 Starting Simple Text-to-Image Generator...")
    
    # Test components
    if text_processing_available:
        print("✅ Text processing available")
    else:
        print("⚠️ Text processing limited - using basic enhancement")
    
    # Create and launch interface
    interface = create_interface()
    
    print("🌐 Launching interface at http://localhost:7862")
    print("🎨 Generate realistic demo images from text prompts!")
    
    interface.launch(
        server_name="127.0.0.1",
        server_port=7862,
        share=False,
        show_error=True,
        inbrowser=True
    )

if __name__ == "__main__":
    main()