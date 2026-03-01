"""
Test Suite for Feature Engineering Pipeline
============================================
Tests the feature mapping and engineering components that transform
raw transactions into 57 ML-ready features for fraud detection.
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from main import ImprovedFeatureMapper, FeatureEngineer, RealTransaction


class TestImprovedFeatureMapper:
    """Test the ImprovedFeatureMapper class"""

    @pytest.fixture
    def sample_transaction(self):
        """Create a sample transaction for testing"""
        return RealTransaction(
            card_number="1234-5678-9012-3456",
            transaction_amount=150.50,
            merchant_name="Amazon",
            merchant_category="Online Retail",
            transaction_type="Purchase",
            location_city="New York",
            location_country="USA",
            card_type="Visa",
            transaction_hour=14,
            day_of_week=3,
            is_online=True,
            is_international=False,
            distance_from_home=5.2
        )

    def test_hash_to_float_deterministic(self):
        """Test that hash_to_float is deterministic (same input = same output)"""
        result1 = ImprovedFeatureMapper.hash_to_float("test_string", seed=42)
        result2 = ImprovedFeatureMapper.hash_to_float("test_string", seed=42)
        assert result1 == result2

    def test_hash_to_float_different_seeds(self):
        """Test that different seeds produce different results"""
        result1 = ImprovedFeatureMapper.hash_to_float("test_string", seed=1)
        result2 = ImprovedFeatureMapper.hash_to_float("test_string", seed=2)
        assert result1 != result2

    def test_hash_to_float_range(self):
        """Test that hash_to_float returns values in [-1, 1] range"""
        for i in range(100):
            result = ImprovedFeatureMapper.hash_to_float(f"string_{i}", seed=i)
            assert -1 <= result <= 1

    def test_fraud_score_range(self, sample_transaction):
        """Test that fraud score is in [0, 1] range"""
        score = ImprovedFeatureMapper.calculate_fraud_score(sample_transaction)
        assert 0 <= score <= 1

    def test_fraud_score_high_amount(self):
        """Test that high transaction amounts increase fraud score"""
        # Low amount transaction
        low_amount_txn = RealTransaction(
            card_number="1234-5678-9012-3456",
            transaction_amount=50.0,
            merchant_name="Store",
            merchant_category="Retail",
            transaction_type="Purchase",
            location_city="NYC",
            location_country="USA",
            card_type="Visa",
            transaction_hour=12,
            day_of_week=3,
            is_online=False,
            is_international=False,
            distance_from_home=2.0
        )

        # High amount transaction (everything else same)
        high_amount_txn = RealTransaction(
            card_number="1234-5678-9012-3456",
            transaction_amount=6000.0,  # > $5000
            merchant_name="Store",
            merchant_category="Retail",
            transaction_type="Purchase",
            location_city="NYC",
            location_country="USA",
            card_type="Visa",
            transaction_hour=12,
            day_of_week=3,
            is_online=False,
            is_international=False,
            distance_from_home=2.0
        )

        low_score = ImprovedFeatureMapper.calculate_fraud_score(low_amount_txn)
        high_score = ImprovedFeatureMapper.calculate_fraud_score(high_amount_txn)

        assert high_score > low_score

    def test_fraud_score_international(self):
        """Test that international transactions increase fraud score"""
        domestic_txn = RealTransaction(
            card_number="1234-5678-9012-3456",
            transaction_amount=100.0,
            merchant_name="Store",
            merchant_category="Retail",
            transaction_type="Purchase",
            location_city="NYC",
            location_country="USA",
            card_type="Visa",
            transaction_hour=12,
            day_of_week=3,
            is_online=False,
            is_international=False,
            distance_from_home=2.0
        )

        international_txn = RealTransaction(
            card_number="1234-5678-9012-3456",
            transaction_amount=100.0,
            merchant_name="Store",
            merchant_category="Retail",
            transaction_type="Purchase",
            location_city="London",
            location_country="UK",
            card_type="Visa",
            transaction_hour=12,
            day_of_week=3,
            is_online=False,
            is_international=True,
            distance_from_home=3500.0
        )

        domestic_score = ImprovedFeatureMapper.calculate_fraud_score(domestic_txn)
        international_score = ImprovedFeatureMapper.calculate_fraud_score(international_txn)

        assert international_score > domestic_score

    def test_fraud_score_unusual_hours(self):
        """Test that unusual hours (early morning) increase fraud score"""
        # Normal hour transaction
        normal_hour_txn = RealTransaction(
            card_number="1234-5678-9012-3456",
            transaction_amount=100.0,
            merchant_name="Store",
            merchant_category="Retail",
            transaction_type="Purchase",
            location_city="NYC",
            location_country="USA",
            card_type="Visa",
            transaction_hour=14,  # 2 PM
            day_of_week=3,
            is_online=False,
            is_international=False,
            distance_from_home=2.0
        )

        # Early morning transaction
        unusual_hour_txn = RealTransaction(
            card_number="1234-5678-9012-3456",
            transaction_amount=100.0,
            merchant_name="Store",
            merchant_category="Retail",
            transaction_type="Purchase",
            location_city="NYC",
            location_country="USA",
            card_type="Visa",
            transaction_hour=2,  # 2 AM
            day_of_week=3,
            is_online=False,
            is_international=False,
            distance_from_home=2.0
        )

        normal_score = ImprovedFeatureMapper.calculate_fraud_score(normal_hour_txn)
        unusual_score = ImprovedFeatureMapper.calculate_fraud_score(unusual_hour_txn)

        assert unusual_score > normal_score

    def test_map_to_v_features_count(self, sample_transaction):
        """Test that map_to_v_features returns exactly 28 V-features"""
        v_features = ImprovedFeatureMapper.map_to_v_features(sample_transaction)
        assert len(v_features) == 28
        assert all(f"V{i}" in v_features for i in range(1, 29))

    def test_map_to_v_features_no_nans(self, sample_transaction):
        """Test that V-features don't contain NaN values"""
        v_features = ImprovedFeatureMapper.map_to_v_features(sample_transaction)
        for key, value in v_features.items():
            assert not np.isnan(value), f"Feature {key} is NaN"
            assert np.isfinite(value), f"Feature {key} is infinite"


class TestFeatureEngineer:
    """Test the FeatureEngineer class"""

    @pytest.fixture
    def sample_v_features(self):
        """Create sample V-features for testing"""
        return {f"V{i}": np.random.randn() for i in range(1, 29)}

    @pytest.fixture
    def sample_transaction(self):
        """Create a sample transaction"""
        return RealTransaction(
            card_number="1234-5678-9012-3456",
            transaction_amount=150.50,
            merchant_name="Amazon",
            merchant_category="Online Retail",
            transaction_type="Purchase",
            location_city="New York",
            location_country="USA",
            card_type="Visa",
            transaction_hour=14,
            day_of_week=3,
            is_online=True,
            is_international=False,
            distance_from_home=5.2
        )

    def test_create_features_count(self, sample_v_features, sample_transaction):
        """Test that create_features generates exactly 57 features"""
        df = FeatureEngineer.create_features(sample_v_features, sample_transaction)
        assert df.shape[0] == 1  # One row
        assert df.shape[1] == 57  # 57 features

    def test_create_features_no_nans(self, sample_v_features, sample_transaction):
        """Test that engineered features don't contain NaN values"""
        df = FeatureEngineer.create_features(sample_v_features, sample_transaction)
        nan_count = df.isnull().sum().sum()
        assert nan_count == 0, f"Found {nan_count} NaN values in engineered features"

    def test_create_features_no_infinites(self, sample_v_features, sample_transaction):
        """Test that engineered features don't contain infinite values"""
        df = FeatureEngineer.create_features(sample_v_features, sample_transaction)
        inf_count = np.isinf(df.values).sum()
        assert inf_count == 0, f"Found {inf_count} infinite values in engineered features"

    def test_amount_transformations_present(self, sample_v_features, sample_transaction):
        """Test that amount transformations are present in features"""
        df = FeatureEngineer.create_features(sample_v_features, sample_transaction)
        assert 'Amount_log' in df.columns
        assert 'Amount_sqrt' in df.columns
        assert 'Amount_squared' in df.columns

    def test_time_features_present(self, sample_v_features, sample_transaction):
        """Test that time-based features are present"""
        df = FeatureEngineer.create_features(sample_v_features, sample_transaction)
        assert 'Time_sin' in df.columns
        assert 'Time_cos' in df.columns
        assert 'Time_Hour_bin' in df.columns

    def test_statistical_features_present(self, sample_v_features, sample_transaction):
        """Test that statistical aggregation features are present"""
        df = FeatureEngineer.create_features(sample_v_features, sample_transaction)
        assert 'V_sum' in df.columns
        assert 'V_mean' in df.columns
        assert 'V_std' in df.columns
        assert 'V_max' in df.columns
        assert 'V_min' in df.columns
        assert 'V_range' in df.columns

    def test_interaction_features_present(self, sample_v_features, sample_transaction):
        """Test that interaction features are present"""
        df = FeatureEngineer.create_features(sample_v_features, sample_transaction)
        assert 'V1_V2_interaction' in df.columns
        assert 'V3_V4_interaction' in df.columns

    def test_ratio_features_safe_division(self):
        """Test that ratio features handle division by zero safely"""
        # Create V-features where some are zero
        zero_v_features = {f"V{i}": 0.0 if i in [2, 4] else 1.0 for i in range(1, 29)}

        sample_transaction = RealTransaction(
            card_number="1234-5678-9012-3456",
            transaction_amount=100.0,
            merchant_name="Store",
            merchant_category="Retail",
            transaction_type="Purchase",
            location_city="NYC",
            location_country="USA",
            card_type="Visa",
            transaction_hour=12,
            day_of_week=3,
            is_online=False,
            is_international=False,
            distance_from_home=2.0
        )

        df = FeatureEngineer.create_features(zero_v_features, sample_transaction)

        # Should not have NaN or infinite values even with zeros
        assert df.isnull().sum().sum() == 0
        assert not np.isinf(df.values).any()

    def test_get_risk_level_thresholds(self):
        """Test risk level classification thresholds"""
        assert FeatureEngineer.get_risk_level(0.9) == "CRITICAL"
        assert FeatureEngineer.get_risk_level(0.7) == "HIGH"
        assert FeatureEngineer.get_risk_level(0.5) == "MEDIUM"
        assert FeatureEngineer.get_risk_level(0.3) == "LOW"
        assert FeatureEngineer.get_risk_level(0.1) == "MINIMAL"

    def test_get_risk_level_boundary_cases(self):
        """Test risk level classification at exact boundaries"""
        assert FeatureEngineer.get_risk_level(0.8) == "CRITICAL"  # >= 0.8
        assert FeatureEngineer.get_risk_level(0.6) == "HIGH"  # >= 0.6
        assert FeatureEngineer.get_risk_level(0.4) == "MEDIUM"  # >= 0.4
        assert FeatureEngineer.get_risk_level(0.2) == "LOW"  # >= 0.2
        assert FeatureEngineer.get_risk_level(0.0) == "MINIMAL"  # < 0.2


class TestEndToEndFeaturePipeline:
    """Test the complete feature engineering pipeline"""

    def test_transaction_to_features_pipeline(self):
        """Test complete pipeline: transaction -> V-features -> 57 features"""
        # Create transaction
        transaction = RealTransaction(
            card_number="1234-5678-9012-3456",
            transaction_amount=250.75,
            merchant_name="Best Buy",
            merchant_category="Electronics",
            transaction_type="Purchase",
            location_city="San Francisco",
            location_country="USA",
            card_type="MasterCard",
            transaction_hour=18,
            day_of_week=5,
            is_online=False,
            is_international=False,
            distance_from_home=15.5
        )

        # Step 1: Map to V-features
        v_features = ImprovedFeatureMapper.map_to_v_features(transaction)
        assert len(v_features) == 28

        # Step 2: Engineer features
        df = FeatureEngineer.create_features(v_features, transaction)
        assert df.shape == (1, 57)

        # Step 3: Verify no data quality issues
        assert df.isnull().sum().sum() == 0
        assert not np.isinf(df.values).any()

    def test_multiple_transactions_batch(self):
        """Test feature engineering on multiple transactions"""
        transactions = [
            RealTransaction(
                card_number=f"1234-5678-9012-{i:04d}",
                transaction_amount=100.0 + i * 10,
                merchant_name=f"Merchant_{i}",
                merchant_category="Retail",
                transaction_type="Purchase",
                location_city="NYC",
                location_country="USA",
                card_type="Visa",
                transaction_hour=(10 + i) % 24,
                day_of_week=i % 7,
                is_online=i % 2 == 0,
                is_international=False,
                distance_from_home=i * 2.5
            )
            for i in range(10)
        ]

        all_features = []
        for txn in transactions:
            v_features = ImprovedFeatureMapper.map_to_v_features(txn)
            df = FeatureEngineer.create_features(v_features, txn)
            all_features.append(df)

        combined_df = pd.concat(all_features, ignore_index=True)
        assert combined_df.shape == (10, 57)
        assert combined_df.isnull().sum().sum() == 0


class TestFeatureConsistency:
    """Test that features are consistent and reproducible"""

    def test_same_transaction_same_features(self):
        """Test that same transaction produces same features"""
        transaction = RealTransaction(
            card_number="1234-5678-9012-3456",
            transaction_amount=100.0,
            merchant_name="Store",
            merchant_category="Retail",
            transaction_type="Purchase",
            location_city="NYC",
            location_country="USA",
            card_type="Visa",
            transaction_hour=12,
            day_of_week=3,
            is_online=False,
            is_international=False,
            distance_from_home=5.0
        )

        # Generate features twice
        v_features1 = ImprovedFeatureMapper.map_to_v_features(transaction)
        df1 = FeatureEngineer.create_features(v_features1, transaction)

        v_features2 = ImprovedFeatureMapper.map_to_v_features(transaction)
        df2 = FeatureEngineer.create_features(v_features2, transaction)

        # Should be identical
        pd.testing.assert_frame_equal(df1, df2)


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '--tb=short'])
