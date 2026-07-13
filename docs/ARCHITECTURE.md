# Architecture & System Design

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Risk Prediction Pipeline                  │
└─────────────────────────────────────────────────────────────┘

1. DATA COLLECTION LAYER
   ├── Historical QA Data (CSV/Database)
   ├── Code Repository Metrics (Git)
   ├── Developer Information (HR Systems)
   └── Defect Tracking (JIRA/ServiceNow)

2. DATA PROCESSING LAYER
   ├── Data Cleaning
   ├── Missing Value Handling
   ├── Outlier Detection
   └── Feature Normalization

3. FEATURE ENGINEERING LAYER
   ├── Code Metrics Calculation
   ├── Developer Experience Scoring
   ├── Historical Risk Aggregation
   └── Interaction Features

4. MODEL TRAINING LAYER
   ├── Train/Test Split (80/20)
   ├── Hyperparameter Tuning
   ├── Cross-Validation
   └── Model Selection (RF/XGBoost/LightGBM)

5. PREDICTION LAYER
   ├── Risk Score Calculation (0-100)
   ├── Risk Level Classification (Low/Med/High)
   └── Feature Importance Extraction

6. EXPLAINABILITY LAYER
   ├── SHAP Value Computation
   ├── Top N Factor Extraction
   ├── Direction Analysis (↑ increases risk, ↓ decreases)
   └── LLM-based Text Generation

7. PRESENTATION LAYER
   ├── Dashboard Display
   ├── API Endpoints
   ├── Email Notifications
   └── Slack Integration
```

## Component Architecture

### 1. Data Module (`src/data/`)
Responsible for loading and preprocessing data.

```python
src/data/
├── loader.py              # Load from CSV, databases, APIs
├── cleaner.py             # Handle missing values, outliers
└── preprocessor.py        # Normalization, encoding
```

**Responsibilities:**
- Read historical feature data
- Handle missing values
- Remove duplicates
- Normalize ranges

### 2. Features Module (`src/features/`)
Transforms raw data into meaningful features.

```python
src/features/
├── code_metrics.py        # Files changed, lines added, complexity
├── developer_metrics.py   # Experience, team size, past defect rate
├── qa_metrics.py          # Test coverage, automation level
├── story_metrics.py       # Complexity, dependencies, points
└── feature_engineering.py # Combinations, interactions
```

**Output Features:**
```
[files_changed, lines_added, lines_deleted, complexity_score,
 developer_experience, team_size, past_defect_rate, 
 test_coverage, automation_coverage, historical_failure_rate,
 story_points, dependency_count, days_to_release, ...]
```

### 3. Model Module (`src/model/`)
Training and prediction logic.

```python
src/model/
├── train.py               # Model training pipeline
├── predictor.py           # Load model and make predictions
└── utils.py               # Cross-validation, metrics
```

**Supported Models:**
- Random Forest (baseline)
- XGBoost (gradient boosting)
- LightGBM (fast, memory-efficient)

### 4. Explainability Module (`src/explainability/`)
Makes predictions interpretable.

```python
src/explainability/
├── shap_explainer.py      # SHAP force plots, waterfall plots
├── importance.py          # Feature importance ranking
└── text_generator.py      # Natural language explanations
```

**Output:**
```
Risk Score: 87%
Risk Level: HIGH

Top Contributing Factors:
1. Large code churn (+18% impact) ↑ INCREASES RISK
2. Payment module history (+15% impact) ↑ INCREASES RISK
3. Low test coverage (+12% impact) ↑ INCREASES RISK
4. Multiple developers (+10% impact) ↑ INCREASES RISK
5. Senior review assigned (-8% impact) ↓ DECREASES RISK
```

## Data Schema

### Input Dataset (training_data.csv)

```csv
feature_id,feature_name,files_changed,lines_added,lines_deleted,complexity_score,
developer_experience,team_size,past_defect_rate,test_coverage,automation_coverage,
automation_failures,story_points,dependencies,days_to_release,risk_label

1,Login,5,120,45,2,Senior,3,0.05,0.95,0.90,0.02,3,1,15,Low
2,Cart,14,700,250,8,Junior,5,0.15,0.45,0.60,0.08,13,4,8,High
3,Search,2,30,15,1,Senior,2,0.02,0.92,0.85,0.01,2,0,15,Low
```

### Feature Definitions

| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| files_changed | int | 1-100 | Number of source files modified |
| lines_added | int | 0-5000 | Lines of code added |
| lines_deleted | int | 0-5000 | Lines of code deleted |
| complexity_score | float | 1-10 | Cyclomatic complexity |
| developer_experience | categorical | {Junior, Mid, Senior} | Developer seniority |
| team_size | int | 1-20 | Team members involved |
| past_defect_rate | float | 0-1 | Historical defect density |
| test_coverage | float | 0-1 | % of code covered by tests |
| automation_coverage | float | 0-1 | % automated tests |
| story_points | int | 1-40 | Estimated complexity |
| dependencies | int | 0-10 | Number of external dependencies |
| risk_label | categorical | {Low, Medium, High} | **TARGET VARIABLE** |

## Training Pipeline

```python
# 1. Load data
df = load_training_data()

# 2. Split features and target
X = df.drop('risk_label', axis=1)
y = df['risk_label']

# 3. Encode categorical variables
X = encode_categorical(X)

# 4. Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 5. Train model
model = XGBClassifier(n_estimators=100, max_depth=6)
model.fit(X_train, y_train)

# 6. Evaluate
accuracy = model.score(X_test, y_test)
print(f"Model Accuracy: {accuracy:.2%}")

# 7. Save model
model.save('models/risk_model.pkl')
```

## Prediction Pipeline

```python
# 1. Load trained model
predictor = RiskPredictor('models/risk_model.pkl')

# 2. Prepare input
features = {
    'files_changed': 12,
    'lines_added': 680,
    'developer_experience': 'Junior',
    'test_coverage': 0.65,
    # ... other features
}

# 3. Make prediction
risk_score, risk_level, probabilities = predictor.predict(features)

# 4. Generate explanation
explanation = explainer.explain(features, model)

# 5. Output
print(f"Risk: {risk_score}% ({risk_level})")
print(f"Explanation: {explanation}")
```

## Integration Points

### 1. Data Sources
- **JIRA/ServiceNow**: Feature history, bug counts
- **Git**: Files changed, lines modified, developers
- **Test Reporting**: Test counts, coverage %, failures
- **HR Systems**: Developer experience levels

### 2. Output Destinations
- **QA Dashboard**: Risk visualization
- **Slack Bot**: Automated notifications
- **JIRA Webhook**: Add risk label to tickets
- **Email Reports**: Daily risk summary

### 3. API Endpoints (Flask)
```
POST /predict
  Input: { features: {...} }
  Output: { risk_score, risk_level, explanation }

GET /model/metrics
  Output: { accuracy, precision, recall, f1 }

GET /dashboard
  Output: HTML dashboard
```

## Performance Considerations

- **Model Size**: ~5MB (XGBoost with 100 trees)
- **Prediction Time**: ~10ms per prediction
- **Training Time**: ~2 minutes on 10K records
- **Memory Usage**: ~200MB for loaded model + data

## Scalability

For production:
- Use PostgreSQL for historical data
- Cache predictions in Redis
- Deploy model as microservice (Docker)
- Use Kubernetes for scaling
- Implement monitoring & retraining schedule
