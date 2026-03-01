"""
Fraud Scoring Service with Abstract Base Class
===============================================
Demonstrates the Open/Closed Principle - open for extension, closed for modification.

By using an abstract base class (ABC), we can:
1. Define the interface that all fraud scorers must implement
2. Easily swap scoring algorithms without changing code that uses them
3. Test with mock scorers
4. Add new scoring strategies (ML-based, rules-based, hybrid) without modifying existing code

OOP Principles Demonstrated:
- Abstraction: FraudScorer defines what, not how
- Encapsulation: Scoring logic is contained in scorer classes
- Open/Closed: New scorers can be added without modifying existing code
- Dependency Inversion: High-level code depends on abstraction, not concrete implementation
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config


class FraudScorer(ABC):
    """
    Abstract base class for fraud scoring algorithms.

    Any class that inherits from this MUST implement the calculate_score() method.
    This ensures consistency across different scoring implementations.

    Example:
        class MLFraudScorer(FraudScorer):
            def calculate_score(self, transaction: Dict) -> float:
                # Use ML model to score
                return model.predict_proba(features)[0][1]
    """

    @abstractmethod
    def calculate_score(self, transaction: Any) -> float:
        """
        Calculate fraud suspicion score for a transaction.

        Args:
            transaction: Transaction data (type depends on implementation)

        Returns:
            Fraud score between 0.0 (legitimate) and 1.0 (definitely fraud)

        Raises:
            Should not raise exceptions - return 0.0 if calculation fails
        """
        pass

    @abstractmethod
    def get_scorer_info(self) -> Dict[str, Any]:
        """
        Get information about this scorer for logging/debugging.

        Returns:
            Dictionary with scorer metadata (name, version, thresholds, etc.)
        """
        pass


class RuleBasedFraudScorer(FraudScorer):
    """
    Rule-based fraud scorer using heuristic thresholds.

    This implementation uses business rules to calculate fraud suspicion:
    - High transaction amounts
    - International transactions
    - Unusual hours (late night/early morning)
    - Distance from home
    - Combination of risk factors

    Thresholds are configurable via Config class.
    """

    def __init__(self, config: Config = None):
        """
        Initialize rule-based fraud scorer.

        Args:
            config: Configuration object with thresholds. If None, uses default Config.
        """
        self.config = config or Config
        self.thresholds = self.config.FRAUD_THRESHOLDS
        self.weights = self.config.FRAUD_SCORE_WEIGHTS

    def calculate_score(self, transaction: Any) -> float:
        """
        Calculate fraud score using rule-based heuristics.

        Scoring logic:
        1. Amount-based scoring (critical/high/medium thresholds)
        2. International transaction flag
        3. Distance from home
        4. Unusual transaction hours
        5. Online + high amount combination
        6. Bonus for multiple risk factors

        Args:
            transaction: RealTransaction object with transaction details

        Returns:
            Fraud score between 0.0 and 1.0
        """
        try:
            fraud_score = 0.0

            # Amount-based scoring
            amount = transaction.transaction_amount
            if amount > self.thresholds["amount_critical"]:
                fraud_score += self.weights["amount_critical"]
            elif amount > self.thresholds["amount_high"]:
                fraud_score += self.weights["amount_high"]
            elif amount > self.thresholds["amount_medium"]:
                fraud_score += self.weights["amount_medium"]

            # International transaction
            if transaction.is_international:
                fraud_score += self.weights["international"]

            # Distance from home
            distance = transaction.distance_from_home
            if distance > self.thresholds["distance_suspicious"]:
                fraud_score += self.weights["distance"]
            elif distance > 500:
                fraud_score += self.weights["distance"] * 0.75
            elif distance > 100:
                fraud_score += self.weights["distance"] * 0.5

            # Unusual hours (early morning is most suspicious)
            hour = transaction.transaction_hour
            if hour in [0, 1, 2, 3, 4]:  # 12am - 4am
                fraud_score += self.weights["unusual_hour"]
            elif hour in [22, 23]:  # 10pm - 11pm
                fraud_score += self.weights["unusual_hour"] * 0.67

            # Online + high amount combination
            if transaction.is_online and amount > self.thresholds["amount_medium"]:
                fraud_score += self.weights["online_high_amount"]

            # Count cumulative risk factors and add bonus if many present
            risk_factors = self._count_risk_factors(transaction)
            if risk_factors >= 3:
                fraud_score += self.weights["risk_factor_bonus"]

            # Cap at 1.0
            return min(1.0, fraud_score)

        except Exception as e:
            # Log error but don't crash - return neutral score
            print(f"Error calculating fraud score: {e}")
            return 0.0

    def _count_risk_factors(self, transaction: Any) -> int:
        """
        Count number of risk factors present in transaction.

        Risk factors:
        - High amount (> $2000)
        - International
        - Far from home (> 500km)
        - Very early morning (< 6am)

        Args:
            transaction: Transaction to analyze

        Returns:
            Number of risk factors (0-4)
        """
        risk_count = 0

        if transaction.transaction_amount > self.thresholds["amount_high"]:
            risk_count += 1
        if transaction.is_international:
            risk_count += 1
        if transaction.distance_from_home > 500:
            risk_count += 1
        if transaction.transaction_hour < 6:
            risk_count += 1

        return risk_count

    def get_scorer_info(self) -> Dict[str, Any]:
        """
        Get information about this scorer.

        Returns:
            Dictionary with scorer metadata
        """
        return {
            "scorer_type": "RuleBasedFraudScorer",
            "version": "1.0",
            "thresholds": self.thresholds,
            "weights": self.weights,
            "description": "Heuristic-based fraud scoring using business rules"
        }

    def explain_score(self, transaction: Any) -> Dict[str, Any]:
        """
        Explain how fraud score was calculated for a transaction.

        Useful for debugging and showing users why a transaction was flagged.

        Args:
            transaction: Transaction to explain

        Returns:
            Dictionary with score breakdown
        """
        explanation = {
            "total_score": 0.0,
            "factors": []
        }

        # Check each factor and explain contribution
        amount = transaction.transaction_amount

        if amount > self.thresholds["amount_critical"]:
            contribution = self.weights["amount_critical"]
            explanation["factors"].append({
                "factor": "Critical Amount",
                "value": f"${amount:.2f}",
                "contribution": contribution,
                "reason": f"Amount > ${self.thresholds['amount_critical']}"
            })
            explanation["total_score"] += contribution
        elif amount > self.thresholds["amount_high"]:
            contribution = self.weights["amount_high"]
            explanation["factors"].append({
                "factor": "High Amount",
                "value": f"${amount:.2f}",
                "contribution": contribution,
                "reason": f"Amount > ${self.thresholds['amount_high']}"
            })
            explanation["total_score"] += contribution

        if transaction.is_international:
            contribution = self.weights["international"]
            explanation["factors"].append({
                "factor": "International Transaction",
                "value": True,
                "contribution": contribution,
                "reason": "Transaction from foreign country"
            })
            explanation["total_score"] += contribution

        distance = transaction.distance_from_home
        if distance > self.thresholds["distance_suspicious"]:
            contribution = self.weights["distance"]
            explanation["factors"].append({
                "factor": "Distance from Home",
                "value": f"{distance:.1f} km",
                "contribution": contribution,
                "reason": f"Distance > {self.thresholds['distance_suspicious']} km"
            })
            explanation["total_score"] += contribution

        hour = transaction.transaction_hour
        if hour in [0, 1, 2, 3, 4]:
            contribution = self.weights["unusual_hour"]
            explanation["factors"].append({
                "factor": "Unusual Hour",
                "value": f"{hour}:00",
                "contribution": contribution,
                "reason": "Early morning transaction (12am-4am)"
            })
            explanation["total_score"] += contribution

        risk_count = self._count_risk_factors(transaction)
        if risk_count >= 3:
            contribution = self.weights["risk_factor_bonus"]
            explanation["factors"].append({
                "factor": "Multiple Risk Factors",
                "value": risk_count,
                "contribution": contribution,
                "reason": f"{risk_count} risk factors present"
            })
            explanation["total_score"] += contribution

        explanation["total_score"] = min(1.0, explanation["total_score"])
        return explanation


class MLFraudScorer(FraudScorer):
    """
    Machine Learning-based fraud scorer (placeholder for future implementation).

    This would use a trained ML model (separate from the main KNN model)
    specifically for quick fraud scoring before full feature engineering.

    Could use:
    - Lightweight model (Logistic Regression, simple neural net)
    - Fewer features (just amount, location, time)
    - Faster inference than full KNN with 57 features
    """

    def __init__(self, model_path: str = None):
        """
        Initialize ML-based fraud scorer.

        Args:
            model_path: Path to trained model (if None, falls back to rules)
        """
        self.model_path = model_path
        self.model = None
        # TODO: Load model if path provided

    def calculate_score(self, transaction: Any) -> float:
        """
        Calculate fraud score using ML model.

        Currently not implemented - falls back to 0.5 (neutral score).

        Args:
            transaction: Transaction data

        Returns:
            Fraud probability from ML model
        """
        # TODO: Implement ML-based scoring
        # For now, return neutral score
        return 0.5

    def get_scorer_info(self) -> Dict[str, Any]:
        """Get ML scorer information"""
        return {
            "scorer_type": "MLFraudScorer",
            "version": "0.1-placeholder",
            "model_path": self.model_path,
            "description": "ML-based fraud scoring (not yet implemented)"
        }


# Factory function for creating scorers
def create_fraud_scorer(scorer_type: str = "rule_based", **kwargs) -> FraudScorer:
    """
    Factory function to create fraud scorer instances.

    This demonstrates the Factory Pattern - centralizes object creation
    and makes it easy to swap implementations.

    Args:
        scorer_type: Type of scorer ("rule_based" or "ml")
        **kwargs: Additional arguments for scorer initialization

    Returns:
        FraudScorer instance

    Example:
        scorer = create_fraud_scorer("rule_based")
        score = scorer.calculate_score(transaction)
    """
    if scorer_type == "rule_based":
        return RuleBasedFraudScorer(**kwargs)
    elif scorer_type == "ml":
        return MLFraudScorer(**kwargs)
    else:
        raise ValueError(f"Unknown scorer type: {scorer_type}")


if __name__ == "__main__":
    # Demonstration
    from main import RealTransaction

    print("Fraud Scorer Demonstration\n" + "="*50)

    # Create a sample transaction
    transaction = RealTransaction(
        card_number="3456",  # Last 4 digits
        transaction_amount=6500.0,  # High amount
        merchant_name="Overseas Store",
        merchant_category="Electronics",
        transaction_type="Purchase",
        location_city="London",
        location_country="UK",
        card_type="Visa",
        transaction_hour=2,  # 2 AM
        day_of_week=3,
        is_online=True,
        is_international=True,  # International
        distance_from_home=3500.0  # Far from home
    )

    # Create scorer and calculate score
    scorer = create_fraud_scorer("rule_based")
    score = scorer.calculate_score(transaction)

    print(f"\n📊 Transaction Analysis:")
    print(f"   Amount: ${transaction.transaction_amount:.2f}")
    print(f"   International: {transaction.is_international}")
    print(f"   Distance: {transaction.distance_from_home} km")
    print(f"   Hour: {transaction.transaction_hour}:00")

    print(f"\n🎯 Fraud Score: {score:.3f} ({score*100:.1f}%)")

    print(f"\n📋 Scorer Info:")
    import json
    print(json.dumps(scorer.get_scorer_info(), indent=2))

    print(f"\n💡 Score Explanation:")
    explanation = scorer.explain_score(transaction)
    print(json.dumps(explanation, indent=2))
