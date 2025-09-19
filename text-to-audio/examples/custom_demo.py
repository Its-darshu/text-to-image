"""
Quick Custom Demo - Convert Your Own Text to Audio
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from main import TextToAudioConverter

def main():
    print("🎯 Custom Text-to-Audio Demo")
    print("=" * 35)
    
    # Initialize converter
    converter = TextToAudioConverter()
    
    # Custom texts to convert
    custom_texts = [
        "Hello! This is your custom text-to-audio system working perfectly!",
        "The project is now complete and ready for production use.",
        "You can convert any text into high-quality speech audio files.",
        "This system uses lightweight Hugging Face models for excellent results."
    ]
    
    print(f"🔄 Converting {len(custom_texts)} custom texts...")
    
    for i, text in enumerate(custom_texts, 1):
        print(f"\n📝 Converting text {i}: {text[:50]}...")
        
        output_path = converter.convert_text(text, f"custom_demo_{i}")
        
        if output_path:
            file_size = Path(output_path).stat().st_size / 1024  # KB
            print(f"✅ Success! Generated: {Path(output_path).name} ({file_size:.1f} KB)")
        else:
            print("❌ Failed to convert")
    
    print(f"\n🎉 Custom demo completed!")
    
    # Show all generated files
    output_dir = Path("output")
    if output_dir.exists():
        audio_files = list(output_dir.glob("custom_demo_*.wav"))
        print(f"\n📁 Generated {len(audio_files)} custom audio files:")
        for file_path in audio_files:
            size_kb = file_path.stat().st_size / 1024
            print(f"   🎵 {file_path.name} ({size_kb:.1f} KB)")
    
    converter.cleanup()

if __name__ == "__main__":
    main()