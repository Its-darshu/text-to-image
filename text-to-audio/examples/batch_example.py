"""
Batch Processing Example: Convert Multiple Texts

This script demonstrates batch processing capabilities for converting
multiple texts to audio files efficiently.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from main import TextToAudioConverter


def main():
    print("📦 Batch Processing Example")
    print("=" * 35)
    
    # Initialize the converter
    print("Initializing text-to-audio converter...")
    converter = TextToAudioConverter()
    
    # Configure for batch processing
    converter.update_config(
        audio_format="wav",
        normalize_audio=True,
        apply_fade=True
    )
    
    # Sample texts for batch processing
    texts = [
        "Welcome to our daily news briefing for today.",
        
        "In technology news, artificial intelligence continues to advance rapidly. New breakthroughs in natural language processing are making AI more accessible to everyday users.",
        
        "Weather update: Today will be partly cloudy with temperatures reaching 75 degrees Fahrenheit. There's a slight chance of rain in the evening.",
        
        "Sports recap: The local team won their game yesterday with a final score of 3 to 1. The next match is scheduled for this weekend.",
        
        "Reminder: Don't forget to attend the community meeting tomorrow at 7 PM in the town hall. We'll be discussing the upcoming festivals and events.",
        
        "Thank you for listening to today's briefing. Have a wonderful day and we'll see you again tomorrow with more updates."
    ]
    
    print(f"\n📝 Processing {len(texts)} texts in batch...")
    
    # Process all texts
    output_paths = converter.convert_batch(texts, "news_briefing")
    
    print(f"\n✅ Batch processing completed!")
    print(f"Generated {len(output_paths)} audio files:")
    
    for i, path in enumerate(output_paths, 1):
        if path:
            file_size = Path(path).stat().st_size / 1024  # KB
            print(f"  {i}. {Path(path).name} ({file_size:.1f} KB)")
        else:
            print(f"  {i}. [FAILED]")
    
    # Calculate some statistics
    successful_conversions = len([p for p in output_paths if p])
    success_rate = (successful_conversions / len(texts)) * 100
    
    print(f"\n📊 Batch Statistics:")
    print(f"  Total texts: {len(texts)}")
    print(f"  Successful conversions: {successful_conversions}")
    print(f"  Success rate: {success_rate:.1f}%")
    
    # Estimate total audio duration
    total_words = sum(len(text.split()) for text in texts)
    estimated_duration = (total_words / 150) * 60  # ~150 words per minute
    print(f"  Estimated total duration: {estimated_duration:.1f} seconds")
    
    # Show individual text statistics
    print(f"\n📋 Individual Text Statistics:")
    for i, text in enumerate(texts, 1):
        word_count = len(text.split())
        char_count = len(text)
        estimated_time = (word_count / 150) * 60
        print(f"  Text {i}: {word_count} words, {char_count} chars, ~{estimated_time:.1f}s")
    
    # Cleanup
    converter.cleanup()
    print("\n✨ Batch processing example completed!")


if __name__ == "__main__":
    main()