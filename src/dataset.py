"""
Dataset utilities for fine-tuning text-to-image models
This module provides tools for creating and managing training datasets.
"""

import os
import json
import torch
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import requests
from io import BytesIO
import csv

from config import FINE_TUNE_CONFIG
from tokenizer import TextProcessor

class TextImageDataset(Dataset):
    """Dataset class for text-image pairs"""
    
    def __init__(self, data_file, image_dir, tokenizer, image_size=512, split="train"):
        """
        Initialize the dataset
        
        Args:
            data_file (str): Path to the CSV file with text-image pairs
            image_dir (str): Directory containing images
            tokenizer: Text tokenizer
            image_size (int): Size to resize images to
            split (str): Dataset split (train/validation)
        """
        self.data_file = data_file
        self.image_dir = image_dir
        self.tokenizer = tokenizer
        self.image_size = image_size
        self.split = split
        
        # Load data
        self.data = self.load_data()
        
        # Image transformations
        self.image_transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.CenterCrop(image_size) if FINE_TUNE_CONFIG["center_crop"] else transforms.Lambda(lambda x: x),
            transforms.RandomHorizontalFlip() if FINE_TUNE_CONFIG["random_flip"] and split == "train" else transforms.Lambda(lambda x: x),
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5])  # Normalize to [-1, 1]
        ])
    
    def load_data(self):
        """Load data from CSV file"""
        data = []
        
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append({
                        'text': row['text'],
                        'image_path': row['image_path']
                    })
        
        return data
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        """Get a single item from the dataset"""
        item = self.data[idx]
        
        # Load and process image
        image_path = os.path.join(self.image_dir, item['image_path'])
        
        try:
            image = Image.open(image_path).convert('RGB')
            image = self.image_transform(image)
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            # Return a black image as fallback
            image = torch.zeros(3, self.image_size, self.image_size)
        
        # Process text
        text = item['text']
        tokens = self.tokenizer.tokenize_text(text)
        
        return {
            'image': image,
            'text': text,
            'input_ids': tokens['input_ids'].squeeze(),
            'attention_mask': tokens['attention_mask'].squeeze()
        }


class DatasetCreator:
    """Helper class to create training datasets"""
    
    def __init__(self, base_dir="data"):
        """
        Initialize dataset creator
        
        Args:
            base_dir (str): Base directory for data
        """
        self.base_dir = base_dir
        self.train_dir = os.path.join(base_dir, "train")
        self.val_dir = os.path.join(base_dir, "validation")
        
        # Create directories
        os.makedirs(self.train_dir, exist_ok=True)
        os.makedirs(self.val_dir, exist_ok=True)
    
    def create_sample_dataset(self):
        """Create a minimal sample dataset for testing"""
        print("📁 Creating sample dataset...")
        
        # Define sample data
        sample_data = [
            {
                "text": "a cute dog playing in the park",
                "description": "Sample dog image for training",
                "category": "animal"
            },
            {
                "text": "a professional portrait of a human",
                "description": "Sample human portrait for training", 
                "category": "human"
            },
            {
                "text": "a beautiful landscape with mountains",
                "description": "Sample landscape for training",
                "category": "landscape"
            },
            {
                "text": "a modern car on the street",
                "description": "Sample car image for training",
                "category": "vehicle"
            }
        ]
        
        # Create train CSV
        train_csv_path = os.path.join(self.train_dir, "dataset.csv")
        with open(train_csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['text', 'image_path', 'category'])
            
            for i, item in enumerate(sample_data):
                image_name = f"sample_{i+1}.jpg"
                writer.writerow([item['text'], image_name, item['category']])
        
        # Create validation CSV (smaller subset)
        val_csv_path = os.path.join(self.val_dir, "dataset.csv")
        with open(val_csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['text', 'image_path', 'category'])
            
            # Use first 2 items for validation
            for i in range(2):
                item = sample_data[i]
                image_name = f"sample_{i+1}.jpg"
                writer.writerow([item['text'], image_name, item['category']])
        
        # Create placeholder images (since we don't have real images)
        self.create_placeholder_images()
        
        print("✅ Sample dataset created!")
        print(f"📂 Training data: {train_csv_path}")
        print(f"📂 Validation data: {val_csv_path}")
        
        return train_csv_path, val_csv_path
    
    def create_placeholder_images(self):
        """Create placeholder images for the sample dataset"""
        from PIL import Image, ImageDraw, ImageFont
        
        # Define placeholder data
        placeholders = [
            {"name": "sample_1.jpg", "text": "DOG", "color": (255, 200, 200)},
            {"name": "sample_2.jpg", "text": "HUMAN", "color": (200, 255, 200)},
            {"name": "sample_3.jpg", "text": "LANDSCAPE", "color": (200, 200, 255)},
            {"name": "sample_4.jpg", "text": "CAR", "color": (255, 255, 200)}
        ]
        
        for placeholder in placeholders:
            # Create image for training
            img = Image.new('RGB', (512, 512), placeholder["color"])
            draw = ImageDraw.Draw(img)
            
            # Add text
            try:
                # Try to use a system font
                font = ImageFont.truetype("arial.ttf", 60)
            except:
                # Fallback to default font
                font = ImageFont.load_default()
            
            # Get text size and center it
            bbox = draw.textbbox((0, 0), placeholder["text"], font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (512 - text_width) // 2
            y = (512 - text_height) // 2
            
            draw.text((x, y), placeholder["text"], fill=(0, 0, 0), font=font)
            
            # Save to both train and validation directories
            train_path = os.path.join(self.train_dir, placeholder["name"])
            val_path = os.path.join(self.val_dir, placeholder["name"])
            
            img.save(train_path)
            if placeholder["name"] in ["sample_1.jpg", "sample_2.jpg"]:  # Only first 2 for validation
                img.save(val_path)
    
    def add_custom_data(self, text_prompt, image_path, split="train"):
        """
        Add custom text-image pair to the dataset
        
        Args:
            text_prompt (str): Text description
            image_path (str): Path to the image file
            split (str): Dataset split (train/validation)
        """
        csv_file = os.path.join(self.train_dir if split == "train" else self.val_dir, "dataset.csv")
        
        # Get next image name
        existing_data = []
        if os.path.exists(csv_file):
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                existing_data = list(reader)
        
        next_id = len(existing_data) + 1
        image_name = f"custom_{next_id}.jpg"
        
        # Copy image to dataset directory
        import shutil
        target_dir = self.train_dir if split == "train" else self.val_dir
        target_path = os.path.join(target_dir, image_name)
        shutil.copy2(image_path, target_path)
        
        # Add to CSV
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not existing_data:  # Write header if file is new
                writer.writerow(['text', 'image_path', 'category'])
            writer.writerow([text_prompt, image_name, 'custom'])
        
        print(f"✅ Added custom data: '{text_prompt}' -> {image_name}")


def create_data_loader(dataset, batch_size=None, shuffle=True, num_workers=0):
    """
    Create a DataLoader for the dataset
    
    Args:
        dataset: TextImageDataset instance
        batch_size (int): Batch size for training
        shuffle (bool): Whether to shuffle the data
        num_workers (int): Number of worker processes
        
    Returns:
        DataLoader: PyTorch DataLoader
    """
    if batch_size is None:
        batch_size = FINE_TUNE_CONFIG["batch_size"]
    
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )


def main():
    """Test dataset creation"""
    print("🧪 Testing dataset creation...")
    
    # Create dataset
    creator = DatasetCreator()
    train_csv, val_csv = creator.create_sample_dataset()
    
    # Test loading
    processor = TextProcessor()
    
    # Create datasets
    train_dataset = TextImageDataset(
        data_file=train_csv,
        image_dir=os.path.dirname(train_csv),
        tokenizer=processor,
        split="train"
    )
    
    val_dataset = TextImageDataset(
        data_file=val_csv,
        image_dir=os.path.dirname(val_csv),
        tokenizer=processor,
        split="validation"
    )
    
    print(f"📊 Training samples: {len(train_dataset)}")
    print(f"📊 Validation samples: {len(val_dataset)}")
    
    # Test data loading
    if len(train_dataset) > 0:
        sample = train_dataset[0]
        print(f"🔍 Sample data shapes:")
        print(f"   Image: {sample['image'].shape}")
        print(f"   Text: '{sample['text']}'")
        print(f"   Tokens: {sample['input_ids'].shape}")


if __name__ == "__main__":
    main()