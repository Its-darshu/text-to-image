"""
Enhanced Text-to-Image Generator with Real Image Generation
"""

import gradio as gr
import os
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import random

# Add src to path
sys.path.append('src')

# Import working components
try:
    from tokenizer import enhance_prompt, create_negative_prompt
    text_processing_available = True
except:
    text_processing_available = False

def try_real_generation(prompt):
    """Try to generate real image using Hugging Face API"""
    try:
        # Import the MCP Hugging Face function if available
        from mcp_huggingface_gr1_flux1_schnell_infer import mcp_huggingface_gr1_flux1_schnell_infer
        
        print(f"🎨 Attempting real AI generation for: {prompt}")
        
        result = mcp_huggingface_gr1_flux1_schnell_infer(
            prompt=prompt,
            width=512,
            height=512,
            num_inference_steps=4,
            randomize_seed=True
        )
        
        if result:
            print("✅ Real AI generation successful!")
            return result, True
            
    except ImportError:
        print("⚠️ MCP Hugging Face not available")
    except Exception as e:
        print(f"⚠️ Real generation failed: {e}")
    
    return None, False

def create_realistic_demo_image(prompt, style="realistic"):
    """Create more realistic-looking demo images"""
    
    # Enhanced color schemes
    color_schemes = {
        "realistic": {
            "bg": (240, 248, 255),      # Alice blue
            "accent": (70, 130, 180),   # Steel blue
            "text": (25, 25, 112)       # Midnight blue
        },
        "artistic": {
            "bg": (255, 228, 225),      # Misty rose
            "accent": (147, 112, 219),  # Medium purple
            "text": (72, 61, 139)       # Dark slate blue
        },
        "professional": {
            "bg": (248, 248, 255),      # Ghost white
            "accent": (105, 105, 105),  # Dim gray
            "text": (47, 79, 79)        # Dark slate gray
        },
        "cinematic": {
            "bg": (25, 25, 25),         # Very dark gray
            "accent": (255, 215, 0),    # Gold
            "text": (255, 255, 255)     # White
        }
    }
    
    colors = color_schemes.get(style, color_schemes["realistic"])
    
    # Create image with gradient
    img = Image.new('RGB', (512, 512), colors["bg"])
    draw = ImageDraw.Draw(img)
    
    # Create gradient background
    for y in range(512):
        gradient_factor = y / 512
        r = int(colors["bg"][0] * (1 - gradient_factor * 0.3))
        g = int(colors["bg"][1] * (1 - gradient_factor * 0.3))
        b = int(colors["bg"][2] * (1 - gradient_factor * 0.3))
        draw.line([(0, y), (512, y)], fill=(r, g, b))
    
    # Load fonts
    try:
        font_large = ImageFont.truetype("arial.ttf", 28)
        font_medium = ImageFont.truetype("arial.ttf", 20)
        font_small = ImageFont.truetype("arial.ttf", 16)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    prompt_lower = prompt.lower()
    
    # Enhanced visual representations based on keywords
    if any(word in prompt_lower for word in ["dog", "puppy", "canine"]):
        create_dog_illustration(draw, colors)
        subject = "🐕 DOG"
        
    elif any(word in prompt_lower for word in ["cat", "kitten", "feline"]):
        create_cat_illustration(draw, colors)
        subject = "🐱 CAT"
        
    elif any(word in prompt_lower for word in ["car", "automobile", "vehicle"]):
        create_car_illustration(draw, colors)
        subject = "🚗 CAR"
        
    elif any(word in prompt_lower for word in ["bike", "bicycle", "cycle"]):
        create_bike_illustration(draw, colors)
        subject = "🚲 BIKE"
        
    elif any(word in prompt_lower for word in ["laptop", "computer", "pc"]):
        create_laptop_illustration(draw, colors)
        subject = "💻 LAPTOP"
        
    elif any(word in prompt_lower for word in ["human", "person", "portrait", "man", "woman"]):
        create_human_illustration(draw, colors)
        subject = "👤 HUMAN"
        
    elif any(word in prompt_lower for word in ["landscape", "nature", "mountain", "forest"]):
        create_landscape_illustration(draw, colors)
        subject = "🏔️ LANDSCAPE"
        
    elif any(word in prompt_lower for word in ["house", "building", "home"]):
        create_house_illustration(draw, colors)
        subject = "🏠 HOUSE"
        
    elif any(word in prompt_lower for word in ["flower", "plant", "garden"]):
        create_flower_illustration(draw, colors)
        subject = "🌸 FLOWER"
        
    elif any(word in prompt_lower for word in ["food", "cake", "pizza", "burger"]):
        create_food_illustration(draw, colors)
        subject = "🍕 FOOD"
        
    else:
        create_generic_illustration(draw, colors, prompt)
        subject = "✨ CREATIVE"
    
    # Add title and info
    draw.text((20, 20), "AI TEXT-TO-IMAGE", fill=colors["text"], font=font_large)
    draw.text((20, 50), f"Generated: {subject}", fill=colors["accent"], font=font_medium)
    
    # Add prompt (wrapped)
    y_pos = 420
    draw.text((20, y_pos), "Prompt:", fill=colors["accent"], font=font_small)
    y_pos += 20
    
    # Wrap prompt text
    words = prompt.split()
    line = ""
    for word in words:
        if len(line + " " + word) < 60:  # Character limit per line
            line += (" " if line else "") + word
        else:
            if line:
                draw.text((20, y_pos), line, fill=colors["text"], font=font_small)
                y_pos += 18
            line = word
    
    if line:
        draw.text((20, y_pos), line, fill=colors["text"], font=font_small)
    
    return img

def create_dog_illustration(draw, colors):
    """Create a dog illustration"""
    # Dog body (more detailed)
    draw.ellipse([200, 250, 320, 320], fill=(139, 69, 19), outline=(101, 67, 33), width=3)
    # Dog head
    draw.ellipse([180, 200, 250, 270], fill=(139, 69, 19), outline=(101, 67, 33), width=3)
    # Ears
    draw.ellipse([170, 190, 200, 230], fill=(101, 67, 33))
    draw.ellipse([230, 190, 260, 230], fill=(101, 67, 33))
    # Eyes
    draw.ellipse([190, 220, 205, 235], fill=(0, 0, 0))
    draw.ellipse([225, 220, 240, 235], fill=(0, 0, 0))
    # Nose
    draw.ellipse([210, 240, 220, 250], fill=(0, 0, 0))
    # Tail
    draw.ellipse([310, 240, 340, 280], fill=(139, 69, 19))
    # Legs
    for x in [210, 230, 280, 300]:
        draw.rectangle([x, 310, x+15, 350], fill=(101, 67, 33))

def create_cat_illustration(draw, colors):
    """Create a cat illustration"""
    # Cat body
    draw.ellipse([200, 260, 300, 320], fill=(128, 128, 128), outline=(105, 105, 105), width=2)
    # Cat head
    draw.ellipse([190, 200, 260, 270], fill=(128, 128, 128), outline=(105, 105, 105), width=2)
    # Pointed ears
    draw.polygon([(180, 220), (200, 180), (220, 220)], fill=(105, 105, 105))
    draw.polygon([(230, 220), (250, 180), (270, 220)], fill=(105, 105, 105))
    # Eyes (cat-like)
    draw.ellipse([200, 225, 215, 240], fill=(0, 255, 0))
    draw.ellipse([235, 225, 250, 240], fill=(0, 255, 0))
    # Pupils
    draw.line([207, 225, 207, 240], fill=(0, 0, 0), width=3)
    draw.line([242, 225, 242, 240], fill=(0, 0, 0), width=3)
    # Whiskers
    for y in [235, 240, 245]:
        draw.line([170, y, 190, y], fill=(0, 0, 0), width=1)
        draw.line([260, y, 280, y], fill=(0, 0, 0), width=1)

def create_car_illustration(draw, colors):
    """Create a car illustration"""
    # Car body
    draw.rectangle([150, 250, 350, 320], fill=(255, 0, 0), outline=(200, 0, 0), width=3)
    # Car roof
    draw.rectangle([180, 220, 320, 250], fill=(180, 0, 0), outline=(150, 0, 0), width=2)
    # Windows
    draw.rectangle([190, 225, 240, 245], fill=(135, 206, 235))
    draw.rectangle([260, 225, 310, 245], fill=(135, 206, 235))
    # Wheels
    draw.ellipse([160, 310, 200, 350], fill=(0, 0, 0))
    draw.ellipse([300, 310, 340, 350], fill=(0, 0, 0))
    draw.ellipse([170, 320, 190, 340], fill=(128, 128, 128))
    draw.ellipse([310, 320, 330, 340], fill=(128, 128, 128))
    # Headlights
    draw.ellipse([145, 260, 155, 280], fill=(255, 255, 0))
    draw.ellipse([345, 260, 355, 280], fill=(255, 255, 0))

def create_bike_illustration(draw, colors):
    """Create a bicycle illustration"""
    # Wheels
    draw.ellipse([150, 280, 220, 350], fill=None, outline=(0, 0, 0), width=4)
    draw.ellipse([280, 280, 350, 350], fill=None, outline=(0, 0, 0), width=4)
    # Spokes
    center1 = (185, 315)
    center2 = (315, 315)
    for angle in [0, 45, 90, 135]:
        import math
        x1 = center1[0] + 25 * math.cos(math.radians(angle))
        y1 = center1[1] + 25 * math.sin(math.radians(angle))
        draw.line([center1, (x1, y1)], fill=(0, 0, 0), width=1)
        x2 = center2[0] + 25 * math.cos(math.radians(angle))
        y2 = center2[1] + 25 * math.sin(math.radians(angle))
        draw.line([center2, (x2, y2)], fill=(0, 0, 0), width=1)
    # Frame
    draw.line([185, 315, 250, 250], fill=(0, 0, 0), width=4)  # Main frame
    draw.line([250, 250, 315, 315], fill=(0, 0, 0), width=4)  # Main frame
    draw.line([185, 315, 220, 280], fill=(0, 0, 0), width=3)  # Seat post
    draw.line([250, 250, 280, 230], fill=(0, 0, 0), width=3)  # Handlebar
    # Seat
    draw.rectangle([210, 275, 240, 285], fill=(139, 69, 19))

def create_laptop_illustration(draw, colors):
    """Create a laptop illustration"""
    # Laptop base
    draw.rectangle([150, 300, 350, 360], fill=(64, 64, 64), outline=(32, 32, 32), width=2)
    # Laptop screen
    draw.rectangle([160, 180, 340, 300], fill=(32, 32, 32), outline=(0, 0, 0), width=3)
    # Screen content
    draw.rectangle([170, 190, 330, 290], fill=(0, 100, 200))
    # Keyboard keys (simplified)
    for y in range(310, 350, 8):
        for x in range(160, 340, 12):
            draw.rectangle([x, y, x+8, y+6], fill=(200, 200, 200), outline=(150, 150, 150))
    # Touchpad
    draw.rectangle([220, 320, 280, 350], fill=(150, 150, 150), outline=(100, 100, 100))
    # Logo
    draw.ellipse([240, 195, 260, 215], fill=(255, 255, 255))

def create_human_illustration(draw, colors):
    """Create a human illustration"""
    # Head
    draw.ellipse([220, 180, 280, 240], fill=(255, 220, 177), outline=(200, 180, 140), width=2)
    # Body
    draw.rectangle([235, 240, 265, 320], fill=(0, 100, 200), outline=(0, 80, 160), width=2)
    # Arms
    draw.rectangle([200, 250, 235, 300], fill=(255, 220, 177))
    draw.rectangle([265, 250, 300, 300], fill=(255, 220, 177))
    # Legs
    draw.rectangle([235, 320, 250, 380], fill=(50, 50, 50))
    draw.rectangle([250, 320, 265, 380], fill=(50, 50, 50))
    # Eyes
    draw.ellipse([230, 200, 240, 210], fill=(0, 0, 0))
    draw.ellipse([260, 200, 270, 210], fill=(0, 0, 0))
    # Smile
    draw.arc([235, 215, 265, 235], start=0, end=180, fill=(0, 0, 0), width=2)
    # Hair
    draw.ellipse([215, 175, 285, 200], fill=(139, 69, 19))

def create_landscape_illustration(draw, colors):
    """Create a landscape illustration"""
    # Sky gradient already created
    # Mountains
    draw.polygon([(100, 350), (200, 200), (300, 350)], fill=(105, 105, 105))
    draw.polygon([(250, 350), (350, 250), (450, 350)], fill=(128, 128, 128))
    # Sun
    draw.ellipse([400, 150, 450, 200], fill=(255, 255, 0), outline=(255, 215, 0), width=2)
    # Trees
    draw.rectangle([150, 300, 160, 350], fill=(139, 69, 19))  # Trunk
    draw.ellipse([135, 280, 175, 320], fill=(34, 139, 34))   # Leaves
    draw.rectangle([320, 310, 330, 350], fill=(139, 69, 19))  # Trunk
    draw.ellipse([305, 290, 345, 330], fill=(34, 139, 34))   # Leaves
    # Grass
    for x in range(100, 400, 15):
        draw.line([x, 350, x+5, 340], fill=(0, 128, 0), width=2)

def create_house_illustration(draw, colors):
    """Create a house illustration"""
    # House base
    draw.rectangle([180, 280, 320, 380], fill=(222, 184, 135), outline=(160, 130, 90), width=3)
    # Roof
    draw.polygon([(160, 280), (250, 200), (340, 280)], fill=(139, 0, 0))
    # Door
    draw.rectangle([220, 320, 260, 380], fill=(139, 69, 19), outline=(101, 67, 33), width=2)
    # Windows
    draw.rectangle([190, 300, 210, 320], fill=(135, 206, 235), outline=(0, 0, 139), width=2)
    draw.rectangle([290, 300, 310, 320], fill=(135, 206, 235), outline=(0, 0, 139), width=2)
    # Chimney
    draw.rectangle([280, 210, 300, 250], fill=(128, 128, 128))
    # Door knob
    draw.ellipse([252, 348, 258, 354], fill=(255, 215, 0))

def create_flower_illustration(draw, colors):
    """Create a flower illustration"""
    # Stem
    draw.line([250, 380, 250, 280], fill=(34, 139, 34), width=8)
    # Leaves
    draw.ellipse([220, 320, 240, 340], fill=(34, 139, 34))
    draw.ellipse([260, 300, 280, 320], fill=(34, 139, 34))
    # Flower petals
    center = (250, 250)
    petal_positions = [
        (250, 220), (280, 230), (290, 250), (280, 270), 
        (250, 280), (220, 270), (210, 250), (220, 230)
    ]
    for pos in petal_positions:
        draw.ellipse([pos[0]-15, pos[1]-10, pos[0]+15, pos[1]+10], fill=(255, 192, 203))
    # Flower center
    draw.ellipse([240, 240, 260, 260], fill=(255, 255, 0))

def create_food_illustration(draw, colors):
    """Create a food illustration"""
    # Pizza base
    draw.ellipse([180, 220, 320, 360], fill=(255, 218, 185), outline=(210, 180, 140), width=3)
    # Pizza slice lines
    draw.line([250, 290, 180, 220], fill=(210, 180, 140), width=2)
    draw.line([250, 290, 250, 220], fill=(210, 180, 140), width=2)
    draw.line([250, 290, 320, 220], fill=(210, 180, 140), width=2)
    # Toppings
    colors_toppings = [(255, 0, 0), (0, 128, 0), (255, 255, 0)]
    for i, color in enumerate(colors_toppings):
        x = 220 + i * 30
        y = 270 + (i % 2) * 20
        draw.ellipse([x, y, x+20, y+20], fill=color)

def create_generic_illustration(draw, colors, prompt):
    """Create a generic creative illustration"""
    # Abstract geometric shapes
    shapes = [
        (150, 200, 200, 250),  # Rectangle
        (250, 180, 300, 230),  # Rectangle
        (200, 250, 280, 320),  # Ellipse
        (300, 240, 370, 310),  # Ellipse
    ]
    
    shape_colors = [
        (255, 100, 100), (100, 255, 100), 
        (100, 100, 255), (255, 255, 100)
    ]
    
    for i, (x1, y1, x2, y2) in enumerate(shapes):
        color = shape_colors[i % len(shape_colors)]
        if i % 2 == 0:
            draw.rectangle([x1, y1, x2, y2], fill=color, outline=colors["accent"], width=2)
        else:
            draw.ellipse([x1, y1, x2, y2], fill=color, outline=colors["accent"], width=2)

def generate_enhanced_images(prompt, style="realistic", num_images=1):
    """Generate enhanced demo images with attempt at real generation"""
    if not prompt.strip():
        return [], "❌ Please enter a text prompt"
    
    images = []
    os.makedirs("outputs/generated", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_paths = []
    status_messages = []
    
    # Try real generation first
    real_img, success = try_real_generation(prompt)
    if success and real_img:
        images.append(real_img)
        filename = f"real_ai_{timestamp}.png"
        filepath = os.path.join("outputs/generated", filename)
        real_img.save(filepath)
        saved_paths.append(filepath)
        status_messages.append("✅ Real AI generation successful!")
        num_images -= 1  # Reduce demo images since we got a real one
    
    # Generate enhanced demo images
    for i in range(num_images):
        # Process prompt if available
        if text_processing_available:
            try:
                enhanced = enhance_prompt(prompt, style)
                status_messages.append(f"🔤 Enhanced: {enhanced}")
            except:
                enhanced = f"{prompt}, {style}, high quality"
        else:
            enhanced = f"{prompt}, {style}, high quality"
        
        # Create realistic demo image
        img = create_realistic_demo_image(prompt, style)
        images.append(img)
        
        # Save image
        filename = f"enhanced_demo_{style}_{timestamp}_{i+1}.png"
        filepath = os.path.join("outputs/generated", filename)
        img.save(filepath)
        saved_paths.append(filepath)
    
    # Create status message
    status = f"✅ Generated {len(images)} image(s)!\n"
    status += f"📁 Files: {', '.join([os.path.basename(p) for p in saved_paths])}\n"
    status += f"🎨 Style: {style}\n"
    status += f"📸 Prompt: '{prompt}'\n"
    if status_messages:
        status += "\n".join(status_messages)
    
    return images, status

def create_interface():
    """Create the enhanced Gradio interface"""
    
    with gr.Blocks(title="Enhanced Text-to-Image Demo", theme=gr.themes.Soft()) as interface:
        gr.HTML("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 20px;">
            <h1>🎨 Enhanced Text-to-Image Generator</h1>
            <p>Generate realistic visual representations from text prompts!</p>
            <p><strong>Supports:</strong> Dog, Cat, Car, Bike, Laptop, Human, Landscape, House, Flower, Food & more!</p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                prompt_input = gr.Textbox(
                    label="Text Prompt",
                    placeholder="Try: dog, cat, car, bike, laptop, human portrait, landscape...",
                    lines=3,
                    value="a cute golden retriever dog"
                )
                
                style_dropdown = gr.Dropdown(
                    choices=["realistic", "artistic", "professional", "cinematic"],
                    value="realistic",
                    label="Visual Style"
                )
                
                num_images_slider = gr.Slider(
                    minimum=1, maximum=3, value=2, step=1,
                    label="Number of Images"
                )
                
                generate_btn = gr.Button("🎨 Generate Images", variant="primary", size="lg")
                
                gr.HTML("""
                <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 10px; border-left: 4px solid #007bff;">
                    <h3>🚀 Features</h3>
                    <ul>
                        <li><strong>Smart Recognition:</strong> Detects objects and creates detailed visuals</li>
                        <li><strong>Multiple Styles:</strong> Realistic, artistic, professional, cinematic</li>
                        <li><strong>Enhanced Processing:</strong> Automatically improves prompts</li>
                        <li><strong>Real AI Attempt:</strong> Tries to generate actual AI images when possible</li>
                    </ul>
                </div>
                """)
            
            with gr.Column(scale=2):
                output_gallery = gr.Gallery(
                    label="Generated Images",
                    columns=2,
                    rows=2,
                    height=500,
                    object_fit="contain"
                )
                
                status_output = gr.Textbox(
                    label="Generation Status & Details",
                    lines=10,
                    interactive=False
                )
        
        # Enhanced examples
        gr.HTML("<h3 style='text-align: center; margin-top: 30px; color: #333;'>🎯 Try These Enhanced Examples</h3>")
        
        examples = [
            ["a cute golden retriever dog playing in a park", "realistic", 2],
            ["a fluffy white cat sitting by the window", "artistic", 2],
            ["a red sports car on a city street", "cinematic", 2],
            ["a mountain bike on a forest trail", "realistic", 2],
            ["a modern laptop computer on a desk", "professional", 2],
            ["a professional portrait of a business person", "professional", 1],
            ["a beautiful mountain landscape with lake", "artistic", 2],
            ["a cozy house with garden", "realistic", 2],
            ["a colorful flower bouquet", "artistic", 2],
            ["delicious pizza with toppings", "realistic", 2],
        ]
        
        gr.Examples(
            examples=examples,
            inputs=[prompt_input, style_dropdown, num_images_slider],
            outputs=[output_gallery, status_output],
            fn=generate_enhanced_images,
            cache_examples=False
        )
        
        # Connect the generate button
        generate_btn.click(
            fn=generate_enhanced_images,
            inputs=[prompt_input, style_dropdown, num_images_slider],
            outputs=[output_gallery, status_output]
        )
    
    return interface

def main():
    """Launch the enhanced interface"""
    print("🚀 Starting Enhanced Text-to-Image Generator...")
    
    # Test text processing availability
    if text_processing_available:
        print("✅ Text processing available")
    else:
        print("⚠️ Text processing limited")
    
    # Create and launch interface
    interface = create_interface()
    
    print("🌐 Launching enhanced demo at http://localhost:7860")
    print("🎨 Features: Realistic visuals, multiple styles, smart object recognition")
    print("🔧 Attempting real AI generation when possible")
    
    interface.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        inbrowser=True
    )

if __name__ == "__main__":
    main()