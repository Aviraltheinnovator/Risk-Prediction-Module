"""
Risk Prediction Model - Inference

This module loads a trained model and makes risk predictions for new features/code changes.
"""

import pickle
import logging
from typing import Dict, Tuple, List, Optional
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskPredictor:
    """Loads and uses trained risk prediction model"""

    # Risk levels
    RISK_LEVELS = {
        0: 'Low',
        1: 'Medium',
        2: 'High'
    }

    def __init__(self, model_path: str):
        """Initialize predictor with trained model"""
        logger.info(f"Loading model from {model_path}")

        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)

            self.model = model_data['model']
            self.label_encoders = model_data['label_encoders']
            self.feature_names = model_data['feature_names']
            self.is_loaded = True

            logger.info("Model loaded successfully")
        except FileNotFoundError:
            logger.error(f"Model file not found: {model_path}")
            self.is_loaded = False

    def predict(self, features: Dict) -> Tuple[float, str, Dict]:
        """
        Make risk prediction for a feature

        Args:
            features: Dictionary with feature values

        Returns:
            Tuple of (risk_score, risk_level, probabilities)
        """

        if not self.is_loaded:
            raise RuntimeError("Model not loaded")

        # Prepare feature vector
        feature_vector = self._prepare_features(features)

        # Get probabilities
        probabilities = self.model.predict_proba([feature_vector])[0]

        # Get prediction
        risk_class = self.model.predict([feature_vector])[0]
        risk_level = self.RISK_LEVELS.get(risk_class, 'Unknown')

        # Calculate risk score (0-100) based on max probability
        # High risk = class 2, Medium = class 1, Low = class 0
        risk_score = max(probabilities) * 100

        # Adjust score based on class: if High risk class, emphasize higher score
        if risk_class == 2:  # High risk
            risk_score = max(67, risk_score)
        elif risk_class == 1:  # Medium risk
            if risk_score < 34:
                risk_score = 34
            if risk_score > 66:
                risk_score = 66

        prob_dict = {
            'Low': float(probabilities[0]),
            'Medium': float(probabilities[1]),
            'High': float(probabilities[2])
        }

        logger.info(f"Prediction: {risk_level} ({risk_score:.0f}%)")

        return risk_score, risk_level, prob_dict

    def predict_batch(self, features_list: List[Dict]) -> List[Dict]:
        """Make predictions for multiple features"""

        results = []
        for i, features in enumerate(features_list):
            risk_score, risk_level, probs = self.predict(features)
            results.append({
                'index': i,
                'risk_score': risk_score,
                'risk_level': risk_level,
                'probabilities': probs
            })

        return results

    def _prepare_features(self, features: Dict) -> np.ndarray:
        """Convert feature dictionary to model input vector"""

        vector = []

        for feature_name in self.feature_names:
            if feature_name not in features:
                raise ValueError(f"Missing required feature: {feature_name}")

            value = features[feature_name]

            # Encode categorical features
            if feature_name in self.label_encoders:
                le = self.label_encoders[feature_name]
                if isinstance(value, str):
                    value = le.transform([value])[0]

            vector.append(value)

        return np.array(vector).reshape(1, -1)[0]

    def get_feature_names(self) -> List[str]:
        """Get list of required feature names"""
        return self.feature_names


# Example usage
def example_predictions():
    """Example: Make predictions on sample features"""

    predictor = RiskPredictor('models/risk_model.pkl')

    # Example 1: Low risk change
    low_risk_features = {
        'module': 'Auth',
        'files_changed': 3,
        'lines_added': 50,
        'lines_deleted': 20,
        'complexity_score': 2,
        'developer_experience': 'Senior',
        'team_size': 1,
        'past_defect_rate': 0.05,
        'test_coverage': 0.95,
        'automation_coverage': 0.90,
        'regression_failures': 0,
        'story_points': 3,
        'dependencies': 0,
        'days_to_release': 15,
        'bugs_found': 0
    }

    print("\n=== Example 1: Low Risk ===")
    try:
        score, level, probs = predictor.predict(low_risk_features)
        print(f"Risk Score: {score:.0f}%")
        print(f"Risk Level: {level}")
        print(f"Probabilities: {probs}")
    except Exception as e:
        print(f"Error: {e}")

    # Example 2: Medium risk change
    medium_risk_features = {
        'module': 'Commerce',
        'files_changed': 7,
        'lines_added': 250,
        'lines_deleted': 85,
        'complexity_score': 3,
        'developer_experience': 'Mid',
        'team_size': 2,
        'past_defect_rate': 0.12,
        'test_coverage': 0.68,
        'automation_coverage': 0.58,
        'regression_failures': 3,
        'story_points': 6,
        'dependencies': 2,
        'days_to_release': 11,
        'bugs_found': 3
    }

    print("\n=== Example 2: Medium Risk ===")
    try:
        score, level, probs = predictor.predict(medium_risk_features)
        print(f"Risk Score: {score:.0f}%")
        print(f"Risk Level: {level}")
        print(f"Probabilities: {probs}")
    except Exception as e:
        print(f"Error: {e}")

    # Example 3: High risk change
    high_risk_features = {
        'module': 'Payment',
        'files_changed': 14,
        'lines_added': 650,
        'lines_deleted': 200,
        'complexity_score': 8,
        'developer_experience': 'Junior',
        'team_size': 2,
        'past_defect_rate': 0.20,
        'test_coverage': 0.45,
        'automation_coverage': 0.40,
        'regression_failures': 6,
        'story_points': 13,
        'dependencies': 3,
        'days_to_release': 5,
        'bugs_found': 8
    }

    print("\n=== Example 3: High Risk ===")
    try:
        score, level, probs = predictor.predict(high_risk_features)
        print(f"Risk Score: {score:.0f}%")
        print(f"Risk Level: {level}")
        print(f"Probabilities: {probs}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    example_predictions()
