"""
IMPROVED Simple Q&A with Better Audio Generation

This script provides clear answers and reliable audio generation.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from main import TextToAudioConverter

# Improved Q&A knowledge base with shorter, clearer answers
QA_DATABASE = {
    "what is artificial intelligence": "AI is computer technology that makes machines smart like humans. It helps computers learn, understand speech, and solve problems automatically.",
    
    "what is ai": "AI means Artificial Intelligence. It makes computers think and learn so they can help people with many different tasks.",
    
    "how does text to speech work": "Text to speech reads written words and speaks them out loud using computer voices that sound like real people.",
    
    "what is machine learning": "Machine learning teaches computers to learn from examples. The computer looks at lots of data and figures out patterns by itself.",
    
    "what is python": "Python is a computer programming language that is easy to read and write. Many people use it to build websites and AI programs.",
    
    "how do neural networks work": "Neural networks work like the human brain with many connected parts that help computers recognize patterns and make decisions.",
    
    "what is deep learning": "Deep learning uses many layers of artificial brain cells to understand complex things like images, speech, and text.",
    
    "what are the benefits of ai": "AI helps people by doing boring tasks automatically, making better medical diagnoses, and solving complex problems quickly.",
    
    "how does speech recognition work": "Speech recognition listens to your voice and converts the sounds into written text using artificial intelligence.",
    
    "what is this system": "This is a smart system that answers your questions about technology and converts the answers into audio you can listen to.",
    
    "how do i use this": "Just ask any question about technology or AI. The system will give you an answer and create an audio file you can hear.",
    
    "what can you do": "I can answer questions about technology and AI, then convert my answers into clear spoken audio for you to listen to.",
    
    "how does machine learning work": "Machine learning works by showing computers many examples. The computer finds patterns and learns to make good predictions.",
    
    "what is programming": "Programming is writing step by step instructions that tell computers exactly what to do using special computer languages.",
    
    "what is data science": "Data science uses computers and math to find useful information hidden in large amounts of data and numbers.",
    
    "what is computer vision": "Computer vision teaches computers to see and understand images and videos just like human eyes and brain do.",
    
    "what is natural language processing": "Natural language processing helps computers understand and work with human language like the words we speak and write.",
    
    "how does this audio work": "This system converts text answers into speech audio files using artificial intelligence voice technology.",
    
    "is the audio working": "Yes, the audio is working. Each answer creates a high quality audio file that you can listen to right away.",
}

def normalize_question(question):
    """Normalize question for matching."""
    return question.lower().strip().rstrip('?').rstrip('.')

def find_answer(question):
    """Find answer for a question with better matching."""
    normalized_q = normalize_question(question)
    
    # Direct match
    if normalized_q in QA_DATABASE:
        return QA_DATABASE[normalized_q]
    
    # Better partial matching with key words
    question_words = normalized_q.split()
    best_match = None
    max_matches = 0
    
    for db_question, answer in QA_DATABASE.items():
        db_words = db_question.split()
        matches = sum(1 for word in question_words if word in db_words and len(word) > 2)
        
        if matches > max_matches and matches > 0:
            max_matches = matches
            best_match = answer
    
    return best_match

def test_audio_generation():
    """Test that audio generation is working properly."""
    print("🎵 Testing Audio Generation...")
    converter = TextToAudioConverter()
    
    test_text = "This is a test to verify that audio generation is working correctly."
    audio_path = converter.convert_text(test_text, "audio_test")
    
    if audio_path and Path(audio_path).exists():
        file_size = Path(audio_path).stat().st_size / 1024
        print(f"✅ Audio test successful: {Path(audio_path).name} ({file_size:.1f} KB)")
        
        # Try to play the test audio
        play_success = converter.play_audio_file(audio_path)
        if play_success:
            print("🎧 Audio playback test successful!")
        else:
            print("💾 Audio file created successfully (playback may need manual action)")
        
        converter.cleanup()
        return True
    else:
        print("❌ Audio generation test failed")
        converter.cleanup()
        return False

def answer_question(question):
    """Answer a question and convert to audio with better error handling."""
    print(f"❓ Question: {question}")
    
    answer = find_answer(question)
    
    if answer:
        print(f"💬 Answer: {answer}")
        print()
        
        # Convert to audio with error handling
        print("🔄 Converting answer to audio...")
        converter = TextToAudioConverter()
        
        try:
            audio_path = converter.convert_text(answer, "qa_answer")
            
            if audio_path and Path(audio_path).exists():
                file_size = Path(audio_path).stat().st_size / 1024
                print(f"✅ Audio answer generated: {Path(audio_path).name} ({file_size:.1f} KB)")
                
                # Try to play audio
                print("🎧 Playing audio answer...")
                play_success = converter.play_audio_file(audio_path)
                
                if play_success:
                    print("🎵 Audio played successfully!")
                else:
                    print("💾 Audio saved successfully! You can play it manually.")
                    print(f"📁 Location: {audio_path}")
                
                print(f"📊 Audio file size: {file_size:.1f} KB")
                print(f"📂 Saved in: {Path(audio_path).parent}")
            else:
                print("❌ Failed to generate audio file.")
        
        except Exception as e:
            print(f"❌ Error generating audio: {e}")
        
        finally:
            converter.cleanup()
        
        return True
    else:
        print("❌ Sorry, I don't know the answer to that question.")
        print("\n💡 Try asking about:")
        print("   • What is AI?")
        print("   • How does machine learning work?")
        print("   • What is Python programming?")
        print("   • How does text to speech work?")
        print("   • What can you do?")
        return False

def interactive_mode():
    """Run in interactive question mode with audio testing."""
    print("🎓 Interactive Q&A Mode with Audio")
    print("=" * 35)
    
    # First test audio generation
    if not test_audio_generation():
        print("⚠️ Audio generation test failed, but you can still get text answers.")
    
    print("\nAsk me questions about AI, programming, and technology!")
    print("Type 'help' to see example questions")
    print("Type 'test' to test audio generation")
    print("Type 'quit' to exit\n")
    
    while True:
        try:
            question = input("❓ Your question: ").strip()
            
            if not question:
                print("⚠️ Please enter a question!")
                continue
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Thank you for using the Q&A system!")
                break
            
            if question.lower() == 'test':
                test_audio_generation()
                continue
            
            if question.lower() == 'help':
                print("\n💡 Example questions you can ask:")
                print("   • What is artificial intelligence?")
                print("   • How does machine learning work?")
                print("   • What is Python programming?")
                print("   • How does text to speech work?")
                print("   • What can this system do?")
                print("   • Is the audio working?")
                print()
                continue
            
            print("\n" + "─" * 50)
            success = answer_question(question)
            print("─" * 50)
            
            if success:
                continue_choice = input("\nAsk another question? (y/n): ").strip().lower()
                if continue_choice != 'y':
                    print("👋 Thank you for using the Q&A system!")
                    break
            
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

def main():
    """Main function with audio verification."""
    print("🎓 Improved Q&A Text-to-Audio System")
    print("=" * 42)
    
    if len(sys.argv) > 1:
        # Command line mode
        question = " ".join(sys.argv[1:])
        answer_question(question)
    else:
        # Interactive mode with audio testing
        interactive_mode()

if __name__ == "__main__":
    main()