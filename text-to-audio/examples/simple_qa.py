"""
Simple Q&A Command Line Tool

Usage: 
- python simple_qa.py "your question here"
- python simple_qa.py (for interactive mode)

This tool answers questions and converts the answers to audio.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from main import TextToAudioConverter

# Built-in Q&A knowledge base
QA_DATABASE = {
    "what is artificial intelligence": "Artificial Intelligence, or AI, is the simulation of human intelligence in machines. It includes machine learning, natural language processing, and computer vision to enable computers to perform tasks that typically require human intelligence.",
    
    "what is ai": "AI stands for Artificial Intelligence. It's technology that enables machines to simulate human intelligence, including learning, reasoning, and problem-solving capabilities.",
    
    "how does text to speech work": "Text-to-speech works by converting written text into spoken words using neural networks. The system analyzes text, understands pronunciation patterns, and generates natural-sounding speech audio using advanced AI models.",
    
    "what is machine learning": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from data without being explicitly programmed. It uses algorithms to identify patterns and make predictions or decisions.",
    
    "what is python": "Python is a high-level, interpreted programming language known for its simple, readable syntax. It's widely used in web development, data science, artificial intelligence, automation, and many other applications.",
    
    "how do neural networks work": "Neural networks are computing systems inspired by biological brains. They consist of interconnected nodes that process information using weighted connections, learning patterns from data to make predictions or classifications.",
    
    "what is deep learning": "Deep learning is a subset of machine learning that uses artificial neural networks with multiple layers. It's particularly effective for complex tasks like image recognition, natural language processing, and speech synthesis.",
    
    "what are the benefits of ai": "AI benefits include task automation, improved decision-making, enhanced productivity, better healthcare diagnostics, personalized experiences, advanced data analysis, and solutions to complex global challenges.",
    
    "how does speech recognition work": "Speech recognition converts spoken language into text using acoustic models and language processing. It analyzes audio waves, identifies speech patterns, and matches sounds to words using machine learning algorithms.",
    
    "what is this system": "This is a text-to-audio system that can answer questions and convert the answers into high-quality speech audio. You can ask questions about AI, technology, and programming, and get both text and audio responses.",
    
    "how do i use this": "You can use this system by asking questions either through the command line or interactive mode. The system will find relevant answers and convert them to audio files that you can listen to.",
    
    "what can you do": "I can answer questions about artificial intelligence, machine learning, programming, and technology topics. I convert my answers into high-quality audio files that you can listen to immediately.",
}

def normalize_question(question):
    """Normalize question for matching."""
    return question.lower().strip().rstrip('?').rstrip('.')

def find_answer(question):
    """Find answer for a question."""
    normalized_q = normalize_question(question)
    
    # Direct match
    if normalized_q in QA_DATABASE:
        return QA_DATABASE[normalized_q]
    
    # Partial matching
    for db_question, answer in QA_DATABASE.items():
        if normalized_q in db_question or any(word in db_question for word in normalized_q.split() if len(word) > 3):
            return answer
    
    # No match found
    return None

def answer_question(question):
    """Answer a question and convert to audio."""
    print(f"❓ Question: {question}")
    
    answer = find_answer(question)
    
    if answer:
        print(f"💬 Answer: {answer}")
        print()
        
        # Convert to audio
        print("🔄 Converting answer to audio...")
        converter = TextToAudioConverter()
        
        audio_path = converter.convert_text(answer, "qa_answer")
        
        if audio_path:
            file_size = Path(audio_path).stat().st_size / 1024
            print(f"✅ Audio answer generated: {Path(audio_path).name} ({file_size:.1f} KB)")
            
            # Try to play audio
            print("🎧 Playing audio answer...")
            play_success = converter.play_audio_file(audio_path)
            
            if play_success:
                print("🎵 Audio played successfully!")
            else:
                print("💾 Audio saved. You can play it manually.")
                print(f"📁 Location: {audio_path}")
        else:
            print("❌ Failed to generate audio.")
        
        converter.cleanup()
        return True
    else:
        print("❌ Sorry, I don't know the answer to that question.")
        print("\n💡 Try asking about:")
        print("   • Artificial Intelligence")
        print("   • Machine Learning") 
        print("   • Python Programming")
        print("   • Text-to-Speech")
        print("   • Neural Networks")
        print("   • Deep Learning")
        return False

def interactive_mode():
    """Run in interactive question mode."""
    print("🎓 Interactive Q&A Mode")
    print("=" * 25)
    print("Ask me questions about AI, programming, and technology!")
    print("Type 'help' to see example questions")
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
            
            if question.lower() == 'help':
                print("\n💡 Example questions you can ask:")
                print("   • What is artificial intelligence?")
                print("   • How does machine learning work?")
                print("   • What is Python programming?")
                print("   • How does text to speech work?")
                print("   • What are neural networks?")
                print("   • What can this system do?")
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
    """Main function."""
    print("🎓 Simple Q&A Text-to-Audio System")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        # Command line mode
        question = " ".join(sys.argv[1:])
        answer_question(question)
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()