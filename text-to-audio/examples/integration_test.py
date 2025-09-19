"""
Final Integration Test

This script runs comprehensive tests to validate the entire text-to-audio system.
"""

import sys
import os
from pathlib import Path
import time

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from main import TextToAudioConverter
from text_processor import TextProcessor
from tts_model import TTSModelManager
from audio_processor import AudioProcessor

def test_text_processor():
    """Test text processing functionality."""
    print("🧪 Testing Text Processor...")
    processor = TextProcessor()
    
    test_text = "Hello Dr. Smith! Today is 25°C. Visit www.example.com at 3:30 PM."
    cleaned = processor.clean_text(test_text)
    chunks = processor.preprocess_for_tts(test_text)
    stats = processor.get_text_stats(test_text)
    
    assert len(cleaned) > 0, "Text cleaning failed"
    assert len(chunks) > 0, "Text chunking failed"
    assert stats["word_count"] > 0, "Text stats failed"
    
    print("✅ Text Processor tests passed")
    return True

def test_tts_model():
    """Test TTS model functionality."""
    print("🧪 Testing TTS Model...")
    tts = TTSModelManager()
    
    info = tts.get_model_info()
    assert info["loaded"] == True, "Model not loaded"
    
    audio = tts.synthesize_speech("This is a test.")
    assert audio is not None, "Speech synthesis failed"
    assert len(audio) > 0, "Generated audio is empty"
    
    tts.cleanup()
    print("✅ TTS Model tests passed")
    return True

def test_audio_processor():
    """Test audio processing functionality."""
    print("🧪 Testing Audio Processor...")
    processor = AudioProcessor()
    
    # Create dummy audio data
    import numpy as np
    dummy_audio = np.random.randn(1000).astype(np.float32) * 0.1
    
    # Test normalization
    normalized = processor.normalize_audio(dummy_audio)
    assert len(normalized) == len(dummy_audio), "Normalization failed"
    
    # Test fade
    faded = processor.apply_fade(dummy_audio, sample_rate=16000)
    assert len(faded) == len(dummy_audio), "Fade application failed"
    
    # Test saving
    output_path = processor.save_audio(dummy_audio, "test_audio", 16000)
    assert Path(output_path).exists(), "Audio saving failed"
    
    # Test loading
    loaded_audio, sample_rate = processor.load_audio(output_path)
    assert len(loaded_audio) > 0, "Audio loading failed"
    assert sample_rate == 16000, "Sample rate mismatch"
    
    processor.cleanup()
    print("✅ Audio Processor tests passed")
    return True

def test_complete_pipeline():
    """Test the complete text-to-audio pipeline."""
    print("🧪 Testing Complete Pipeline...")
    converter = TextToAudioConverter()
    
    # Test simple conversion
    test_texts = [
        "Short test.",
        "This is a medium length test sentence with several words.",
        "Hello! How are you today? I hope this longer text works well too."
    ]
    
    successful_conversions = 0
    
    for i, text in enumerate(test_texts, 1):
        output_path = converter.convert_text(text, f"pipeline_test_{i}")
        if output_path and Path(output_path).exists():
            successful_conversions += 1
            print(f"  ✅ Test {i} passed: {Path(output_path).name}")
        else:
            print(f"  ❌ Test {i} failed")
    
    # Test batch conversion
    batch_outputs = converter.convert_batch(test_texts[:2], "batch_test")
    batch_successful = len([p for p in batch_outputs if p and Path(p).exists()])
    
    print(f"  ✅ Batch test: {batch_successful}/2 successful")
    
    converter.cleanup()
    
    assert successful_conversions >= 2, f"Only {successful_conversions} conversions succeeded"
    assert batch_successful >= 1, "Batch conversion failed"
    
    print("✅ Complete Pipeline tests passed")
    return True

def main():
    """Run all tests."""
    print("🚀 Starting Comprehensive Integration Tests")
    print("=" * 50)
    
    start_time = time.time()
    tests_passed = 0
    total_tests = 4
    
    try:
        # Run individual component tests
        if test_text_processor():
            tests_passed += 1
        
        if test_tts_model():
            tests_passed += 1
        
        if test_audio_processor():
            tests_passed += 1
        
        # Run integration test
        if test_complete_pipeline():
            tests_passed += 1
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    end_time = time.time()
    test_duration = end_time - start_time
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print(f"  Tests passed: {tests_passed}/{total_tests}")
    print(f"  Success rate: {tests_passed/total_tests*100:.1f}%")
    print(f"  Test duration: {test_duration:.2f} seconds")
    
    # Check generated files
    output_dir = Path("../output")
    if output_dir.exists():
        audio_files = list(output_dir.glob("*.wav"))
        print(f"  Generated files: {len(audio_files)}")
        
        total_size = sum(f.stat().st_size for f in audio_files) / 1024  # KB
        print(f"  Total audio size: {total_size:.1f} KB")
    
    if tests_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! System is fully functional.")
        return True
    else:
        print(f"\n⚠️ {total_tests - tests_passed} tests failed. System has issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)