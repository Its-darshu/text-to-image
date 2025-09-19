"""
Advanced Example: Question-Answer Audio Generation

This script demonstrates how to convert question-answer pairs into audio files,
perfect for creating educational content, FAQ audio, or interactive voice responses.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from main import TextToAudioConverter


def main():
    print("🎓 Question-Answer Audio Generation Example")
    print("=" * 50)
    
    # Initialize the converter
    print("Initializing text-to-audio converter...")
    converter = TextToAudioConverter()
    
    # Configure for better Q&A audio
    converter.update_config(
        audio_format="wav",
        apply_fade=True,
        noise_reduction=False,
        segment_gap_ms=750  # Longer pause between Q&A
    )
    
    # Sample Q&A pairs
    qa_pairs = [
        {
            "question": "What is artificial intelligence?",
            "answer": "Artificial intelligence, or AI, is the simulation of human intelligence in machines that are programmed to think and learn like humans. It includes machine learning, natural language processing, and computer vision."
        },
        {
            "question": "How does machine learning work?",
            "answer": "Machine learning works by training algorithms on large datasets to recognize patterns and make predictions. The system learns from examples without being explicitly programmed for every scenario."
        },
        {
            "question": "What are the benefits of text-to-speech technology?",
            "answer": "Text-to-speech technology helps with accessibility for visually impaired users, enables hands-free content consumption, supports language learning, and can create audio content from written materials automatically."
        },
        {
            "question": "How can I improve my Python programming skills?",
            "answer": "To improve Python skills, practice coding daily, work on real projects, read other people's code, contribute to open source projects, and learn from online resources like tutorials and documentation."
        }
    ]
    
    print(f"\n📚 Converting {len(qa_pairs)} question-answer pairs...")
    
    # Convert Q&A pairs to audio
    output_paths = converter.convert_questions_and_answers(
        qa_pairs, 
        include_questions=True
    )
    
    print(f"\n✅ Generated {len(output_paths)} audio files:")
    for i, path in enumerate(output_paths, 1):
        print(f"  {i}. {path}")
    
    # Also create answer-only versions
    print("\n🔄 Creating answer-only versions...")
    answer_only_paths = converter.convert_questions_and_answers(
        qa_pairs,
        include_questions=False
    )
    
    print(f"\n✅ Generated {len(answer_only_paths)} answer-only files:")
    for i, path in enumerate(answer_only_paths, 1):
        print(f"  {i}. {path}")
    
    # Get system information
    print("\n📊 System Information:")
    info = converter.get_system_info()
    print(f"  Model: {info['model_name']}")
    print(f"  Device: {info['device']}")
    print(f"  Output format: {info['config']['audio_format']}")
    
    # Cleanup
    converter.cleanup()
    print("\n✨ Q&A example completed!")


if __name__ == "__main__":
    main()