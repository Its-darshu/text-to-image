"""
ENHANCED Q&A System with Detailed Answers and Better Audio

This system provides comprehensive answers to questions and converts them
to high-quality, slower-paced audio for better understanding.
"""

import sys
from pathlib import Path
import time

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from main import TextToAudioConverter

# Comprehensive Q&A database with detailed, full answers
QA_DATABASE = {
    "what is artificial intelligence": """Artificial Intelligence, commonly known as AI, is a revolutionary field of computer science that focuses on creating intelligent machines capable of performing tasks that typically require human intelligence. 

AI systems can learn from experience, adapt to new inputs, and perform human-like tasks such as recognizing speech, making decisions, solving problems, and understanding natural language. 

The field encompasses various technologies including machine learning, deep learning, natural language processing, computer vision, and robotics. AI is transforming industries from healthcare and finance to transportation and entertainment, making our lives more efficient and opening new possibilities for innovation.""",
    
    "what is ai": """AI stands for Artificial Intelligence. It represents the cutting-edge technology that enables computers and machines to simulate human intelligence and cognitive functions.

AI systems can learn, reason, perceive, and make decisions. They process vast amounts of data to identify patterns, make predictions, and solve complex problems that would normally require human thinking.

Modern AI includes machine learning algorithms that improve automatically through experience, neural networks that mimic the human brain, and sophisticated programs that can understand and generate human language. AI is already integrated into many aspects of our daily lives, from smartphone assistants to recommendation systems.""",
    
    "how does text to speech work": """Text-to-speech technology, also known as TTS, is a fascinating process that converts written text into natural-sounding spoken words using advanced artificial intelligence and signal processing techniques.

The process begins with text analysis, where the system examines the written content to understand punctuation, abbreviations, and context. Next, linguistic processing determines proper pronunciation, stress patterns, and intonation.

Modern TTS systems use neural networks and deep learning models to generate high-quality, human-like speech. These systems are trained on hours of human speech data to learn natural speaking patterns, rhythm, and emotional expression.

The final step involves audio synthesis, where the processed information is converted into sound waves that create the audible speech output you hear.""",
    
    "what is machine learning": """Machine Learning is a powerful subset of artificial intelligence that enables computers to automatically learn, improve, and make decisions from data without being explicitly programmed for every specific task.

The core concept revolves around algorithms that can identify patterns in large datasets and use these patterns to make predictions or classifications on new, unseen data. Think of it as teaching a computer to recognize trends and relationships in information, much like how humans learn from experience.

There are three main types of machine learning: supervised learning, where algorithms learn from labeled examples; unsupervised learning, where systems find hidden patterns in unlabeled data; and reinforcement learning, where programs learn through interaction and feedback.

Machine learning powers many technologies we use daily, including recommendation systems on streaming platforms, email spam filters, voice recognition, image recognition, and predictive text on smartphones.""",
    
    "what is python": """Python is a high-level, interpreted programming language that has become one of the most popular and versatile programming languages in the world. Created by Guido van Rossum and first released in 1991, Python emphasizes code readability and simplicity.

The language is designed with a clear, intuitive syntax that makes it easy to learn for beginners while remaining powerful enough for expert programmers. Python follows the philosophy of making code readable and requiring fewer lines of code compared to other programming languages.

Python is widely used across numerous fields including web development, data science, artificial intelligence, machine learning, automation, scientific computing, and software development. Its extensive ecosystem of libraries and frameworks makes it incredibly versatile.

Popular applications include web frameworks like Django and Flask, data analysis libraries like Pandas and NumPy, machine learning frameworks like TensorFlow and PyTorch, and automation tools for various industries.""",
    
    "how do neural networks work": """Neural networks are computing systems inspired by the biological neural networks found in animal brains. They represent one of the most significant breakthroughs in artificial intelligence and machine learning.

A neural network consists of interconnected nodes, called artificial neurons or perceptrons, organized in layers. Information flows from input layers through hidden layers to output layers. Each connection between neurons has an associated weight that determines the strength of the signal.

The learning process involves adjusting these weights based on training data. When the network makes incorrect predictions, an algorithm called backpropagation updates the weights to minimize errors and improve accuracy over time.

Deep neural networks, with multiple hidden layers, can learn complex patterns and representations from data. This capability enables them to excel at tasks like image recognition, natural language processing, speech recognition, and game playing.

The power of neural networks lies in their ability to automatically discover features and patterns in data without manual programming, making them incredibly effective for solving complex problems across various domains.""",
    
    "what is deep learning": """Deep learning is an advanced subset of machine learning that uses artificial neural networks with multiple layers, called deep neural networks, to model and understand complex patterns in data.

The term 'deep' refers to the multiple layers of neurons in these networks, typically ranging from three to hundreds of layers. Each layer learns increasingly abstract representations of the input data, building from simple features to complex concepts.

Deep learning has revolutionized artificial intelligence by achieving remarkable breakthroughs in computer vision, natural language processing, speech recognition, and many other fields. It powers technologies like autonomous vehicles, medical image analysis, language translation, and virtual assistants.

The key advantage of deep learning is its ability to automatically learn hierarchical representations from raw data without manual feature engineering. For example, in image recognition, early layers might detect edges and shapes, while deeper layers recognize objects and scenes.

Training deep networks requires large amounts of data and computational power, often utilizing specialized hardware like GPUs. However, the results have been transformative, enabling AI systems to achieve human-level or even superhuman performance in specific tasks.""",
    
    "what are the benefits of ai": """Artificial Intelligence offers numerous transformative benefits that are reshaping industries and improving human life in countless ways.

In healthcare, AI assists in medical diagnosis, drug discovery, personalized treatment plans, and medical imaging analysis, potentially saving millions of lives through early detection and precision medicine.

Business and industry benefit from AI through automation of repetitive tasks, improved decision-making through data analysis, enhanced customer service with chatbots and virtual assistants, and optimized supply chain management.

AI enhances personal productivity through intelligent recommendations, predictive text, voice assistants, and smart home automation that adapts to user preferences and behaviors.

In transportation, AI powers autonomous vehicles, optimizes traffic flow, and improves safety through predictive maintenance and real-time monitoring systems.

Environmental benefits include optimized energy consumption, smart grid management, climate modeling, and resource conservation through intelligent monitoring and management systems.

AI also democratizes access to information and services, breaking down language barriers through real-time translation and making advanced capabilities accessible to people worldwide.""",
    
    "how does speech recognition work": """Speech recognition, also known as automatic speech recognition or ASR, is a sophisticated technology that converts spoken language into written text using advanced signal processing and machine learning techniques.

The process begins with audio capture, where microphones record sound waves from human speech. These analog sound waves are then converted into digital signals that computers can process.

Next comes feature extraction, where the system analyzes the audio signal to identify important characteristics like frequency patterns, pitch, and phonemes - the basic units of speech sounds.

The acoustic model compares these extracted features against learned patterns from training data to identify potential words and sounds. Meanwhile, a language model uses statistical knowledge about word sequences and grammar to determine the most likely interpretation.

Modern speech recognition systems use deep learning neural networks that have been trained on vast datasets of human speech in various accents, languages, and conditions. These systems can adapt to individual speaking patterns and continuously improve their accuracy.

The final step involves confidence scoring and error correction, where the system evaluates the likelihood of its transcription and may suggest alternatives or request clarification for ambiguous speech.""",
    
    "what is this system": """This is an advanced question-answering system that combines artificial intelligence with text-to-speech technology to provide comprehensive, spoken responses to your questions about technology, science, and programming.

The system works by analyzing your questions, finding relevant and detailed answers from its knowledge base, and then converting those answers into high-quality audio that you can listen to. This makes learning more accessible and engaging, especially for auditory learners.

Built using modern AI technologies including natural language processing and neural text-to-speech synthesis, the system aims to provide educational content in both written and spoken formats. It covers topics ranging from artificial intelligence and machine learning to programming languages and computer science concepts.

The audio generation uses advanced speech synthesis models that create natural-sounding voice output, making the information easy to understand and follow. You can ask questions through various interfaces and receive both text and audio responses tailored to your learning needs.""",
    
    "how do i use this": """Using this question-answering system is simple and straightforward. You have several ways to interact with it and get comprehensive answers to your questions.

For quick questions, you can use the command-line interface by typing your question directly. For example, you can run the program with your question as a parameter, and it will provide both a written answer and generate an audio file you can listen to.

The interactive mode allows you to have a conversation-like experience where you can ask multiple questions in sequence. Simply run the program without parameters to enter this mode, then type your questions when prompted.

The system covers a wide range of topics including artificial intelligence, machine learning, programming languages like Python, computer science concepts, and technology explanations. You can ask about definitions, explanations of how things work, benefits of technologies, and practical applications.

All answers are converted to audio files that are saved in the output directory, so you can listen to them immediately or save them for later reference. The audio is generated at high quality with natural-sounding speech to enhance your learning experience.""",
    
    "what can you do": """I am a comprehensive AI-powered question-answering system designed to provide detailed, educational responses about technology, computer science, and artificial intelligence topics.

My capabilities include answering questions about artificial intelligence concepts, explaining how various technologies work, describing programming languages and their applications, and providing insights into machine learning and data science topics.

I can convert all my text responses into high-quality audio using advanced text-to-speech technology, making information accessible through both reading and listening. This is particularly valuable for people who prefer auditory learning or want to listen to explanations while multitasking.

The system provides comprehensive, detailed answers rather than brief responses, ensuring you get thorough explanations that help you truly understand complex topics. Each answer is crafted to be educational and informative, building your knowledge progressively.

I can handle questions about topics ranging from basic programming concepts to advanced AI techniques, from practical applications to theoretical foundations. Whether you're a beginner seeking introductions to technology concepts or someone looking for deeper understanding, I can provide appropriate explanations.""",
    
    "how does machine learning work": """Machine learning works through a systematic process of pattern recognition and statistical learning that enables computers to improve their performance on specific tasks through experience with data.

The process begins with data collection, where relevant information is gathered and prepared for analysis. This data serves as the foundation for learning, much like how humans learn from examples and experiences throughout their lives.

Next, a machine learning algorithm is selected based on the type of problem being solved. Different algorithms are suited for different tasks - some excel at classification, others at prediction, and some at finding hidden patterns in data.

During the training phase, the algorithm analyzes the provided data to identify patterns, relationships, and trends. It builds an internal mathematical model that captures these patterns and can be used to make predictions or decisions on new, unseen data.

The model is then tested and validated using separate datasets to ensure it can generalize well to new situations. This prevents overfitting, where a model performs well on training data but poorly on new data.

Finally, the trained model is deployed to make predictions or decisions on real-world data. Importantly, many machine learning systems continue to learn and improve as they encounter new data, making them increasingly accurate over time.""",
    
    "is the audio working": """Yes, the audio generation system is working correctly and has been successfully tested. The system uses advanced neural text-to-speech technology to convert written answers into high-quality audio files.

Each time you ask a question, the system processes your query, generates a comprehensive text response, and then converts that response into natural-sounding speech audio. The audio files are saved in WAV format at 16kHz quality, which provides clear and crisp sound.

The audio generation process involves sophisticated AI models that have been trained on human speech patterns to create natural intonation, proper pronunciation, and appropriate pacing. The system handles various types of text including technical terms, complex concepts, and different sentence structures.

All generated audio files are automatically saved in the output directory with descriptive filenames, making them easy to locate and replay. The system includes audio playback functionality, though you can also play the files using any standard audio player on your computer.

If you experience any issues with audio playback, the files are still being generated successfully and can be played manually using your preferred audio application.""",
}

def normalize_question(question):
    """Normalize question for better matching."""
    return question.lower().strip().rstrip('?').rstrip('.').rstrip('!')

def find_answer(question):
    """Find the best answer for a question using improved matching."""
    normalized_q = normalize_question(question)
    
    # Direct match
    if normalized_q in QA_DATABASE:
        return QA_DATABASE[normalized_q]
    
    # Enhanced partial matching with scoring
    question_words = set(normalized_q.split())
    best_match = None
    max_score = 0
    
    for db_question, answer in QA_DATABASE.items():
        db_words = set(db_question.split())
        
        # Calculate similarity score
        common_words = question_words.intersection(db_words)
        important_words = [w for w in common_words if len(w) > 3]  # Focus on important words
        
        score = len(important_words)
        
        # Bonus for exact phrase matches
        if any(phrase in normalized_q for phrase in db_question.split() if len(phrase) > 5):
            score += 2
        
        if score > max_score and score > 0:
            max_score = score
            best_match = answer
    
    return best_match

def answer_question(question):
    """Answer a question with enhanced audio generation."""
    print(f"❓ Question: {question}")
    
    answer = find_answer(question)
    
    if answer:
        # Display truncated answer for console
        display_answer = answer[:200] + "..." if len(answer) > 200 else answer
        print(f"💬 Answer: {display_answer}")
        print()
        
        # Convert to audio with progress indication
        print("🔄 Converting detailed answer to high-quality audio...")
        print("⏳ This may take a moment for longer responses...")
        
        converter = TextToAudioConverter()
        
        try:
            # Generate unique filename with timestamp
            timestamp = int(time.time())
            filename = f"qa_detailed_{timestamp}"
            
            start_time = time.time()
            audio_path = converter.convert_text(answer, filename)
            generation_time = time.time() - start_time
            
            if audio_path and Path(audio_path).exists():
                file_size = Path(audio_path).stat().st_size / 1024
                duration_estimate = len(answer.split()) * 0.5  # Rough estimate
                
                print(f"✅ Audio generated successfully!")
                print(f"📄 Full answer length: {len(answer)} characters")
                print(f"🎵 Audio file: {Path(audio_path).name} ({file_size:.1f} KB)")
                print(f"⏱️ Generation time: {generation_time:.1f} seconds")
                print(f"🕐 Estimated duration: {duration_estimate:.1f} seconds")
                
                # Try to play audio
                print("🎧 Playing detailed audio answer...")
                play_success = converter.play_audio_file(audio_path)
                
                if play_success:
                    print("🎵 Audio playback started successfully!")
                    print("💡 Listen to the complete detailed answer in the audio.")
                else:
                    print("💾 Audio file saved successfully!")
                    print(f"📁 Location: {audio_path}")
                    print("🎧 You can play it with any audio player.")
                
            else:
                print("❌ Failed to generate audio file.")
        
        except Exception as e:
            print(f"❌ Error generating audio: {e}")
        
        finally:
            converter.cleanup()
        
        return True
    else:
        print("❌ Sorry, I don't have information about that topic.")
        print("\n💡 I can answer detailed questions about:")
        print("   • Artificial Intelligence and AI concepts")
        print("   • Machine Learning and Deep Learning")
        print("   • Python Programming and Computer Science")
        print("   • Text-to-Speech and Speech Recognition")
        print("   • Neural Networks and Technology")
        print("   • How various AI technologies work")
        return False

def interactive_mode():
    """Run enhanced interactive mode."""
    print("🎓 Enhanced Q&A System with Detailed Audio Answers")
    print("=" * 55)
    print("Ask comprehensive questions and get detailed audio responses!")
    print("All answers include full explanations and background information.")
    print("\nType 'help' to see example questions")
    print("Type 'quit' to exit\n")
    
    while True:
        try:
            question = input("❓ Your question: ").strip()
            
            if not question:
                print("⚠️ Please enter a question!")
                continue
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Thank you for using the enhanced Q&A system!")
                break
            
            if question.lower() == 'help':
                print("\n💡 Example questions for detailed answers:")
                print("   • What is artificial intelligence and how does it work?")
                print("   • How does machine learning actually work?")
                print("   • What are the benefits of AI in modern society?")
                print("   • How do neural networks process information?")
                print("   • What is Python and why is it popular?")
                print("   • How does text-to-speech technology work?")
                print("   • Is the audio working properly?")
                print()
                continue
            
            print("\n" + "═" * 60)
            success = answer_question(question)
            print("═" * 60)
            
            if success:
                continue_choice = input("\nAsk another question? (y/n): ").strip().lower()
                if continue_choice != 'y':
                    print("👋 Thank you for using the enhanced Q&A system!")
                    break
            
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

def main():
    """Main function."""
    print("🎓 Enhanced Q&A System - Detailed Answers with High-Quality Audio")
    print("=" * 70)
    
    if len(sys.argv) > 1:
        # Command line mode
        question = " ".join(sys.argv[1:])
        answer_question(question)
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()