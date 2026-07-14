# Risk Prediction Framework - Complete Guide

## Overview

This framework predicts defect risk for code changes by:
1. **Monitoring Git repositories** for code changes
2. **Extracting metrics** from commits (files changed, complexity, etc.)
3. **Running ML prediction** to assess risk
4. **Generating reports** with recommendations

---

## Repository Structure Explained

### 1. **Data Layer** (`data/training_data.csv`)

Historical training data with 85 features showing code changes and their outcomes:

```csv
feature_id, feature_name, files_changed, lines_added, complexity_score, 
developer_experience, test_coverage, bugs_found, risk_label

1, Login, 5, 120, 2, Senior, 0.95, 1, Low
2, Payment Gateway, 14, 780, 8, Junior, 0.45, 8, High
```

**Why it matters**: The ML model learns patterns from this data. Each row = one deployment/feature release.

---

### 2. **ML Pipeline** (`src/`)

#### **src/train.py** - Training Script
```python
trainer = RiskModelTrainer()
df = trainer.load_data('data/training_data.csv')
X, y = trainer.preprocess_data(df)
trainer.train_model(X_train, y_train)
trainer.save_model('models/risk_model.pkl')
```

**Flow**:
- Loads historical data
- Encodes categorical features (developer experience: Senior→0, Mid→1, Junior→2)
- Trains Random Forest classifier
- Saves trained model (~5MB)

#### **src/predictor.py** - Prediction Script
```python
predictor = RiskPredictor('models/risk_model.pkl')
risk_score, risk_level, probs = predictor.predict({
    'files_changed': 12,
    'lines_added': 650,
    'developer_experience': 'Junior',
    # ... other features
})
# Output: 87%, High, {'Low': 0.05, 'Medium': 0.08, 'High': 0.87}
```

---

### 3. **Code Examples** (`modules/`)

Real ServiceNow code at different risk levels:

| Module | Risk | Files | Lines | Reason |
|--------|------|-------|-------|--------|
| **auth_service.py** | 🟢 Low (15%) | 3 | 50 | Simple, well-tested, senior dev |
| **incident_management.py** | 🟠 Medium (55%) | 7 | 250 | Multiple files, mid-level team |
| **payment_integration.py** | 🔴 High (87%) | 14 | 780 | Complex, junior devs, 3 APIs |

These demonstrate what different risk levels look like in code.

---

### 4. **Documentation** (`docs/`)

- **ARCHITECTURE.md**: System design and data flow
- **RISK_METRICS.md**: How risk score is calculated (40% code, 25% developer, 20% QA, 15% story)
- **API.md**: Python API reference

---

### 5. **Analysis Examples** (`examples/code_changes.md`)

Before/after code comparisons showing:
- What code changed
- Why it's high/low/medium risk
- What testing is needed
- Real risk factors identified

---

## Current Features & Required Inputs

### Current Setup (Manual Input)

```python
features = {
    'module': 'Payment',
    'files_changed': 14,
    'lines_added': 650,
    'complexity_score': 8,
    'developer_experience': 'Junior',
    'team_size': 2,
    'past_defect_rate': 0.20,
    'test_coverage': 0.45,
    'automation_coverage': 0.40,
    'regression_failures': 6,
    'story_points': 13,
    'dependencies': 3,
    'days_to_release': 5
}

predictor.predict(features)  # Returns: 87%, High
```

**The problem**: You have to manually fill in these values. ❌

---

## The Gap: Git Integration

Currently, the framework requires you to manually input:
- ✗ How many files changed?
- ✗ How many lines added?
- ✗ Who developed it?
- ✗ What's the complexity?

**Solution**: Automatically extract these from Git commits! ✓

---

## Next Phase: Git Monitoring Framework

To make this framework **production-ready**, we need to:

### Phase 1: Git Metrics Extraction
Extract automatically from commits:
```
git diff HEAD~1
    ↓
Parse changed files
    ↓
Count lines changed
    ↓
Calculate complexity (cyclomatic complexity)
    ↓
Identify developers
    ↓
Look up historical data
```

### Phase 2: Automatic Prediction
When a PR/commit arrives:
```
1. Extract metrics from Git
2. Lookup developer experience
3. Get test coverage from CI
4. Run ML prediction
5. Post risk comment on PR
6. Suggest testing strategy
```

### Phase 3: Continuous Learning
Keep improving the model:
```
1. Monitor what bugs were found
2. Track prediction accuracy
3. Retrain model monthly
4. Improve predictions over time
```

---

## Implementation Roadmap

### **Phase 1: Git Integration Module** (What we'll build)

Create `src/git_monitor.py`:

```python
class GitRiskAnalyzer:
    def __init__(self, repo_path):
        self.repo = Repository(repo_path)
    
    def get_recent_commit_metrics(self, commit_sha):
        """Extract metrics from a single commit"""
        commit = self.repo.get_commit(commit_sha)
        
        # Calculate metrics
        files_changed = len(commit.changed_files)
        lines_added = sum(file.additions for file in commit.changed_files)
        lines_deleted = sum(file.deletions for file in commit.changed_files)
        complexity = calculate_complexity(commit.diff)
        
        return {
            'files_changed': files_changed,
            'lines_added': lines_added,
            'lines_deleted': lines_deleted,
            'complexity_score': complexity,
            'developer': commit.author.name,
            'timestamp': commit.timestamp
        }
    
    def analyze_pull_request(self, pr_number):
        """Analyze full PR for risk"""
        pr = self.repo.get_pull_request(pr_number)
        
        all_commits = pr.get_commits()
        total_files = set()
        total_lines_added = 0
        total_lines_deleted = 0
        
        for commit in all_commits:
            metrics = self.get_recent_commit_metrics(commit.sha)
            total_files.update(metrics['files_changed'])
            total_lines_added += metrics['lines_added']
            total_lines_deleted += metrics['lines_deleted']
        
        return {
            'files_changed': len(total_files),
            'lines_added': total_lines_added,
            'lines_deleted': total_lines_deleted,
            'developer_count': len(pr.get_contributors()),
            'complexity_score': avg_complexity
        }
```

---

### **Phase 2: Metrics Pipeline** (Extract all features)

Create `src/metrics_extractor.py`:

```python
class MetricsExtractor:
    def extract_from_git(self, repo_path, pr_number):
        """Extract code metrics from Git"""
        git_analyzer = GitRiskAnalyzer(repo_path)
        code_metrics = git_analyzer.analyze_pull_request(pr_number)
        
        return code_metrics
    
    def extract_developer_metrics(self, developers_list):
        """Get developer experience from database"""
        # Query: dev_database.get_developer_experience(name)
        return {
            'developer_experience': 'Mid',  # or 'Senior', 'Junior'
            'team_size': len(developers_list),
            'past_defect_rate': 0.12
        }
    
    def extract_qa_metrics(self, repo_path, affected_modules):
        """Get test coverage from CI"""
        # Query: ci_server.get_coverage(affected_modules)
        return {
            'test_coverage': 0.75,
            'automation_coverage': 0.68,
            'regression_failures': 2
        }
    
    def combine_features(self, git_metrics, dev_metrics, qa_metrics):
        """Combine all metrics into prediction features"""
        return {
            **git_metrics,
            **dev_metrics,
            **qa_metrics,
            'story_points': 8,
            'dependencies': 2,
            'days_to_release': 7
        }
```

---

### **Phase 3: PR Risk Analyzer** (Automated PR checking)

Create `src/pr_risk_analyzer.py`:

```python
class PRRiskAnalyzer:
    def __init__(self, model_path, repo_path):
        self.predictor = RiskPredictor(model_path)
        self.extractor = MetricsExtractor()
        self.repo_path = repo_path
    
    def analyze_pr(self, pr_number):
        """Analyze PR and return risk prediction"""
        
        # Step 1: Extract metrics from Git
        code_metrics = self.extractor.extract_from_git(
            self.repo_path, pr_number
        )
        
        # Step 2: Get developer info
        developers = get_pr_developers(self.repo_path, pr_number)
        dev_metrics = self.extractor.extract_developer_metrics(developers)
        
        # Step 3: Get QA metrics
        qa_metrics = self.extractor.extract_qa_metrics(
            self.repo_path, 
            code_metrics['affected_modules']
        )
        
        # Step 4: Combine all features
        features = self.extractor.combine_features(
            code_metrics, dev_metrics, qa_metrics
        )
        
        # Step 5: Get prediction
        risk_score, risk_level, probs = self.predictor.predict(features)
        
        return {
            'pr_number': pr_number,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'probabilities': probs,
            'features_used': features,
            'recommendation': self.get_recommendation(risk_level)
        }
    
    def get_recommendation(self, risk_level):
        """Get testing recommendation based on risk level"""
        recommendations = {
            'Low': '✓ Quick sanity check, minimal testing needed',
            'Medium': '⚠️ Standard regression + manual UAT',
            'High': '🔴 Full QA cycle + extended testing + canary deployment'
        }
        return recommendations[risk_level]
```

---

## Usage Flow: From Code Change to Risk Prediction

### Scenario: New Payment Feature

```
1. Developer pushes to GitHub
   └─> git push origin feature/payment-enhancements

2. GitHub detects new PR
   └─> PR #234 created

3. Webhook triggers Risk Analyzer
   └─> POST /webhook/pr -> analyze_pr(234)

4. Framework extracts metrics
   ├─ Git: 12 files, 680 lines added
   ├─ Developer: 2 junior devs (past defect rate: 15%)
   ├─ QA: Payment module has 8 historical bugs
   └─ Story: 13 story points, 3 dependencies

5. ML Prediction
   └─> Risk Score: 87% (HIGH) ⚠️

6. Post Comment on PR
   ┌─────────────────────────────────────┐
   │ 🔴 HIGH RISK PREDICTION: 87%       │
   │                                     │
   │ Contributing Factors:              │
   │ • 12 files changed (+18%)          │
   │ • Payment module history (+15%)    │
   │ • Low test coverage (+12%)         │
   │ • 2 junior developers (+10%)       │
   │                                     │
   │ Recommendation:                    │
   │ Run: Payment → Auth → Checkout     │
   │ Manual UAT required for workflows  │
   └─────────────────────────────────────┘

7. QA Team Reviews
   └─> Allocates 2 days for testing
       (instead of checking code manually)
```

---

## Real Implementation Example

### Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install GitPython pylint radon  # For git and complexity analysis

# 2. Train the model (one-time)
python src/train.py

# 3. Install GitHub webhook (or use CLI)
gh webhook add --url https://your-server.com/webhook --events pull_request
```

### Python Usage

```python
from src.pr_risk_analyzer import PRRiskAnalyzer

# Initialize
analyzer = PRRiskAnalyzer(
    model_path='models/risk_model.pkl',
    repo_path='/path/to/repo'
)

# Analyze a PR
result = analyzer.analyze_pr(pr_number=234)

print(f"Risk: {result['risk_score']:.0f}%")
print(f"Level: {result['risk_level']}")
print(f"Recommendation: {result['recommendation']}")
```

### Output

```
Risk: 87%
Level: High
Recommendation: 🔴 Full QA cycle + extended testing + canary deployment

Features analyzed:
- files_changed: 12
- lines_added: 680
- developer_experience: Junior
- test_coverage: 0.45
- complexity_score: 8.5
- historical_defects_in_module: 8
```

---

## Integration Scenarios

### Scenario 1: GitHub Actions Workflow

```yaml
# .github/workflows/risk-prediction.yml
name: Risk Prediction
on: [pull_request]

jobs:
  analyze-risk:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run Risk Prediction
        run: |
          python -c "
          from src.pr_risk_analyzer import PRRiskAnalyzer
          analyzer = PRRiskAnalyzer('models/risk_model.pkl', '.')
          result = analyzer.analyze_pr(${{ github.event.number }})
          print(f'Risk: {result[\"risk_score\"]}%')
          print(f'Level: {result[\"risk_level\"]}')
          "
      
      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '🔴 HIGH RISK: 87%\n\nRecommended testing: Full regression + UAT'
            })
```

### Scenario 2: Webhook Server (Flask)

```python
from flask import Flask, request
from src.pr_risk_analyzer import PRRiskAnalyzer

app = Flask(__name__)
analyzer = PRRiskAnalyzer('models/risk_model.pkl', '/path/to/repo')

@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    data = request.json
    
    if data['action'] == 'opened':
        pr_number = data['pull_request']['number']
        result = analyzer.analyze_pr(pr_number)
        
        # Post comment
        post_comment_on_pr(
            pr_number,
            f"🔴 Risk: {result['risk_score']}% ({result['risk_level']})\n"
            f"{result['recommendation']}"
        )
    
    return {'status': 'ok'}
```

### Scenario 3: JIRA Integration

```python
from jira import JIRA

jira = JIRA(server='https://jira.company.com')

def update_jira_with_risk(issue_key, risk_score, risk_level):
    issue = jira.issue(issue_key)
    
    # Add risk label
    issue.fields.labels.append(f'risk-{risk_level.lower()}')
    
    # Add custom field
    issue.update(customfield_10001=risk_score)
    
    # Add comment
    jira.add_comment(issue_key, 
        f"🤖 Risk Prediction: {risk_score}% ({risk_level})\n"
        f"Model Confidence: High"
    )
```

---

## Monitoring & Continuous Improvement

### Track Prediction Accuracy

```python
def log_prediction(pr_number, predicted_risk, actual_bugs_found):
    """Log prediction vs actual outcome"""
    
    # Store in database
    db.predictions.insert({
        'pr_number': pr_number,
        'predicted_risk': predicted_risk,
        'actual_bugs': len(actual_bugs_found),
        'was_accurate': (predicted_risk == 'High') if actual_bugs_found else True,
        'date': datetime.now()
    })

# Monthly retraining
def retrain_model_monthly():
    """Retrain model with latest data every month"""
    
    # Collect new data from past month
    new_data = db.predictions.find({
        'date': {'$gte': datetime.now() - timedelta(days=30)}
    })
    
    # Add to training dataset
    df = pd.concat([
        pd.read_csv('data/training_data.csv'),
        pd.DataFrame(new_data)
    ])
    
    # Retrain
    trainer = RiskModelTrainer()
    trainer.train_model_from_data(df)
    trainer.save_model('models/risk_model_v2.pkl')
```

---

## Metrics Dashboard

Display in your team dashboard:

```
📊 Risk Prediction Metrics (Last 30 Days)

✅ Model Accuracy: 87%
  - True Positives (Predicted High, Had Bugs): 15
  - True Negatives (Predicted Low, No Bugs): 42
  - False Positives: 5
  - False Negatives: 2

📈 Risk Distribution
  - Low Risk: 35% (26 PRs)
  - Medium Risk: 45% (34 PRs)
  - High Risk: 20% (15 PRs)

🐛 Bugs by Risk Level
  - Low Risk PRs: 1 bug (4% defect rate)
  - Medium Risk PRs: 8 bugs (24% defect rate)
  - High Risk PRs: 23 bugs (153% defect rate) ⚠️

💡 Top Risk Factors This Month
  1. Files changed (18% importance)
  2. Developer experience (14%)
  3. Test coverage (12%)
  4. Module history (11%)
  5. Complexity (10%)
```

---

## Summary: From Current State to Production

| Phase | Status | What You Get |
|-------|--------|-------------|
| **Current** | ✅ Complete | Trained ML model, manual feature input, prediction API |
| **Phase 1** | 📋 Plan | Git metrics extraction, automated feature collection |
| **Phase 2** | 📋 Plan | GitHub/JIRA integration, webhook handlers |
| **Phase 3** | 📋 Plan | Dashboard, continuous learning, accuracy tracking |

---

## Next Steps

1. **Understand the current model**: Run `python src/train.py` to train locally
2. **Test predictions**: Use `python src/predictor.py` to see output
3. **Build git extraction**: Extend `src/` with `git_monitor.py`
4. **Integrate with CI/CD**: Add GitHub Actions workflow
5. **Monitor accuracy**: Track predictions vs actual defects
6. **Continuous improvement**: Retrain monthly with real data

This framework will grow more accurate as it learns from real deployments!
