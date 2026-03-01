"""
Comprehensive Test Suite for KNN Classifier
===========================================
Tests the from-scratch KNN implementation for correctness,
edge cases, and comparison with sklearn's implementation.
"""

import pytest
import numpy as np
from sklearn.neighbors import KNeighborsClassifier as SklearnKNN
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import sys
from pathlib import Path

# Add parent directory to path to import knn_classifier
sys.path.insert(0, str(Path(__file__).parent.parent))
from knn_classifier import KNNClassifier


class TestKNNBasics:
    """Test basic KNN functionality"""

    def test_initialization(self):
        """Test KNN initializes with correct parameters"""
        knn = KNNClassifier(k=5, distance_metric='euclidean', weights='uniform')
        assert knn.k == 5
        assert knn.distance_metric == 'euclidean'
        assert knn.weights == 'uniform'

    def test_fit_stores_training_data(self):
        """Test that fit() properly stores training data (lazy learning)"""
        knn = KNNClassifier(k=3)
        X_train = np.array([[1, 2], [3, 4], [5, 6]])
        y_train = np.array([0, 1, 0])

        knn.fit(X_train, y_train)

        assert np.array_equal(knn.X_train, X_train)
        assert np.array_equal(knn.y_train, y_train)
        assert hasattr(knn, 'X_train') and hasattr(knn, 'y_train')

    def test_simple_2d_classification(self):
        """Test KNN on simple 2D dataset"""
        # Create simple dataset: points at (0,0) and (10,10) are class 0, (0,10) and (10,0) are class 1
        X_train = np.array([[0, 0], [0, 10], [10, 0], [10, 10]])
        y_train = np.array([0, 1, 1, 0])

        knn = KNNClassifier(k=1, distance_metric='euclidean')
        knn.fit(X_train, y_train)

        # Test point near (0,0) should be class 0
        assert knn.predict([[1, 1]])[0] == 0
        # Test point near (0,10) should be class 1
        assert knn.predict([[1, 9]])[0] == 1


class TestDistanceMetrics:
    """Test different distance metrics"""

    def test_euclidean_distance(self):
        """Test Euclidean distance metric"""
        knn = KNNClassifier(k=3, distance_metric='euclidean')
        X_train = np.array([[0, 0], [1, 1], [2, 2]])
        y_train = np.array([0, 0, 1])

        knn.fit(X_train, y_train)
        pred = knn.predict([[0.5, 0.5]])
        assert pred[0] == 0  # Closer to first two points

    def test_manhattan_distance(self):
        """Test Manhattan distance metric"""
        knn = KNNClassifier(k=3, distance_metric='manhattan')
        X_train = np.array([[0, 0], [1, 1], [2, 2]])
        y_train = np.array([0, 0, 1])

        knn.fit(X_train, y_train)
        pred = knn.predict([[0.5, 0.5]])
        assert pred[0] == 0

    def test_minkowski_distance(self):
        """Test Minkowski distance metric"""
        knn = KNNClassifier(k=3, distance_metric='minkowski', p=3)
        X_train = np.array([[0, 0], [1, 1], [2, 2]])
        y_train = np.array([0, 0, 1])

        knn.fit(X_train, y_train)
        pred = knn.predict([[0.5, 0.5]])
        assert pred[0] == 0


class TestWeightingSchemes:
    """Test uniform vs distance-weighted voting"""

    def test_uniform_weights(self):
        """Test uniform weighting (all neighbors count equally)"""
        # Dataset where uniform voting gives different result than distance weighting
        X_train = np.array([[0, 0], [0.1, 0.1], [5, 5]])  # Two class-0 close together, one class-1 far
        y_train = np.array([0, 0, 1])

        knn = KNNClassifier(k=3, weights='uniform')
        knn.fit(X_train, y_train)

        # Point at (1,1) - with uniform weights, majority is class 0
        pred = knn.predict([[1, 1]])
        assert pred[0] == 0

    def test_distance_weights(self):
        """Test distance-weighted voting (closer neighbors count more)"""
        X_train = np.array([[0, 0], [1, 1], [10, 10]])
        y_train = np.array([0, 0, 1])

        knn = KNNClassifier(k=3, weights='distance')
        knn.fit(X_train, y_train)

        # Closer neighbors should have more weight
        pred = knn.predict([[0.5, 0.5]])
        assert pred[0] == 0


class TestProbabilityPrediction:
    """Test probability prediction functionality"""

    def test_predict_proba_shape(self):
        """Test that predict_proba returns correct shape"""
        X_train = np.array([[0, 0], [1, 1], [2, 2], [3, 3]])
        y_train = np.array([0, 0, 1, 1])

        knn = KNNClassifier(k=3)
        knn.fit(X_train, y_train)

        proba = knn.predict_proba([[1.5, 1.5]])
        assert proba.shape == (1, 2)  # 1 sample, 2 classes

    def test_predict_proba_sums_to_one(self):
        """Test that probabilities sum to 1"""
        X_train = np.array([[0, 0], [1, 1], [2, 2], [3, 3]])
        y_train = np.array([0, 0, 1, 1])

        knn = KNNClassifier(k=3)
        knn.fit(X_train, y_train)

        proba = knn.predict_proba([[1.5, 1.5]])
        assert np.allclose(proba.sum(axis=1), 1.0)

    def test_predict_proba_uniform_vs_distance(self):
        """Test that distance weighting affects probabilities"""
        X_train = np.array([[0, 0], [0.1, 0.1], [5, 5]])
        y_train = np.array([0, 0, 1])

        # With uniform weights
        knn_uniform = KNNClassifier(k=3, weights='uniform')
        knn_uniform.fit(X_train, y_train)
        proba_uniform = knn_uniform.predict_proba([[0.5, 0.5]])

        # With distance weights
        knn_distance = KNNClassifier(k=3, weights='distance')
        knn_distance.fit(X_train, y_train)
        proba_distance = knn_distance.predict_proba([[0.5, 0.5]])

        # Distance weighting should give higher confidence to class 0 (closer neighbors)
        assert proba_distance[0, 0] > proba_uniform[0, 0]


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_k_equals_1(self):
        """Test with K=1 (nearest neighbor only)"""
        X_train = np.array([[0, 0], [1, 1], [2, 2]])
        y_train = np.array([0, 1, 1])

        knn = KNNClassifier(k=1)
        knn.fit(X_train, y_train)

        # Point very close to [0,0] should be class 0
        pred = knn.predict([[0.01, 0.01]])
        assert pred[0] == 0

    def test_k_larger_than_dataset(self):
        """Test that K larger than dataset size doesn't break"""
        X_train = np.array([[0, 0], [1, 1]])
        y_train = np.array([0, 1])

        # K=5 but only 2 samples - should use all available samples
        knn = KNNClassifier(k=5)
        knn.fit(X_train, y_train)

        pred = knn.predict([[0.1, 0.1]])
        assert pred[0] in [0, 1]  # Should still make a prediction

    def test_all_same_class(self):
        """Test dataset with only one class"""
        X_train = np.array([[0, 0], [1, 1], [2, 2]])
        y_train = np.array([1, 1, 1])  # All class 1

        knn = KNNClassifier(k=3)
        knn.fit(X_train, y_train)

        pred = knn.predict([[5, 5]])
        assert pred[0] == 1  # Should always predict class 1

    def test_tie_breaking(self):
        """Test tie-breaking behavior with even K"""
        X_train = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
        y_train = np.array([0, 0, 1, 1])

        knn = KNNClassifier(k=4, weights='uniform')
        knn.fit(X_train, y_train)

        # Point at center - should be tie, uses Counter.most_common which picks first occurrence
        pred = knn.predict([[0.5, 0.5]])
        assert pred[0] in [0, 1]  # Either is valid for a tie


class TestComparisonWithSklearn:
    """Compare our implementation with sklearn's KNN"""

    def test_predictions_match_sklearn_euclidean(self):
        """Test that predictions match sklearn with Euclidean distance"""
        np.random.seed(42)
        X, y = make_classification(n_samples=100, n_features=5, n_informative=3,
                                   n_redundant=0, n_classes=2, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # Our implementation
        our_knn = KNNClassifier(k=5, distance_metric='euclidean', weights='uniform')
        our_knn.fit(X_train, y_train)
        our_pred = our_knn.predict(X_test)

        # Sklearn implementation
        sklearn_knn = SklearnKNN(n_neighbors=5, metric='euclidean', weights='uniform')
        sklearn_knn.fit(X_train, y_train)
        sklearn_pred = sklearn_knn.predict(X_test)

        # Should have very high agreement (>95%)
        agreement = accuracy_score(sklearn_pred, our_pred)
        assert agreement > 0.95, f"Only {agreement:.1%} agreement with sklearn"

    def test_predictions_match_sklearn_manhattan(self):
        """Test that predictions match sklearn with Manhattan distance"""
        np.random.seed(42)
        X, y = make_classification(n_samples=100, n_features=5, n_informative=3,
                                   n_redundant=0, n_classes=2, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # Our implementation
        our_knn = KNNClassifier(k=5, distance_metric='manhattan', weights='uniform')
        our_knn.fit(X_train, y_train)
        our_pred = our_knn.predict(X_test)

        # Sklearn implementation
        sklearn_knn = SklearnKNN(n_neighbors=5, metric='manhattan', weights='uniform')
        sklearn_knn.fit(X_train, y_train)
        sklearn_pred = sklearn_knn.predict(X_test)

        # Should have very high agreement (>95%)
        agreement = accuracy_score(sklearn_pred, our_pred)
        assert agreement > 0.95, f"Only {agreement:.1%} agreement with sklearn"

    def test_distance_weighted_vs_sklearn(self):
        """Test distance-weighted predictions match sklearn"""
        np.random.seed(42)
        X, y = make_classification(n_samples=100, n_features=5, n_informative=3,
                                   n_redundant=0, n_classes=2, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # Our implementation
        our_knn = KNNClassifier(k=5, distance_metric='euclidean', weights='distance')
        our_knn.fit(X_train, y_train)
        our_pred = our_knn.predict(X_test)

        # Sklearn implementation
        sklearn_knn = SklearnKNN(n_neighbors=5, metric='euclidean', weights='distance')
        sklearn_knn.fit(X_train, y_train)
        sklearn_pred = sklearn_knn.predict(X_test)

        # Should have very high agreement (>90% for weighted)
        agreement = accuracy_score(sklearn_pred, our_pred)
        assert agreement > 0.90, f"Only {agreement:.1%} agreement with sklearn"


class TestScoreMethod:
    """Test the score() method for accuracy calculation"""

    def test_score_calculation(self):
        """Test that score() returns correct accuracy"""
        X_train = np.array([[0, 0], [1, 1], [2, 2], [3, 3]])
        y_train = np.array([0, 0, 1, 1])
        X_test = np.array([[0.5, 0.5], [2.5, 2.5]])
        y_test = np.array([0, 1])

        knn = KNNClassifier(k=3)
        knn.fit(X_train, y_train)

        score = knn.score(X_test, y_test)
        assert 0 <= score <= 1  # Score should be between 0 and 1
        assert score == 1.0  # Should get 100% on this simple test


class TestMultipleTestSamples:
    """Test prediction on multiple samples at once"""

    def test_batch_prediction(self):
        """Test predicting on multiple samples"""
        X_train = np.array([[0, 0], [1, 1], [2, 2], [3, 3]])
        y_train = np.array([0, 0, 1, 1])

        knn = KNNClassifier(k=3)
        knn.fit(X_train, y_train)

        X_test = np.array([[0.5, 0.5], [2.5, 2.5], [1.5, 1.5]])
        preds = knn.predict(X_test)

        assert len(preds) == 3
        assert preds[0] == 0  # Near class 0 samples
        assert preds[1] == 1  # Near class 1 samples


class TestGetParams:
    """Test get_params() method"""

    def test_get_params_returns_dict(self):
        """Test that get_params() returns parameter dictionary"""
        knn = KNNClassifier(k=7, distance_metric='manhattan', weights='distance', p=3)
        params = knn.get_params()

        assert isinstance(params, dict)
        assert params['k'] == 7
        assert params['distance_metric'] == 'manhattan'
        assert params['weights'] == 'distance'
        assert params['p'] == 3


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '--tb=short'])
