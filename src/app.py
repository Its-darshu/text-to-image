"""
Simple web interface for text-to-image generation
This module provides a Gradio-based interface for easy interaction.
"""

import gradio as gr
import os
from PIL import Image
import torch

from generator import TextToImageGenerator
from tokenizer import enhance_prompt, create_negative_prompt
from dataset import DatasetCreator
from fine_tuner import TextToImageFineTuner

class TextToImageInterface:
    """Web interface for text-to-image generation"""
    
    def __init__(self):
        """Initialize the interface"""
        self.generator = None
        self.fine_tuner = None
        
        # Create output directories
        os.makedirs("outputs/generated", exist_ok=True)
        os.makedirs("outputs/models", exist_ok=True)
    
    def initialize_generator(self, model_name="flux_schnell"):
        """Initialize the image generator"""
        if self.generator is None:
            print(f"🚀 Initializing generator with model: {model_name}")
            self.generator = TextToImageGenerator(model_name=model_name)
        return self.generator
    
    def generate_image(self, prompt, negative_prompt="", num_images=1, seed=None, 
                      use_enhancement=True, enhancement_style="realistic"):
        """
        Generate images from text prompt
        
        Args:
            prompt (str): Text description
            negative_prompt (str): Negative prompt
            num_images (int): Number of images to generate
            seed (int): Random seed
            use_enhancement (bool): Whether to enhance the prompt
            enhancement_style (str): Style of enhancement
            
        Returns:
            tuple: (list of images, status message)
        """
        try:
            # Initialize generator if needed
            generator = self.initialize_generator()
            
            # Enhance prompt if requested
            if use_enhancement and prompt.strip():
                enhanced_prompt = enhance_prompt(prompt, style=enhancement_style)
                print(f"✨ Enhanced prompt: {enhanced_prompt}")
            else:
                enhanced_prompt = prompt
            
            # Use default negative prompt if none provided
            if not negative_prompt.strip():
                negative_prompt = create_negative_prompt()
            
            # Generate images
            images, saved_paths = generator.generate_and_save(
                prompt=enhanced_prompt,
                negative_prompt=negative_prompt,
                num_images=num_images,
                seed=seed
            )
            
            status = f"✅ Generated {len(images)} image(s) successfully!\\nSaved to: {', '.join(saved_paths)}"
            
            return images, status
            
        except Exception as e:
            error_msg = f"❌ Error generating image: {str(e)}"
            print(error_msg)
            return [], error_msg
    
    def create_training_data(self, text_prompt, image):
        """
        Add training data for fine-tuning
        
        Args:
            text_prompt (str): Text description
            image: PIL Image
            
        Returns:
            str: Status message
        """
        try:
            if not text_prompt.strip():
                return "❌ Please provide a text prompt"
            
            if image is None:
                return "❌ Please provide an image"
            
            # Save the image temporarily
            temp_image_path = "temp_training_image.jpg"
            image.save(temp_image_path)
            
            # Add to dataset
            creator = DatasetCreator()
            creator.add_custom_data(text_prompt, temp_image_path, split="train")
            
            # Clean up
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
            
            return f"✅ Added training data: '{text_prompt}'"
            
        except Exception as e:
            return f"❌ Error adding training data: {str(e)}"
    
    def start_fine_tuning(self, num_epochs=2, learning_rate=1e-5):
        """
        Start fine-tuning process
        
        Args:
            num_epochs (int): Number of training epochs
            learning_rate (float): Learning rate
            
        Returns:
            str: Status message
        """
        try:
            print("🎯 Starting fine-tuning...")
            
            # Initialize fine-tuner
            if self.fine_tuner is None:
                self.fine_tuner = TextToImageFineTuner()
            
            # Prepare dataset
            train_dataloader, val_dataloader = self.fine_tuner.prepare_dataset()
            
            if len(train_dataloader.dataset) == 0:
                return "❌ No training data found. Please add some training examples first."
            
            # Start training
            self.fine_tuner.train(
                train_dataloader=train_dataloader,
                val_dataloader=val_dataloader,
                num_epochs=num_epochs,
                learning_rate=learning_rate
            )
            
            return f"✅ Fine-tuning completed! Trained for {num_epochs} epochs."
            
        except Exception as e:
            return f"❌ Error during fine-tuning: {str(e)}"
    
    def create_gradio_interface(self):
        """Create the Gradio web interface"""
        
        # Custom CSS for better styling
        css = """
        .gradio-container {
            font-family: 'Arial', sans-serif;
        }
        .title {
            text-align: center;
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 1em;
            color: #2563eb;
        }
        .section-title {
            font-size: 1.2em;
            font-weight: bold;
            margin: 1em 0 0.5em 0;
            color: #1f2937;
        }
        """
        
        with gr.Blocks(css=css, title="Text-to-Image Generator") as interface:
            
            # Title
            gr.HTML('<div class="title">🎨 Text-to-Image Generator</div>')
            gr.HTML('<p style="text-align: center; color: #6b7280;">Generate images from text using lightweight AI models</p>')
            
            with gr.Tabs():
                
                # Image Generation Tab
                with gr.Tab("🖼️ Generate Images"):
                    gr.HTML('<div class="section-title">Image Generation</div>')
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            prompt_input = gr.Textbox(
                                label="Text Prompt",
                                placeholder="Enter your text description (e.g., 'a cute dog playing in a park')",
                                lines=3
                            )
                            
                            negative_prompt_input = gr.Textbox(
                                label="Negative Prompt (Optional)",
                                placeholder="What to avoid in the image",
                                lines=2
                            )
                            
                            with gr.Row():
                                num_images_slider = gr.Slider(
                                    minimum=1, maximum=4, value=1, step=1,
                                    label="Number of Images"
                                )
                                
                                seed_input = gr.Number(
                                    label="Seed (Optional)",
                                    placeholder="Random seed for reproducible results"
                                )
                            
                            with gr.Row():
                                use_enhancement = gr.Checkbox(
                                    label="Enhance Prompt",
                                    value=True
                                )
                                
                                enhancement_style = gr.Dropdown(
                                    choices=["realistic", "artistic", "professional", "cinematic"],
                                    value="realistic",
                                    label="Enhancement Style"
                                )
                            
                            generate_btn = gr.Button("🎨 Generate Images", variant="primary")
                        
                        with gr.Column(scale=1):
                            output_gallery = gr.Gallery(
                                label="Generated Images",
                                show_label=True,
                                elem_id="gallery",
                                columns=2,
                                rows=2,
                                height="auto"
                            )
                            
                            status_output = gr.Textbox(
                                label="Status",
                                lines=3,
                                interactive=False
                            )
                
                # Fine-tuning Tab
                with gr.Tab("🔧 Fine-tuning"):
                    gr.HTML('<div class="section-title">Model Fine-tuning</div>')
                    gr.HTML('<p style="color: #6b7280;">Add custom training data and fine-tune the model</p>')
                    
                    with gr.Row():
                        with gr.Column():
                            gr.HTML('<h3>Add Training Data</h3>')
                            
                            training_prompt = gr.Textbox(
                                label="Training Prompt",
                                placeholder="Describe what the image shows",
                                lines=2
                            )
                            
                            training_image = gr.Image(
                                label="Training Image",
                                type="pil"
                            )
                            
                            add_data_btn = gr.Button("➕ Add Training Data", variant="secondary")
                            
                            add_status = gr.Textbox(
                                label="Status",
                                lines=2,
                                interactive=False
                            )
                        
                        with gr.Column():
                            gr.HTML('<h3>Start Fine-tuning</h3>')
                            
                            epochs_slider = gr.Slider(
                                minimum=1, maximum=10, value=2, step=1,
                                label="Training Epochs"
                            )
                            
                            lr_input = gr.Number(
                                label="Learning Rate",
                                value=1e-5,
                                format="%.1e"
                            )
                            
                            finetune_btn = gr.Button("🚀 Start Fine-tuning", variant="primary")
                            
                            finetune_status = gr.Textbox(
                                label="Fine-tuning Status",
                                lines=5,
                                interactive=False
                            )
                
                # Instructions Tab
                with gr.Tab("📖 Instructions"):
                    gr.HTML('''
                    <div class="section-title">How to Use</div>
                    
                    <h3>🖼️ Image Generation</h3>
                    <ol>
                        <li><strong>Enter a text prompt:</strong> Describe the image you want to generate (e.g., "a cute dog playing in a sunny park")</li>
                        <li><strong>Optional settings:</strong>
                            <ul>
                                <li><strong>Negative prompt:</strong> Describe what you don't want in the image</li>
                                <li><strong>Number of images:</strong> Generate multiple variations</li>
                                <li><strong>Seed:</strong> Use the same number for reproducible results</li>
                                <li><strong>Enhancement:</strong> Automatically improve your prompt for better results</li>
                            </ul>
                        </li>
                        <li><strong>Click "Generate Images"</strong> and wait for the results</li>
                    </ol>
                    
                    <h3>🔧 Fine-tuning</h3>
                    <ol>
                        <li><strong>Add training data:</strong> Upload images with text descriptions</li>
                        <li><strong>Collect multiple examples:</strong> The more diverse data, the better the results</li>
                        <li><strong>Start fine-tuning:</strong> Train the model on your custom data</li>
                        <li><strong>Wait for completion:</strong> Fine-tuning may take some time</li>
                    </ol>
                    
                    <h3>💡 Tips</h3>
                    <ul>
                        <li><strong>Be descriptive:</strong> More detailed prompts usually give better results</li>
                        <li><strong>Use keywords:</strong> Include style keywords like "photorealistic", "artistic", "detailed"</li>
                        <li><strong>Experiment:</strong> Try different enhancement styles and settings</li>
                        <li><strong>Fine-tune carefully:</strong> Start with a few high-quality training examples</li>
                    </ul>
                    
                    <h3>📁 File Locations</h3>
                    <ul>
                        <li><strong>Generated images:</strong> <code>outputs/generated/</code></li>
                        <li><strong>Training data:</strong> <code>data/train/</code></li>
                        <li><strong>Fine-tuned models:</strong> <code>outputs/models/</code></li>
                    </ul>
                    ''')
            
            # Connect the interface functions
            generate_btn.click(
                fn=self.generate_image,
                inputs=[prompt_input, negative_prompt_input, num_images_slider, 
                       seed_input, use_enhancement, enhancement_style],
                outputs=[output_gallery, status_output]
            )
            
            add_data_btn.click(
                fn=self.create_training_data,
                inputs=[training_prompt, training_image],
                outputs=[add_status]
            )
            
            finetune_btn.click(
                fn=self.start_fine_tuning,
                inputs=[epochs_slider, lr_input],
                outputs=[finetune_status]
            )
        
        return interface


def main():
    """Launch the web interface"""
    print("🌐 Starting Text-to-Image Web Interface...")
    
    # Create interface
    app = TextToImageInterface()
    interface = app.create_gradio_interface()
    
    # Launch the interface
    interface.launch(
        server_name="0.0.0.0",  # Allow access from other devices
        server_port=7860,
        share=False,  # Set to True to create a public link
        show_error=True
    )


if __name__ == "__main__":
    main()