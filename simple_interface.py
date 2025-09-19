"""
Simple working web interface for text-to-image generation
"""

import gradio as gr
import os
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Add src to path
sys.path.append('src')

# Import working components
try:
    from tokenizer import enhance_prompt, create_negative_prompt
    text_processing_available = True
except:
    text_processing_available = False

def generate_real_image_with_api(prompt):
    """Try to generate real image using Hugging Face API"""
    try:
        # Import the MCP Hugging Face function
        import sys
        sys.path.append('..')
        
        # Try using the Hugging Face Flux model
        result = mcp_huggingface_gr1_flux1_schnell_infer(
            prompt=prompt,
            width=512,
            height=512,
            num_inference_steps=4,
            randomize_seed=True
        )
        
        if result and hasattr(result, 'url'):
            # Download and return the image
            import requests
            response = requests.get(result.url)
            if response.status_code == 200:
                from io import BytesIO
                img = Image.open(BytesIO(response.content))
                return img, True
                
    except Exception as e:
        print(f"API generation failed: {e}")
    
    return None, False

def generate_demo_image(prompt, style="realistic", num_images=1):
    """Generate demo images with better visual representations"""
    if not prompt.strip():
        return [], "❌ Please enter a text prompt"
    
    images = []
    os.makedirs("outputs/generated", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_paths = []
    
    # Color schemes for different styles
    color_schemes = {
        "realistic": (135, 206, 235),    # Sky blue
        "artistic": (147, 112, 219),     # Medium purple
        "professional": (70, 130, 180),  # Steel blue
        "cinematic": (25, 25, 112)       # Midnight blue
    }
    
    base_color = color_schemes.get(style, color_schemes["realistic"])
    
    for i in range(num_images):
        # Create image with gradient effect
        img = Image.new('RGB', (512, 512), base_color)
        draw = ImageDraw.Draw(img)
        
        # Add gradient effect
        for y in range(512):
            color_intensity = int(255 * (y / 512))
            line_color = (
                min(255, base_color[0] + color_intensity // 4),
                min(255, base_color[1] + color_intensity // 4),
                min(255, base_color[2] + color_intensity // 4)
            )
            draw.line([(0, y), (512, y)], fill=line_color)
        
        # Load fonts
        try:
            font_title = ImageFont.truetype("arial.ttf", 36)
            font_prompt = ImageFont.truetype("arial.ttf", 24)
            font_small = ImageFont.truetype("arial.ttf", 18)
        except:
            font_title = ImageFont.load_default()
            font_prompt = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Add title
        draw.text((20, 20), "AI TEXT-TO-IMAGE", fill=(255, 255, 255), font=font_title)
        draw.text((20, 60), f"DEMO #{i+1}", fill=(255, 255, 255), font=font_prompt)
        
        # Process and display prompt
        if text_processing_available:
            try:
                enhanced = enhance_prompt(prompt, style)
                negative = create_negative_prompt()
            except:
                enhanced = f"{prompt}, {style}, high quality"
                negative = "low quality, blurry"
        else:
            enhanced = f"{prompt}, {style}, high quality"
            negative = "low quality, blurry"
        
        # Add prompt text (wrapped)
        y_pos = 120
        max_width = 472  # 512 - 40 for margins
        
        # Original prompt
        draw.text((20, y_pos), "Original:", fill=(255, 255, 0), font=font_small)
        y_pos += 25
        
        # Wrap text
        words = prompt.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if len(test_line) * 10 < max_width:  # Rough character width estimation
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        for line in lines[:3]:  # Max 3 lines
            draw.text((20, y_pos), line, fill=(255, 255, 255), font=font_prompt)
            y_pos += 30
        
        # Enhanced prompt
        y_pos += 20
        draw.text((20, y_pos), "Enhanced:", fill=(255, 255, 0), font=font_small)
        y_pos += 25
        
        # Wrap enhanced text
        enhanced_words = enhanced.split()
        enhanced_lines = []
        current_line = ""
        
        for word in enhanced_words:
            test_line = current_line + (" " if current_line else "") + word
            if len(test_line) * 8 < max_width:
                current_line = test_line
            else:
                if current_line:
                    enhanced_lines.append(current_line)
                current_line = word
        
        if current_line:
            enhanced_lines.append(current_line)
        
        for line in enhanced_lines[:4]:  # Max 4 lines
            draw.text((20, y_pos), line, fill=(200, 255, 200), font=font_small)
            y_pos += 22
        
        # Add visual elements based on prompt keywords
        prompt_lower = prompt.lower()
        
        # Draw simple representations
        if "dog" in prompt_lower:
            # Simple dog representation
            draw.ellipse([400, 350, 480, 400], fill=(139, 69, 19))  # Body
            draw.ellipse([380, 330, 420, 370], fill=(139, 69, 19))  # Head
            draw.ellipse([385, 335, 395, 345], fill=(0, 0, 0))      # Eye
            draw.ellipse([405, 335, 415, 345], fill=(0, 0, 0))      # Eye
            draw.text((380, 410), "🐕", fill=(255, 255, 255), font=font_prompt)
        
        elif "human" in prompt_lower or "person" in prompt_lower:
            # Simple human representation
            draw.ellipse([430, 320, 470, 360], fill=(255, 220, 177))  # Head
            draw.rectangle([440, 360, 460, 420], fill=(100, 100, 255))  # Body
            draw.text((420, 430), "👤", fill=(255, 255, 255), font=font_prompt)
        
        elif "car" in prompt_lower:
            # Simple car representation
            draw.rectangle([380, 360, 480, 400], fill=(255, 0, 0))  # Body
            draw.ellipse([390, 395, 420, 425], fill=(0, 0, 0))     # Wheel
            draw.ellipse([450, 395, 480, 425], fill=(0, 0, 0))     # Wheel
            draw.text((420, 430), "🚗", fill=(255, 255, 255), font=font_prompt)
        
        elif "landscape" in prompt_lower:
            # Simple landscape
            # Mountains
            draw.polygon([(380, 400), (420, 320), (460, 400)], fill=(105, 105, 105))
            draw.polygon([(440, 400), (480, 340), (512, 400)], fill=(105, 105, 105))
            # Sun
            draw.ellipse([450, 330, 480, 360], fill=(255, 255, 0))
            draw.text((420, 430), "🏔️", fill=(255, 255, 255), font=font_prompt)
        
        # Add timestamp and style info
        draw.text((20, 480), f"Style: {style} | Generated: {timestamp}", 
                 fill=(255, 255, 255), font=font_small)
        
        images.append(img)
        
        # Save image
        filename = f"demo_{style}_{timestamp}_{i+1}.png"
        filepath = os.path.join("outputs/generated", filename)
        img.save(filepath)
        saved_paths.append(filepath)
    
    status = f"✅ Generated {len(images)} demo image(s)!\n"
    status += f"📁 Saved to: {', '.join(saved_paths)}\n"
    status += f"🎨 Style: {style}\n"
    if text_processing_available:
        status += "🔤 Text processing: Active\n"
    else:
        status += "⚠️ Text processing: Limited\n"
    status += f"📸 Original prompt: '{prompt}'"
    
    return images, status

def create_interface():
    """Create the Gradio interface"""
    
    with gr.Blocks(title="Text-to-Image Demo", theme=gr.themes.Soft()) as interface:
        gr.HTML("""
        <div style="text-align: center; padding: 20px;">
            <h1>🎨 Text-to-Image Generation Demo</h1>
            <p>Enter a text prompt and generate demo images with enhanced text processing!</p>
            <p><strong>Examples:</strong> "a cute dog", "human portrait", "red car", "mountain landscape"</p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                prompt_input = gr.Textbox(
                    label="Text Prompt",
                    placeholder="Enter your description (e.g., 'a cute dog playing in a park')",
                    lines=3,
                    value="a cute dog playing in a sunny park"
                )
                
                style_dropdown = gr.Dropdown(
                    choices=["realistic", "artistic", "professional", "cinematic"],
                    value="realistic",
                    label="Generation Style"
                )
                
                num_images_slider = gr.Slider(
                    minimum=1, maximum=4, value=1, step=1,
                    label="Number of Images"
                )
                
                generate_btn = gr.Button("🎨 Generate Demo Images", variant="primary", size="lg")
                
                gr.HTML("""
                <div style="margin-top: 20px; padding: 15px; background: #f0f0f0; border-radius: 10px;">
                    <h3>📖 How This Works</h3>
                    <ul>
                        <li><strong>Text Processing:</strong> Enhances prompts with quality keywords</li>
                        <li><strong>Demo Generation:</strong> Creates visual representations with text</li>
                        <li><strong>Style Effects:</strong> Different color schemes and layouts</li>
                        <li><strong>Visual Elements:</strong> Simple icons based on prompt keywords</li>
                    </ul>
                    <p><em>For real AI generation, setup the full models using the documentation.</em></p>
                </div>
                """)
            
            with gr.Column(scale=2):
                output_gallery = gr.Gallery(
                    label="Generated Demo Images",
                    columns=2,
                    rows=2,
                    height=400,
                    object_fit="contain"
                )
                
                status_output = gr.Textbox(
                    label="Generation Status & Info",
                    lines=8,
                    interactive=False
                )
        
        # Examples section
        gr.HTML("<h3 style='text-align: center; margin-top: 30px;'>📋 Try These Examples</h3>")
        
        examples = [
            ["a cute dog playing in a park", "realistic", 1],
            ["professional portrait of a human", "professional", 1],
            ["red sports car on city street", "cinematic", 1],
            ["beautiful mountain landscape", "artistic", 1],
        ]
        
        gr.Examples(
            examples=examples,
            inputs=[prompt_input, style_dropdown, num_images_slider],
            outputs=[output_gallery, status_output],
            fn=generate_demo_image,
            cache_examples=False
        )
        
        # Connect the generate button
        generate_btn.click(
            fn=generate_demo_image,
            inputs=[prompt_input, style_dropdown, num_images_slider],
            outputs=[output_gallery, status_output]
        )
    
    return interface

def main():
    """Launch the interface"""
    print("🚀 Starting Text-to-Image Demo Interface...")
    
    # Test text processing availability
    if text_processing_available:
        print("✅ Text processing available")
    else:
        print("⚠️ Text processing limited")
    
    # Create and launch interface
    interface = create_interface()
    
    print("🌐 Launching demo at http://localhost:7860")
    print("📝 This is a demo version - it creates visual representations")
    print("🔧 For real AI generation, setup the full models")
    
    interface.launch(
        server_name="127.0.0.1",  # Use localhost instead of 0.0.0.0
        server_port=7860,
        share=False,
        show_error=True,
        inbrowser=True  # Auto-open browser
    )

if __name__ == "__main__":
    main()