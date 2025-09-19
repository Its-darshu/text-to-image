"""
Simple dataset creation script that doesn't require model loading
"""

import os
import sys
import csv
from PIL import Image, ImageDraw, ImageFont

def create_sample_dataset():
    """Create a minimal sample dataset for testing"""
    print("📁 Creating sample dataset...")
    
    # Create directories
    train_dir = "data/train"
    val_dir = "data/validation"
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)
    
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
    train_csv_path = os.path.join(train_dir, "dataset.csv")
    with open(train_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['text', 'image_path', 'category'])
        
        for i, item in enumerate(sample_data):
            image_name = f"sample_{i+1}.jpg"
            writer.writerow([item['text'], image_name, item['category']])
    
    # Create validation CSV (smaller subset)
    val_csv_path = os.path.join(val_dir, "dataset.csv")
    with open(val_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['text', 'image_path', 'category'])
        
        # Use first 2 items for validation
        for i in range(2):
            item = sample_data[i]
            image_name = f"sample_{i+1}.jpg"
            writer.writerow([item['text'], image_name, item['category']])
    
    # Create placeholder images
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
        try:
            bbox = draw.textbbox((0, 0), placeholder["text"], font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            # Fallback for older PIL versions
            text_width, text_height = draw.textsize(placeholder["text"], font=font)
        
        x = (512 - text_width) // 2
        y = (512 - text_height) // 2
        
        draw.text((x, y), placeholder["text"], fill=(0, 0, 0), font=font)
        
        # Save to both train and validation directories
        train_path = os.path.join(train_dir, placeholder["name"])
        val_path = os.path.join(val_dir, placeholder["name"])
        
        img.save(train_path)
        if placeholder["name"] in ["sample_1.jpg", "sample_2.jpg"]:  # Only first 2 for validation
            img.save(val_path)
    
    print("✅ Sample dataset created!")
    print(f"📂 Training data: {train_csv_path}")
    print(f"📂 Validation data: {val_csv_path}")
    
    return train_csv_path, val_csv_path

if __name__ == "__main__":
    create_sample_dataset()