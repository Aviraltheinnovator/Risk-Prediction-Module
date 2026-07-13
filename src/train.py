"""
Risk Prediction Model Training Pipeline

This script trains a machine learning model to predict defect risk based on
code change metrics, developer experience, QA metrics, and story metrics.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
import pickle
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskModelTrainer:
    """Trains risk prediction model"""

    def __init__(self, test_size=0.2, random_state=42):
        self.test_size = test_size
        self.random_state = random_state
        self.model = None
        self.label_encoders = {}
        self.feature_names = None

    def load_data(self, filepath):
        """Load training data from CSV"""
        logger.info(f"Loading data from {filepath}")
        df = pd.read_csv(filepath)
        logger.info(f"Loaded {len(df)} records with {len(df.columns)} columns")
        return df

    def preprocess_data(self, df):
        """Preprocess and prepare data for training"""
        logger.info("Preprocessing data...")

        # Drop non-feature columns
        df = df.drop(['feature_id', 'feature_name'], axis=1)

        # Encode categorical variables
        categorical_features = ['module', 'developer_experience', 'risk_label']

        for col in categorical_features:
            if col in df.columns:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col])
                self.label_encoders[col] = le

        # Separate features and target
        X = df.drop('risk_label', axis=1)
        y = df['risk_label']

        self.feature_names = X.columns.tolist()

        logger.info(f"Features: {self.feature_names}")
        logger.info(f"Target distribution:\n{pd.Series(y).value_counts()}")

        return X, y

    def split_data(self, X, y):
        """Split data into train and test sets"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state, stratify=y
        )

        logger.info(f"Train set: {len(X_train)} samples")
        logger.info(f"Test set: {len(X_test)} samples")

        return X_train, X_test, y_train, y_test

    def train_model(self, X_train, y_train):
        """Train Random Forest classifier"""
        logger.info("Training Random Forest model...")

        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=self.random_state,
            n_jobs=-1
        )

        self.model.fit(X_train, y_train)

        logger.info("Model training completed")

        return self.model

    def evaluate_model(self, X_test, y_test):
        """Evaluate model performance"""
        logger.info("Evaluating model...")

        y_pred = self.model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')

        logger.info(f"Accuracy: {accuracy:.4f}")
        logger.info(f"Precision: {precision:.4f}")
        logger.info(f"Recall: {recall:.4f}")
        logger.info(f"F1-Score: {f1:.4f}")

        logger.info("\nConfusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        logger.info(cm)

        logger.info("\nClassification Report:")
        report = classification_report(y_test, y_pred)
        logger.info(report)

        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'confusion_matrix': cm
        }

    def cross_validate(self, X, y, cv=5):
        """Perform cross-validation"""
        logger.info(f"Performing {cv}-fold cross-validation...")

        scores = cross_val_score(self.model, X, y, cv=cv, scoring='f1_weighted')

        logger.info(f"CV Scores: {scores}")
        logger.info(f"Mean CV Score: {scores.mean():.4f} (+/- {scores.std():.4f})")

        return scores

    def get_feature_importance(self, top_n=10):
        """Get feature importance rankings"""
        if self.model is None:
            raise ValueError("Model not trained yet")

        importances = self.model.feature_importances_
        indices = np.argsort(importances)[::-1][:top_n]

        logger.info(f"\nTop {top_n} Important Features:")
        for i, idx in enumerate(indices):
            logger.info(f"{i+1}. {self.feature_names[idx]}: {importances[idx]:.4f}")

        return {self.feature_names[i]: importances[i] for i in indices}

    def save_model(self, filepath):
        """Save trained model to file"""
        logger.info(f"Saving model to {filepath}")

        model_data = {
            'model': self.model,
            'label_encoders': self.label_encoders,
            'feature_names': self.feature_names
        }

        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

        logger.info("Model saved successfully")


def main():
    """Main training pipeline"""

    # Configuration
    DATA_PATH = 'data/training_data.csv'
    MODEL_PATH = 'models/risk_model.pkl'

    # Initialize trainer
    trainer = RiskModelTrainer(test_size=0.2, random_state=42)

    # Load data
    df = trainer.load_data(DATA_PATH)

    # Preprocess
    X, y = trainer.preprocess_data(df)

    # Split data
    X_train, X_test, y_train, y_test = trainer.split_data(X, y)

    # Train model
    trainer.train_model(X_train, y_train)

    # Evaluate
    metrics = trainer.evaluate_model(X_test, y_test)

    # Cross-validate
    trainer.cross_validate(X, y, cv=5)

    # Feature importance
    trainer.get_feature_importance(top_n=10)

    # Save model
    trainer.save_model(MODEL_PATH)

    logger.info("\n✓ Training completed successfully!")


if __name__ == '__main__':
    main()
