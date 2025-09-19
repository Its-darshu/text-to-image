#!/usr/bin/env python3
"""
Setup script for Text-to-Image Generation Project
This script installs all required dependencies and sets up the environment.
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages from requirements.txt"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ All packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False
    return True

def create_directories():
    """Create necessary directories if they don't exist"""
    dirs = ["data/train", "data/validation", "outputs/generated", "outputs/models", "models/cache"]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✓ Created directory: {dir_path}")

def main():
    print("🚀 Setting up Text-to-Image Generation Project...")
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed during package installation")
        return
    
    # Create directories
    create_directories()
    
    print("\n✨ Setup completed successfully!")
    print("You can now run the main application with: python src/main.py")

if __name__ == "__main__":
    main()