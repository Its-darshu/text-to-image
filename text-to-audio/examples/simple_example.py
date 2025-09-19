"""
Simple Example: Basic Text-to-Speech Conversion

This script demonstrates the most basic usage of the text-to-audio system.
Perfect for getting started quickly.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from main import TextToAudioConverter


def main():
    print("🎵 Simple Text-to-Speech Example")
    print("=" * 40)
    
    # Initialize the converter
    print("Initializing text-to-audio converter...")
    converter = TextToAudioConverter()
    
    # Simple text conversion
    text = "Hello world! This is a simple text-to-speech demonstration."
    
    print(f"\n📝 Converting text: '{text}'")
    
    # Convert text to audio
    output_path = converter.convert_text(text, "simple_example")
    
    if output_path:
        print(f"✅ Success! Audio saved to: {output_path}")
        
        # Try to play the audio
        print("\n🔊 Attempting to play audio...")
        played = converter.play_audio_file(output_path)
        
        if played:
            print("🎵 Audio playback started!")
        else:
            print("⚠️ Audio playback not available, but file was saved successfully.")
            
    else:
        print("❌ Failed to convert text to audio")
    
    # Cleanup
    converter.cleanup()
    print("\n✨ Example completed!")


if __name__ == "__main__":
    main()