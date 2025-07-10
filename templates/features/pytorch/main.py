"""PyTorch deep learning template with training pipeline and best practices."""

from __future__ import annotations

import logging
import random
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torch.utils.tensorboard import SummaryWriter

__version__ = "0.1.0"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set random seeds for reproducibility
def set_seed(seed: int = 42) -> None:
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    logger.info(f"Random seed set to {seed}")


class SampleDataset(Dataset):
    """Sample dataset for demonstration purposes."""
    
    def __init__(self, num_samples: int = 1000, input_dim: int = 10, num_classes: int = 3):
        """Initialize the sample dataset.
        
        Args:
            num_samples: Number of samples to generate
            input_dim: Dimension of input features
            num_classes: Number of output classes
        """
        self.num_samples = num_samples
        self.input_dim = input_dim
        self.num_classes = num_classes
        
        # Generate random data
        self.X = torch.randn(num_samples, input_dim)
        # Create labels with some structure (not completely random)
        weights = torch.randn(input_dim, num_classes)
        logits = torch.mm(self.X, weights)
        self.y = torch.argmax(logits, dim=1)
        
        logger.info(f"Generated dataset with {num_samples} samples, {input_dim} features, {num_classes} classes")
    
    def __len__(self) -> int:
        return self.num_samples
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.X[idx], self.y[idx]


class SimpleNN(nn.Module):
    """Simple neural network for classification."""
    
    def __init__(self, input_dim: int, hidden_dims: list[int], num_classes: int, dropout: float = 0.2):
        """Initialize the neural network.
        
        Args:
            input_dim: Input feature dimension
            hidden_dims: List of hidden layer dimensions
            num_classes: Number of output classes
            dropout: Dropout probability
        """
        super().__init__()
        
        layers = []
        current_dim = input_dim
        
        # Build hidden layers
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(current_dim, hidden_dim),
                nn.ReLU(),
                nn.BatchNorm1d(hidden_dim),
                nn.Dropout(dropout)
            ])
            current_dim = hidden_dim
        
        # Output layer
        layers.append(nn.Linear(current_dim, num_classes))
        
        self.network = nn.Sequential(*layers)
        self.input_dim = input_dim
        self.num_classes = num_classes
        
        # Initialize weights
        self.apply(self._init_weights)
        
        logger.info(f"Created neural network: {input_dim} -> {' -> '.join(map(str, hidden_dims))} -> {num_classes}")
    
    def _init_weights(self, module: nn.Module) -> None:
        """Initialize weights using Xavier initialization."""
        if isinstance(module, nn.Linear):
            nn.init.xavier_uniform_(module.weight)
            nn.init.constant_(module.bias, 0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the network."""
        return self.network(x)


class Trainer:
    """Training class with logging and checkpointing."""
    
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        optimizer: optim.Optimizer,
        criterion: nn.Module,
        device: torch.device,
        log_dir: str = "runs"
    ):
        """Initialize the trainer.
        
        Args:
            model: PyTorch model to train
            train_loader: Training data loader
            val_loader: Validation data loader
            optimizer: Optimizer for training
            criterion: Loss function
            device: Device to train on
            log_dir: Directory for tensorboard logs
        """
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.optimizer = optimizer
        self.criterion = criterion
        self.device = device
        
        # Create directories
        self.checkpoint_dir = Path("checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.writer = SummaryWriter(log_dir)
        self.best_val_loss = float('inf')
        
        logger.info(f"Trainer initialized on device: {device}")
    
    def train_epoch(self, epoch: int) -> Dict[str, float]:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, (data, target) in enumerate(self.train_loader):
            data, target = data.to(self.device), target.to(self.device)
            
            # Zero gradients
            self.optimizer.zero_grad()
            
            # Forward pass
            output = self.model(data)
            loss = self.criterion(output, target)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            # Statistics
            total_loss += loss.item()
            pred = output.argmax(dim=1)
            correct += pred.eq(target).sum().item()
            total += target.size(0)
            
            # Log every 100 batches
            if batch_idx % 100 == 0:
                logger.info(f"Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item():.4f}")
        
        avg_loss = total_loss / len(self.train_loader)
        accuracy = 100.0 * correct / total
        
        return {"loss": avg_loss, "accuracy": accuracy}
    
    def validate(self) -> Dict[str, float]:
        """Validate the model."""
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, target in self.val_loader:
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                total_loss += self.criterion(output, target).item()
                
                pred = output.argmax(dim=1)
                correct += pred.eq(target).sum().item()
                total += target.size(0)
        
        avg_loss = total_loss / len(self.val_loader)
        accuracy = 100.0 * correct / total
        
        return {"loss": avg_loss, "accuracy": accuracy}
    
    def save_checkpoint(self, epoch: int, val_loss: float, is_best: bool = False) -> None:
        """Save model checkpoint."""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'val_loss': val_loss
        }
        
        # Save regular checkpoint
        checkpoint_path = self.checkpoint_dir / f"checkpoint_epoch_{epoch}.pth"
        torch.save(checkpoint, checkpoint_path)
        
        # Save best model
        if is_best:
            best_path = self.checkpoint_dir / "best_model.pth"
            torch.save(checkpoint, best_path)
            logger.info(f"Saved best model with validation loss: {val_loss:.4f}")
    
    def train(self, num_epochs: int) -> None:
        """Train the model for specified number of epochs."""
        logger.info(f"Starting training for {num_epochs} epochs")
        
        for epoch in range(1, num_epochs + 1):
            # Train
            train_metrics = self.train_epoch(epoch)
            
            # Validate
            val_metrics = self.validate()
            
            # Log metrics
            self.writer.add_scalar('Loss/Train', train_metrics['loss'], epoch)
            self.writer.add_scalar('Loss/Validation', val_metrics['loss'], epoch)
            self.writer.add_scalar('Accuracy/Train', train_metrics['accuracy'], epoch)
            self.writer.add_scalar('Accuracy/Validation', val_metrics['accuracy'], epoch)
            
            # Print progress
            logger.info(
                f"Epoch {epoch:3d} | "
                f"Train Loss: {train_metrics['loss']:.4f} | "
                f"Train Acc: {train_metrics['accuracy']:.2f}% | "
                f"Val Loss: {val_metrics['loss']:.4f} | "
                f"Val Acc: {val_metrics['accuracy']:.2f}%"
            )
            
            # Save checkpoint
            is_best = val_metrics['loss'] < self.best_val_loss
            if is_best:
                self.best_val_loss = val_metrics['loss']
            
            self.save_checkpoint(epoch, val_metrics['loss'], is_best)
        
        self.writer.close()
        logger.info("Training completed!")


def main() -> None:
    """Main training pipeline."""
    print(f"PyTorch Deep Learning Template (version {__version__})")
    print(f"PyTorch version: {torch.__version__}")
    
    # Set random seed
    set_seed(42)
    
    # Device configuration
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    if torch.cuda.is_available():
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
    
    # Hyperparameters
    config = {
        'batch_size': 64,
        'learning_rate': 0.001,
        'num_epochs': 10,
        'input_dim': 20,
        'hidden_dims': [128, 64, 32],
        'num_classes': 3,
        'dropout': 0.2,
        'train_size': 8000,
        'val_size': 2000
    }
    
    print("\nConfiguration:")
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    # Create datasets
    print("\nCreating datasets...")
    train_dataset = SampleDataset(config['train_size'], config['input_dim'], config['num_classes'])
    val_dataset = SampleDataset(config['val_size'], config['input_dim'], config['num_classes'])
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=config['batch_size'], shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=config['batch_size'], shuffle=False)
    
    # Create model
    print("\nCreating model...")
    model = SimpleNN(
        input_dim=config['input_dim'],
        hidden_dims=config['hidden_dims'],
        num_classes=config['num_classes'],
        dropout=config['dropout']
    )
    
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"Trainable parameters: {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")
    
    # Create optimizer and loss function
    optimizer = optim.Adam(model.parameters(), lr=config['learning_rate'])
    criterion = nn.CrossEntropyLoss()
    
    # Create trainer and start training
    print("\nStarting training...")
    trainer = Trainer(model, train_loader, val_loader, optimizer, criterion, device)
    trainer.train(config['num_epochs'])
    
    print("\nTraining completed! Check the generated files:")
    print("   - checkpoints/ - Model checkpoints")
    print("   - runs/ - TensorBoard logs")
    print("\nNext steps:")
    print("   - Run 'tensorboard --logdir=runs' to view training progress")
    print("   - Load the best model from checkpoints/best_model.pth")
    print("   - Modify the model architecture and hyperparameters")


if __name__ == "__main__":
    main()
