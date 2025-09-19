"""
Fine-tuning utilities for text-to-image models
This module provides functionality to fine-tune pre-trained models on custom datasets.
"""

import os
import torch
import torch.nn.functional as F
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from diffusers import DDPMScheduler, UNet2DConditionModel
from transformers import CLIPTextModel, CLIPTokenizer
from accelerate import Accelerator
from tqdm.auto import tqdm
import wandb
from datetime import datetime
import json

from config import FINE_TUNE_CONFIG, MODELS
from dataset import TextImageDataset, create_data_loader, DatasetCreator
from tokenizer import TextProcessor

class TextToImageFineTuner:
    """Class for fine-tuning text-to-image models"""
    
    def __init__(self, model_name="small_stable_diffusion", output_dir="outputs/models"):
        """
        Initialize the fine-tuner
        
        Args:
            model_name (str): Name of the base model to fine-tune
            output_dir (str): Directory to save fine-tuned models
        """
        self.model_name = model_name
        self.model_config = MODELS[model_name]
        self.output_dir = output_dir
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize accelerator for distributed training
        self.accelerator = Accelerator(
            gradient_accumulation_steps=FINE_TUNE_CONFIG["gradient_accumulation_steps"],
            mixed_precision="fp16" if torch.cuda.is_available() else "no"
        )
        
        # Models will be loaded during training
        self.unet = None
        self.text_encoder = None
        self.tokenizer = None
        self.noise_scheduler = None
        
        print(f"🎯 Initializing fine-tuner for {model_name}")
        print(f"🖥️  Device: {self.device}")
        print(f"📁 Output directory: {output_dir}")
    
    def load_models(self):
        """Load the models for fine-tuning"""
        try:
            print("📥 Loading models for fine-tuning...")
            
            # Load tokenizer
            self.tokenizer = CLIPTokenizer.from_pretrained(
                self.model_config["name"], 
                subfolder="tokenizer"
            )
            
            # Load text encoder
            self.text_encoder = CLIPTextModel.from_pretrained(
                self.model_config["name"], 
                subfolder="text_encoder"
            )
            
            # Load UNet
            self.unet = UNet2DConditionModel.from_pretrained(
                self.model_config["name"], 
                subfolder="unet"
            )
            
            # Load noise scheduler
            self.noise_scheduler = DDPMScheduler.from_pretrained(
                self.model_config["name"], 
                subfolder="scheduler"
            )
            
            # Freeze text encoder to save memory
            self.text_encoder.requires_grad_(False)
            
            print("✅ Models loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            raise
    
    def prepare_dataset(self, train_csv=None, val_csv=None, create_sample=True):
        """
        Prepare training and validation datasets
        
        Args:
            train_csv (str): Path to training CSV file
            val_csv (str): Path to validation CSV file
            create_sample (bool): Whether to create sample data if files don't exist
            
        Returns:
            tuple: (train_dataloader, val_dataloader)
        """
        print("📊 Preparing dataset...")
        
        # Create sample dataset if needed
        if create_sample and (not train_csv or not os.path.exists(train_csv)):
            creator = DatasetCreator()
            train_csv, val_csv = creator.create_sample_dataset()
        
        # Initialize text processor
        text_processor = TextProcessor()
        
        # Create datasets
        train_dataset = TextImageDataset(
            data_file=train_csv,
            image_dir=os.path.dirname(train_csv),
            tokenizer=text_processor,
            image_size=FINE_TUNE_CONFIG["resolution"],
            split="train"
        )
        
        val_dataset = TextImageDataset(
            data_file=val_csv,
            image_dir=os.path.dirname(val_csv),
            tokenizer=text_processor,
            image_size=FINE_TUNE_CONFIG["resolution"],
            split="validation"
        ) if val_csv and os.path.exists(val_csv) else None
        
        # Create data loaders
        train_dataloader = create_data_loader(
            train_dataset,
            batch_size=FINE_TUNE_CONFIG["batch_size"],
            shuffle=True
        )
        
        val_dataloader = create_data_loader(
            val_dataset,
            batch_size=FINE_TUNE_CONFIG["batch_size"],
            shuffle=False
        ) if val_dataset else None
        
        print(f"📈 Training samples: {len(train_dataset)}")
        if val_dataset:
            print(f"📉 Validation samples: {len(val_dataset)}")
        
        return train_dataloader, val_dataloader
    
    def train(self, train_dataloader, val_dataloader=None, num_epochs=None, learning_rate=None):
        """
        Fine-tune the model
        
        Args:
            train_dataloader: Training data loader
            val_dataloader: Validation data loader (optional)
            num_epochs (int): Number of training epochs
            learning_rate (float): Learning rate
        """
        if self.unet is None:
            self.load_models()
        
        num_epochs = num_epochs or FINE_TUNE_CONFIG["num_epochs"]
        learning_rate = learning_rate or FINE_TUNE_CONFIG["learning_rate"]
        
        print(f"🚀 Starting fine-tuning...")
        print(f"📊 Epochs: {num_epochs}")
        print(f"📈 Learning rate: {learning_rate}")
        print(f"🔄 Batch size: {FINE_TUNE_CONFIG['batch_size']}")
        
        # Setup optimizer
        optimizer = AdamW(
            self.unet.parameters(),
            lr=learning_rate,
            betas=(0.9, 0.999),
            weight_decay=0.01,
            eps=1e-8
        )
        
        # Setup scheduler
        lr_scheduler = CosineAnnealingLR(
            optimizer,
            T_max=num_epochs * len(train_dataloader)
        )
        
        # Prepare for accelerated training
        self.unet, optimizer, train_dataloader, lr_scheduler = self.accelerator.prepare(
            self.unet, optimizer, train_dataloader, lr_scheduler
        )
        
        if val_dataloader:
            val_dataloader = self.accelerator.prepare(val_dataloader)
        
        # Move models to device
        self.text_encoder = self.text_encoder.to(self.accelerator.device)
        self.noise_scheduler = self.noise_scheduler.to(self.accelerator.device)
        
        # Training loop
        global_step = 0
        
        for epoch in range(num_epochs):
            print(f"\n🔄 Epoch {epoch + 1}/{num_epochs}")
            
            # Training phase
            self.unet.train()
            train_loss = 0.0
            
            progress_bar = tqdm(
                train_dataloader,
                desc=f"Training Epoch {epoch + 1}",
                disable=not self.accelerator.is_local_main_process
            )
            
            for step, batch in enumerate(progress_bar):
                with self.accelerator.accumulate(self.unet):
                    # Get text embeddings
                    with torch.no_grad():
                        text_embeddings = self.text_encoder(batch["input_ids"])[0]
                    
                    # Get images
                    clean_images = batch["image"]
                    
                    # Sample noise
                    noise = torch.randn_like(clean_images)
                    
                    # Sample random timesteps
                    timesteps = torch.randint(
                        0, self.noise_scheduler.config.num_train_timesteps,
                        (clean_images.shape[0],),
                        device=clean_images.device
                    ).long()
                    
                    # Add noise to images
                    noisy_images = self.noise_scheduler.add_noise(clean_images, noise, timesteps)
                    
                    # Predict noise
                    noise_pred = self.unet(noisy_images, timesteps, text_embeddings).sample
                    
                    # Calculate loss
                    loss = F.mse_loss(noise_pred, noise, reduction="mean")
                    
                    # Backward pass
                    self.accelerator.backward(loss)
                    
                    if self.accelerator.sync_gradients:
                        self.accelerator.clip_grad_norm_(self.unet.parameters(), 1.0)
                    
                    optimizer.step()
                    lr_scheduler.step()
                    optimizer.zero_grad()
                
                # Update metrics
                train_loss += loss.detach().item()
                global_step += 1
                
                # Update progress bar
                progress_bar.set_postfix({
                    "loss": f"{loss.detach().item():.4f}",
                    "lr": f"{lr_scheduler.get_last_lr()[0]:.6f}"
                })
                
                # Save checkpoint
                if global_step % FINE_TUNE_CONFIG["save_steps"] == 0:
                    self.save_checkpoint(global_step)
                
                # Validation
                if val_dataloader and global_step % FINE_TUNE_CONFIG["validation_steps"] == 0:
                    val_loss = self.validate(val_dataloader)
                    print(f"📊 Validation loss: {val_loss:.4f}")
            
            # End of epoch metrics
            avg_train_loss = train_loss / len(train_dataloader)
            print(f"📈 Average training loss: {avg_train_loss:.4f}")
            
            # Save epoch checkpoint
            self.save_checkpoint(f"epoch_{epoch + 1}")
        
        print("✅ Fine-tuning completed!")
    
    def validate(self, val_dataloader):
        """
        Validate the model
        
        Args:
            val_dataloader: Validation data loader
            
        Returns:
            float: Average validation loss
        """
        self.unet.eval()
        val_loss = 0.0
        
        with torch.no_grad():
            for batch in val_dataloader:
                # Get text embeddings
                text_embeddings = self.text_encoder(batch["input_ids"])[0]
                
                # Get images
                clean_images = batch["image"]
                
                # Sample noise and timesteps
                noise = torch.randn_like(clean_images)
                timesteps = torch.randint(
                    0, self.noise_scheduler.config.num_train_timesteps,
                    (clean_images.shape[0],),
                    device=clean_images.device
                ).long()
                
                # Add noise and predict
                noisy_images = self.noise_scheduler.add_noise(clean_images, noise, timesteps)
                noise_pred = self.unet(noisy_images, timesteps, text_embeddings).sample
                
                # Calculate loss
                loss = F.mse_loss(noise_pred, noise, reduction="mean")
                val_loss += loss.item()
        
        self.unet.train()
        return val_loss / len(val_dataloader)
    
    def save_checkpoint(self, step):
        """
        Save model checkpoint
        
        Args:
            step: Current training step or epoch identifier
        """
        checkpoint_dir = os.path.join(self.output_dir, f"checkpoint_{step}")
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        # Save UNet
        unwrapped_unet = self.accelerator.unwrap_model(self.unet)
        unwrapped_unet.save_pretrained(checkpoint_dir)
        
        # Save training info
        training_info = {
            "step": step,
            "model_name": self.model_name,
            "config": FINE_TUNE_CONFIG,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(os.path.join(checkpoint_dir, "training_info.json"), "w") as f:
            json.dump(training_info, f, indent=2)
        
        print(f"💾 Checkpoint saved: {checkpoint_dir}")
    
    def load_checkpoint(self, checkpoint_path):
        """
        Load a saved checkpoint
        
        Args:
            checkpoint_path (str): Path to the checkpoint directory
        """
        print(f"📥 Loading checkpoint: {checkpoint_path}")
        
        # Load UNet
        self.unet = UNet2DConditionModel.from_pretrained(checkpoint_path)
        
        # Load training info
        info_path = os.path.join(checkpoint_path, "training_info.json")
        if os.path.exists(info_path):
            with open(info_path, "r") as f:
                training_info = json.load(f)
                print(f"📊 Checkpoint info: {training_info}")
        
        print("✅ Checkpoint loaded successfully!")


def main():
    """Example fine-tuning workflow"""
    print("🧪 Testing fine-tuning pipeline...")
    
    # Initialize fine-tuner
    fine_tuner = TextToImageFineTuner()
    
    # Prepare dataset
    train_dataloader, val_dataloader = fine_tuner.prepare_dataset()
    
    # Start fine-tuning (with very few epochs for testing)
    fine_tuner.train(
        train_dataloader=train_dataloader,
        val_dataloader=val_dataloader,
        num_epochs=2,  # Very short for testing
        learning_rate=1e-5
    )
    
    print("✅ Fine-tuning test completed!")


if __name__ == "__main__":
    main()