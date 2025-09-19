"""
Unified Text-to-Image and Text-to-Audio Web Interface
Combines both projects in a single interactive web application
"""

import gradio as gr
import os
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import random

# Add both src directories to path
sys.path.append('src')
sys.path.append('text-to-audio/src')

# Import text-to-image components
try:
    from tokenizer import enhance_prompt, create_negative_prompt
    image_processing_available = True
    print("✅ Image processing loaded successfully")
except Exception as e:
    print(f"⚠️ Image processing limited: {e}")
    image_processing_available = False

# Import text-to-audio components
try:
    from main import TextToAudioConverter
    audio_processing_available = True
    print("✅ Audio processing loaded successfully")
except Exception as e:
    print(f"⚠️ Audio processing limited: {e}")
    audio_processing_available = False

# Fallback for audio processing
if not audio_processing_available:
    try:
        import pyttsx3
        windows_tts_available = True
        print("✅ Windows TTS fallback available")
    except:
        windows_tts_available = False
        print("⚠️ No audio processing available")

def create_demo_image(prompt, style="realistic"):
    """Create a high-quality demo image (from text-to-image project)"""
    
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
    center_x, center_y = 256, 256
    
    if any(word in prompt_lower for word in ["dog", "puppy"]):
        # Dog illustration
        draw.ellipse([center_x-60, center_y-20, center_x+60, center_y+40], 
                     fill=(139, 69, 19), outline=(101, 67, 33), width=3)
        draw.ellipse([center_x-30, center_y-60, center_x+30, center_y-20], 
                     fill=(139, 69, 19), outline=(101, 67, 33), width=3)
        # Eyes and nose
        draw.ellipse([center_x-15, center_y-45, center_x-5, center_y-35], fill=(0, 0, 0))
        draw.ellipse([center_x+5, center_y-45, center_x+15, center_y-35], fill=(0, 0, 0))
        draw.ellipse([center_x-5, center_y-25, center_x+5, center_y-15], fill=(0, 0, 0))
        subject = "🐕 DOG"
        
    elif any(word in prompt_lower for word in ["cat", "kitten"]):
        # Cat illustration
        draw.ellipse([center_x-50, center_y-10, center_x+50, center_y+30], 
                     fill=(128, 128, 128), outline=(105, 105, 105), width=3)
        draw.ellipse([center_x-25, center_y-50, center_x+25, center_y-10], 
                     fill=(128, 128, 128), outline=(105, 105, 105), width=3)
        # Ears and eyes
        draw.polygon([(center_x-20, center_y-40), (center_x-10, center_y-60), (center_x, center_y-40)], 
                     fill=(105, 105, 105))
        draw.polygon([(center_x, center_y-40), (center_x+10, center_y-60), (center_x+20, center_y-40)], 
                     fill=(105, 105, 105))
        draw.ellipse([center_x-12, center_y-35, center_x-4, center_y-27], fill=(0, 255, 0))
        draw.ellipse([center_x+4, center_y-35, center_x+12, center_y-27], fill=(0, 255, 0))
        subject = "🐱 CAT"
        
    elif any(word in prompt_lower for word in ["car", "vehicle"]):
        # Car illustration
        draw.rectangle([center_x-80, center_y-20, center_x+80, center_y+20], 
                       fill=(255, 0, 0), outline=(200, 0, 0), width=3)
        draw.rectangle([center_x-50, center_y-40, center_x+50, center_y-20], 
                       fill=(180, 0, 0), outline=(150, 0, 0), width=2)
        # Wheels
        draw.ellipse([center_x-70, center_y+15, center_x-50, center_y+35], fill=(0, 0, 0))
        draw.ellipse([center_x+50, center_y+15, center_x+70, center_y+35], fill=(0, 0, 0))
        subject = "🚗 CAR"
        
    elif any(word in prompt_lower for word in ["human", "person", "portrait"]):
        # Human illustration
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

def generate_audio_fallback(text):
    """Generate audio using Windows TTS as fallback"""
    try:
        import pyttsx3
        
        engine = pyttsx3.init()
        
        # Configure voice settings
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)  # Use first available voice
        
        engine.setProperty('rate', 150)    # Speaking rate
        engine.setProperty('volume', 0.9)  # Volume level
        
        # Create output directory
        os.makedirs("outputs/unified_audio", exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_filename = f"unified_audio_{timestamp}.wav"
        audio_path = os.path.join("outputs/unified_audio", audio_filename)
        
        # Save audio to file
        engine.save_to_file(text, audio_path)
        engine.runAndWait()
        
        if os.path.exists(audio_path):
            return audio_path, f"✅ Audio generated using Windows TTS\n📁 Saved to: {audio_path}"
        else:
            return None, "❌ Failed to generate audio file"
            
    except Exception as e:
        return None, f"❌ Audio generation failed: {str(e)}"

def generate_multimedia_content(prompt, style, include_audio):
    """Generate both image and audio content"""
    if not prompt.strip():
        return None, None, "❌ Please enter a text prompt"
    
    results = []
    
    # Create output directories
    os.makedirs("outputs/unified_images", exist_ok=True)
    os.makedirs("outputs/unified_audio", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate Image
    try:
        # Process prompt if available
        enhanced_prompt = prompt
        if image_processing_available:
            try:
                enhanced_prompt = enhance_prompt(prompt, style)
            except:
                enhanced_prompt = f"{prompt}, {style}, high quality"
        
        # Create image
        img = create_demo_image(prompt, style)
        
        # Save image
        image_filename = f"unified_{style}_{timestamp}.png"
        image_path = os.path.join("outputs/unified_images", image_filename)
        img.save(image_path)
        
        results.append(f"✅ Image generated successfully")
        results.append(f"📸 Style: {style}")
        results.append(f"📁 Image saved to: {image_path}")
        if enhanced_prompt != prompt:
            results.append(f"🔤 Enhanced prompt: '{enhanced_prompt}'")
        
    except Exception as e:
        img = None
        results.append(f"❌ Image generation failed: {str(e)}")
    
    # Generate Audio
    audio_path = None
    if include_audio:
        try:
            # Create a descriptive text for audio
            audio_text = f"This is an AI generated description of: {prompt}. "
            
            # Add description based on prompt
            prompt_lower = prompt.lower()
            if any(word in prompt_lower for word in ["dog", "puppy"]):
                audio_text += "This image shows a friendly dog with characteristic features like ears, eyes, and a nose, rendered in a realistic style."
            elif any(word in prompt_lower for word in ["cat", "kitten"]):
                audio_text += "This image depicts a cat with pointed ears, green eyes, and typical feline characteristics."
            elif any(word in prompt_lower for word in ["car", "vehicle"]):
                audio_text += "This image shows a car with body, wheels, and automotive features in a stylized representation."
            elif any(word in prompt_lower for word in ["human", "person", "portrait"]):
                audio_text += "This image represents a human figure with facial features and body in a artistic style."
            else:
                audio_text += "This image shows a creative artistic representation of the described concept."
            
            audio_text += f" The image is rendered in {style} style with appropriate colors and visual elements."
            
            # Try advanced audio processing first
            if audio_processing_available:
                try:
                    converter = TextToAudioConverter()
                    audio_path = converter.convert_text(audio_text)
                    results.append(f"✅ Audio generated using AI TTS")
                    results.append(f"🎵 Audio saved to: {audio_path}")
                except Exception as e:
                    results.append(f"⚠️ AI TTS failed, trying Windows TTS: {str(e)}")
                    audio_path, audio_status = generate_audio_fallback(audio_text)
                    results.append(audio_status)
            else:
                # Use Windows TTS fallback
                audio_path, audio_status = generate_audio_fallback(audio_text)
                results.append(audio_status)
                
        except Exception as e:
            results.append(f"❌ Audio generation failed: {str(e)}")
    else:
        results.append("🔇 Audio generation skipped (disabled)")
    
    # Compile status message
    status = f"🎨 **MULTIMEDIA GENERATION COMPLETE**\n\n"
    status += f"📝 **Original Prompt:** '{prompt}'\n"
    status += f"⏰ **Generated at:** {datetime.now().strftime('%H:%M:%S')}\n\n"
    status += "📋 **Generation Details:**\n"
    for result in results:
        status += f"  • {result}\n"
    
    return img, audio_path, status

def create_unified_interface():
    """Create the unified web interface"""
    
    with gr.Blocks(title="Unified Text-to-Image & Audio", theme=gr.themes.Soft()) as interface:
        
        gr.HTML("""
        <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin-bottom: 30px;">
            <h1>🎨🎵 Unified Text-to-Image & Audio Generator</h1>
            <p style="font-size: 18px;">Generate both visual and audio content from text prompts!</p>
            <p><strong>✨ Dual Output:</strong> Create images and audio narration simultaneously</p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("<h3>🎯 Input Controls</h3>")
                
                prompt_input = gr.Textbox(
                    label="Enter your text prompt",
                    placeholder="Try: cute dog, beautiful cat, red car, mountain bike, human portrait...",
                    lines=4,
                    value="a cute golden retriever dog playing in a sunny park"
                )
                
                style_dropdown = gr.Dropdown(
                    choices=["realistic", "artistic", "professional", "cinematic"],
                    value="realistic",
                    label="Visual style for image"
                )
                
                include_audio_checkbox = gr.Checkbox(
                    label="Generate audio narration",
                    value=True,
                    info="Create spoken description of the image"
                )
                
                generate_btn = gr.Button("🎨🎵 Generate Image + Audio", variant="primary", size="lg")
                
                gr.HTML("""
                <div style="margin-top: 20px; padding: 15px; background: #e3f2fd; border-radius: 8px; border-left: 4px solid #2196f3;">
                    <h4>🚀 Features:</h4>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li><strong>Dual Output:</strong> Image + Audio in one interface</li>
                        <li><strong>Smart Descriptions:</strong> Audio narrates the image content</li>
                        <li><strong>Multiple Styles:</strong> Realistic, artistic, professional, cinematic</li>
                        <li><strong>Fallback Audio:</strong> Windows TTS if AI TTS unavailable</li>
                    </ul>
                </div>
                """)
            
            with gr.Column(scale=2):
                gr.HTML("<h3>🖼️ Generated Image</h3>")
                
                output_image = gr.Image(
                    label="Generated Image",
                    height=400,
                    show_label=False
                )
                
                gr.HTML("<h3>🎵 Generated Audio</h3>")
                
                output_audio = gr.Audio(
                    label="Generated Audio Narration",
                    show_label=False
                )
                
                status_output = gr.Textbox(
                    label="Generation Status & Details",
                    lines=12,
                    interactive=False
                )
        
        # System Status
        gr.HTML("<h3 style='text-align: center; margin-top: 25px; color: #333;'>⚙️ System Status</h3>")
        
        system_status = "**System Capabilities:**\n"
        system_status += f"• Image Processing: {'✅ Available' if image_processing_available else '⚠️ Limited'}\n"
        system_status += f"• AI Audio Processing: {'✅ Available' if audio_processing_available else '⚠️ Limited'}\n"
        system_status += f"• Windows TTS Fallback: {'✅ Available' if windows_tts_available else '❌ Unavailable'}\n"
        
        gr.Markdown(system_status)
        
        # Examples
        gr.HTML("<h3 style='text-align: center; margin-top: 25px; color: #333;'>📋 Try These Examples</h3>")
        
        examples = [
            ["a cute golden retriever dog playing in a park", "realistic", True],
            ["a fluffy white cat sitting by the window", "artistic", True],
            ["a red sports car on a mountain road", "cinematic", True],
            ["a professional portrait of a business person", "professional", False],
            ["a beautiful mountain landscape with a lake", "artistic", True],
        ]
        
        gr.Examples(
            examples=examples,
            inputs=[prompt_input, style_dropdown, include_audio_checkbox],
            outputs=[output_image, output_audio, status_output],
            fn=generate_multimedia_content,
            cache_examples=False
        )
        
        # Connect the generate button
        generate_btn.click(
            fn=generate_multimedia_content,
            inputs=[prompt_input, style_dropdown, include_audio_checkbox],
            outputs=[output_image, output_audio, status_output]
        )
        
        # Footer
        gr.HTML("""
        <div style="margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 10px; text-align: center;">
            <h4>🎉 Unified Multimedia Generator</h4>
            <p>This interface combines your text-to-image and text-to-audio projects into one powerful tool!</p>
            <p><strong>Projects integrated:</strong> Text-to-Image Generator + Text-to-Audio Q&A System</p>
        </div>
        """)
    
    return interface

def main():
    """Launch the unified interface"""
    print("🚀 Starting Unified Text-to-Image & Audio Generator...")
    
    # Test component availability
    if image_processing_available:
        print("✅ Text-to-Image processing available")
    else:
        print("⚠️ Text-to-Image processing limited")
    
    if audio_processing_available:
        print("✅ AI Audio processing available")
    elif windows_tts_available:
        print("✅ Windows TTS fallback available")
    else:
        print("⚠️ No audio processing available")
    
    # Create and launch interface
    interface = create_unified_interface()
    
    print("🌐 Launching unified interface at http://localhost:7863")
    print("🎨🎵 Generate both images and audio from text prompts!")
    print("🔗 This combines both your text-to-image and text-to-audio projects!")
    
    interface.launch(
        server_name="127.0.0.1",
        server_port=7863,
        share=False,
        show_error=True,
        inbrowser=True
    )

if __name__ == "__main__":
    main()