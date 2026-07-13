# API Reference

## Risk Prediction API

Python API for making risk predictions on code changes and features.

---

## RiskPredictor

Main class for making risk predictions using a trained model.

### Initialization

```python
from src.predictor import RiskPredictor

predictor = RiskPredictor(model_path='models/risk_model.pkl')
```

### Methods

#### `predict(features: Dict) -> Tuple[float, str, Dict]`

Make a risk prediction for a single feature.

**Parameters:**
- `features` (Dict): Dictionary containing feature values

**Required Features:**
```python
{
    'module': str,                      # Module name (Auth, Payment, etc.)
    'files_changed': int,               # Number of files modified
    'lines_added': int,                 # Lines of code added
    'lines_deleted': int,               # Lines of code deleted
    'complexity_score': float,          # Cyclomatic complexity (1-10)
    'developer_experience': str,        # 'Senior', 'Mid', 'Junior'
    'team_size': int,                   # Number of developers
    'past_defect_rate': float,          # Historical defect rate (0-1)
    'test_coverage': float,             # Test coverage percentage (0-1)
    'automation_coverage': float,       # Automation coverage (0-1)
    'regression_failures': int,         # Historical regression failures
    'story_points': int,                # Story complexity estimate
    'dependencies': int,                # Number of external dependencies
    'days_to_release': int,             # Days until release
    'bugs_found': int                   # Bugs found (for training only)
}
```

**Returns:**
- `risk_score` (float): Numeric risk score (0-100)
- `risk_level` (str): Risk category ('Low', 'Medium', 'High')
- `probabilities` (Dict): Probability for each class
  ```python
  {
      'Low': 0.15,
      'Medium': 0.35,
      'High': 0.50
  }
  ```

**Example:**

```python
features = {
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
    'bugs_found': 0
}

risk_score, risk_level, probs = predictor.predict(features)

print(f"Risk: {risk_score:.0f}% - {risk_level}")
# Output: Risk: 87% - High
```

---

#### `predict_batch(features_list: List[Dict]) -> List[Dict]`

Make predictions for multiple features.

**Parameters:**
- `features_list` (List[Dict]): List of feature dictionaries

**Returns:**
- List of prediction results

**Example:**

```python
features_list = [
    {'module': 'Auth', 'files_changed': 3, ...},
    {'module': 'Payment', 'files_changed': 14, ...},
    {'module': 'Search', 'files_changed': 2, ...}
]

results = predictor.predict_batch(features_list)

for result in results:
    print(f"Index: {result['index']}")
    print(f"Risk: {result['risk_score']:.0f}%")
    print(f"Level: {result['risk_level']}")
```

---

#### `get_feature_names() -> List[str]`

Get list of required feature names.

**Returns:**
- List of feature names in order

**Example:**

```python
feature_names = predictor.get_feature_names()
print(feature_names)
# Output: ['module', 'files_changed', 'lines_added', ...]
```

---

## RiskModelTrainer

Class for training the risk prediction model.

### Initialization

```python
from src.train import RiskModelTrainer

trainer = RiskModelTrainer(test_size=0.2, random_state=42)
```

### Methods

#### `load_data(filepath: str) -> pd.DataFrame`

Load training data from CSV.

**Example:**

```python
df = trainer.load_data('data/training_data.csv')
```

---

#### `preprocess_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]`

Preprocess data for training.

**Returns:**
- `X` (DataFrame): Features
- `y` (Series): Target variable

---

#### `split_data(X, y) -> Tuple`

Split data into train/test sets.

**Returns:**
- `X_train, X_test, y_train, y_test`

---

#### `train_model(X_train, y_train) -> Model`

Train Random Forest classifier.

---

#### `evaluate_model(X_test, y_test) -> Dict`

Evaluate model performance.

**Returns:**
- Dictionary with metrics:
  ```python
  {
      'accuracy': 0.85,
      'precision': 0.87,
      'recall': 0.84,
      'f1': 0.85,
      'confusion_matrix': array([[...]])
  }
  ```

---

#### `save_model(filepath: str) -> None`

Save trained model to file.

**Example:**

```python
trainer.save_model('models/risk_model.pkl')
```

---

## Complete Training Example

```python
from src.train import RiskModelTrainer

# Initialize
trainer = RiskModelTrainer(test_size=0.2, random_state=42)

# Load data
df = trainer.load_data('data/training_data.csv')

# Preprocess
X, y = trainer.preprocess_data(df)

# Split
X_train, X_test, y_train, y_test = trainer.split_data(X, y)

# Train
model = trainer.train_model(X_train, y_train)

# Evaluate
metrics = trainer.evaluate_model(X_test, y_test)
print(f"Accuracy: {metrics['accuracy']:.2%}")

# Cross-validate
scores = trainer.cross_validate(X, y, cv=5)

# Feature importance
importance = trainer.get_feature_importance(top_n=10)

# Save
trainer.save_model('models/risk_model.pkl')
```

---

## Complete Prediction Example

```python
from src.predictor import RiskPredictor

# Load model
predictor = RiskPredictor('models/risk_model.pkl')

# Define feature
features = {
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
    'bugs_found': 0
}

# Predict
risk_score, risk_level, probs = predictor.predict(features)

# Display results
print(f"Risk Score: {risk_score:.0f}%")
print(f"Risk Level: {risk_level}")
print(f"Probabilities:")
for level, prob in probs.items():
    print(f"  {level}: {prob:.1%}")
```

---

## Error Handling

```python
from src.predictor import RiskPredictor

try:
    predictor = RiskPredictor('models/risk_model.pkl')
except FileNotFoundError:
    print("Model file not found")

try:
    risk_score, risk_level, probs = predictor.predict(features)
except RuntimeError as e:
    print(f"Model not loaded: {e}")
except ValueError as e:
    print(f"Invalid features: {e}")
```

---

## Integration Example: Flask API

```python
from flask import Flask, request, jsonify
from src.predictor import RiskPredictor

app = Flask(__name__)
predictor = RiskPredictor('models/risk_model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    """Predict risk for a feature"""
    try:
        features = request.json
        risk_score, risk_level, probs = predictor.predict(features)
        
        return jsonify({
            'risk_score': risk_score,
            'risk_level': risk_level,
            'probabilities': probs
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/predict-batch', methods=['POST'])
def predict_batch():
    """Predict risk for multiple features"""
    try:
        features_list = request.json
        results = predictor.predict_batch(features_list)
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

---

## Risk Level Interpretation

| Risk Level | Risk Score | Recommended Action |
|-----------|-----------|-------------------|
| **Low** 🟢 | 0-33% | Quick sanity check, minimal testing |
| **Medium** 🟠 | 34-66% | Standard regression, manual UAT |
| **High** 🔴 | 67-100% | Full QA cycle, extended testing, phased rollout |
