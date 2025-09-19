"""
Dataset Example: Working with Training Data

This script demonstrates how to work with TTS datasets for training and evaluation.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from dataset_manager import DatasetManager


def main():
    print("📊 Dataset Management Example")
    print("=" * 35)
    
    # Initialize dataset manager
    manager = DatasetManager()
    
    # List available datasets
    print("Available datasets:")
    datasets_info = manager.list_available_datasets()
    for name, info in datasets_info.items():
        print(f"  📁 {name}: {info['name']}")
        print(f"     Type: {info['type']}, Size: {info['size']}")
        print(f"     Language: {info['language']}, Sample Rate: {info['sample_rate']} Hz")
        print()
    
    # Load a small sample of LJSpeech for demonstration
    print("Loading LJSpeech dataset (limited to 10 samples for demo)...")
    
    try:
        dataset = manager.load_ljspeech(max_samples=10)
        
        if dataset:
            print(f"✅ Successfully loaded {len(dataset)} samples")
            
            # Get dataset statistics
            stats = manager.get_dataset_stats('ljspeech')
            if stats:
                print("\n📊 Dataset Statistics:")
                print(f"  Total samples: {stats['total_samples']}")
                
                if 'text_stats' in stats:
                    text_stats = stats['text_stats']
                    print(f"  Text statistics:")
                    print(f"    Average words: {text_stats['avg_words']:.1f}")
                    print(f"    Word range: {text_stats['min_words']}-{text_stats['max_words']}")
                    print(f"    Character range: {text_stats['min_chars']}-{text_stats['max_chars']}")
                
                if 'audio_stats' in stats:
                    audio_stats = stats['audio_stats']
                    print(f"  Audio statistics:")
                    print(f"    Average duration: {audio_stats['avg_duration']:.2f}s")
                    print(f"    Duration range: {audio_stats['min_duration']:.2f}s - {audio_stats['max_duration']:.2f}s")
                    print(f"    Sample rates: {audio_stats['sample_rates']}")
            
            # Show sample data
            print("\n📋 Sample Data:")
            for i in range(min(3, len(dataset))):
                sample = dataset[i]
                print(f"\nSample {i+1}:")
                print(f"  Text: {sample['text'][:80]}...")
                if 'audio' in sample:
                    audio_info = sample['audio']
                    duration = len(audio_info['array']) / audio_info['sampling_rate']
                    print(f"  Audio: {duration:.2f}s at {audio_info['sampling_rate']} Hz")
            
            # Create train/validation/test splits
            print("\n🔄 Creating dataset splits...")
            dataset_splits = manager.prepare_training_split(
                'ljspeech',
                train_ratio=0.7,
                val_ratio=0.2,
                test_ratio=0.1
            )
            
            if dataset_splits:
                print("✅ Dataset splits created:")
                for split_name, split_data in dataset_splits.items():
                    print(f"  {split_name}: {len(split_data)} samples")
            
            # Example: Save dataset (commented out to avoid large files)
            # print("\n💾 Saving dataset...")
            # success = manager.save_dataset('ljspeech', 'saved_datasets/ljspeech_sample')
            # if success:
            #     print("✅ Dataset saved successfully")
            
        else:
            print("❌ Failed to load dataset")
    
    except Exception as e:
        print(f"⚠️ Dataset operation encountered an issue: {e}")
        print("This is normal for demo purposes - full datasets are very large!")
        print("In a real scenario, you would have proper internet connection and storage.")
    
    # Example: Create custom dataset structure
    print("\n🛠️ Custom Dataset Example:")
    print("To create a custom dataset, you would need:")
    print("  1. A directory with audio files (WAV, MP3, etc.)")
    print("  2. A metadata file (CSV or JSON) mapping filenames to text")
    print("  3. Example CSV format:")
    print("     filename1|This is the text for audio file 1")
    print("     filename2|This is the text for audio file 2")
    
    print("\n✨ Dataset management example completed!")


if __name__ == "__main__":
    main()