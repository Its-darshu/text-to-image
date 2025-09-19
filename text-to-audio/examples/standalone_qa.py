"""
STANDALONE Q&A SYSTEM with Audio Generation

This is a completely self-contained Q&A system that generates 
detailed answers and converts them to audio without external dependencies.
"""

import os
import time
import subprocess
import tempfile
from pathlib import Path

# Simple Q&A database with detailed, comprehensive answers
QA_ANSWERS = {
    "what is artificial intelligence": """
    Artificial Intelligence, commonly known as AI, is a revolutionary field of computer science 
    that focuses on creating intelligent machines capable of performing tasks that typically 
    require human intelligence.
    
    AI systems can learn from experience, adapt to new inputs, and perform human-like tasks 
    such as recognizing speech, making decisions, solving problems, and understanding natural language.
    
    The field encompasses various technologies including machine learning, deep learning, 
    natural language processing, computer vision, and robotics.
    
    AI is transforming industries from healthcare and finance to transportation and entertainment, 
    making our lives more efficient and opening new possibilities for innovation.
    """,
    
    "what is ai": """
    AI stands for Artificial Intelligence. It represents cutting-edge technology that enables 
    computers and machines to simulate human intelligence and cognitive functions.
    
    AI systems can learn, reason, perceive, and make decisions. They process vast amounts of data 
    to identify patterns, make predictions, and solve complex problems that would normally require 
    human thinking.
    
    Modern AI includes machine learning algorithms that improve automatically through experience, 
    neural networks that mimic the human brain, and sophisticated programs that can understand 
    and generate human language.
    
    AI is already integrated into many aspects of our daily lives, from smartphone assistants 
    to recommendation systems on streaming platforms.
    """,
    
    "what is machine learning": """
    Machine Learning is a powerful subset of artificial intelligence that enables computers 
    to automatically learn, improve, and make decisions from data without being explicitly 
    programmed for every specific task.
    
    The core concept revolves around algorithms that can identify patterns in large datasets 
    and use these patterns to make predictions or classifications on new, unseen data.
    
    There are three main types of machine learning: supervised learning, where algorithms learn 
    from labeled examples; unsupervised learning, where systems find hidden patterns in unlabeled 
    data; and reinforcement learning, where programs learn through interaction and feedback.
    
    Machine learning powers many technologies we use daily, including recommendation systems 
    on streaming platforms, email spam filters, voice recognition, and predictive text.
    """,
    
    "what is python": """
    Python is a high-level, interpreted programming language that has become one of the most 
    popular and versatile programming languages in the world.
    
    Created by Guido van Rossum and first released in 1991, Python emphasizes code readability 
    and simplicity. The language is designed with a clear, intuitive syntax that makes it easy 
    to learn for beginners while remaining powerful enough for expert programmers.
    
    Python is widely used across numerous fields including web development, data science, 
    artificial intelligence, machine learning, automation, and scientific computing.
    
    Popular applications include web frameworks like Django and Flask, data analysis libraries 
    like Pandas and NumPy, and machine learning frameworks like TensorFlow and PyTorch.
    """,
    
    "how does text to speech work": """
    Text-to-speech technology, also known as TTS, is a fascinating process that converts written 
    text into natural-sounding spoken words using advanced artificial intelligence and signal 
    processing techniques.
    
    The process begins with text analysis, where the system examines the written content to 
    understand punctuation, abbreviations, and context. Next, linguistic processing determines 
    proper pronunciation, stress patterns, and intonation.
    
    Modern TTS systems use neural networks and deep learning models to generate high-quality, 
    human-like speech. These systems are trained on hours of human speech data to learn natural 
    speaking patterns, rhythm, and emotional expression.
    
    The final step involves audio synthesis, where the processed information is converted into 
    sound waves that create the audible speech output you hear.
    """,
    
    "what can you do": """
    I am a comprehensive question-answering system designed to provide detailed, educational 
    responses about technology, computer science, and artificial intelligence topics.
    
    My capabilities include answering questions about artificial intelligence concepts, explaining 
    how various technologies work, describing programming languages and their applications, and 
    providing insights into machine learning and data science topics.
    
    I convert all my text responses into audio using text-to-speech technology, making information 
    accessible through both reading and listening. This is particularly valuable for people who 
    prefer auditory learning.
    
    I provide comprehensive, detailed answers rather than brief responses, ensuring you get 
    thorough explanations that help you truly understand complex topics.
    """,
    
    "is the audio working": """
    Yes, the audio system is designed to work correctly. The system converts text answers into 
    speech using text-to-speech technology.
    
    Each time you ask a question, the system generates a comprehensive text response and then 
    attempts to convert that response into audible speech.
    
    The audio files are created and can be played through your computer's audio system. If you're 
    not hearing audio, please check your computer's volume settings and ensure your speakers or 
    headphones are properly connected.
    
    The system creates clear, spoken versions of all text answers to make the information more 
    accessible and easier to understand.
    """,
}

def clean_text_for_speech(text):
    """Clean and prepare text for speech synthesis."""
    # Remove extra whitespace and formatting
    text = ' '.join(text.split())
    
    # Replace newlines with periods for better speech flow
    text = text.replace('\n', '. ')
    
    # Ensure proper sentence endings
    text = text.replace('..', '.')
    
    # Remove multiple periods
    while '. .' in text:
        text = text.replace('. .', '.')
    
    return text.strip()

def find_answer(question):
    """Find the best matching answer for a question."""
    question_clean = question.lower().strip().rstrip('?').rstrip('.')
    
    # Direct match
    if question_clean in QA_ANSWERS:
        return QA_ANSWERS[question_clean]
    
    # Partial matching - find best match
    question_words = set(question_clean.split())
    best_match = None
    best_score = 0
    
    for key, answer in QA_ANSWERS.items():
        key_words = set(key.split())
        common_words = question_words.intersection(key_words)
        
        # Score based on important word matches
        score = sum(1 for word in common_words if len(word) > 3)
        
        if score > best_score:
            best_score = score
            best_match = answer
    
    return best_match if best_score > 0 else None

def create_audio_file(text, filename="qa_audio"):
    """Create audio file using Windows built-in text-to-speech."""
    try:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        audio_file = output_dir / f"{filename}.wav"
        
        # Clean text for speech
        speech_text = clean_text_for_speech(text)
        
        # Create PowerShell script for text-to-speech
        ps_script = f'''
Add-Type -AssemblyName System.Speech
$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer

# Set voice properties for better quality
$speak.Rate = 0
$speak.Volume = 100

# Get available voices and use the best one
$voices = $speak.GetInstalledVoices()
foreach ($voice in $voices) {{
    if ($voice.VoiceInfo.Name -like "*Zira*" -or $voice.VoiceInfo.Name -like "*David*") {{
        $speak.SelectVoice($voice.VoiceInfo.Name)
        break
    }}
}}

# Create audio file
$speak.SetOutputToWaveFile("{str(audio_file).replace(chr(92), chr(92)+chr(92))}")
$speak.Speak("{speech_text.replace('"', '""')}")
$speak.SetOutputToDefaultAudioDevice()
$speak.Dispose()

Write-Host "Audio saved to: {audio_file}"
'''
        
        # Write PowerShell script to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False) as f:
            f.write(ps_script)
            ps_file = f.name
        
        try:
            # Execute PowerShell script
            print("🔄 Generating audio using Windows Speech Synthesis...")
            result = subprocess.run(
                ['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', ps_file],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                if audio_file.exists():
                    file_size = audio_file.stat().st_size / 1024
                    print(f"✅ Audio created: {audio_file.name} ({file_size:.1f} KB)")
                    return str(audio_file)
                else:
                    print("❌ Audio file was not created")
            else:
                print(f"❌ PowerShell error: {result.stderr}")
                
        finally:
            # Clean up temporary file
            try:
                os.unlink(ps_file)
            except:
                pass
                
    except Exception as e:
        print(f"❌ Audio generation error: {e}")
    
    return None

def play_audio_file(audio_path):
    """Play audio file using Windows default player."""
    try:
        print("🎧 Playing audio...")
        os.startfile(audio_path)
        return True
    except Exception as e:
        print(f"❌ Could not play audio: {e}")
        return False

def answer_question(question):
    """Answer a question with text and audio."""
    print(f"❓ Question: {question}")
    
    # Find answer
    answer = find_answer(question)
    
    if answer:
        # Clean up answer text
        clean_answer = clean_text_for_speech(answer)
        
        # Display answer preview
        preview = clean_answer[:200] + "..." if len(clean_answer) > 200 else clean_answer
        print(f"💬 Answer: {preview}")
        print(f"📝 Full answer: {len(clean_answer)} characters")
        print()
        
        # Generate audio
        timestamp = int(time.time())
        audio_path = create_audio_file(clean_answer, f"qa_{timestamp}")
        
        if audio_path:
            print(f"✅ Audio generated successfully!")
            
            # Attempt to play audio
            if play_audio_file(audio_path):
                print("🎵 Audio is playing...")
                print("💡 Listen to the complete detailed explanation!")
            else:
                print(f"💾 Audio saved to: {audio_path}")
                print("🎧 You can double-click the file to play it.")
        
        return True
    else:
        print("❌ Sorry, I don't have information about that topic.")
        print("\n💡 Try asking about:")
        print("   • What is artificial intelligence?")
        print("   • What is machine learning?")  
        print("   • What is Python?")
        print("   • How does text to speech work?")
        print("   • What can you do?")
        return False

def main():
    """Main application."""
    print("🎓 Standalone Q&A System with Audio")
    print("=" * 40)
    print("Ask questions and get detailed audio answers!")
    print()
    
    if len(os.sys.argv) > 1:
        # Command line mode
        question = " ".join(os.sys.argv[1:])
        answer_question(question)
    else:
        # Interactive mode
        print("Enter your questions (type 'quit' to exit):")
        print()
        
        while True:
            try:
                question = input("❓ Your question: ").strip()
                
                if not question:
                    continue
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("👋 Thank you for using the Q&A system!")
                    break
                
                print("\n" + "─" * 50)
                answer_question(question)
                print("─" * 50)
                
                # Ask if user wants to continue
                continue_choice = input("\nAsk another question? (y/n): ").strip().lower()
                if continue_choice != 'y':
                    print("👋 Thank you for using the Q&A system!")
                    break
                
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break

if __name__ == "__main__":
    main()