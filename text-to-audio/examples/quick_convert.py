"""
Quick Text-to-Audio Converter

Usage: python quick_convert.py "Your text here"
Or run without arguments for interactive mode
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from main import TextToAudioConverter

def convert_text(text, filename=None):
    """Convert text to audio and return the file path."""
    print(f"🔄 Converting: '{text[:50]}{'...' if len(text) > 50 else ''}'")
    
    # Initialize converter
    converter = TextToAudioConverter()
    
    # Convert text
    if not filename:
        filename = "quick_convert"
    
    audio_path = converter.convert_text(text, filename)
    
    if audio_path:
        file_size = Path(audio_path).stat().st_size / 1024
        print(f"✅ Success! Audio saved to: {audio_path}")
        print(f"📊 File size: {file_size:.1f} KB")
        
        # Try to play the audio
        print("🎧 Attempting to play audio...")
        play_success = converter.play_audio_file(audio_path)
        
        if play_success:
            print("🎵 Audio played successfully!")
        else:
            print("💾 Audio file saved. You can play it with any audio player.")
    else:
        print("❌ Conversion failed.")
        audio_path = None
    
    converter.cleanup()
    return audio_path

def interactive_mode():
    """Run in interactive mode."""
    print("🎵 Interactive Text-to-Audio Converter")
    print("=" * 40)
    print("Enter text and press Enter to convert to audio.")
    print("Type 'quit' or 'exit' to stop.\n")
    
    count = 1
    
    while True:
        try:
            text = input(f"📝 Text #{count}: ").strip()
            
            if text.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not text:
                print("⚠️ Please enter some text!")
                continue
            
            # Convert the text
            audio_path = convert_text(text, f"interactive_{count}")
            
            if audio_path:
                print(f"🎉 Conversion #{count} completed!\n")
                count += 1
            else:
                print("❌ Try again with different text.\n")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function."""
    if len(sys.argv) > 1:
        # Command line mode
        text = " ".join(sys.argv[1:])
        print("🎵 Quick Text-to-Audio Converter")
        print("=" * 35)
        convert_text(text)
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()