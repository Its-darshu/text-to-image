"""
Q&A System Demonstration

This script demonstrates the Q&A system working with various questions
and generating audio answers.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from main import TextToAudioConverter

def demo_qa_system():
    """Demonstrate the Q&A system with multiple questions."""
    print("🎓 Q&A System Demonstration")
    print("=" * 40)
    print("This demo shows questions and audio answer generation!\n")
    
    # Initialize converter
    converter = TextToAudioConverter()
    
    # Demo questions with shorter answers for better audio generation
    demo_questions = [
        {
            "question": "What is AI?",
            "answer": "AI is Artificial Intelligence. It enables machines to simulate human intelligence and solve complex problems."
        },
        {
            "question": "What is Python?", 
            "answer": "Python is a programming language known for its simple syntax. It's used in web development, data science, and AI."
        },
        {
            "question": "How does this work?",
            "answer": "This system takes your questions, finds relevant answers, and converts them into speech audio files you can listen to."
        },
        {
            "question": "What can you do?",
            "answer": "I can answer questions about technology topics and convert my responses into high-quality audio files."
        }
    ]
    
    print(f"🔄 Processing {len(demo_questions)} Q&A demonstrations...\n")
    
    generated_files = []
    
    for i, qa in enumerate(demo_questions, 1):
        question = qa["question"]
        answer = qa["answer"]
        
        print(f"📝 Demo {i}/{len(demo_questions)}")
        print(f"❓ Question: {question}")
        print(f"💬 Answer: {answer}")
        
        # Convert answer to audio
        filename = f"qa_demo_{i}"
        audio_path = converter.convert_text(answer, filename)
        
        if audio_path:
            file_size = Path(audio_path).stat().st_size / 1024
            generated_files.append(audio_path)
            
            print(f"✅ Audio generated: {Path(audio_path).name} ({file_size:.1f} KB)")
            
            # Try to play audio
            print("🎧 Playing audio...")
            play_success = converter.play_audio_file(audio_path)
            
            if play_success:
                print("🎵 Audio played successfully!")
            else:
                print("💾 Audio saved successfully!")
            
        else:
            print("❌ Audio generation failed")
        
        print("─" * 50)
    
    # Summary
    print(f"\n🎉 Q&A Demo Completed!")
    print(f"✅ Successfully generated {len(generated_files)} audio answers")
    print(f"📁 Audio files saved in: output/")
    
    print("\n📋 Generated Files:")
    for i, file_path in enumerate(generated_files, 1):
        size = Path(file_path).stat().st_size / 1024
        print(f"   {i}. {Path(file_path).name} ({size:.1f} KB)")
    
    print(f"\n🎯 Total audio generated: {len(generated_files)} question-answer pairs")
    print("💡 You can ask similar questions and get audio answers!")
    
    converter.cleanup()
    return generated_files

def main():
    """Run the Q&A demonstration."""
    try:
        generated_files = demo_qa_system()
        
        print(f"\n✨ Demonstration completed successfully!")
        print(f"🎵 {len(generated_files)} audio files ready for playback")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")

if __name__ == "__main__":
    main()