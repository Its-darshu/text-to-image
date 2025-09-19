"""
Quick test script to verify audio generation is working
"""

import os
import sys
from datetime import datetime

# Add src directories to path
sys.path.append('src')
sys.path.append('text-to-audio/src')

def test_audio_generation():
    """Test the audio generation function"""
    try:
        import pyttsx3
        
        print("🎵 Testing audio generation...")
        
        engine = pyttsx3.init()
        
        # Create output directory
        os.makedirs("outputs/test_audio", exist_ok=True)
        
        # Test text
        test_text = "Hello! This is a test of the audio generation system. The system is working correctly."
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_filename = f"test_audio_{timestamp}.wav"
        audio_path = os.path.abspath(os.path.join("outputs/test_audio", audio_filename))
        
        print(f"📁 Saving to: {audio_path}")
        
        # Configure engine
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        
        # Generate audio
        engine.save_to_file(test_text, audio_path)
        engine.runAndWait()
        
        # Check result
        if os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path)
            print(f"✅ Audio generated successfully!")
            print(f"📂 File: {audio_filename}")
            print(f"📐 Size: {file_size} bytes ({file_size/1024:.1f} KB)")
            print(f"📍 Full path: {audio_path}")
            return True
        else:
            print("❌ Audio file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🎵 AUDIO GENERATION TEST")
    print("=" * 50)
    
    success = test_audio_generation()
    
    if success:
        print("\n🎉 Audio generation is working correctly!")
        print("🌐 The web interface should now be able to generate audio.")
    else:
        print("\n❌ Audio generation failed!")
        print("🔧 Please check the error messages above.")
    
    print("=" * 50)