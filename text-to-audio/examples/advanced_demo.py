"""
Advanced Features Demo - Text-to-Audio System

This demo showcases advanced features like different processing options,
batch processing with configurations, and real-world use cases.
"""

import sys
from pathlib import Path
import time

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from main import TextToAudioConverter

def demo_educational_content():
    """Generate educational content with Q&A format."""
    print("🎓 Educational Content Generation")
    print("-" * 40)
    
    converter = TextToAudioConverter()
    
    # Educational Q&A pairs
    educational_qa = [
        {
            "question": "What is Python programming?",
            "answer": "Python is a high-level, interpreted programming language known for its simple syntax and versatility. It's widely used in web development, data science, artificial intelligence, and automation."
        },
        {
            "question": "How does machine learning differ from traditional programming?",
            "answer": "Traditional programming uses explicit instructions to solve problems, while machine learning uses algorithms that learn patterns from data to make predictions or decisions without being explicitly programmed for every scenario."
        },
        {
            "question": "What are the benefits of using virtual environments in Python?",
            "answer": "Virtual environments allow you to create isolated Python installations for different projects, preventing dependency conflicts and ensuring reproducible development environments across different systems."
        }
    ]
    
    print(f"Converting {len(educational_qa)} educational Q&A pairs...")
    
    # Generate Q&A audio files
    qa_files = converter.convert_questions_and_answers(educational_qa, include_questions=True)
    
    print(f"✅ Generated {len(qa_files)} educational audio files")
    for i, file_path in enumerate(qa_files, 1):
        if file_path:
            size = Path(file_path).stat().st_size / 1024
            print(f"   📚 Educational Q&A {i}: {Path(file_path).name} ({size:.1f} KB)")
    
    converter.cleanup()
    return qa_files

def demo_news_briefing():
    """Generate a news briefing with multiple segments."""
    print("\n📰 News Briefing Generation")
    print("-" * 40)
    
    converter = TextToAudioConverter()
    
    # Configure for news-style audio
    converter.update_config(
        segment_gap_ms=1000,  # Longer pauses between segments
        apply_fade=True,
        normalize_audio=True
    )
    
    news_segments = [
        "Good evening, and welcome to today's technology news briefing.",
        "In breaking news, artificial intelligence continues to transform industries worldwide. Recent developments in large language models are making AI more accessible to businesses of all sizes.",
        "In other tech news, the adoption of text-to-speech technology is accelerating, with new applications in education, accessibility, and content creation showing remarkable growth.",
        "Weather update: Partly cloudy skies are expected tomorrow with temperatures reaching seventy-five degrees Fahrenheit.",
        "That concludes today's briefing. Thank you for listening, and we'll see you tomorrow with more updates."
    ]
    
    print(f"Converting {len(news_segments)} news segments...")
    
    news_files = converter.convert_batch(news_segments, "news_briefing")
    
    print(f"✅ Generated {len(news_files)} news audio segments")
    for i, file_path in enumerate(news_files, 1):
        if file_path:
            size = Path(file_path).stat().st_size / 1024
            print(f"   📻 News Segment {i}: {Path(file_path).name} ({size:.1f} KB)")
    
    converter.cleanup()
    return news_files

def demo_different_configurations():
    """Test different audio processing configurations."""
    print("\n🎛️ Configuration Comparison Demo")
    print("-" * 40)
    
    test_text = "This is a test to compare different audio processing configurations and their effects on the final output quality."
    
    configs = [
        {"name": "Basic", "settings": {"apply_fade": False, "normalize_audio": False, "noise_reduction": False}},
        {"name": "Enhanced", "settings": {"apply_fade": True, "normalize_audio": True, "noise_reduction": False}},
        {"name": "Pro", "settings": {"apply_fade": True, "normalize_audio": True, "noise_reduction": True}}
    ]
    
    results = []
    
    for config in configs:
        print(f"Testing {config['name']} configuration...")
        
        converter = TextToAudioConverter()
        converter.update_config(**config['settings'])
        
        start_time = time.time()
        output_path = converter.convert_text(test_text, f"config_test_{config['name'].lower()}")
        processing_time = time.time() - start_time
        
        if output_path:
            size = Path(output_path).stat().st_size / 1024
            results.append({
                "name": config['name'],
                "file": Path(output_path).name,
                "size_kb": size,
                "time_seconds": processing_time
            })
            print(f"   ✅ {config['name']}: {Path(output_path).name} ({size:.1f} KB, {processing_time:.2f}s)")
        
        converter.cleanup()
    
    print("\n📊 Configuration Comparison Results:")
    for result in results:
        print(f"   🎵 {result['name']}: {result['file']} - {result['size_kb']:.1f} KB - {result['time_seconds']:.2f}s")
    
    return results

def demo_performance_test():
    """Test system performance with various text lengths."""
    print("\n⚡ Performance Testing")
    print("-" * 40)
    
    test_cases = [
        {"name": "Short", "text": "Hello world!", "expected_duration": 1},
        {"name": "Medium", "text": "This is a medium-length sentence that should take a moderate amount of time to process and convert into speech audio.", "expected_duration": 5},
        {"name": "Long", "text": "This is a comprehensive test of the text-to-speech system's ability to handle longer passages of text. The system should maintain consistent quality throughout the entire conversion process, properly handling punctuation, sentence breaks, and maintaining natural speech patterns. This longer text will help us evaluate the system's performance and reliability with extended content.", "expected_duration": 15}
    ]
    
    converter = TextToAudioConverter()
    performance_results = []
    
    for test_case in test_cases:
        print(f"Testing {test_case['name']} text ({len(test_case['text'])} chars)...")
        
        start_time = time.time()
        output_path = converter.convert_text(test_case['text'], f"perf_{test_case['name'].lower()}")
        processing_time = time.time() - start_time
        
        if output_path:
            size = Path(output_path).stat().st_size / 1024
            words = len(test_case['text'].split())
            
            result = {
                "name": test_case['name'],
                "chars": len(test_case['text']),
                "words": words,
                "processing_time": processing_time,
                "size_kb": size,
                "words_per_second": words / processing_time if processing_time > 0 else 0
            }
            
            performance_results.append(result)
            print(f"   ✅ {test_case['name']}: {words} words, {processing_time:.2f}s, {result['words_per_second']:.1f} words/sec")
    
    converter.cleanup()
    
    print("\n📈 Performance Summary:")
    avg_wps = sum(r['words_per_second'] for r in performance_results) / len(performance_results)
    print(f"   Average processing speed: {avg_wps:.1f} words per second")
    
    return performance_results

def main():
    """Run all advanced demos."""
    print("🚀 Advanced Text-to-Audio Features Demo")
    print("=" * 50)
    
    start_time = time.time()
    
    # Run all demos
    educational_files = demo_educational_content()
    news_files = demo_news_briefing()
    config_results = demo_different_configurations()
    perf_results = demo_performance_test()
    
    total_time = time.time() - start_time
    
    # Final summary
    print("\n" + "=" * 50)
    print("🎉 Advanced Demo Summary")
    print(f"⏱️  Total demo time: {total_time:.2f} seconds")
    print(f"📚 Educational files: {len(educational_files)} generated")
    print(f"📰 News files: {len(news_files)} generated")
    print(f"🎛️  Configuration tests: {len(config_results)} completed")
    print(f"⚡ Performance tests: {len(perf_results)} completed")
    
    # Count total files generated
    output_dir = Path("output")
    if output_dir.exists():
        all_files = list(output_dir.glob("*.wav"))
        total_size = sum(f.stat().st_size for f in all_files) / 1024
        print(f"💾 Total audio files in this session: {len(all_files)}")
        print(f"📦 Total size: {total_size:.1f} KB")
    
    print("\n✨ All advanced features demonstrated successfully!")

if __name__ == "__main__":
    main()