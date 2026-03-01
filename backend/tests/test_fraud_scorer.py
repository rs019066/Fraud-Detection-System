"""
Test Suite for Fraud Scorer Service
====================================
Tests the fraud scoring abstraction and rule-based implementation.
Demonstrates testing of OOP patterns (abstract classes, concrete implementations).
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from services.fraud_scorer import (
    FraudScorer,
    RuleBasedFraudScorer,
    MLFraudScorer,
    create_fraud_scorer
)
from main import RealTransaction
from config import Config


class TestFraudScorerAbstraction:
    """Test the abstract base class interface"""

    def test_cannot_instantiate_abstract_class(self):
        """Test that FraudScorer (ABC) cannot be instantiated directly"""
        with pytest.raises(TypeError):
            scorer = FraudScorer()

    def test_concrete_classes_implement_interface(self):
        """Test that concrete scorers implement required methods"""
        # RuleBasedFraudScorer should implement all abstract methods
        scorer = RuleBasedFraudScorer()
        assert hasattr(scorer, 'calculate_score')
        assert hasattr(scorer, 'get_scorer_info')
        assert callable(scorer.calculate_score)
        assert callable(scorer.get_scorer_info)


class TestRuleBasedFraudScorer:
    """Test the rule-based fraud scoring implementation"""

    @pytest.fixture
    def scorer(self):
        """Create a rule-based fraud scorer for testing"""
        return RuleBasedFraudScorer()

    @pytest.fixture
    def normal_transaction(self):
        """Create a normal, low-risk transaction"""
        return RealTransaction(
            card_number="1234",
            transaction_amount=50.0,
            merchant_name="Local Store",
            merchant_category="Retail",
            transaction_type="Purchase",
            location_city="Home City",
            location_country="USA",
            card_type="Visa",
            transaction_hour=14,  # 2 PM
            day_of_week=3,
            is_online=False,
            is_international=False,
            distance_from_home=2.0  # 2km from home
        )

    @pytest.fixture
    def suspicious_transaction(self):
        """Create a highly suspicious transaction"""
        return RealTransaction(
            card_number="5678",
            transaction_amount=8000.0,  # Very high amount
            merchant_name="Foreign Store",
            merchant_category="Electronics",
            transaction_type="Purchase",
            location_city="Foreign City",
            location_country="ForeignCountry",
            card_type="Visa",
            transaction_hour=2,  # 2 AM
            day_of_week=3,
            is_online=True,
            is_international=True,
            distance_from_home=5000.0  # 5000km from home
        )

    def test_initialize_with_config(self):
        """Test that scorer can be initialized with custom config"""
        scorer = RuleBasedFraudScorer(config=Config)
        assert scorer.config == Config
        assert scorer.thresholds == Config.FRAUD_THRESHOLDS
        assert scorer.weights == Config.FRAUD_SCORE_WEIGHTS

    def test_score_range(self, scorer, normal_transaction, suspicious_transaction):
        """Test that scores are in valid range [0, 1]"""
        normal_score = scorer.calculate_score(normal_transaction)
        suspicious_score = scorer.calculate_score(suspicious_transaction)

        assert 0 <= normal_score <= 1
        assert 0 <= suspicious_score <= 1

    def test_high_amount_increases_score(self, scorer):
        """Test that high transaction amounts increase fraud score"""
        low_amount_txn = RealTransaction(
            card_number="1234",
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

        high_amount_txn = RealTransaction(
            card_number="1234",
            transaction_amount=6000.0,  # Above critical threshold
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

        low_score = scorer.calculate_score(low_amount_txn)
        high_score = scorer.calculate_score(high_amount_txn)

        assert high_score > low_score

    def test_international_increases_score(self, scorer):
        """Test that international transactions increase fraud score"""
        domestic = RealTransaction(
            card_number="1234",
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

        international = RealTransaction(
            card_number="1234",
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

        domestic_score = scorer.calculate_score(domestic)
        international_score = scorer.calculate_score(international)

        assert international_score > domestic_score

    def test_unusual_hours_increase_score(self, scorer):
        """Test that early morning transactions increase fraud score"""
        normal_hour = RealTransaction(
            card_number="1234",
            transaction_amount=100.0,
            merchant_name="Store",
            merchant_category="Retail",
            transaction_type="Purchase",
            location_city="NYC",
            location_country="USA",
            card_type="Visa",
            transaction_hour=14,  # 2 PM - normal
            day_of_week=3,
            is_online=False,
            is_international=False,
            distance_from_home=5.0
        )

        unusual_hour = RealTransaction(
            card_number="1234",
            transaction_amount=100.0,
            merchant_name="Store",
            merchant_category="Retail",
            transaction_type="Purchase",
            location_city="NYC",
            location_country="USA",
            card_type="Visa",
            transaction_hour=2,  # 2 AM - suspicious
            day_of_week=3,
            is_online=False,
            is_international=False,
            distance_from_home=5.0
        )

        normal_score = scorer.calculate_score(normal_hour)
        unusual_score = scorer.calculate_score(unusual_hour)

        assert unusual_score > normal_score

    def test_distance_increases_score(self, scorer):
        """Test that distance from home increases fraud score"""
        near_home = RealTransaction(
            card_number="1234",
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
            distance_from_home=5.0  # 5km - close
        )

        far_from_home = RealTransaction(
            card_number="1234",
            transaction_amount=100.0,
            merchant_name="Store",
            merchant_category="Retail",
            transaction_type="Purchase",
            location_city="LA",
            location_country="USA",
            card_type="Visa",
            transaction_hour=12,
            day_of_week=3,
            is_online=False,
            is_international=False,
            distance_from_home=1500.0  # 1500km - far
        )

        near_score = scorer.calculate_score(near_home)
        far_score = scorer.calculate_score(far_from_home)

        assert far_score > near_score

    def test_multiple_risk_factors_bonus(self, scorer, suspicious_transaction):
        """Test that multiple risk factors trigger bonus score"""
        # Suspicious transaction has 4+ risk factors
        risk_count = scorer._count_risk_factors(suspicious_transaction)
        assert risk_count >= 3

        score = scorer.calculate_score(suspicious_transaction)
        # Should have bonus applied
        assert score > 0.5  # High score due to multiple factors

    def test_count_risk_factors(self, scorer, normal_transaction, suspicious_transaction):
        """Test risk factor counting"""
        normal_risk_count = scorer._count_risk_factors(normal_transaction)
        suspicious_risk_count = scorer._count_risk_factors(suspicious_transaction)

        assert normal_risk_count == 0  # Normal transaction has no risk factors
        assert suspicious_risk_count >= 3  # Suspicious has multiple

    def test_get_scorer_info(self, scorer):
        """Test that get_scorer_info returns proper metadata"""
        info = scorer.get_scorer_info()

        assert isinstance(info, dict)
        assert info["scorer_type"] == "RuleBasedFraudScorer"
        assert "version" in info
        assert "thresholds" in info
        assert "weights" in info
        assert "description" in info

    def test_explain_score(self, scorer, suspicious_transaction):
        """Test score explanation functionality"""
        explanation = scorer.explain_score(suspicious_transaction)

        assert isinstance(explanation, dict)
        assert "total_score" in explanation
        assert "factors" in explanation
        assert isinstance(explanation["factors"], list)
        assert len(explanation["factors"]) > 0

        # Each factor should have required fields
        for factor in explanation["factors"]:
            assert "factor" in factor
            assert "value" in factor
            assert "contribution" in factor
            assert "reason" in factor

    def test_score_capped_at_one(self, scorer, suspicious_transaction):
        """Test that score is capped at 1.0 even with many risk factors"""
        score = scorer.calculate_score(suspicious_transaction)
        assert score <= 1.0


class TestMLFraudScorer:
    """Test the ML-based fraud scorer (placeholder implementation)"""

    def test_ml_scorer_initialization(self):
        """Test ML scorer can be initialized"""
        scorer = MLFraudScorer()
        assert scorer is not None

    def test_ml_scorer_implements_interface(self):
        """Test that ML scorer implements required methods"""
        scorer = MLFraudScorer()
        assert hasattr(scorer, 'calculate_score')
        assert hasattr(scorer, 'get_scorer_info')

    def test_ml_scorer_placeholder_returns_neutral_score(self):
        """Test that placeholder ML scorer returns 0.5 (neutral)"""
        scorer = MLFraudScorer()
        transaction = RealTransaction(
            card_number="1234",
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

        score = scorer.calculate_score(transaction)
        assert score == 0.5  # Placeholder implementation


class TestFactoryFunction:
    """Test the factory function for creating scorers"""

    def test_create_rule_based_scorer(self):
        """Test factory creates rule-based scorer"""
        scorer = create_fraud_scorer("rule_based")
        assert isinstance(scorer, RuleBasedFraudScorer)

    def test_create_ml_scorer(self):
        """Test factory creates ML scorer"""
        scorer = create_fraud_scorer("ml")
        assert isinstance(scorer, MLFraudScorer)

    def test_invalid_scorer_type_raises_error(self):
        """Test that invalid scorer type raises ValueError"""
        with pytest.raises(ValueError):
            scorer = create_fraud_scorer("invalid_type")

    def test_factory_passes_kwargs(self):
        """Test that factory passes kwargs to scorer"""
        scorer = create_fraud_scorer("rule_based", config=Config)
        assert scorer.config == Config


class TestScorerPolymorphism:
    """Test polymorphic behavior of different scorers"""

    def test_all_scorers_have_same_interface(self):
        """Test that all scorers can be used polymorphically"""
        scorers = [
            create_fraud_scorer("rule_based"),
            create_fraud_scorer("ml")
        ]

        transaction = RealTransaction(
            card_number="1234",
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

        # All scorers should work with same interface
        for scorer in scorers:
            score = scorer.calculate_score(transaction)
            assert 0 <= score <= 1

            info = scorer.get_scorer_info()
            assert isinstance(info, dict)


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '--tb=short'])
