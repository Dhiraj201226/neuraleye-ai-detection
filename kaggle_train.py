import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
from tqdm import tqdm

# ==============================================================================
# KAGGLE TRAINING SCRIPT - DEEPFAKE / AI IMAGE DETECTION
# ==============================================================================
# Instructions for Kaggle:
# 1. Turn on the GPU (P100 or T4x2) in the Kaggle Notebook settings on the right.
# 2. Add the "ArtiFact" or "GenImage" dataset to your Kaggle Notebook via "Add Data".
# 3. Update the DATA_DIR variable below to point to the dataset directory.
#    (Usually it looks like "/kaggle/input/artifact-dataset/...")
# 4. Run this script! Once finished, it will save `deepfake_model.pth`.
#    Download this file and we will load it in your FastAPI backend!
# ==============================================================================

# --- CONFIGURATION ---
# Change this path to where your Kaggle dataset is located.
# The dataset should have subfolders for classes, e.g., DATA_DIR/real and DATA_DIR/fake
DATA_DIR = "/kaggle/input/datasets/birdy654/cifake-real-and-ai-generated-synthetic-images/train"
TEST_DIR = "/kaggle/input/datasets/birdy654/cifake-real-and-ai-generated-synthetic-images/test" # Optional, if you have a val split

BATCH_SIZE = 32
EPOCHS = 10
LEARNING_RATE = 0.0001
NUM_CLASSES = 2 # Real (0) and Fake/AI (1)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# --- DATA TRANSFORMS ---
# For high-res images, we resize to 224x224 which is standard for pretrained models.
# Data augmentation helps prevent overfitting.
data_transforms = {
    'train': transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'val': transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
}

def main():
    if not os.path.exists(DATA_DIR):
        print(f"ERROR: Data directory {DATA_DIR} not found. Please update the path.")
        return

    # --- LOAD DATASET ---
    train_dataset = datasets.ImageFolder(DATA_DIR, transform=data_transforms['train'])
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=2)
    
    val_loader = None
    if os.path.exists(TEST_DIR):
        val_dataset = datasets.ImageFolder(TEST_DIR, transform=data_transforms['val'])
        val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=2)
        print(f"Loaded {len(train_dataset)} training images and {len(val_dataset)} validation images.")
    else:
        print(f"Loaded {len(train_dataset)} training images. (No validation set found)")

    print(f"Classes: {train_dataset.classes}")

    # --- BUILD MODEL ---
    # We use ResNet-50 as our primary deepfake detection model
    model = models.resnet50(pretrained=True)
    
    # Freeze the early layers to speed up training
    for param in model.parameters():
        param.requires_grad = False
        
    # Replace the final classification layer for our 2 classes (Real vs Fake)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, NUM_CLASSES)
    
    model = model.to(device)

    # --- OPTIMIZER & LOSS ---
    # We only optimize the final layer we just added
    optimizer = optim.Adam(model.fc.parameters(), lr=LEARNING_RATE)
    criterion = nn.CrossEntropyLoss()

    # --- TRAINING LOOP ---
    print("Starting Training...")
    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0
        corrects = 0
        total = 0

        # Wrap train_loader with tqdm for a progress bar
        progress_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{EPOCHS}")
        
        for inputs, labels in progress_bar:
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()

            # Forward pass
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            _, preds = torch.max(outputs, 1)

            # Backward pass
            loss.backward()
            optimizer.step()

            # Statistics
            running_loss += loss.item() * inputs.size(0)
            corrects += torch.sum(preds == labels.data)
            total += inputs.size(0)
            
            progress_bar.set_postfix({'loss': loss.item()})

        epoch_loss = running_loss / total
        epoch_acc = corrects.double() / total
        
        print(f"Epoch {epoch+1} | Train Loss: {epoch_loss:.4f} | Train Acc: {epoch_acc:.4f}")

        # --- VALIDATION LOOP ---
        if val_loader:
            model.eval()
            val_loss = 0.0
            val_corrects = 0
            val_total = 0
            with torch.no_grad():
                for inputs, labels in val_loader:
                    inputs, labels = inputs.to(device), labels.to(device)
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)
                    _, preds = torch.max(outputs, 1)
                    val_loss += loss.item() * inputs.size(0)
                    val_corrects += torch.sum(preds == labels.data)
                    val_total += inputs.size(0)
                    
            val_epoch_loss = val_loss / val_total
            val_epoch_acc = val_corrects.double() / val_total
            print(f"Epoch {epoch+1} | Val Loss: {val_epoch_loss:.4f} | Val Acc: {val_epoch_acc:.4f}")

    # --- SAVE MODEL ---
    save_path = "deepfake_resnet50.pth"
    torch.save(model.state_dict(), save_path)
    print(f"Training Complete! Model saved to {save_path}")
    print("Download this file from Kaggle and place it in your local project directory.")

if __name__ == '__main__':
    main()
