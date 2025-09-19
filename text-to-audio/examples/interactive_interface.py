"""
Interactive Text-to-Audio Interface

This script provides a user-friendly interface where users can:
1. Enter text and immediately hear it as audio
2. Work with datasets for training
3. Batch process multiple texts
4. Save and manage audio files
"""

import sys
import os
from pathlib import Path
import time

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from main import TextToAudioConverter
from dataset_manager import DatasetManager

class InteractiveTextToAudio:
    """Interactive interface for text-to-audio conversion."""
    
    def __init__(self):
        """Initialize the interactive system."""
        print("🎵 Initializing Interactive Text-to-Audio System...")
        self.converter = TextToAudioConverter()
        self.dataset_manager = DatasetManager()
        self.session_files = []
        
        print("✅ System ready!")
        print(f"📂 Audio files will be saved in: {self.converter.output_dir}")
        print()
    
    def show_menu(self):
        """Display the main menu."""
        print("🎯 Text-to-Audio Interactive Menu")
        print("=" * 40)
        print("1. 🎵 Convert text to audio (and play)")
        print("2. 📚 Question-Answer mode")
        print("3. 📦 Batch process texts")
        print("4. 📊 Dataset operations")
        print("5. 🔧 System settings")
        print("6. 📁 View generated files")
        print("7. 🎧 Play existing audio file")
        print("8. ❌ Exit")
        print("=" * 40)
    
    def convert_text_interactive(self):
        """Interactive text conversion with immediate playback."""
        print("\n🎵 Text-to-Audio Conversion")
        print("-" * 30)
        
        while True:
            text = input("\n📝 Enter text to convert (or 'back' to return): ").strip()
            
            if text.lower() == 'back':
                break
            
            if not text:
                print("⚠️ Please enter some text!")
                continue
            
            print(f"🔄 Converting: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            
            # Generate filename with timestamp
            timestamp = int(time.time())
            filename = f"interactive_{timestamp}"
            
            # Convert text to audio
            start_time = time.time()
            audio_path = self.converter.convert_text(text, filename)
            conversion_time = time.time() - start_time
            
            if audio_path:
                self.session_files.append(audio_path)
                file_size = Path(audio_path).stat().st_size / 1024
                
                print(f"✅ Conversion successful!")
                print(f"   📄 File: {Path(audio_path).name}")
                print(f"   📊 Size: {file_size:.1f} KB")
                print(f"   ⏱️ Time: {conversion_time:.2f} seconds")
                
                # Attempt to play audio
                print("🎧 Playing audio...")
                play_success = self.converter.play_audio_file(audio_path)
                
                if not play_success:
                    print("ℹ️ Audio file saved successfully but playback not available.")
                    print(f"   You can play the file manually: {audio_path}")
                
                # Ask if user wants to convert more text
                continue_choice = input("\n🔄 Convert another text? (y/n): ").strip().lower()
                if continue_choice != 'y':
                    break
            else:
                print("❌ Conversion failed. Please try again.")
    
    def question_answer_mode(self):
        """Interactive question-answer conversion."""
        print("\n📚 Question-Answer Mode")
        print("-" * 25)
        
        qa_pairs = []
        
        while True:
            print(f"\n📋 Q&A Pair #{len(qa_pairs) + 1}")
            question = input("❓ Question (or 'done' to finish): ").strip()
            
            if question.lower() == 'done':
                break
            
            if not question:
                print("⚠️ Please enter a question!")
                continue
            
            answer = input("💬 Answer: ").strip()
            
            if not answer:
                print("⚠️ Please enter an answer!")
                continue
            
            qa_pairs.append({"question": question, "answer": answer})
            print(f"✅ Added Q&A pair #{len(qa_pairs)}")
        
        if not qa_pairs:
            print("ℹ️ No Q&A pairs to process.")
            return
        
        print(f"\n🔄 Converting {len(qa_pairs)} Q&A pairs...")
        
        # Convert Q&A pairs
        audio_files = self.converter.convert_questions_and_answers(qa_pairs, include_questions=True)
        
        successful = [f for f in audio_files if f]
        self.session_files.extend(successful)
        
        print(f"✅ Generated {len(successful)} Q&A audio files:")
        for i, file_path in enumerate(successful, 1):
            if file_path:
                size = Path(file_path).stat().st_size / 1024
                print(f"   {i}. {Path(file_path).name} ({size:.1f} KB)")
        
        # Offer to play the files
        if successful:
            play_choice = input(f"\n🎧 Play the Q&A audio files? (y/n): ").strip().lower()
            if play_choice == 'y':
                for i, file_path in enumerate(successful, 1):
                    print(f"\n🎵 Playing Q&A {i}/{len(successful)}: {Path(file_path).name}")
                    self.converter.play_audio_file(file_path)
                    if i < len(successful):
                        input("   Press Enter for next audio...")
    
    def batch_process_mode(self):
        """Interactive batch processing."""
        print("\n📦 Batch Processing Mode")
        print("-" * 25)
        
        texts = []
        
        print("📝 Enter texts to process (one per line):")
        print("   Type 'DONE' on a new line when finished")
        
        while True:
            text = input(f"Text #{len(texts) + 1}: ").strip()
            
            if text.upper() == 'DONE':
                break
            
            if text:
                texts.append(text)
                print(f"✅ Added text #{len(texts)}")
        
        if not texts:
            print("ℹ️ No texts to process.")
            return
        
        print(f"\n🔄 Processing {len(texts)} texts...")
        
        # Process batch
        batch_files = self.converter.convert_batch(texts, "batch_interactive")
        
        successful = [f for f in batch_files if f]
        self.session_files.extend(successful)
        
        print(f"✅ Generated {len(successful)} audio files:")
        for i, file_path in enumerate(successful, 1):
            if file_path:
                size = Path(file_path).stat().st_size / 1024
                print(f"   {i}. {Path(file_path).name} ({size:.1f} KB)")
    
    def dataset_operations(self):
        """Dataset management operations."""
        print("\n📊 Dataset Operations")
        print("-" * 20)
        
        while True:
            print("\nDataset Menu:")
            print("1. 📋 List available datasets")
            print("2. 📥 Load LJSpeech sample (demo)")
            print("3. 📊 Show dataset statistics")
            print("4. 🔙 Back to main menu")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '1':
                self.list_datasets()
            elif choice == '2':
                self.load_sample_dataset()
            elif choice == '3':
                self.show_dataset_stats()
            elif choice == '4':
                break
            else:
                print("❌ Invalid choice. Please select 1-4.")
    
    def list_datasets(self):
        """List available datasets."""
        print("\n📋 Available Datasets:")
        datasets = self.dataset_manager.list_available_datasets()
        
        for name, info in datasets.items():
            print(f"\n📁 {name.upper()}:")
            print(f"   Name: {info['name']}")
            print(f"   Type: {info['type']}")
            print(f"   Language: {info['language']}")
            print(f"   Sample Rate: {info['sample_rate']} Hz")
            print(f"   Size: {info['size']}")
    
    def load_sample_dataset(self):
        """Load a sample dataset."""
        print("\n📥 Loading LJSpeech Sample Dataset...")
        print("ℹ️ Loading 5 samples for demonstration...")
        
        try:
            dataset = self.dataset_manager.load_ljspeech(max_samples=5)
            
            if dataset:
                print(f"✅ Loaded {len(dataset)} samples successfully!")
                
                # Show sample data
                print("\n📋 Sample Data:")
                for i in range(min(3, len(dataset))):
                    sample = dataset[i]
                    print(f"\nSample {i+1}:")
                    print(f"   Text: {sample['text'][:80]}...")
                    if 'audio' in sample:
                        audio_info = sample['audio']
                        duration = len(audio_info['array']) / audio_info['sampling_rate']
                        print(f"   Audio: {duration:.2f}s at {audio_info['sampling_rate']} Hz")
            else:
                print("❌ Failed to load dataset")
                
        except Exception as e:
            print(f"⚠️ Dataset loading issue: {e}")
            print("This is normal for demo purposes - datasets are large!")
    
    def show_dataset_stats(self):
        """Show dataset statistics."""
        dataset_name = input("\n📊 Enter dataset name (ljspeech): ").strip() or "ljspeech"
        
        stats = self.dataset_manager.get_dataset_stats(dataset_name)
        
        if stats:
            print(f"\n📊 Statistics for '{dataset_name}':")
            print(f"   Total samples: {stats['total_samples']}")
            
            if 'text_stats' in stats:
                ts = stats['text_stats']
                print(f"   Average words: {ts['avg_words']:.1f}")
                print(f"   Word range: {ts['min_words']}-{ts['max_words']}")
            
            if 'audio_stats' in stats:
                aus = stats['audio_stats']
                print(f"   Average duration: {aus['avg_duration']:.2f}s")
                print(f"   Sample rates: {aus['sample_rates']}")
        else:
            print(f"❌ No statistics available for '{dataset_name}'")
            print("   Make sure the dataset is loaded first.")
    
    def system_settings(self):
        """Configure system settings."""
        print("\n🔧 System Settings")
        print("-" * 15)
        
        current_config = self.converter.config
        
        print("Current Configuration:")
        for key, value in current_config.items():
            print(f"   {key}: {value}")
        
        print("\nAvailable settings to modify:")
        print("1. audio_format (wav, mp3, flac, ogg)")
        print("2. normalize_audio (True/False)")
        print("3. apply_fade (True/False)")
        print("4. noise_reduction (True/False)")
        print("5. segment_gap_ms (milliseconds)")
        
        setting = input("\nEnter setting name (or 'back'): ").strip()
        
        if setting.lower() == 'back':
            return
        
        if setting in current_config:
            new_value = input(f"New value for {setting} (current: {current_config[setting]}): ").strip()
            
            # Convert to appropriate type
            if setting in ['normalize_audio', 'apply_fade', 'noise_reduction']:
                new_value = new_value.lower() == 'true'
            elif setting == 'segment_gap_ms':
                try:
                    new_value = int(new_value)
                except ValueError:
                    print("❌ Invalid number")
                    return
            
            self.converter.update_config(**{setting: new_value})
            print(f"✅ Updated {setting} to {new_value}")
        else:
            print("❌ Invalid setting name")
    
    def view_generated_files(self):
        """View generated audio files."""
        print("\n📁 Generated Audio Files")
        print("-" * 25)
        
        output_dir = Path(self.converter.output_dir)
        if output_dir.exists():
            audio_files = list(output_dir.glob("*.wav"))
            
            if audio_files:
                print(f"Found {len(audio_files)} audio files:")
                for i, file_path in enumerate(audio_files, 1):
                    size = file_path.stat().st_size / 1024
                    modified = file_path.stat().st_mtime
                    mod_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(modified))
                    print(f"   {i}. {file_path.name} ({size:.1f} KB) - {mod_time}")
            else:
                print("No audio files found.")
        else:
            print("Output directory not found.")
        
        if self.session_files:
            print(f"\n📊 Session files generated: {len(self.session_files)}")
    
    def play_existing_file(self):
        """Play an existing audio file."""
        print("\n🎧 Play Existing Audio File")
        print("-" * 25)
        
        output_dir = Path(self.converter.output_dir)
        if not output_dir.exists():
            print("❌ Output directory not found.")
            return
        
        audio_files = list(output_dir.glob("*.wav"))
        
        if not audio_files:
            print("❌ No audio files found.")
            return
        
        print("Available audio files:")
        for i, file_path in enumerate(audio_files, 1):
            size = file_path.stat().st_size / 1024
            print(f"   {i}. {file_path.name} ({size:.1f} KB)")
        
        try:
            choice = int(input(f"\nSelect file (1-{len(audio_files)}): ")) - 1
            
            if 0 <= choice < len(audio_files):
                selected_file = audio_files[choice]
                print(f"🎵 Playing: {selected_file.name}")
                
                success = self.converter.play_audio_file(str(selected_file))
                if not success:
                    print("⚠️ Playback failed or not available")
            else:
                print("❌ Invalid file number")
                
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
    
    def run(self):
        """Run the interactive interface."""
        print("🎉 Welcome to Interactive Text-to-Audio System!")
        print()
        
        try:
            while True:
                self.show_menu()
                choice = input("\n🎯 Select option (1-8): ").strip()
                
                if choice == '1':
                    self.convert_text_interactive()
                elif choice == '2':
                    self.question_answer_mode()
                elif choice == '3':
                    self.batch_process_mode()
                elif choice == '4':
                    self.dataset_operations()
                elif choice == '5':
                    self.system_settings()
                elif choice == '6':
                    self.view_generated_files()
                elif choice == '7':
                    self.play_existing_file()
                elif choice == '8':
                    print("\n👋 Thank you for using Text-to-Audio System!")
                    break
                else:
                    print("❌ Invalid choice. Please select 1-8.")
                
                input("\nPress Enter to continue...")
                print("\n" + "="*50)
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
        
        finally:
            # Cleanup
            self.converter.cleanup()
            print("✅ System cleaned up successfully.")


def main():
    """Main function to run the interactive interface."""
    interface = InteractiveTextToAudio()
    interface.run()


if __name__ == "__main__":
    main()