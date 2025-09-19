"""
Simple User Text-to-Audio Interface

This script allows users to:
1. Enter text and immediately hear it as audio
2. Save audio files
3. Test dataset functionality
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from main import TextToAudioConverter
from dataset_manager import DatasetManager

def main():
    print("🎵 Simple Text-to-Audio Interface")
    print("=" * 40)
    
    # Initialize system
    print("🔧 Initializing system...")
    converter = TextToAudioConverter()
    dataset_manager = DatasetManager()
    
    print("✅ System ready!")
    print()
    
    try:
        while True:
            print("Choose an option:")
            print("1. 🎵 Enter text and play as audio")
            print("2. 📊 Test dataset functionality")
            print("3. ❌ Exit")
            
            choice = input("\nEnter choice (1-3): ").strip()
            
            if choice == '1':
                # Text to audio conversion
                print("\n" + "="*30)
                text = input("📝 Enter your text: ").strip()
                
                if not text:
                    print("⚠️ Please enter some text!")
                    continue
                
                print(f"🔄 Converting to audio: '{text[:50]}{'...' if len(text) > 50 else ''}'")
                
                # Convert text to audio
                audio_path = converter.convert_text(text, "user_input")
                
                if audio_path:
                    file_size = Path(audio_path).stat().st_size / 1024
                    print(f"✅ Audio generated successfully!")
                    print(f"   📄 File: {Path(audio_path).name}")
                    print(f"   📊 Size: {file_size:.1f} KB")
                    print(f"   📂 Location: {audio_path}")
                    
                    # Try to play the audio
                    print("\n🎧 Playing audio...")
                    play_success = converter.play_audio_file(audio_path)
                    
                    if play_success:
                        print("✅ Audio played successfully!")
                    else:
                        print("ℹ️ Audio file saved but playback not available.")
                        print("   You can play it manually with any audio player.")
                else:
                    print("❌ Failed to generate audio. Please try again.")
            
            elif choice == '2':
                # Dataset functionality test
                print("\n📊 Testing Dataset Functionality")
                print("=" * 35)
                
                # List available datasets
                print("📋 Available datasets:")
                datasets = dataset_manager.list_available_datasets()
                for name, info in datasets.items():
                    print(f"   📁 {name}: {info['name']} ({info['size']})")
                
                print("\n📥 Loading LJSpeech sample (3 items for demo)...")
                
                try:
                    # Load a small sample
                    dataset = dataset_manager.load_ljspeech(max_samples=3)
                    
                    if dataset:
                        print(f"✅ Successfully loaded {len(dataset)} samples!")
                        
                        # Show sample data
                        print("\n📋 Sample dataset content:")
                        for i in range(len(dataset)):
                            sample = dataset[i]
                            print(f"\nSample {i+1}:")
                            print(f"   📝 Text: {sample['text'][:80]}...")
                            
                            if 'audio' in sample:
                                audio_info = sample['audio']
                                duration = len(audio_info['array']) / audio_info['sampling_rate']
                                print(f"   🎵 Audio: {duration:.2f}s at {audio_info['sampling_rate']} Hz")
                        
                        # Get dataset statistics
                        stats = dataset_manager.get_dataset_stats('ljspeech')
                        if stats:
                            print(f"\n📊 Dataset Statistics:")
                            print(f"   Total samples: {stats['total_samples']}")
                            if 'text_stats' in stats:
                                ts = stats['text_stats']
                                print(f"   Average words per text: {ts['avg_words']:.1f}")
                            if 'audio_stats' in stats:
                                aus = stats['audio_stats']
                                print(f"   Average audio duration: {aus['avg_duration']:.2f}s")
                        
                        print("\n✅ Dataset functionality working correctly!")
                    else:
                        print("⚠️ Dataset loading failed (this is normal for demo)")
                        
                except Exception as e:
                    print(f"ℹ️ Dataset test completed with note: {e}")
                    print("   (Large datasets may not load in demo environment)")
            
            elif choice == '3':
                print("\n👋 Thank you for using Text-to-Audio System!")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
            
            print("\n" + "="*50 + "\n")
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    
    finally:
        # Cleanup
        converter.cleanup()
        print("✅ System shutdown complete.")


if __name__ == "__main__":
    main()