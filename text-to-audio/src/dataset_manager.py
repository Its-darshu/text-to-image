"""
Training Dataset Support Module

This module provides integration with common TTS datasets for model training
and fine-tuning, including LJSpeech, LibriTTS, and custom datasets.
"""

import os
import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
from datasets import Dataset, DatasetDict, load_dataset
import torchaudio
import torch
import numpy as np
import logging
from urllib.request import urlopen
import tarfile
import zipfile
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatasetManager:
    """
    Manages TTS datasets for training and evaluation.
    
    Supported datasets:
    - LJSpeech Dataset
    - LibriTTS
    - Common Voice
    - Custom datasets
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the dataset manager.
        
        Args:
            data_dir: Directory to store datasets
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Dataset configurations
        self.dataset_configs = {
            "ljspeech": {
                "name": "LJSpeech-1.1",
                "url": "https://data.keithito.com/data/speech/LJSpeech-1.1.tar.bz2",
                "type": "single_speaker",
                "sample_rate": 22050,
                "language": "en",
                "size": "~2.6GB"
            },
            "libritts": {
                "name": "LibriTTS",
                "hf_dataset": "parler-tts/libritts_r_filtered",
                "type": "multi_speaker",
                "sample_rate": 24000,
                "language": "en",
                "size": "Large"
            },
            "common_voice": {
                "name": "Common Voice",
                "hf_dataset": "mozilla-foundation/common_voice_13_0",
                "type": "multi_speaker",
                "sample_rate": 48000,
                "language": "multiple",
                "size": "Very Large"
            }
        }
        
        self.loaded_datasets = {}
    
    def list_available_datasets(self) -> Dict[str, Dict[str, Any]]:
        """List all available datasets with their configurations."""
        return self.dataset_configs.copy()
    
    def download_ljspeech(self, force_download: bool = False) -> bool:
        """
        Download and extract the LJSpeech dataset.
        
        Args:
            force_download: Whether to re-download if already exists
            
        Returns:
            True if successful, False otherwise
        """
        dataset_path = self.data_dir / "LJSpeech-1.1"
        
        if dataset_path.exists() and not force_download:
            logger.info("LJSpeech dataset already exists")
            return True
        
        try:
            logger.info("Downloading LJSpeech dataset...")
            
            # Download using Hugging Face datasets (easier and more reliable)
            dataset = load_dataset("lj_speech", split="train")
            
            # Create directory structure
            dataset_path.mkdir(parents=True, exist_ok=True)
            wavs_dir = dataset_path / "wavs"
            wavs_dir.mkdir(exist_ok=True)
            
            # Save metadata
            metadata_path = dataset_path / "metadata.csv"
            
            with open(metadata_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter='|')
                
                for i, item in enumerate(dataset):
                    # Save audio file
                    audio_data = item['audio']['array']
                    sample_rate = item['audio']['sampling_rate']
                    
                    audio_filename = f"LJ{i+1:03d}-{i+1:04d}.wav"
                    audio_path = wavs_dir / audio_filename
                    
                    # Convert to tensor and save
                    audio_tensor = torch.tensor(audio_data, dtype=torch.float32)
                    torchaudio.save(str(audio_path), audio_tensor.unsqueeze(0), sample_rate)
                    
                    # Write metadata
                    normalized_text = item['normalized_text']
                    writer.writerow([audio_filename.replace('.wav', ''), normalized_text, normalized_text])
                    
                    if (i + 1) % 100 == 0:
                        logger.info(f"Processed {i + 1} audio files")
            
            logger.info(f"LJSpeech dataset downloaded and saved to {dataset_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download LJSpeech dataset: {e}")
            return False
    
    def load_ljspeech(self, max_samples: Optional[int] = None) -> Optional[Dataset]:
        """
        Load the LJSpeech dataset.
        
        Args:
            max_samples: Maximum number of samples to load (None for all)
            
        Returns:
            Loaded dataset or None if failed
        """
        try:
            logger.info("Loading LJSpeech dataset...")
            
            # Load from Hugging Face for simplicity
            dataset = load_dataset("lj_speech", split="train")
            
            if max_samples:
                dataset = dataset.select(range(min(max_samples, len(dataset))))
                logger.info(f"Limited dataset to {max_samples} samples")
            
            self.loaded_datasets['ljspeech'] = dataset
            logger.info(f"Loaded LJSpeech dataset with {len(dataset)} samples")
            
            return dataset
            
        except Exception as e:
            logger.error(f"Failed to load LJSpeech dataset: {e}")
            return None
    
    def load_libritts(
        self, 
        subset: str = "train-clean-100", 
        max_samples: Optional[int] = None
    ) -> Optional[Dataset]:
        """
        Load the LibriTTS dataset.
        
        Args:
            subset: Dataset subset to load
            max_samples: Maximum number of samples to load
            
        Returns:
            Loaded dataset or None if failed
        """
        try:
            logger.info(f"Loading LibriTTS dataset (subset: {subset})...")
            
            # Load smaller subset for demonstration
            dataset = load_dataset("parler-tts/libritts_r_filtered", subset, split="train")
            
            if max_samples:
                dataset = dataset.select(range(min(max_samples, len(dataset))))
            
            self.loaded_datasets['libritts'] = dataset
            logger.info(f"Loaded LibriTTS dataset with {len(dataset)} samples")
            
            return dataset
            
        except Exception as e:
            logger.error(f"Failed to load LibriTTS dataset: {e}")
            return None
    
    def create_custom_dataset(
        self,
        audio_dir: str,
        text_file: str,
        dataset_name: str = "custom",
        audio_format: str = "wav"
    ) -> Optional[Dataset]:
        """
        Create a dataset from custom audio files and text.
        
        Args:
            audio_dir: Directory containing audio files
            text_file: Path to text file (CSV or JSON format)
            dataset_name: Name for the custom dataset
            audio_format: Audio file format
            
        Returns:
            Created dataset or None if failed
        """
        try:
            logger.info(f"Creating custom dataset: {dataset_name}")
            
            audio_dir = Path(audio_dir)
            if not audio_dir.exists():
                raise ValueError(f"Audio directory not found: {audio_dir}")
            
            # Load text mappings
            text_data = self._load_text_mappings(text_file)
            
            # Prepare dataset items
            dataset_items = []
            
            for audio_file, text in text_data.items():
                audio_path = audio_dir / f"{audio_file}.{audio_format}"
                
                if audio_path.exists():
                    try:
                        # Load audio
                        audio_data, sample_rate = torchaudio.load(str(audio_path))
                        
                        dataset_items.append({
                            "audio": {
                                "path": str(audio_path),
                                "array": audio_data.numpy().squeeze(),
                                "sampling_rate": sample_rate
                            },
                            "text": text,
                            "id": audio_file
                        })
                        
                    except Exception as e:
                        logger.warning(f"Failed to load audio {audio_path}: {e}")
                        continue
                else:
                    logger.warning(f"Audio file not found: {audio_path}")
            
            if not dataset_items:
                raise ValueError("No valid audio-text pairs found")
            
            # Create Hugging Face dataset
            dataset = Dataset.from_list(dataset_items)
            self.loaded_datasets[dataset_name] = dataset
            
            logger.info(f"Created custom dataset '{dataset_name}' with {len(dataset)} samples")
            return dataset
            
        except Exception as e:
            logger.error(f"Failed to create custom dataset: {e}")
            return None
    
    def _load_text_mappings(self, text_file: str) -> Dict[str, str]:
        """Load text mappings from CSV or JSON file."""
        text_path = Path(text_file)
        
        if not text_path.exists():
            raise ValueError(f"Text file not found: {text_path}")
        
        if text_path.suffix.lower() == '.csv':
            return self._load_csv_mappings(text_path)
        elif text_path.suffix.lower() == '.json':
            return self._load_json_mappings(text_path)
        else:
            raise ValueError(f"Unsupported text file format: {text_path.suffix}")
    
    def _load_csv_mappings(self, csv_path: Path) -> Dict[str, str]:
        """Load text mappings from CSV file."""
        mappings = {}
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='|')
            
            for row in reader:
                if len(row) >= 2:
                    file_id = row[0]
                    text = row[1]
                    mappings[file_id] = text
        
        return mappings
    
    def _load_json_mappings(self, json_path: Path) -> Dict[str, str]:
        """Load text mappings from JSON file."""
        with open(json_path, 'r', encoding='utf-8') as f:
            mappings = json.load(f)
        
        return mappings
    
    def get_dataset_stats(self, dataset_name: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a loaded dataset.
        
        Args:
            dataset_name: Name of the dataset
            
        Returns:
            Dictionary with dataset statistics
        """
        if dataset_name not in self.loaded_datasets:
            logger.error(f"Dataset '{dataset_name}' not loaded")
            return None
        
        dataset = self.loaded_datasets[dataset_name]
        
        try:
            # Basic stats
            stats = {
                "name": dataset_name,
                "total_samples": len(dataset),
                "columns": dataset.column_names if hasattr(dataset, 'column_names') else [],
            }
            
            # Text statistics
            if "text" in dataset[0]:
                texts = [item["text"] for item in dataset]
                word_counts = [len(text.split()) for text in texts]
                char_counts = [len(text) for text in texts]
                
                stats["text_stats"] = {
                    "avg_words": np.mean(word_counts),
                    "min_words": np.min(word_counts),
                    "max_words": np.max(word_counts),
                    "avg_chars": np.mean(char_counts),
                    "min_chars": np.min(char_counts),
                    "max_chars": np.max(char_counts),
                }
            
            # Audio statistics (sample a few items)
            if "audio" in dataset[0]:
                sample_indices = np.random.choice(
                    len(dataset), 
                    min(100, len(dataset)), 
                    replace=False
                )
                
                durations = []
                sample_rates = []
                
                for idx in sample_indices:
                    audio_info = dataset[int(idx)]["audio"]
                    if isinstance(audio_info, dict):
                        if "array" in audio_info and "sampling_rate" in audio_info:
                            duration = len(audio_info["array"]) / audio_info["sampling_rate"]
                            durations.append(duration)
                            sample_rates.append(audio_info["sampling_rate"])
                
                if durations:
                    stats["audio_stats"] = {
                        "avg_duration": np.mean(durations),
                        "min_duration": np.min(durations),
                        "max_duration": np.max(durations),
                        "total_duration": np.sum(durations) * len(dataset) / len(sample_indices),
                        "sample_rates": list(set(sample_rates)),
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to compute dataset statistics: {e}")
            return None
    
    def prepare_training_split(
        self,
        dataset_name: str,
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        test_ratio: float = 0.1,
        seed: int = 42
    ) -> Optional[DatasetDict]:
        """
        Split dataset into train/validation/test sets.
        
        Args:
            dataset_name: Name of the dataset to split
            train_ratio: Ratio for training set
            val_ratio: Ratio for validation set
            test_ratio: Ratio for test set
            seed: Random seed for reproducibility
            
        Returns:
            DatasetDict with train/val/test splits
        """
        if dataset_name not in self.loaded_datasets:
            logger.error(f"Dataset '{dataset_name}' not loaded")
            return None
        
        if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-6:
            raise ValueError("Train, validation, and test ratios must sum to 1.0")
        
        try:
            dataset = self.loaded_datasets[dataset_name]
            
            # Split dataset
            train_val_split = dataset.train_test_split(
                test_size=(val_ratio + test_ratio),
                seed=seed
            )
            
            if val_ratio > 0 and test_ratio > 0:
                val_test_ratio = test_ratio / (val_ratio + test_ratio)
                val_test_split = train_val_split["test"].train_test_split(
                    test_size=val_test_ratio,
                    seed=seed
                )
                
                dataset_dict = DatasetDict({
                    "train": train_val_split["train"],
                    "validation": val_test_split["train"],
                    "test": val_test_split["test"]
                })
            elif val_ratio > 0:
                dataset_dict = DatasetDict({
                    "train": train_val_split["train"],
                    "validation": train_val_split["test"]
                })
            else:
                dataset_dict = DatasetDict({
                    "train": train_val_split["train"],
                    "test": train_val_split["test"]
                })
            
            logger.info(f"Dataset split created:")
            for split_name, split_data in dataset_dict.items():
                logger.info(f"  {split_name}: {len(split_data)} samples")
            
            return dataset_dict
            
        except Exception as e:
            logger.error(f"Failed to split dataset: {e}")
            return None
    
    def save_dataset(self, dataset_name: str, output_path: str) -> bool:
        """
        Save a loaded dataset to disk.
        
        Args:
            dataset_name: Name of the dataset to save
            output_path: Output directory path
            
        Returns:
            True if successful, False otherwise
        """
        if dataset_name not in self.loaded_datasets:
            logger.error(f"Dataset '{dataset_name}' not loaded")
            return False
        
        try:
            dataset = self.loaded_datasets[dataset_name]
            output_path = Path(output_path)
            output_path.mkdir(parents=True, exist_ok=True)
            
            dataset.save_to_disk(str(output_path))
            logger.info(f"Dataset '{dataset_name}' saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save dataset: {e}")
            return False
    
    def load_saved_dataset(self, dataset_path: str, dataset_name: str) -> bool:
        """
        Load a previously saved dataset from disk.
        
        Args:
            dataset_path: Path to saved dataset
            dataset_name: Name to assign to loaded dataset
            
        Returns:
            True if successful, False otherwise
        """
        try:
            dataset = Dataset.load_from_disk(dataset_path)
            self.loaded_datasets[dataset_name] = dataset
            logger.info(f"Loaded dataset '{dataset_name}' from {dataset_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load dataset from {dataset_path}: {e}")
            return False


def main():
    """Example usage of the DatasetManager."""
    print("TTS Dataset Manager Demo")
    print("=" * 35)
    
    # Initialize dataset manager
    manager = DatasetManager()
    
    # List available datasets
    print("Available datasets:")
    datasets_info = manager.list_available_datasets()
    for name, info in datasets_info.items():
        print(f"  - {name}: {info['name']} ({info['size']})")
    print()
    
    # Load LJSpeech dataset (limited samples for demo)
    print("Loading LJSpeech dataset (limited to 100 samples)...")
    ljspeech_dataset = manager.load_ljspeech(max_samples=100)
    
    if ljspeech_dataset:
        print(f"✓ Loaded {len(ljspeech_dataset)} samples")
        
        # Get dataset statistics
        stats = manager.get_dataset_stats('ljspeech')
        if stats:
            print("Dataset Statistics:")
            print(f"  Total samples: {stats['total_samples']}")
            if 'text_stats' in stats:
                text_stats = stats['text_stats']
                print(f"  Average words per text: {text_stats['avg_words']:.1f}")
                print(f"  Text length range: {text_stats['min_chars']}-{text_stats['max_chars']} chars")
            if 'audio_stats' in stats:
                audio_stats = stats['audio_stats']
                print(f"  Average audio duration: {audio_stats['avg_duration']:.2f}s")
                print(f"  Sample rates: {audio_stats['sample_rates']}")
        
        # Create train/val/test splits
        print("\nCreating train/validation/test splits...")
        dataset_splits = manager.prepare_training_split('ljspeech')
        
        if dataset_splits:
            print("✓ Dataset splits created successfully")
        
        # Show sample data
        print("\nSample data:")
        sample = ljspeech_dataset[0]
        print(f"  Text: {sample['text'][:100]}...")
        if 'audio' in sample:
            audio_info = sample['audio']
            print(f"  Audio shape: {np.array(audio_info['array']).shape}")
            print(f"  Sample rate: {audio_info['sampling_rate']} Hz")
    
    print("\nDataset manager demo completed!")


if __name__ == "__main__":
    main()