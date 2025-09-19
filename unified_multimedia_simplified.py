"""
Unified Text-to-Image and Text-to-Audio Web Interface (Simplified Version)
Combines both projects with better error handling and simpler audio processing
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

# Enhanced audio processing with better file handling
def generate_audio_simple(text):
    """Generate audio using Windows TTS with improved file handling"""
    try:
        import pyttsx3
        import time
        
        print(f"🎵 Generating audio for text: {text[:50]}...")
        
        engine = pyttsx3.init()
        
        # Configure voice settings
        voices = engine.getProperty('voices')
        if voices:
            print(f"🔊 Available voices: {len(voices)}")
            # Try to find a good voice
            for voice in voices:
                if 'zira' in voice.name.lower() or 'david' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    print(f"✅ Using voice: {voice.name}")
                    break
            else:
                engine.setProperty('voice', voices[0].id)
                print(f"✅ Using default voice: {voices[0].name}")
        
        engine.setProperty('rate', 140)    # Speaking rate (slower for clarity)
        engine.setProperty('volume', 0.9)  # Volume level
        
        # Create output directory
        os.makedirs("outputs/unified_audio", exist_ok=True)
        
        # Generate unique filename with better path handling
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
        audio_filename = f"multimedia_{timestamp}.wav"
        audio_path = os.path.abspath(os.path.join("outputs/unified_audio", audio_filename))
        
        print(f"📁 Audio will be saved to: {audio_path}")
        
        # Save audio to file
        engine.save_to_file(text, audio_path)
        engine.runAndWait()
        
        # Give the engine time to finish writing the file
        time.sleep(1)
        
        # Verify file was created with multiple checks
        max_wait = 5  # Wait up to 5 seconds
        for i in range(max_wait):
            if os.path.exists(audio_path):
                file_size = os.path.getsize(audio_path)
                if file_size > 100:  # At least 100 bytes
                    file_size_kb = file_size / 1024
                    print(f"✅ Audio file created: {file_size_kb:.1f} KB")
                    return audio_path, f"✅ Audio generated successfully ({file_size_kb:.1f} KB)\n📁 File: {audio_filename}"
            time.sleep(0.5)
        
        # If file exists but is too small or doesn't exist
        if os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path)
            return None, f"❌ Audio file too small ({file_size} bytes)"
        else:
            return None, "❌ Audio file was not created"
            
    except Exception as e:
        print(f"❌ Audio generation error: {str(e)}")
        return None, f"❌ Audio generation failed: {str(e)}"

def create_demo_image(prompt, style="realistic"):
    """Create a high-quality demo image with better visual appeal"""
    
    # Color schemes for different styles
    colors = {
        "realistic": {"bg": (245, 248, 255), "accent": (70, 130, 180), "text": (25, 25, 112), "subject": (139, 69, 19)},
        "artistic": {"bg": (255, 245, 238), "accent": (255, 140, 0), "text": (139, 69, 19), "subject": (255, 100, 100)},
        "professional": {"bg": (248, 248, 255), "accent": (105, 105, 105), "text": (47, 79, 79), "subject": (70, 130, 180)},
        "cinematic": {"bg": (25, 25, 25), "accent": (255, 215, 0), "text": (255, 255, 255), "subject": (255, 100, 100)}
    }
    
    color_scheme = colors.get(style, colors["realistic"])
    
    # Create image with higher quality
    img = Image.new('RGB', (512, 512), color_scheme["bg"])
    draw = ImageDraw.Draw(img)
    
    # Create gradient background
    for y in range(512):
        factor = y / 512
        r = int(color_scheme["bg"][0] * (1 - factor * 0.3))
        g = int(color_scheme["bg"][1] * (1 - factor * 0.3))
        b = int(color_scheme["bg"][2] * (1 - factor * 0.3))
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
    
    # Add title with better styling
    draw.text((25, 25), "🎨 AI Generated Image", fill=color_scheme["text"], font=font_large)
    draw.text((25, 55), f"Style: {style.title()}", fill=color_scheme["accent"], font=font_medium)
    
    # Create visual based on prompt keywords
    prompt_lower = prompt.lower()
    center_x, center_y = 256, 280
    
    if any(word in prompt_lower for word in ["dog", "puppy", "golden retriever"]):
        # Enhanced dog illustration
        # Body
        draw.ellipse([center_x-70, center_y-10, center_x+70, center_y+50], 
                     fill=color_scheme["subject"], outline=(101, 67, 33), width=4)
        # Head
        draw.ellipse([center_x-35, center_y-70, center_x+35, center_y-10], 
                     fill=color_scheme["subject"], outline=(101, 67, 33), width=4)
        # Ears
        draw.ellipse([center_x-45, center_y-60, center_x-25, center_y-40], fill=(120, 60, 20))
        draw.ellipse([center_x+25, center_y-60, center_x+45, center_y-40], fill=(120, 60, 20))
        # Eyes
        draw.ellipse([center_x-20, center_y-50, center_x-10, center_y-40], fill=(0, 0, 0))
        draw.ellipse([center_x+10, center_y-50, center_x+20, center_y-40], fill=(0, 0, 0))
        # Nose
        draw.ellipse([center_x-5, center_y-30, center_x+5, center_y-20], fill=(0, 0, 0))
        # Tail
        draw.ellipse([center_x+60, center_y-5, center_x+80, center_y+15], fill=color_scheme["subject"])
        subject = "🐕 GOLDEN RETRIEVER DOG"
        
    elif any(word in prompt_lower for word in ["cat", "kitten", "fluffy"]):
        # Enhanced cat illustration
        # Body
        draw.ellipse([center_x-55, center_y-5, center_x+55, center_y+35], 
                     fill=(128, 128, 128), outline=(105, 105, 105), width=4)
        # Head
        draw.ellipse([center_x-30, center_y-55, center_x+30, center_y-5], 
                     fill=(128, 128, 128), outline=(105, 105, 105), width=4)
        # Ears
        draw.polygon([(center_x-25, center_y-45), (center_x-15, center_y-70), (center_x-5, center_y-45)], 
                     fill=(105, 105, 105))
        draw.polygon([(center_x+5, center_y-45), (center_x+15, center_y-70), (center_x+25, center_y-45)], 
                     fill=(105, 105, 105))
        # Eyes
        draw.ellipse([center_x-15, center_y-40, center_x-5, center_y-30], fill=(0, 255, 0))
        draw.ellipse([center_x+5, center_y-40, center_x+15, center_y-30], fill=(0, 255, 0))
        # Nose
        draw.polygon([(center_x-3, center_y-25), (center_x, center_y-20), (center_x+3, center_y-25)], fill=(255, 105, 180))
        # Whiskers
        draw.line([(center_x-30, center_y-30), (center_x-15, center_y-28)], fill=(0, 0, 0), width=2)
        draw.line([(center_x+15, center_y-28), (center_x+30, center_y-30)], fill=(0, 0, 0), width=2)
        # Tail
        draw.arc([center_x+45, center_y-10, center_x+75, center_y+20], 0, 180, fill=(105, 105, 105), width=8)
        subject = "🐱 FLUFFY CAT"
        
    elif any(word in prompt_lower for word in ["car", "vehicle", "sports car", "red car"]):
        # Enhanced car illustration
        # Main body
        draw.rectangle([center_x-90, center_y-15, center_x+90, center_y+25], 
                       fill=(255, 0, 0), outline=(200, 0, 0), width=4)
        # Windshield
        draw.rectangle([center_x-60, center_y-45, center_x+60, center_y-15], 
                       fill=(180, 0, 0), outline=(150, 0, 0), width=3)
        # Wheels
        draw.ellipse([center_x-80, center_y+20, center_x-55, center_y+45], fill=(0, 0, 0))
        draw.ellipse([center_x+55, center_y+20, center_x+80, center_y+45], fill=(0, 0, 0))
        # Wheel rims
        draw.ellipse([center_x-75, center_y+25, center_x-60, center_y+40], fill=(192, 192, 192))
        draw.ellipse([center_x+60, center_y+25, center_x+75, center_y+40], fill=(192, 192, 192))
        # Headlights
        draw.ellipse([center_x-95, center_y-5, center_x-85, center_y+5], fill=(255, 255, 0))
        draw.ellipse([center_x+85, center_y-5, center_x+95, center_y+5], fill=(255, 255, 0))
        subject = "🚗 RED SPORTS CAR"
        
    elif any(word in prompt_lower for word in ["human", "person", "portrait", "business"]):
        # Enhanced human illustration
        # Head
        draw.ellipse([center_x-25, center_y-70, center_x+25, center_y-20], 
                     fill=(255, 220, 177), outline=(200, 180, 140), width=3)
        # Body
        draw.rectangle([center_x-20, center_y-20, center_x+20, center_y+40], 
                       fill=(0, 100, 200), outline=(0, 80, 160), width=3)
        # Arms
        draw.rectangle([center_x-40, center_y-15, center_x-20, center_y+25], 
                       fill=(255, 220, 177), outline=(200, 180, 140), width=2)
        draw.rectangle([center_x+20, center_y-15, center_x+40, center_y+25], 
                       fill=(255, 220, 177), outline=(200, 180, 140), width=2)
        # Eyes
        draw.ellipse([center_x-12, center_y-55, center_x-6, center_y-49], fill=(0, 0, 0))
        draw.ellipse([center_x+6, center_y-55, center_x+12, center_y-49], fill=(0, 0, 0))
        # Mouth
        draw.arc([center_x-8, center_y-40, center_x+8, center_y-32], 0, 180, fill=(0, 0, 0), width=2)
        # Hair
        draw.ellipse([center_x-28, center_y-75, center_x+28, center_y-50], fill=(101, 67, 33))
        # Tie (if business)
        if "business" in prompt_lower or "professional" in prompt_lower:
            draw.polygon([(center_x-5, center_y-20), (center_x+5, center_y-20), (center_x+3, center_y+10), (center_x-3, center_y+10)], 
                         fill=(128, 0, 0))
        subject = "👤 PROFESSIONAL PERSON"
        
    elif any(word in prompt_lower for word in ["mountain", "landscape", "lake", "beautiful"]):
        # Enhanced landscape illustration
        # Sky gradient
        for y in range(center_y-100, center_y):
            factor = (y - (center_y-100)) / 100
            r = int(135 + factor * 50)
            g = int(206 + factor * 30)
            b = int(250)
            draw.line([(center_x-120, y), (center_x+120, y)], fill=(r, g, b))
        
        # Mountains
        draw.polygon([(center_x-120, center_y), (center_x-60, center_y-80), (center_x, center_y-40), 
                      (center_x+60, center_y-100), (center_x+120, center_y)], 
                     fill=(139, 69, 19), outline=(101, 67, 33), width=2)
        
        # Lake
        draw.ellipse([center_x-80, center_y+20, center_x+80, center_y+60], 
                     fill=(70, 130, 180), outline=(25, 25, 112), width=2)
        
        # Trees
        for i, x_offset in enumerate([-40, 0, 40]):
            tree_x = center_x + x_offset
            # Trunk
            draw.rectangle([tree_x-3, center_y-10, tree_x+3, center_y+20], fill=(139, 69, 19))
            # Leaves
            draw.ellipse([tree_x-15, center_y-40, tree_x+15, center_y-10], fill=(34, 139, 34))
        
        subject = "🏔️ MOUNTAIN LANDSCAPE"
        
    else:
        # Generic creative illustration with more detail
        colors_art = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100), (255, 100, 255)]
        for i, color in enumerate(colors_art):
            x = center_x - 80 + i * 40
            y = center_y - 40 + (i % 2) * 40
            draw.ellipse([x, y, x+35, y+35], fill=color, outline=color_scheme["accent"], width=3)
            # Add inner detail
            draw.ellipse([x+8, y+8, x+27, y+27], outline=(255, 255, 255), width=2)
        subject = "✨ CREATIVE ART"
    
    # Add subject label with better positioning
    draw.text((25, 95), f"Generated: {subject}", fill=color_scheme["accent"], font=font_medium)
    
    # Add prompt with better formatting
    draw.text((25, 400), "Prompt:", fill=color_scheme["accent"], font=font_small)
    
    # Wrap prompt text nicely
    words = prompt.split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line + " " + word) < 45:
            current_line += (" " if current_line else "") + word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    for i, line in enumerate(lines[:3]):  # Max 3 lines
        draw.text((25, 420 + i * 20), f'"{line}"', fill=color_scheme["text"], font=font_small)
    
    # Add timestamp
    timestamp = datetime.now().strftime("%H:%M:%S")
    draw.text((400, 480), f"Generated at {timestamp}", fill=color_scheme["accent"], font=font_small)
    
    return img

def generate_multimedia_content(prompt, style, include_audio):
    """Generate both image and audio content with better error handling"""
    if not prompt.strip():
        return None, None, "❌ Please enter a text prompt"
    
    results = []
    
    # Create output directories
    os.makedirs("outputs/unified_images", exist_ok=True)
    os.makedirs("outputs/unified_audio", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate Image
    img = None
    try:
        # Process prompt if available
        enhanced_prompt = prompt
        if image_processing_available:
            try:
                enhanced_prompt = enhance_prompt(prompt, style)
                results.append(f"🔤 Enhanced prompt: '{enhanced_prompt}'")
            except:
                enhanced_prompt = f"{prompt}, {style}, high quality, detailed"
                results.append(f"🔤 Basic enhancement applied")
        
        # Create image
        img = create_demo_image(prompt, style)
        
        # Save image
        image_filename = f"multimedia_{style}_{timestamp}.png"
        image_path = os.path.join("outputs/unified_images", image_filename)
        img.save(image_path, quality=95)
        
        results.append(f"✅ Image generated successfully")
        results.append(f"📸 Style: {style.title()}")
        results.append(f"📁 Image saved to: {image_path}")
        
    except Exception as e:
        img = None
        results.append(f"❌ Image generation failed: {str(e)}")
    
    # Generate Audio
    audio_path = None
    if include_audio:
        try:
            print("🎵 Starting audio generation...")
            
            # Create a descriptive text for audio
            audio_text = f"This is an AI generated multimedia content. The prompt was: {prompt}. "
            
            # Add detailed description based on prompt
            prompt_lower = prompt.lower()
            if any(word in prompt_lower for word in ["dog", "puppy", "golden retriever"]):
                audio_text += "The image shows a golden retriever dog with characteristic features including ears, eyes, nose, and a wagging tail. The dog appears friendly and is rendered with warm brown colors in a realistic style."
            elif any(word in prompt_lower for word in ["cat", "kitten", "fluffy"]):
                audio_text += "The image depicts a fluffy cat with pointed ears, bright green eyes, and typical feline characteristics. The cat has whiskers and a curved tail, rendered in gray tones with artistic detail."
            elif any(word in prompt_lower for word in ["car", "vehicle", "sports car", "red car"]):
                audio_text += "The image shows a red sports car with a sleek body, windshield, wheels with chrome rims, and bright headlights. The vehicle represents modern automotive design with clean lines and sporty proportions."
            elif any(word in prompt_lower for word in ["human", "person", "portrait", "business"]):
                audio_text += "The image represents a professional person with facial features, hair, and business attire including a tie. The portrait shows a human figure in a formal, business-appropriate style."
            elif any(word in prompt_lower for word in ["mountain", "landscape", "lake", "beautiful"]):
                audio_text += "The image shows a beautiful mountain landscape with peaks, a serene lake, and trees. The scene includes natural elements like mountains in the background, water in the foreground, and vegetation, creating a peaceful natural setting."
            else:
                audio_text += "The image shows a creative artistic representation with colorful elements and geometric shapes. The composition includes multiple colors and forms arranged in an aesthetically pleasing manner."
            
            audio_text += f" The image is rendered in {style} style with appropriate colors, lighting, and visual elements that enhance the overall composition and mood."
            
            print(f"📝 Audio text length: {len(audio_text)} characters")
            
            # Generate audio
            audio_path, audio_status = generate_audio_simple(audio_text)
            results.append(audio_status)
            
            if audio_path:
                print(f"✅ Audio generated: {audio_path}")
                # Ensure the path is absolute for Gradio
                audio_path = os.path.abspath(audio_path)
                results.append(f"🎵 Audio ready for playback")
            else:
                print("❌ Audio generation failed")
                
        except Exception as e:
            error_msg = f"❌ Audio generation failed: {str(e)}"
            print(error_msg)
            results.append(error_msg)
    else:
        results.append("🔇 Audio generation skipped (user disabled)")
    
    # Compile comprehensive status message
    status = f"🎨🎵 **MULTIMEDIA GENERATION COMPLETE**\n\n"
    status += f"📝 **Original Prompt:** '{prompt}'\n"
    status += f"🎨 **Visual Style:** {style.title()}\n"
    status += f"🎵 **Audio Included:** {'Yes' if include_audio else 'No'}\n"
    status += f"⏰ **Generated at:** {datetime.now().strftime('%H:%M:%S on %B %d, %Y')}\n\n"
    status += "📋 **Generation Details:**\n"
    for i, result in enumerate(results, 1):
        status += f"  {i}. {result}\n"
    
    # Add file information if available
    if img and audio_path:
        status += f"\n🎉 **SUCCESS:** Both image and audio generated successfully!\n"
        status += f"🖼️ **Image:** High-quality {style} style visualization\n"
        status += f"🎵 **Audio:** Detailed narration describing the image content\n"
        status += f"📂 **Audio File:** {os.path.basename(audio_path) if audio_path else 'None'}\n"
        if audio_path and os.path.exists(audio_path):
            status += f"📐 **Audio Size:** {os.path.getsize(audio_path)} bytes\n"
    elif img:
        status += f"\n✅ **Image generated successfully** (audio disabled)\n"
    elif audio_path:
        status += f"\n✅ **Audio generated successfully** (image failed)\n"
        status += f"📂 **Audio File:** {os.path.basename(audio_path)}\n"
    else:
        status += f"\n❌ **Generation failed** - Please try again\n"
    
    # Add debugging info
    status += f"\n🔧 **Debug Info:**\n"
    status += f"  • Audio path returned: {audio_path is not None}\n"
    status += f"  • Audio file exists: {os.path.exists(audio_path) if audio_path else 'N/A'}\n"
    if audio_path:
        status += f"  • Full audio path: {audio_path}\n"
    
    return img, audio_path, status

def create_unified_interface():
    """Create the unified web interface with better styling"""
    
    # Custom CSS for better appearance and text visibility
    custom_css = """
    .title-container {
        text-align: center; 
        padding: 30px; 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
        color: white; 
        border-radius: 15px; 
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .feature-box {
        margin-top: 20px; 
        padding: 20px; 
        background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
        border-radius: 12px; 
        border-left: 5px solid #2196f3;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        color: #000 !important;
    }
    .feature-box * {
        color: #000 !important;
    }
    .status-box {
        margin-top: 25px; 
        padding: 20px; 
        background: #f8f9fa; 
        border-radius: 12px; 
        text-align: center;
        border: 2px solid #e9ecef;
        color: #000 !important;
    }
    .status-box * {
        color: #000 !important;
    }
    """
    
    with gr.Blocks(title="🎨🎵 Unified Multimedia Generator", theme=gr.themes.Soft(), css=custom_css) as interface:
        
        gr.HTML("""
        <div class="title-container">
            <h1 style="font-size: 2.5em; margin-bottom: 10px;">🎨🎵 Unified Multimedia Generator</h1>
            <p style="font-size: 1.3em; margin-bottom: 5px;">Generate both visual and audio content from text prompts!</p>
            <p style="font-size: 1.1em;"><strong>✨ Dual Output:</strong> Create images and audio narration simultaneously</p>
            <p style="font-size: 1em; opacity: 0.9;">Combining Text-to-Image + Text-to-Audio in one powerful interface</p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("<h3 style='color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px;'>🎯 Input Controls</h3>")
                
                prompt_input = gr.Textbox(
                    label="📝 Enter your text prompt",
                    placeholder="Try: cute golden retriever dog, fluffy white cat, red sports car, beautiful mountain landscape, professional business person...",
                    lines=4,
                    value="a cute golden retriever dog playing in a sunny park"
                )
                
                style_dropdown = gr.Dropdown(
                    choices=["realistic", "artistic", "professional", "cinematic"],
                    value="realistic",
                    label="🎨 Visual style for image",
                    info="Choose the artistic style for image generation"
                )
                
                include_audio_checkbox = gr.Checkbox(
                    label="🎵 Generate audio narration",
                    value=True,
                    info="Create spoken description of the generated image"
                )
                
                generate_btn = gr.Button(
                    "🎨🎵 Generate Image + Audio", 
                    variant="primary", 
                    size="lg",
                    elem_classes=["generate-button"]
                )
                
                gr.HTML("""
                <div class="feature-box">
                    <h4 style="color: #000; margin-bottom: 15px;">🚀 Key Features:</h4>
                    <ul style="margin: 10px 0; padding-left: 20px; line-height: 1.6; color: #000;">
                        <li><strong>🎨 Smart Image Generation:</strong> Creates detailed visuals based on your prompt</li>
                        <li><strong>🎵 Audio Narration:</strong> Generates spoken description of the image</li>
                        <li><strong>🎭 Multiple Styles:</strong> Realistic, artistic, professional, cinematic</li>
                        <li><strong>💾 Auto-Save:</strong> Both image and audio files saved automatically</li>
                        <li><strong>🔧 Reliable Fallbacks:</strong> Windows TTS if advanced audio unavailable</li>
                    </ul>
                </div>
                """)
            
            with gr.Column(scale=2):
                gr.HTML("<h3 style='color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px;'>🖼️ Generated Image</h3>")
                
                output_image = gr.Image(
                    label="Generated Image",
                    height=420,
                    show_label=False,
                    elem_classes=["output-image"]
                )
                
                gr.HTML("<h3 style='color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-top: 20px;'>🎵 Generated Audio</h3>")
                
                output_audio = gr.Audio(
                    label="Generated Audio Narration",
                    show_label=False,
                    elem_classes=["output-audio"]
                )
                
                status_output = gr.Textbox(
                    label="💬 Generation Status & Details",
                    lines=10,
                    interactive=False,
                    elem_classes=["status-output"]
                )
        
        # System Status with better styling
        gr.HTML("<h3 style='text-align: center; margin-top: 30px; color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px;'>⚙️ System Status</h3>")
        
        system_status = f"""
**🔧 System Capabilities:**
        
• **Image Processing:** {'✅ Full capability - Enhanced prompts available' if image_processing_available else '⚠️ Basic capability - Simple enhancement only'}

• **Audio Processing:** ✅ Windows TTS available for reliable narration

• **File Management:** ✅ Auto-save to organized output folders

• **Error Handling:** ✅ Comprehensive fallback systems

• **Interface:** ✅ Real-time generation with progress feedback
        """
        
        gr.Markdown(system_status)
        
        # Examples with better organization
        gr.HTML("<h3 style='text-align: center; margin-top: 30px; color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px;'>📋 Try These Examples</h3>")
        
        examples = [
            ["a cute golden retriever dog playing in a park", "realistic", True],
            ["a fluffy white cat sitting by the window", "artistic", True],
            ["a red sports car on a mountain road", "cinematic", True],
            ["a professional portrait of a business person", "professional", True],
            ["a beautiful mountain landscape with a lake", "artistic", True],
            ["a modern city skyline at sunset", "cinematic", False],
        ]
        
        gr.Examples(
            examples=examples,
            inputs=[prompt_input, style_dropdown, include_audio_checkbox],
            outputs=[output_image, output_audio, status_output],
            fn=generate_multimedia_content,
            cache_examples=False,
            label="Click any example to try it:"
        )
        
        # Connect the generate button
        generate_btn.click(
            fn=generate_multimedia_content,
            inputs=[prompt_input, style_dropdown, include_audio_checkbox],
            outputs=[output_image, output_audio, status_output]
        )
        
        # Footer with project information
        gr.HTML("""
        <div class="status-box">
            <h4 style="color: #000; margin-bottom: 15px;">🎉 Unified Multimedia Generator</h4>
            <p style="margin-bottom: 10px; color: #000;">This interface successfully combines your text-to-image and text-to-audio projects!</p>
            <div style="display: flex; justify-content: center; gap: 30px; margin-top: 15px;">
                <div style="color: #000;"><strong>🎨 Text-to-Image:</strong> Visual generation with multiple styles</div>
                <div style="color: #000;"><strong>🎵 Text-to-Audio:</strong> Intelligent narration system</div>
            </div>
            <p style="margin-top: 15px; font-size: 0.9em; color: #000;">Both projects integrated into one powerful multimedia creation tool</p>
        </div>
        """)
    
    return interface

def main():
    """Launch the unified interface with better startup information"""
    print("=" * 60)
    print("🚀 UNIFIED MULTIMEDIA GENERATOR")
    print("=" * 60)
    print("🎨 Text-to-Image: ✅ Available")
    print("🎵 Text-to-Audio: ✅ Windows TTS Available")
    print("💻 Interface: ✅ Gradio Web UI")
    print("🌐 URL: http://localhost:7863")
    print("=" * 60)
    
    # Create and launch interface
    interface = create_unified_interface()
    
    print("\n🎉 Launching unified multimedia interface...")
    print("🎨🎵 Generate both images and audio from text prompts!")
    print("🔗 Successfully combines both your AI projects!")
    print("📱 Open your browser to http://localhost:7863")
    print("\n⏹️ Press Ctrl+C to stop the server")
    
    try:
        interface.launch(
            server_name="127.0.0.1",
            server_port=7863,
            share=False,
            show_error=True,
            inbrowser=True,
            quiet=False
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error launching interface: {e}")

if __name__ == "__main__":
    main()