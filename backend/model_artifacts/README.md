# Model Artifacts

This directory contains the trained KNN fraud detection model and preprocessing artifacts.

## Files

- **model.pkl** (113 MB, not tracked in git) - Trained KNN model
- **scaler.pkl** (2.6 KB) - StandardScaler for feature normalization
- **features.pkl** (504 B) - Feature names list
- **model_config.json** (556 B) - Model configuration and metadata

## Getting model.pkl

The `model.pkl` file is too large for GitHub (>100 MB limit). You have three options:

### Option 1: Train the model locally (Recommended)
```bash
cd backend
python train_model.py
```
This will generate all model artifacts including `model.pkl` (~5-10 minutes).

### Option 2: Download from release
Check the [Releases](https://github.com/Rupak2002/Fraud-Detection-System/releases) page for a pre-trained model.

### Option 3: Use Git LFS (for contributors)
If you need to version control the model:
```bash
# Install Git LFS
git lfs install

# Track the model file
git lfs track "backend/model_artifacts/model.pkl"

# Commit and push
git add .gitattributes backend/model_artifacts/model.pkl
git commit -m "Add model.pkl with Git LFS"
git push
```

## Model Details

- **Algorithm**: KNN (K=3, distance-weighted)
- **Features**: 57 engineered features
- **Training Data**: creditcard.csv (284,807 transactions)
- **Class Balance**: SMOTE (0.5) + RandomUnderSampler (0.8)
- **Performance**: 99.76% accuracy, 86.73% recall
