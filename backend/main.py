# main.py - REFACTORED VERSION
"""
Credit Card Fraud Detection API
With OOP architecture demonstrating SOLID principles
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, Float, Boolean, DateTime, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Dict
from datetime import datetime
from messages_routes import messages_router
import numpy as np
import pandas as pd
import joblib
import json
from pathlib import Path
import hashlib
import traceback

# Import from our new modules (demonstrating modular architecture)
from config import Config
from exceptions import (
    ModelLoadException,
    PredictionException,
    InvalidTransactionException,
    TransactionNotFoundException
)
from services.fraud_scorer import RuleBasedFraudScorer, create_fraud_scorer
from auth.routes import router as auth_router
from auth.dependencies import get_current_user, require_admin

# ===================================================
#    DATABASE SETUP (using Config)
# ===================================================
SQLALCHEMY_DATABASE_URL = Config.DATABASE_URL  # Now uses centralized config
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TransactionDB(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    card_number = Column(String)
    transaction_amount = Column(Float)
    merchant_name = Column(String)
    merchant_category = Column(String)
    transaction_type = Column(String)
    location_city = Column(String)
    location_country = Column(String)
    card_type = Column(String)
    transaction_hour = Column(Integer)
    day_of_week = Column(Integer)
    is_online = Column(Boolean)
    is_international = Column(Boolean)
    distance_from_home = Column(Float)
    is_fraud = Column(Boolean)
    fraud_probability = Column(Float)
    risk_score = Column(Float)
    created_by_user_id = Column(Integer, nullable=True)  # Track which user created this transaction
    created_by_username = Column(String, nullable=True)  # For easier querying
    created_at = Column(DateTime, default=datetime.utcnow)

class UserDB(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="analyst")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    def to_dict(self):
        """Convert user to dictionary for API responses"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }

Base.metadata.create_all(bind=engine)

# ===================================================
#    PYDANTIC MODELS
# ===================================================
class RealTransaction(BaseModel):
    card_number: str = Field(..., description="Last 4 digits")
    card_type: str = Field(..., description="Visa, Mastercard, Amex, Discover")
    transaction_amount: float = Field(..., gt=0)
    merchant_name: str = Field(...)
    merchant_category: str = Field(...)
    location_city: str = Field(...)
    location_country: str = Field(default="USA")
    is_online: bool = Field(default=False)
    is_international: bool = Field(default=False)
    transaction_hour: int = Field(..., ge=0, le=23)
    day_of_week: int = Field(..., ge=0, le=6)
    transaction_type: str = Field(...)
    distance_from_home: float = Field(default=0, ge=0)

    @field_validator('card_number')
    @classmethod
    def validate_card_number(cls, v):
        if len(v) not in [4, 16]:
            raise ValueError('Card number should be last 4 digits or full 16 digits')
        return v

    @field_validator('transaction_amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Transaction amount must be positive')
        if v > 1000000:
            raise ValueError('Transaction amount seems unrealistic')
        return v

class PredictionResponse(BaseModel):
    id: int
    is_fraud: bool
    fraud_probability: float
    confidence: str
    risk_score: float
    details: Dict
    transaction_summary: Dict

class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    card_number: str
    transaction_amount: float
    merchant_name: str
    merchant_category: str
    is_fraud: bool
    fraud_probability: float
    risk_score: float
    created_by_username: Optional[str] = None
    created_at: datetime

# ===================================================
#    IMPROVED FEATURE MAPPING (Refactored to use FraudScorer)
# ===================================================
class ImprovedFeatureMapper:
    """
    Maps raw transaction data to 28 V-features for ML model.

    Demonstrates OOP refactoring:
    - Fraud scoring logic extracted to services/fraud_scorer.py
    - Uses dependency injection (class-level fraud_scorer)
    - Easier to test (can mock fraud_scorer)
    """

    # Class-level fraud scorer instance (dependency injection)
    fraud_scorer = create_fraud_scorer("rule_based")
    @staticmethod
    def hash_to_float(text: str, seed: int = 0) -> float:
        try:
            hash_val = int(hashlib.md5(f"{text}{seed}".encode()).hexdigest(), 16)
            return ((hash_val % 6000) / 1000) - 3
        except Exception:
            return 0.0
    
    @staticmethod
    def calculate_fraud_score(transaction: RealTransaction) -> float:
        """
        Calculate fraud score using the fraud scorer service.

        Demonstrates separation of concerns - fraud scoring logic is now in
        services/fraud_scorer.py instead of inline here.

        Benefits:
        - Easier to test (mock the fraud_scorer)
        - Easier to swap algorithms (rule-based vs ML-based)
        - Follows Single Responsibility Principle
        - Configuration managed centrally in config.py
        """
        return ImprovedFeatureMapper.fraud_scorer.calculate_score(transaction)
    
    @staticmethod
    def map_to_v_features(transaction: RealTransaction) -> Dict:
        try:
            fraud_score = ImprovedFeatureMapper.calculate_fraud_score(transaction)
            amount = transaction.transaction_amount
            hour = transaction.transaction_hour
            
            amount_log = np.log1p(amount)
            amount_norm = amount_log / 10
            
            v_features = {}
            
            v_features['V1'] = amount_norm * (2 if fraud_score > 0.5 else -1) * (1 + fraud_score)
            v_features['V2'] = amount_norm * np.sin(hour * np.pi / 12) * (1 + fraud_score * 2)
            v_features['V3'] = amount_norm * np.cos(hour * np.pi / 12) * (1 + fraud_score * 2)
            v_features['V4'] = (amount / 1000) * (2 if transaction.is_international else -1) * (1 + fraud_score)
            
            v_features['V5'] = (transaction.distance_from_home / 100) * (1 + fraud_score * 3)
            v_features['V6'] = fraud_score * 5 if transaction.is_international else -fraud_score * 2
            v_features['V7'] = ImprovedFeatureMapper.hash_to_float(transaction.merchant_category) * (1 + fraud_score)
            v_features['V8'] = ImprovedFeatureMapper.hash_to_float(transaction.location_city) * (1 + fraud_score)
            
            v_features['V9'] = (1 if hour < 6 else -1) * amount_norm * (1 + fraud_score * 2)
            v_features['V10'] = np.sqrt(amount) * (2 if transaction.is_international else -1) * (1 + fraud_score)
            v_features['V11'] = (transaction.distance_from_home / 100) * (1 + fraud_score * 2)
            v_features['V12'] = fraud_score * 4 - 2
            
            v_features['V13'] = np.sin(hour * 2 * np.pi / 24) * amount_norm * (1 + fraud_score * 2)
            v_features['V14'] = np.cos(hour * 2 * np.pi / 24) * amount_norm * (1 + fraud_score * 2)
            v_features['V15'] = (transaction.day_of_week / 7) * (2 if fraud_score > 0.4 else -1)
            v_features['V16'] = (2 if hour < 6 or hour > 22 else -1) * amount_norm * (1 + fraud_score * 3)
            v_features['V17'] = amount_norm * (2 if transaction.is_online else -1) * (1 + fraud_score)
            
            card_hash = ImprovedFeatureMapper.hash_to_float(transaction.card_number)
            merchant_hash = ImprovedFeatureMapper.hash_to_float(transaction.merchant_name)
            
            v_features['V18'] = card_hash * amount_norm * (1 + fraud_score * 2)
            v_features['V19'] = merchant_hash * (1 + fraud_score * 3)
            v_features['V20'] = (2 if transaction.is_online and amount > 1000 else -1) * fraud_score * 3
            v_features['V21'] = (transaction.distance_from_home / 500) * amount_norm * (1 + fraud_score * 3)
            v_features['V22'] = fraud_score * 5 - 2.5
            v_features['V23'] = (amount / 100) * (3 if hour in [2, 3, 4] else -1) * (1 + fraud_score * 2)
            
            v_features['V24'] = fraud_score * amount_norm * 4
            v_features['V25'] = (transaction.distance_from_home / 100) * (1 + fraud_score * 4)
            v_features['V26'] = (3 if amount > 1000 and transaction.is_international else -2) * (1 + fraud_score)
            v_features['V27'] = np.sqrt(amount) * (2 if transaction.is_international else -1) * (1 + fraud_score * 3)
            v_features['V28'] = fraud_score * 6 - 3
            
            return v_features
        except Exception as e:
            print(f"Error in map_to_v_features: {e}")
            traceback.print_exc()
            # Return default features
            return {f'V{i}': 0.0 for i in range(1, 29)}

# ===================================================
#    FEATURE ENGINEERING
# ===================================================
class FeatureEngineer:
    @staticmethod
    def create_features(v_features: Dict, real_transaction: RealTransaction) -> pd.DataFrame:
        try:
            df = pd.DataFrame([v_features])
            df['Time'] = real_transaction.transaction_hour * 3600
            df['Amount'] = real_transaction.transaction_amount
            
            df['V1_V2'] = df['V1'] * df['V2']
            df['V1_V3'] = df['V1'] * df['V3']
            df['V4_V12'] = df['V4'] * df['V12']
            df['V10_V14'] = df['V10'] * df['V14']
            df['V4_V17'] = df['V4'] * df['V17']
            
            for i in [1, 2, 3, 4, 10, 12, 14, 17]:
                df[f'V{i}_squared'] = df[f'V{i}'] ** 2
            
            df['Amount_log'] = np.log1p(df['Amount'])
            df['Amount_sqrt'] = np.sqrt(df['Amount'])
            df['Amount_squared'] = df['Amount'] ** 2
            
            df['Time_hour'] = (df['Time'] / 3600) % 24
            df['Time_sin'] = np.sin(2 * np.pi * df['Time_hour'] / 24)
            df['Time_cos'] = np.cos(2 * np.pi * df['Time_hour'] / 24)
            time_bins = pd.cut(df['Time_hour'], bins=[0, 6, 12, 18, 24], labels=[0, 1, 2, 3])
            df['Time_of_day'] = pd.to_numeric(time_bins, errors='coerce').fillna(0).astype(int)
            
            v_cols = [f'V{i}' for i in range(1, 29)]
            df['V_sum'] = df[v_cols].sum(axis=1)
            df['V_mean'] = df[v_cols].mean(axis=1)
            df['V_std'] = df[v_cols].std(axis=1).fillna(0)
            df['V_max'] = df[v_cols].max(axis=1)
            df['V_min'] = df[v_cols].min(axis=1)
            df['V_range'] = df['V_max'] - df['V_min']
            
            df['Amount_to_V_sum'] = df['Amount'] / (df['V_sum'].abs() + 1)
            
            df = df.fillna(0)
            df = df.replace([np.inf, -np.inf], 0)
            
            return df
        except Exception as e:
            print(f"Error in create_features: {e}")
            traceback.print_exc()
            raise
    
    @staticmethod
    def get_risk_level(probability: float) -> str:
        """
        Classify fraud probability into human-readable risk levels.

        Now uses Config.RISK_THRESHOLDS instead of hardcoded values.
        Demonstrates centralized configuration management.
        """
        thresholds = Config.RISK_THRESHOLDS

        if probability >= thresholds["critical"]:
            return "CRITICAL"
        elif probability >= thresholds["high"]:
            return "HIGH"
        elif probability >= thresholds["medium"]:
            return "MEDIUM"
        elif probability >= thresholds["low"]:
            return "LOW"
        else:
            return "MINIMAL"

# ===================================================
#    MODEL SERVICE
# ===================================================
class ModelService:
    """
    Service for loading and managing the fraud detection ML model.

    Now uses Config for paths and thresholds (demonstrates dependency on config).
    """
    def __init__(self, model_dir: str = None):
        # Use Config.MODEL_DIR if not specified
        model_dir = model_dir or Config.MODEL_DIR
        self.model_dir = Path(model_dir)
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.config = None
        self.load_model()
    
    def load_model(self):
        try:
            self.model = joblib.load(self.model_dir / 'model.pkl')
            self.scaler = joblib.load(self.model_dir / 'scaler.pkl')
            self.feature_names = joblib.load(self.model_dir / 'features.pkl')
            
            with open(self.model_dir / 'model_config.json', 'r') as f:
                self.config = json.load(f)
            
            print("✅ Model loaded successfully!")
            print(f"   Features required: {len(self.feature_names)}")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            traceback.print_exc()
            raise
    
    def predict(self, real_transaction: RealTransaction) -> Dict:
        try:
            v_features = ImprovedFeatureMapper.map_to_v_features(real_transaction)
            df = FeatureEngineer.create_features(v_features, real_transaction)
            
            # Ensure all features exist
            for feature in self.feature_names:
                if feature not in df.columns:
                    df[feature] = 0
            
            df = df[self.feature_names]
            X_scaled = self.scaler.transform(df)
            
            fraud_prob = float(self.model.predict_proba(X_scaled)[0][1])
            threshold = self.config.get('threshold', 0.5) * 0.8
            is_fraud = fraud_prob >= threshold
            
            risk_score = min(100, fraud_prob * 120)
            confidence = FeatureEngineer.get_risk_level(fraud_prob)
            
            return {
                'is_fraud': bool(is_fraud),
                'fraud_probability': float(fraud_prob),
                'risk_score': float(risk_score),
                'confidence': confidence,
                'threshold': float(threshold)
            }
        except Exception as e:
            print(f"Error in predict: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

# ===================================================
#    REPOSITORY
# ===================================================
class TransactionRepository:
    @staticmethod
    def create(db: Session, transaction: RealTransaction, prediction: Dict, user_id: int = None, username: str = None) -> TransactionDB:
        try:
            db_transaction = TransactionDB(
                card_number=transaction.card_number,
                transaction_amount=transaction.transaction_amount,
                merchant_name=transaction.merchant_name,
                merchant_category=transaction.merchant_category,
                transaction_type=transaction.transaction_type,
                location_city=transaction.location_city,
                location_country=transaction.location_country,
                card_type=transaction.card_type,
                transaction_hour=transaction.transaction_hour,
                day_of_week=transaction.day_of_week,
                is_online=transaction.is_online,
                is_international=transaction.is_international,
                distance_from_home=transaction.distance_from_home,
                is_fraud=prediction['is_fraud'],
                fraud_probability=prediction['fraud_probability'],
                risk_score=prediction['risk_score'],
                created_by_user_id=user_id,
                created_by_username=username
            )
            db.add(db_transaction)
            db.commit()
            db.refresh(db_transaction)
            return db_transaction
        except Exception as e:
            db.rollback()
            print(f"Database error: {e}")
            traceback.print_exc()
            raise

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100, user_id: int = None, role: str = None) -> List[TransactionDB]:
        """
        Get transactions with role-based filtering:
        - Admins see ALL transactions
        - Analysts see ONLY their own transactions
        """
        try:
            query = db.query(TransactionDB)

            # Filter by user_id for analysts (admins see all)
            if role == "analyst" and user_id is not None:
                query = query.filter(TransactionDB.created_by_user_id == user_id)

            return query.order_by(TransactionDB.created_at.desc()).offset(skip).limit(limit).all()
        except Exception as e:
            print(f"Database query error: {e}")
            return []
    
    @staticmethod
    def get_by_id(db: Session, transaction_id: int) -> Optional[TransactionDB]:
        return db.query(TransactionDB).filter(TransactionDB.id == transaction_id).first()
    
    @staticmethod
    def delete(db: Session, transaction_id: int) -> bool:
        transaction = db.query(TransactionDB).filter(TransactionDB.id == transaction_id).first()
        if transaction:
            db.delete(transaction)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_statistics(db: Session, user_id: int = None, role: str = None) -> Dict:
        """
        Get statistics with role-based filtering:
        - Admins see ALL transaction statistics
        - Analysts see ONLY their own transaction statistics
        """
        try:
            query = db.query(TransactionDB)

            # Filter by user_id for analysts (admins see all)
            if role == "analyst" and user_id is not None:
                query = query.filter(TransactionDB.created_by_user_id == user_id)

            total = query.count()
            fraudulent = query.filter(TransactionDB.is_fraud == True).count()
            return {
                'total_transactions': total,
                'fraudulent_transactions': fraudulent,
                'fraud_rate': fraudulent / total if total > 0 else 0,
                'legitimate_transactions': total - fraudulent
            }
        except Exception as e:
            print(f"Statistics error: {e}")
            return {
                'total_transactions': 0,
                'fraudulent_transactions': 0,
                'fraud_rate': 0,
                'legitimate_transactions': 0
            }

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

model_service = ModelService()

# ===================================================
#    FASTAPI APP
# ===================================================
app = FastAPI(
    title="KNN Fraud Detection API",
    description="Improved Fraud Detection",
    version="3.1.0"
)

# CORS Configuration (from Config)
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,  # Now configurable via environment variable
    allow_credentials=Config.CORS_ALLOW_CREDENTIALS,
    allow_methods=Config.CORS_ALLOW_METHODS,
    allow_headers=Config.CORS_ALLOW_HEADERS,
)

# Include authentication router
app.include_router(auth_router)

# Include messages router
app.include_router(messages_router)

@app.get("/")
async def root():
    return {
        "service": "KNN Fraud Detection API",
        "version": "3.1.0",
        "status": "active",
        "documentation": "/docs"
    }

@app.post("/api/predict", response_model=PredictionResponse)
async def predict_transaction(
    transaction: RealTransaction,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Requires authentication
):
    try:
        prediction = model_service.predict(transaction)
        # Save transaction with user tracking
        db_transaction = TransactionRepository.create(
            db,
            transaction,
            prediction,
            user_id=current_user.get("user_id"),
            username=current_user.get("username")
        )

        return PredictionResponse(
            id=db_transaction.id,
            is_fraud=prediction['is_fraud'],
            fraud_probability=prediction['fraud_probability'],
            confidence=prediction['confidence'],
            risk_score=prediction['risk_score'],
            details={
                'threshold': prediction['threshold'],
                'created_at': db_transaction.created_at.isoformat(),
                'tested_by': current_user.get("username")
            },
            transaction_summary={
                'amount': transaction.transaction_amount,
                'merchant': transaction.merchant_name,
                'location': f"{transaction.location_city}, {transaction.location_country}",
                'card_type': transaction.card_type,
                'is_online': transaction.is_online
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Predict endpoint error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/api/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Requires authentication
):
    """
    Get transactions with role-based access control:
    - Admins see ALL transactions
    - Analysts see ONLY their own transactions
    """
    try:
        return TransactionRepository.get_all(
            db,
            skip,
            limit,
            user_id=current_user.get("user_id"),
            role=current_user.get("role")
        )
    except Exception as e:
        print(f"Get transactions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = TransactionRepository.get_by_id(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@app.delete("/api/transactions/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)  # Requires admin role
):
    success = TransactionRepository.delete(db, transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted successfully"}

@app.get("/api/statistics")
async def get_statistics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Requires authentication
):
    """
    Get statistics with role-based access control:
    - Admins see system-wide statistics (all transactions)
    - Analysts see only their own transaction statistics
    """
    return TransactionRepository.get_statistics(
        db,
        user_id=current_user.get("user_id"),
        role=current_user.get("role")
    )

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model_service.model is not None,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/options")
async def get_options():
    return {
        "card_types": ["Visa", "Mastercard", "American Express", "Discover"],
        "merchant_categories": [
            "Online Shopping", "Grocery Store", "Gas Station", "Restaurant",
            "Department Store", "Electronics", "Clothing", "Pharmacy",
            "Hotel", "Airline", "Entertainment", "ATM Withdrawal"
        ],
        "transaction_types": ["Purchase", "Online", "Contactless", "Chip & PIN", "Swipe", "Withdrawal"],
        "countries": ["USA", "Canada", "UK", "Mexico", "France", "Germany", "Japan", "Australia"]
    }

@app.get("/api/fraud-scenarios")
async def get_fraud_scenarios():
    return {
        "scenarios": [
            {
                "name": "Normal Purchase",
                "description": "Typical local purchase",
                "data": {
                    "card_number": "1234",
                    "card_type": "Visa",
                    "transaction_amount": 45.99,
                    "merchant_name": "Walmart",
                    "merchant_category": "Grocery Store",
                    "location_city": "New York",
                    "location_country": "USA",
                    "is_online": False,
                    "is_international": False,
                    "transaction_hour": 14,
                    "day_of_week": 2,
                    "transaction_type": "Chip & PIN",
                    "distance_from_home": 2.5
                },
                "expected": "legitimate"
            },
            {
                "name": "High Risk Fraud",
                "description": "International, high amount, unusual hour",
                "data": {
                    "card_number": "5678",
                    "card_type": "Mastercard",
                    "transaction_amount": 4999.99,
                    "merchant_name": "Unknown Electronics XYZ",
                    "merchant_category": "Electronics",
                    "location_city": "Tokyo",
                    "location_country": "Japan",
                    "is_online": True,
                    "is_international": True,
                    "transaction_hour": 3,
                    "day_of_week": 6,
                    "transaction_type": "Online",
                    "distance_from_home": 6789
                },
                "expected": "fraud"
            },
            {
                "name": "Suspicious Online",
                "description": "Large online purchase, far from home",
                "data": {
                    "card_number": "9012",
                    "card_type": "Visa",
                    "transaction_amount": 2500.00,
                    "merchant_name": "Online Store ABC",
                    "merchant_category": "Online Shopping",
                    "location_city": "Los Angeles",
                    "location_country": "USA",
                    "is_online": True,
                    "is_international": False,
                    "transaction_hour": 2,
                    "day_of_week": 1,
                    "transaction_type": "Online",
                    "distance_from_home": 850
                },
                "expected": "fraud"
            },
            {
                "name": "International Travel",
                "description": "Moderate amount, international, hotel",
                "data": {
                    "card_number": "3456",
                    "card_type": "American Express",
                    "transaction_amount": 350.00,
                    "merchant_name": "Marriott Hotel",
                    "merchant_category": "Hotel",
                    "location_city": "London",
                    "location_country": "UK",
                    "is_online": False,
                    "is_international": True,
                    "transaction_hour": 15,
                    "day_of_week": 4,
                    "transaction_type": "Swipe",
                    "distance_from_home": 3500
                },
                "expected": "medium_risk"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("  🚀 IMPROVED Fraud Detection API (FIXED)")
    print("="*60)
    print("\n✨ Features:")
    print("   • Better error handling")
    print("   • Improved fraud detection")
    print("   • CORS properly configured")
    print("\n📡 Server: http://localhost:8000")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)