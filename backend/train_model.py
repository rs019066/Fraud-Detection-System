# train_model.py (Fixed - Handles NaN values)
"""
Model Training Script - Using Sklearn KNN
Fixed version that handles NaN values properly
"""

import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

class FraudDetectionTrainer:
    """
    Comprehensive trainer for fraud detection model
    Uses sklearn KNN with proper NaN handling
    """
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.df = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.scaler = StandardScaler()
        self.scaler_temp = None
        self.model = None
        self.feature_names = None
        
    def load_data(self):
        """Load and initial exploration"""
        print("📊 Loading dataset...")
        self.df = pd.read_csv(self.data_path)
        
        print(f"✅ Dataset loaded: {self.df.shape}")
        print(f"   • Features: {self.df.shape[1]}")
        print(f"   • Samples: {self.df.shape[0]}")
        print(f"   • Fraud cases: {self.df['Class'].sum()}")
        print(f"   • Fraud rate: {self.df['Class'].mean():.4%}")
        
        # Check for missing values in original data
        missing = self.df.isnull().sum().sum()
        if missing > 0:
            print(f"   ⚠️  Missing values found: {missing}")
            print("   Filling missing values with 0...")
            self.df = self.df.fillna(0)
        
    def feature_engineering(self):
        """Advanced feature engineering with NaN handling"""
        print("\n🔧 Engineering features...")
        
        df = self.df.copy()
        
        # Interaction features
        df['V1_V2'] = df['V1'] * df['V2']
        df['V1_V3'] = df['V1'] * df['V3']
        df['V4_V12'] = df['V4'] * df['V12']
        df['V10_V14'] = df['V10'] * df['V14']
        df['V4_V17'] = df['V4'] * df['V17']
        
        # Squared features
        for i in [1, 2, 3, 4, 10, 12, 14, 17]:
            df[f'V{i}_squared'] = df[f'V{i}'] ** 2
        
        # Amount transformations
        df['Amount_log'] = np.log1p(df['Amount'])
        df['Amount_sqrt'] = np.sqrt(df['Amount'])
        df['Amount_squared'] = df['Amount'] ** 2
        
        # Time-based features
        df['Time_hour'] = (df['Time'] / 3600) % 24
        df['Time_sin'] = np.sin(2 * np.pi * df['Time_hour'] / 24)
        df['Time_cos'] = np.cos(2 * np.pi * df['Time_hour'] / 24)
        
        # Time of day (convert to numeric to avoid NaN)
        time_bins = pd.cut(df['Time_hour'], 
                          bins=[0, 6, 12, 18, 24],
                          labels=[0, 1, 2, 3])
        df['Time_of_day'] = pd.to_numeric(time_bins, errors='coerce').fillna(0).astype(int)
        
        # Statistical features with NaN handling
        v_cols = [f'V{i}' for i in range(1, 29)]
        df['V_sum'] = df[v_cols].sum(axis=1)
        df['V_mean'] = df[v_cols].mean(axis=1)
        df['V_std'] = df[v_cols].std(axis=1).fillna(0)  # std can be NaN for single values
        df['V_max'] = df[v_cols].max(axis=1)
        df['V_min'] = df[v_cols].min(axis=1)
        df['V_range'] = df['V_max'] - df['V_min']
        
        # Ratio features with safe division
        df['Amount_to_V_sum'] = df['Amount'] / (df['V_sum'].abs() + 1)
        
        # Final NaN check and cleanup
        nan_cols = df.columns[df.isnull().any()].tolist()
        if nan_cols:
            print(f"   ⚠️  Found NaN in columns: {nan_cols}")
            print("   Filling NaN values with 0...")
            df = df.fillna(0)
        
        # Replace inf values
        df = df.replace([np.inf, -np.inf], 0)
        
        print(f"✅ Features engineered: {df.shape[1]} total features")
        print(f"   Final NaN count: {df.isnull().sum().sum()}")
        
        self.df = df
        
    def prepare_data(self, test_size=0.2, balance_data=True):
        """Prepare data with SMOTE"""
        print("\n📦 Preparing data...")
        
        # Separate features and target
        X = self.df.drop(['Class'], axis=1)
        y = self.df['Class']
        
        # Final check before split
        print(f"   • Pre-split NaN check: {X.isnull().sum().sum()}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"   • Train samples: {X_train.shape[0]}")
        print(f"   • Test samples: {X_test.shape[0]}")
        print(f"   • Train fraud rate: {y_train.mean():.4%}")
        
        # Handle imbalanced data
        if balance_data:
            print("\n⚖️ Balancing dataset with SMOTE...")
            
            # Scale before SMOTE
            self.scaler_temp = StandardScaler()
            X_train_scaled = self.scaler_temp.fit_transform(X_train)
            
            print(f"   • Scaled data NaN check: {np.isnan(X_train_scaled).sum()}")
            
            # SMOTE + undersampling strategy
            # SMOTE sampling_strategy=0.5: Generate synthetic fraud samples until minority class
            # is 50% of majority class size. This avoids extreme oversampling which can lead to
            # overfitting on synthetic data, while still providing enough fraud examples to learn from.
            # Why 0.5? Balance between: (1) giving model enough fraud patterns to learn, and
            # (2) not overwhelming with synthetic data that may not represent real fraud perfectly.
            smote = SMOTE(sampling_strategy=0.5, random_state=42)

            # RandomUnderSampler sampling_strategy=0.8: After SMOTE, undersample majority class
            # so that legitimate transactions = 80% of total. This gives final ~44% fraud rate.
            # Why undersample? (1) Reduces training time, (2) prevents model from being biased
            # toward majority class, (3) combined with SMOTE gives balanced dataset without
            # losing too much information from undersampling alone or overfitting from oversampling alone.
            undersample = RandomUnderSampler(sampling_strategy=0.8, random_state=42)
            
            X_train_balanced, y_train_balanced = smote.fit_resample(X_train_scaled, y_train)
            X_train_balanced, y_train_balanced = undersample.fit_resample(
                X_train_balanced, y_train_balanced
            )
            
            print(f"✅ Balanced dataset:")
            print(f"   • New train samples: {X_train_balanced.shape[0]}")
            print(f"   • New fraud rate: {y_train_balanced.mean():.4%}")
            
            self.X_train = X_train_balanced
            self.y_train = y_train_balanced
            self.X_test = self.scaler_temp.transform(X_test)
        else:
            self.X_train = self.scaler.fit_transform(X_train)
            self.y_train = y_train
            self.X_test = self.scaler.transform(X_test)
        
        self.y_test = y_test
        self.feature_names = X.columns.tolist()
        
        print(f"✅ Data prepared successfully")
        
    def find_optimal_k(self, k_range=range(3, 21, 2)):
        """Find optimal K value"""
        print("\n🔍 Finding optimal K value...")
        
        best_score = 0
        best_k = 5
        scores = []
        
        for k in k_range:
            knn = KNeighborsClassifier(
                n_neighbors=k, 
                weights='distance',
                metric='euclidean',
                n_jobs=-1
            )
            
            # Stratified k-fold cross-validation (n_splits=3)
            # Why 3 folds? Balance between: (1) having enough validation data per fold (33% of train set)
            # and (2) computational efficiency (3 folds = faster than 5 or 10 folds).
            # Stratified ensures each fold maintains the same fraud/legitimate ratio as the full dataset,
            # critical for imbalanced data where random splits could create folds with too few fraud cases.
            # This prevents: fold 1 having 50% fraud while fold 2 has only 30%, which would give unreliable
            # K-selection results. Each fold gets representative sample for robust evaluation.
            skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
            fold_scores = []
            
            for train_idx, val_idx in skf.split(self.X_train, self.y_train):
                X_train_fold = self.X_train[train_idx]
                y_train_fold = self.y_train[train_idx]
                X_val_fold = self.X_train[val_idx]
                y_val_fold = self.y_train[val_idx]
                
                knn.fit(X_train_fold, y_train_fold)
                y_pred = knn.predict(X_val_fold)
                
                score = f1_score(y_val_fold, y_pred)
                fold_scores.append(score)
            
            avg_score = np.mean(fold_scores)
            scores.append(avg_score)
            
            print(f"   K={k}: F1-Score = {avg_score:.4f}")
            
            if avg_score > best_score:
                best_score = avg_score
                best_k = k
        
        print(f"\n✅ Best K value: {best_k} (F1-Score: {best_score:.4f})")
        return best_k
    
    def train_model(self, k=None):
        """Train the final model"""
        print("\n🎯 Training final model...")
        
        if k is None:
            k = self.find_optimal_k()
        
        # Train with optimal parameters
        self.model = KNeighborsClassifier(
            n_neighbors=k,
            weights='distance',
            metric='euclidean',
            n_jobs=-1
        )
        
        self.model.fit(self.X_train, self.y_train)
        
        print(f"✅ Model trained successfully with K={k}")
        
    def evaluate_model(self):
        """Comprehensive model evaluation"""
        print("\n📈 Evaluating model...")
        
        # Predictions
        y_pred = self.model.predict(self.X_test)
        y_pred_proba = self.model.predict_proba(self.X_test)[:, 1]
        
        # Calculate metrics
        accuracy = accuracy_score(self.y_test, y_pred)
        precision = precision_score(self.y_test, y_pred)
        recall = recall_score(self.y_test, y_pred)
        f1 = f1_score(self.y_test, y_pred)
        roc_auc = roc_auc_score(self.y_test, y_pred_proba)
        
        print("\n📊 Model Performance:")
        print(f"   • Accuracy:  {accuracy:.4f}")
        print(f"   • Precision: {precision:.4f}")
        print(f"   • Recall:    {recall:.4f}")
        print(f"   • F1-Score:  {f1:.4f}")
        print(f"   • ROC-AUC:   {roc_auc:.4f}")
        
        # Confusion Matrix
        cm = confusion_matrix(self.y_test, y_pred)
        print("\n📋 Confusion Matrix:")
        print(f"   TN: {cm[0,0]:5d}  |  FP: {cm[0,1]:5d}")
        print(f"   FN: {cm[1,0]:5d}  |  TP: {cm[1,1]:5d}")
        
        # Classification Report
        print("\n📑 Classification Report:")
        print(classification_report(self.y_test, y_pred, 
                                   target_names=['Legitimate', 'Fraud']))
        
        return {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'roc_auc': float(roc_auc),
            'confusion_matrix': cm.tolist()
        }
    
    def find_optimal_threshold(self):
        """Find optimal threshold"""
        print("\n🎚️ Finding optimal threshold...")
        
        y_pred_proba = self.model.predict_proba(self.X_test)[:, 1]
        
        best_f1 = 0
        best_threshold = 0.5
        
        thresholds = np.arange(0.1, 0.9, 0.05)
        
        for threshold in thresholds:
            y_pred_threshold = (y_pred_proba >= threshold).astype(int)
            f1 = f1_score(self.y_test, y_pred_threshold)
            
            if f1 > best_f1:
                best_f1 = f1
                best_threshold = threshold
        
        print(f"✅ Optimal threshold: {best_threshold:.2f} (F1: {best_f1:.4f})")
        return float(best_threshold)
    
    def save_model(self, output_dir='model_artifacts'):
        """Save model and artifacts"""
        print(f"\n💾 Saving model to {output_dir}...")
        
        Path(output_dir).mkdir(exist_ok=True)
        
        # Save model, scaler, and features
        joblib.dump(self.model, f'{output_dir}/model.pkl')
        
        # Save the correct scaler
        scaler_to_save = self.scaler_temp if self.scaler_temp is not None else self.scaler
        joblib.dump(scaler_to_save, f'{output_dir}/scaler.pkl')
        joblib.dump(self.feature_names, f'{output_dir}/features.pkl')
        
        # Save configuration
        performance = self.evaluate_model()
        threshold = self.find_optimal_threshold()
        
        config = {
            'threshold': threshold,
            'k_neighbors': int(self.model.n_neighbors),
            'weights': self.model.weights,
            'distance_metric': self.model.metric,
            'performance': performance,
            'features_count': len(self.feature_names)
        }
        
        with open(f'{output_dir}/model_config.json', 'w') as f:
            json.dump(config, f, indent=4)
        
        print("✅ Model saved successfully!")
        print(f"   • Model: {output_dir}/model.pkl")
        print(f"   • Scaler: {output_dir}/scaler.pkl")
        print(f"   • Features: {output_dir}/features.pkl")
        print(f"   • Config: {output_dir}/model_config.json")

def main():
    """Main training pipeline"""
    print("=" * 60)
    print("  KNN FRAUD DETECTION - MODEL TRAINING")
    print("=" * 60)
    
    try:
        # Initialize trainer
        trainer = FraudDetectionTrainer('creditcard.csv')
        
        # Training pipeline
        trainer.load_data()
        trainer.feature_engineering()
        trainer.prepare_data(balance_data=True)
        trainer.train_model()
        trainer.evaluate_model()
        trainer.save_model()
        
        print("\n" + "=" * 60)
        print("  ✅ TRAINING COMPLETE!")
        print("=" * 60)
        
    except FileNotFoundError:
        print("\n❌ ERROR: creditcard.csv not found!")
        print("Please download the dataset from:")
        print("https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()