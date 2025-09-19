"""
Image Gallery Viewer - Display all generated realistic images
"""

import gradio as gr
import os
from PIL import Image
import glob

def load_batch_images():
    """Load all images from the batch realistic folder"""
    batch_folder = "outputs/batch_realistic"
    if not os.path.exists(batch_folder):
        return [], "❌ No batch images found. Run batch_realistic_generator.py first!"
    
    # Find all PNG files
    image_files = glob.glob(os.path.join(batch_folder, "*.png"))
    
    if not image_files:
        return [], "❌ No images found in batch folder!"
    
    # Sort files by name
    image_files.sort()
    
    # Load images
    images = []
    image_info = []
    
    for file_path in image_files:
        try:
            img = Image.open(file_path)
            images.append(img)
            
            # Extract info from filename
            filename = os.path.basename(file_path)
            # Parse filename like "dog_1_golden_retriever_20250920_033714.png"
            parts = filename.replace('.png', '').split('_')
            if len(parts) >= 4:
                category = parts[0]
                number = parts[1]
                variation = ' '.join(parts[2:-2])  # Everything except timestamp
                info = f"{category.title()} #{number}: {variation.title()}"
            else:
                info = filename
            
            image_info.append(info)
            
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    return images, image_info

def create_gallery_interface():
    """Create the image gallery interface"""
    
    with gr.Blocks(title="AI Generated Image Gallery", theme=gr.themes.Soft()) as interface:
        
        gr.HTML("""
        <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin-bottom: 30px;">
            <h1>🖼️ AI Generated Image Gallery</h1>
            <p style="font-size: 18px;">Realistic Demo Images Collection</p>
            <p><strong>Categories:</strong> Dogs 🐕 | Cats 🐱 | Cars 🚗 | Bikes 🚲 | Laptops 💻</p>
        </div>
        """)
        
        # Load images automatically
        images, image_info = load_batch_images()
        
        if images:
            gr.HTML(f"""
            <div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px; margin-bottom: 20px;">
                <h2>✅ Successfully Loaded {len(images)} Images</h2>
                <p>High-quality realistic demo images generated for your request</p>
            </div>
            """)
            
            # Create gallery
            gallery = gr.Gallery(
                value=images,
                label="Generated Image Collection",
                columns=4,
                rows=5,
                height=600,
                object_fit="contain",
                show_label=True
            )
            
            # Show image information
            gr.HTML("<h3>📋 Image Details</h3>")
            info_text = "\n".join([f"{i+1:2d}. {info}" for i, info in enumerate(image_info)])
            gr.Textbox(
                value=info_text,
                label="Generated Images List",
                lines=25,
                interactive=False
            )
            
            # Statistics
            categories = {}
            for info in image_info:
                category = info.split(':')[0].split('#')[0].strip()
                categories[category] = categories.get(category, 0) + 1
            
            stats_text = "📊 **Generation Statistics:**\n\n"
            for category, count in categories.items():
                stats_text += f"• {category}: {count} images\n"
            stats_text += f"\n**Total:** {len(images)} images"
            
            gr.Markdown(stats_text)
            
        else:
            gr.HTML("""
            <div style="text-align: center; padding: 40px; background: #fff3cd; border-radius: 10px; border-left: 4px solid #ffc107;">
                <h2>⚠️ No Images Found</h2>
                <p>Please run the batch generator first:</p>
                <code>python batch_realistic_generator.py</code>
            </div>
            """)
        
        # Instructions
        gr.HTML("""
        <div style="margin-top: 30px; padding: 20px; background: #d1ecf1; border-radius: 10px; border-left: 4px solid #17a2b8;">
            <h3>🔧 How to Generate Real AI Images</h3>
            <p>The images shown here are realistic demo representations. To generate actual AI images:</p>
            <ol>
                <li><strong>Use Enhanced Generator:</strong> <code>python enhanced_generator.py</code></li>
                <li><strong>Set up Hugging Face:</strong> Get API access for real AI models</li>
                <li><strong>Download Models:</strong> FLUX.1-schnell or Stable Diffusion models</li>
                <li><strong>GPU Setup:</strong> For faster real AI generation</li>
            </ol>
        </div>
        """)
    
    return interface

def main():
    """Launch the gallery viewer"""
    print("🖼️ Starting Image Gallery Viewer...")
    
    # Check if images exist
    batch_folder = "outputs/batch_realistic"
    if os.path.exists(batch_folder):
        image_count = len(glob.glob(os.path.join(batch_folder, "*.png")))
        print(f"📸 Found {image_count} images to display")
    else:
        print("⚠️ No batch images found - will show instructions")
    
    # Create and launch interface
    interface = create_gallery_interface()
    
    print("🌐 Launching gallery at http://localhost:7861")
    print("🖼️ View all your generated realistic images in the browser")
    
    interface.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False,
        show_error=True,
        inbrowser=True
    )

if __name__ == "__main__":
    main()