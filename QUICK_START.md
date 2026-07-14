# Quick Start Guide: Risk Prediction Framework

## What You Have

A **complete ML framework** that:
1. ✅ **Trains on historical data** - 85 features with known outcomes
2. ✅ **Makes predictions** - Risk score (0-100%) + testing recommendations
3. ✅ **Monitors git repositories** - Extracts metrics from code changes
4. ✅ **Analyzes PRs automatically** - Suggests testing strategies

---

## 5-Minute Setup

### Step 1: Install Dependencies

```bash
cd Risk-Prediction-Module

# Python dependencies
pip install -r requirements.txt

# Add git and complexity analysis tools
pip install GitPython radon
```

### Step 2: Train the Model (One-time)

```bash
# Train Random Forest on historical data
python src/train.py

# Output:
# ✓ Loaded 85 records
# ✓ Model accuracy: 85%
# ✓ Saved to: models/risk_model.pkl
```

### Step 3: Try a Manual Prediction

```bash
python src/predictor.py

# Output:
# === Example 1: Low Risk ===
# Risk Score: 15%
# Risk Level: Low
# 
# === Example 2: Medium Risk ===
# Risk Score: 52%
# Risk Level: Medium
# 
# === Example 3: High Risk ===
# Risk Score: 87%
# Risk Level: High
```

### Step 4: Analyze a Real Repository

```bash
python -c "
from src.pr_analyzer import PRRiskAnalyzer

# Initialize with your repo
analyzer = PRRiskAnalyzer(
    model_path='models/risk_model.pkl',
    repo_path='.'  # Current directory
)

# Analyze a branch compared to main
result = analyzer.analyze_branch('feature', 'main', module='Auth')

print(f'Risk: {result[\"risk_score\"]:.0f}%')
print(f'Level: {result[\"risk_level\"]}')
print(analyzer.generate_pr_comment(result))
"
```

---

## How It Works: Three Components

### 1️⃣ Git Monitor (`src/git_monitor.py`)

**What it does**: Extracts metrics from git repositories

```python
from src.git_monitor import GitRiskAnalyzer

analyzer = GitRiskAnalyzer('/path/to/your/repo')

# Get recent commits
commits = analyzer.get_branch_commits('main', num_commits=5)
for commit in commits:
    print(f"{commit['commit_sha']}: {commit['author']}")
    print(f"  Files: {commit['files_changed']}, Changes: +{commit['lines_added']}")

# Analyze a feature branch
metrics = analyzer.analyze_branch_changes('feature', 'main')
print(f"Files changed: {metrics['files_changed']}")
print(f"Complexity: {metrics['complexity_score']}")
print(f"Contributors: {metrics['num_contributors']}")
```

**Extracts**:
- ✓ Files changed
- ✓ Lines added/deleted
- ✓ Code complexity
- ✓ Number of contributors
- ✓ Commits in PR

### 2️⃣ Predictor (`src/predictor.py`)

**What it does**: Makes risk predictions using trained ML model

```python
from src.predictor import RiskPredictor

predictor = RiskPredictor('models/risk_model.pkl')

# Make a prediction
features = {
    'module': 'Payment',
    'files_changed': 12,
    'lines_added': 650,
    'developer_experience': 'Junior',
    'test_coverage': 0.45,
    # ... other features
}

risk_score, risk_level, probs = predictor.predict(features)
# Output: 87%, High, {'Low': 0.05, 'Medium': 0.08, 'High': 0.87}
```

**Returns**:
- ✓ Risk score (0-100%)
- ✓ Risk level (Low/Medium/High)
- ✓ Confidence probabilities

### 3️⃣ PR Analyzer (`src/pr_analyzer.py`)

**What it does**: Connects everything together for PR analysis

```python
from src.pr_analyzer import PRRiskAnalyzer

analyzer = PRRiskAnalyzer(
    model_path='models/risk_model.pkl',
    repo_path='/path/to/repo'
)

# Analyze a PR
result = analyzer.analyze_branch('feature-branch', 'main')

# Result includes:
# - risk_score: 87%
# - risk_level: High
# - metrics: {files_changed: 12, complexity: 8, ...}
# - recommendation: {testing_level, test_suites, deployment_strategy, ...}
```

---

## Use Cases

### Use Case 1: Analyze a Feature Branch

```python
from src.pr_analyzer import PRRiskAnalyzer

analyzer = PRRiskAnalyzer('models/risk_model.pkl', '.')

# Analyze the "payment-gateway" branch
result = analyzer.analyze_branch('payment-gateway', 'main', module='Payment')

print(f"Risk: {result['risk_score']:.0f}%")
print(f"Level: {result['risk_level']}")
print(f"Recommendation: {result['recommendation']['testing_level']}")

# Get a comment to post on PR
pr_comment = analyzer.generate_pr_comment(result)
print(pr_comment)
```

**Output**:
```
Risk: 87%
Level: High
Recommendation: Full QA cycle with extended testing

🔴 Risk Prediction: 87% (High)

📊 Code Metrics
- Files Changed: 12
- Lines Added: 680
- Complexity Score: 8.5
- Contributors: 2
- Commits: 5

📋 Testing Recommendation
- Level: Full QA cycle with extended testing
- Test Suites: Full regression suite, Integration tests, Performance tests, Security tests
- Manual Testing: ✓ Required
- Code Review: ✓ Required
- Deployment: Canary deployment (5% → 25% → 50% → 100%)
- Time Estimate: 2-3 days

⚠️ On-call engineer coverage recommended during deployment
🔒 Security review required before deployment
```

### Use Case 2: Monitor Multiple Branches

```python
from src.pr_analyzer import PRRiskAnalyzer

analyzer = PRRiskAnalyzer('models/risk_model.pkl', '.')

branches = [
    ('feature/auth-refresh', 'Auth'),
    ('feature/payment-gateway', 'Payment'),
    ('feature/search-optimization', 'Search')
]

for branch, module in branches:
    result = analyzer.analyze_branch(branch, 'main', module=module)
    
    print(f"{module}:")
    print(f"  Risk: {result['risk_score']:.0f}% ({result['risk_level']})")
    print(f"  Files: {result['metrics']['files_changed']}")
    print()
```

**Output**:
```
Auth:
  Risk: 25% (Low)
  Files: 3

Payment:
  Risk: 87% (High)
  Files: 12

Search:
  Risk: 45% (Medium)
  Files: 6
```

### Use Case 3: Get Testing Recommendations

```python
from src.pr_analyzer import PRRiskAnalyzer

analyzer = PRRiskAnalyzer('models/risk_model.pkl', '.')
result = analyzer.analyze_branch('feature', 'main')

rec = result['recommendation']

print(f"Testing Level: {rec['testing_level']}")
print(f"Test Suites: {', '.join(rec['test_suites'])}")
print(f"Manual Testing: {rec['manual_testing']}")
print(f"Deployment: {rec['deployment']}")
print(f"Time: {rec['time_estimate']}")
```

**Output**:
```
Testing Level: Full QA cycle with extended testing
Test Suites: Full regression suite, Integration tests, Performance tests, Security tests
Manual Testing: True
Deployment: Canary deployment (5% → 25% → 50% → 100%)
Time: 2-3 days
```

---

## Integration: How to Connect to Your Workflow

### Option 1: GitHub Actions (Automated)

Create `.github/workflows/risk-prediction.yml`:

```yaml
name: Risk Prediction
on: [pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install GitPython radon

      - name: Analyze Risk
        run: |
          python -c "
          from src.pr_analyzer import PRRiskAnalyzer
          
          analyzer = PRRiskAnalyzer(
              'models/risk_model.pkl',
              '.'
          )
          
          # Get PR info from GitHub context
          pr_branch = '${{ github.head_ref }}'
          base_branch = '${{ github.base_ref }}'
          
          result = analyzer.analyze_branch(pr_branch, base_branch)
          
          print(f'Risk: {result[\"risk_score\"]:.0f}%')
          print(result[\"recommendation\"])
          "

      - name: Post Comment
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const comment = fs.readFileSync('risk_analysis.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            })
```

### Option 2: Manual Command Line

```bash
# Analyze a branch before pushing
python -c "
from src.pr_analyzer import PRRiskAnalyzer

analyzer = PRRiskAnalyzer('models/risk_model.pkl', '.')
result = analyzer.analyze_branch('my-feature', 'main')

print(f'Risk: {result[\"risk_score\"]:.0f}%')

if result['risk_level'] == 'High':
    print('⚠️  HIGH RISK - Extended testing recommended')
"
```

### Option 3: Slack Integration

```python
from src.pr_analyzer import PRRiskAnalyzer
import requests

analyzer = PRRiskAnalyzer('models/risk_model.pkl', '.')
result = analyzer.analyze_branch('feature', 'main')

# Send to Slack
slack_message = {
    'text': f"🔴 Risk: {result['risk_score']:.0f}%",
    'blocks': [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f"*Risk: {result['risk_score']:.0f}% ({result['risk_level']})*\n{result['recommendation']['testing_level']}"
            }
        }
    ]
}

requests.post('YOUR_SLACK_WEBHOOK_URL', json=slack_message)
```

---

## Understanding the Output

### Risk Levels & What They Mean

```
🟢 LOW (0-33%)
   └─ Safe to merge with minimal testing
   └─ Quick sanity check, smoke tests
   └─ Can deploy directly to production

🟠 MEDIUM (34-66%)
   └─ Standard review and testing required
   └─ Run regression tests + manual UAT
   └─ Standard deployment process

🔴 HIGH (67-100%)
   └─ Extended QA and careful review
   └─ Full regression, performance, security tests
   └─ Canary deployment with on-call support
```

### Metrics Explained

```
Files Changed: 12
   └─ Number of source files modified
   └─ More files = higher risk

Lines Added: 680
   └─ Amount of new code
   └─ More lines = more complexity

Complexity Score: 8.5
   └─ Cyclomatic complexity (1-10 scale)
   └─ Higher = harder to test

Contributors: 2
   └─ Number of developers involved
   └─ More people = coordination challenges

Commits: 5
   └─ Number of commits in PR
   └─ More commits = larger scope
```

---

## Troubleshooting

### Model not found
```
Error: Model file not found: models/risk_model.pkl
```
**Fix**: Train the model first: `python src/train.py`

### GitPython not installed
```
Error: ImportError: No module named 'git'
```
**Fix**: Install it: `pip install GitPython`

### Can't analyze repository
```
Error: Invalid git repository: /path/to/repo
```
**Fix**: Make sure the path is a valid git repository with a .git directory

### Features don't match
```
ValueError: Missing required feature: developer_experience
```
**Fix**: Check that all 14 features are provided in the feature dictionary

---

## Next Steps

1. **Train the model**: `python src/train.py`
2. **Test predictions**: `python src/predictor.py`
3. **Analyze a branch**: `python -c "from src.pr_analyzer import PRRiskAnalyzer; ..."`
4. **Set up automation**: Add to GitHub Actions / CI/CD
5. **Monitor results**: Track predictions vs actual defects
6. **Improve model**: Retrain monthly with real data

---

## Documentation

- `README.md` - Project overview
- `FRAMEWORK_GUIDE.md` - Detailed architecture and design
- `docs/ARCHITECTURE.md` - System design
- `docs/RISK_METRICS.md` - How risk is calculated
- `docs/API.md` - Python API reference
- `examples/code_changes.md` - Real code examples

---

## Questions?

Check the docs or review the example code in:
- `modules/low_risk/`, `modules/medium_risk/`, `modules/high_risk/` - Code examples
- `examples/code_changes.md` - Real before/after comparisons
