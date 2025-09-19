"""
Main entry point for the Text-to-Image Generation Project
This script provides a command-line interface for all functionality.
"""

import argparse
import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from generator import TextToImageGenerator
from dataset import DatasetCreator
from fine_tuner import TextToImageFineTuner
from app import TextToImageInterface

def generate_images(args):
    """Generate images from command line"""
    print("🎨 Generating images...")
    
    # Create generator
    generator = TextToImageGenerator(model_name=args.model)
    
    # Generate images
    images, paths = generator.generate_and_save(
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        num_images=args.num_images,
        seed=args.seed
    )
    
    print(f"✅ Generated {len(images)} image(s)")
    for path in paths:
        print(f"💾 Saved: {path}")

def create_dataset(args):
    """Create sample dataset"""
    print("📁 Creating dataset...")
    
    creator = DatasetCreator()
    train_csv, val_csv = creator.create_sample_dataset()
    
    print(f"✅ Dataset created!")
    print(f"📂 Training data: {train_csv}")
    print(f"📂 Validation data: {val_csv}")

def fine_tune_model(args):
    """Fine-tune model"""
    print("🎯 Starting fine-tuning...")
    
    # Initialize fine-tuner
    fine_tuner = TextToImageFineTuner(model_name=args.model)
    
    # Prepare dataset
    train_dataloader, val_dataloader = fine_tuner.prepare_dataset()
    
    # Start training
    fine_tuner.train(
        train_dataloader=train_dataloader,
        val_dataloader=val_dataloader,
        num_epochs=args.epochs,
        learning_rate=args.learning_rate
    )
    
    print("✅ Fine-tuning completed!")

def launch_interface(args):
    """Launch web interface"""
    print("🌐 Launching web interface...")
    
    app = TextToImageInterface()
    interface = app.create_gradio_interface()
    
    interface.launch(
        server_name="0.0.0.0",
        server_port=args.port,
        share=args.share,
        show_error=True
    )

def setup_project(args):
    """Setup the project"""
    print("🚀 Setting up project...")
    
    # Import and run setup
    import subprocess
    subprocess.run([sys.executable, "setup.py"], check=True)
    
    print("✅ Project setup completed!")

def main():
    """Main command-line interface"""
    parser = argparse.ArgumentParser(
        description="Text-to-Image Generation Project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py setup                           # Setup the project
  python main.py generate "a cute dog"           # Generate an image
  python main.py interface                       # Launch web interface
  python main.py dataset                         # Create sample dataset
  python main.py finetune --epochs 5             # Fine-tune model
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup the project')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate images')
    generate_parser.add_argument('prompt', help='Text prompt for image generation')
    generate_parser.add_argument('--negative-prompt', default='', help='Negative prompt')
    generate_parser.add_argument('--num-images', type=int, default=1, help='Number of images to generate')
    generate_parser.add_argument('--seed', type=int, help='Random seed')
    generate_parser.add_argument('--model', default='flux_schnell', help='Model to use')
    
    # Dataset command
    dataset_parser = subparsers.add_parser('dataset', help='Create sample dataset')
    
    # Fine-tune command
    finetune_parser = subparsers.add_parser('finetune', help='Fine-tune model')
    finetune_parser.add_argument('--model', default='small_stable_diffusion', help='Model to fine-tune')
    finetune_parser.add_argument('--epochs', type=int, default=2, help='Number of training epochs')
    finetune_parser.add_argument('--learning-rate', type=float, default=1e-5, help='Learning rate')
    
    # Interface command
    interface_parser = subparsers.add_parser('interface', help='Launch web interface')
    interface_parser.add_argument('--port', type=int, default=7860, help='Port for web interface')
    interface_parser.add_argument('--share', action='store_true', help='Create public link')
    
    args = parser.parse_args()
    
    if args.command == 'setup':
        setup_project(args)
    elif args.command == 'generate':
        generate_images(args)
    elif args.command == 'dataset':
        create_dataset(args)
    elif args.command == 'finetune':
        fine_tune_model(args)
    elif args.command == 'interface':
        launch_interface(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()