"""
Risk Prediction Module

A machine learning solution for predicting defect risk in code changes
to enable data-driven QA testing prioritization.
"""

__version__ = "1.0.0"
__author__ = "Capstone Project"

from .predictor import RiskPredictor
from .train import RiskModelTrainer

__all__ = ['RiskPredictor', 'RiskModelTrainer']
