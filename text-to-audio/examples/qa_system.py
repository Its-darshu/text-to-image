"""
Interactive Q&A Text-to-Audio System

This system allows users to:
1. Ask questions and get audio answers
2. Build a knowledge base of Q&A pairs
3. Convert Q&A pairs to audio files
4. Play audio answers immediately
"""

import sys
from pathlib import Path
import json
import time

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from main import TextToAudioConverter

class QATextToAudio:
    """Interactive Q&A system with text-to-audio conversion."""
    
    def __init__(self):
        """Initialize the Q&A system."""
        print("🎓 Initializing Q&A Text-to-Audio System...")
        self.converter = TextToAudioConverter()
        self.qa_database = self.load_qa_database()
        print("✅ System ready!\n")
    
    def load_qa_database(self):
        """Load or create Q&A database."""
        db_file = Path("qa_database.json")
        
        if db_file.exists():
            try:
                with open(db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # Default Q&A database
        return {
            "what is artificial intelligence": "Artificial Intelligence, or AI, is the simulation of human intelligence in machines. It includes machine learning, natural language processing, and computer vision to enable computers to perform tasks that typically require human intelligence.",
            
            "how does text to speech work": "Text-to-speech works by converting written text into spoken words. It uses neural networks to analyze text, understand pronunciation, and generate natural-sounding speech audio using advanced deep learning models.",
            
            "what is machine learning": "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed. It uses algorithms to identify patterns and make predictions.",
            
            "what is python programming": "Python is a high-level, interpreted programming language known for its simple syntax and versatility. It's widely used in web development, data science, artificial intelligence, and automation.",
            
            "how do neural networks work": "Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes that process information, learn patterns from data, and make predictions through weighted connections and activation functions.",
            
            "what are the benefits of ai": "AI benefits include automation of repetitive tasks, improved decision-making through data analysis, enhanced productivity, better healthcare diagnostics, personalized user experiences, and solutions to complex problems.",
            
            "what is deep learning": "Deep learning is a subset of machine learning that uses artificial neural networks with multiple layers to model and understand complex patterns in data. It's particularly effective for tasks like image recognition and natural language processing.",
            
            "how does speech recognition work": "Speech recognition converts spoken language into text using acoustic models, language models, and signal processing. It analyzes audio waves, identifies phonemes, and matches them to words using machine learning algorithms.",
        }
    
    def save_qa_database(self):
        """Save Q&A database to file."""
        try:
            with open("qa_database.json", 'w', encoding='utf-8') as f:
                json.dump(self.qa_database, f, indent=2, ensure_ascii=False)
            print("💾 Q&A database saved successfully!")
        except Exception as e:
            print(f"⚠️ Failed to save database: {e}")
    
    def normalize_question(self, question):
        """Normalize question for matching."""
        return question.lower().strip().rstrip('?')
    
    def find_answer(self, question):
        """Find answer for a question."""
        normalized_q = self.normalize_question(question)
        
        # Exact match
        if normalized_q in self.qa_database:
            return self.qa_database[normalized_q]
        
        # Partial match
        for db_question, answer in self.qa_database.items():
            if normalized_q in db_question or db_question in normalized_q:
                return answer
        
        # No match found
        return None
    
    def add_qa_pair(self, question, answer):
        """Add new Q&A pair to database."""
        normalized_q = self.normalize_question(question)
        self.qa_database[normalized_q] = answer
        self.save_qa_database()
        print(f"✅ Added new Q&A pair to database!")
    
    def ask_question(self, question):
        """Process a question and return audio answer."""
        print(f"❓ Question: {question}")
        
        answer = self.find_answer(question)
        
        if answer:
            print(f"💬 Answer found: {answer[:100]}{'...' if len(answer) > 100 else ''}")
            
            # Convert answer to audio
            timestamp = int(time.time())
            filename = f"qa_answer_{timestamp}"
            
            print("🔄 Converting answer to audio...")
            audio_path = self.converter.convert_text(answer, filename)
            
            if audio_path:
                file_size = Path(audio_path).stat().st_size / 1024
                print(f"✅ Audio answer generated: {Path(audio_path).name} ({file_size:.1f} KB)")
                
                # Try to play the audio
                print("🎧 Playing audio answer...")
                play_success = self.converter.play_audio_file(audio_path)
                
                if play_success:
                    print("🎵 Audio answer played successfully!")
                else:
                    print("💾 Audio answer saved. Play it manually for audio.")
                
                return audio_path, answer
            else:
                print("❌ Failed to generate audio answer.")
                return None, answer
        else:
            print("❌ Sorry, I don't have an answer for that question.")
            
            # Offer to add new Q&A pair
            add_new = input("Would you like to add an answer for this question? (y/n): ").strip().lower()
            if add_new == 'y':
                new_answer = input("Enter the answer: ").strip()
                if new_answer:
                    self.add_qa_pair(question, new_answer)
                    return self.ask_question(question)  # Try again with new answer
            
            return None, None
    
    def show_available_questions(self):
        """Show available questions in the database."""
        print("\n📋 Available Questions in Database:")
        print("=" * 40)
        
        for i, question in enumerate(sorted(self.qa_database.keys()), 1):
            print(f"{i:2d}. {question.title()}?")
        
        print(f"\nTotal: {len(self.qa_database)} questions available")
    
    def interactive_qa_session(self):
        """Run interactive Q&A session."""
        print("🎓 Interactive Q&A Session")
        print("=" * 30)
        print("Ask any question and get an audio answer!")
        print("Type 'help' to see available questions")
        print("Type 'add' to add a new Q&A pair")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                question = input("❓ Your question: ").strip()
                
                if not question:
                    print("⚠️ Please enter a question!")
                    continue
                
                if question.lower() == 'quit':
                    print("👋 Thank you for using the Q&A system!")
                    break
                
                elif question.lower() == 'help':
                    self.show_available_questions()
                    continue
                
                elif question.lower() == 'add':
                    new_question = input("Enter new question: ").strip()
                    new_answer = input("Enter answer: ").strip()
                    
                    if new_question and new_answer:
                        self.add_qa_pair(new_question, new_answer)
                    else:
                        print("❌ Both question and answer are required!")
                    continue
                
                # Process the question
                print("\n" + "─" * 50)
                audio_path, answer = self.ask_question(question)
                print("─" * 50 + "\n")
                
                if answer:
                    # Ask if they want another question
                    continue_choice = input("Ask another question? (y/n): ").strip().lower()
                    if continue_choice != 'y':
                        break
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
    
    def batch_qa_conversion(self):
        """Convert multiple Q&A pairs to audio files."""
        print("\n📦 Batch Q&A Audio Conversion")
        print("=" * 35)
        
        questions = list(self.qa_database.keys())
        print(f"Converting {len(questions)} Q&A pairs to audio...\n")
        
        generated_files = []
        
        for i, question in enumerate(questions, 1):
            answer = self.qa_database[question]
            
            print(f"🔄 {i}/{len(questions)}: {question.title()}?")
            
            # Create Q&A audio
            qa_text = f"Question: {question.title()}? Answer: {answer}"
            filename = f"qa_batch_{i:03d}"
            
            audio_path = self.converter.convert_text(qa_text, filename)
            
            if audio_path:
                size = Path(audio_path).stat().st_size / 1024
                generated_files.append(audio_path)
                print(f"   ✅ Generated: {Path(audio_path).name} ({size:.1f} KB)")
            else:
                print(f"   ❌ Failed to generate audio")
        
        print(f"\n🎉 Batch conversion completed!")
        print(f"Generated {len(generated_files)} audio files:")
        
        for file_path in generated_files:
            print(f"   🎵 {Path(file_path).name}")
        
        return generated_files
    
    def cleanup(self):
        """Cleanup system resources."""
        self.converter.cleanup()

def main():
    """Main function."""
    print("🎓 Q&A Text-to-Audio System")
    print("=" * 35)
    
    qa_system = QATextToAudio()
    
    try:
        while True:
            print("\nChoose an option:")
            print("1. 🎯 Ask a question (get audio answer)")
            print("2. 📋 Show available questions")
            print("3. ➕ Add new Q&A pair")
            print("4. 🎤 Interactive Q&A session")
            print("5. 📦 Convert all Q&A to audio files")
            print("6. ❌ Exit")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == '1':
                question = input("❓ Enter your question: ").strip()
                if question:
                    print("\n" + "─" * 50)
                    qa_system.ask_question(question)
                    print("─" * 50)
            
            elif choice == '2':
                qa_system.show_available_questions()
            
            elif choice == '3':
                question = input("Enter question: ").strip()
                answer = input("Enter answer: ").strip()
                
                if question and answer:
                    qa_system.add_qa_pair(question, answer)
                else:
                    print("❌ Both question and answer are required!")
            
            elif choice == '4':
                qa_system.interactive_qa_session()
            
            elif choice == '5':
                qa_system.batch_qa_conversion()
            
            elif choice == '6':
                print("👋 Thank you for using the Q&A system!")
                break
            
            else:
                print("❌ Invalid choice. Please select 1-6.")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    
    finally:
        qa_system.cleanup()

if __name__ == "__main__":
    main()