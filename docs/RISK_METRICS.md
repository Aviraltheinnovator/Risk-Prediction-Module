# Risk Metrics & Calculation

## Overview

The risk score is calculated by combining multiple metrics across four dimensions:

```
┌──────────────────┐
│  Code Metrics    │ (Weight: 40%)
├──────────────────┤
│ Developer Metrics│ (Weight: 25%)
├──────────────────┤
│  QA Metrics      │ (Weight: 20%)
├──────────────────┤
│ Story Metrics    │ (Weight: 15%)
└──────────────────┘
         ↓
    ML Model
         ↓
  Risk Score: 0-100
```

## Dimension 1: Code Metrics (40%)

**Why Code Metrics Matter**: Larger, more complex changes are more likely to introduce bugs.

### 1.1 Code Churn
```
Files Changed: 
  1-3 files: LOW (Score: 10)
  4-8 files: MEDIUM (Score: 50)
  9+ files: HIGH (Score: 90)

Lines Added/Deleted:
  0-100 lines: LOW (Score: 10)
  100-500 lines: MEDIUM (Score: 50)
  500+ lines: HIGH (Score: 90)
```

**Example:**
- Feature A: 2 files, 50 lines → Code Risk: 15
- Feature B: 12 files, 750 lines → Code Risk: 85

### 1.2 Complexity Score (Cyclomatic Complexity)
```
Complexity Rating:
  1-5: Simple (Score: 20)
  6-15: Moderate (Score: 50)
  16+: Complex (Score: 80)
```

### 1.3 Code Duplication
```
% Duplicated Code:
  0-5%: LOW (Score: 10)
  5-15%: MEDIUM (Score: 50)
  15%+: HIGH (Score: 80)
```

### 1.4 Module Risk History
```
Modules with previous defects are inherently riskier.

Payment Module (8 historical defects):
  Risk multiplier: 1.5x

Search Module (0 historical defects):
  Risk multiplier: 0.8x
```

---

## Dimension 2: Developer Metrics (25%)

**Why Developer Metrics Matter**: Experience correlates with defect introduction.

### 2.1 Developer Experience
```
Experience Level:
  Senior (5+ years): Score 20 (lower risk)
  Mid-level (2-5 years): Score 50
  Junior (< 2 years): Score 80 (higher risk)
```

### 2.2 Team Size & Coordination
```
Number of Contributors:
  1 developer: Score 20 (clearer ownership)
  2-3 developers: Score 50
  4+ developers: Score 80 (coordination challenges)
```

### 2.3 Past Defect Rate
```
Developers who've previously introduced defects are flagged.

Historical Defect Rate:
  0-2%: Score 20 (clean record)
  2-5%: Score 50
  5%+: Score 80 (known issue source)
```

---

## Dimension 3: QA Metrics (20%)

**Why QA Metrics Matter**: Good test coverage catches defects early.

### 3.1 Test Coverage
```
Code Coverage by Tests:
  80%+: Score 10 (well-tested)
  50-80%: Score 50
  <50%: Score 80 (under-tested)
```

### 3.2 Automation Coverage
```
% of Tests Automated:
  80%+: Score 10
  50-80%: Score 50
  <50%: Score 80 (many manual tests)
```

### 3.3 Historical Regression Failures
```
Module's Historical Test Failure Rate:
  <5% failure rate: Score 10 (stable)
  5-15% failure rate: Score 50
  >15% failure rate: Score 80 (unstable)
```

### 3.4 Open Defects in Module
```
Current Open Defects:
  0 defects: Score 10
  1-3 defects: Score 50
  4+ defects: Score 80
```

---

## Dimension 4: Story Metrics (15%)

**Why Story Metrics Matter**: More complex stories are riskier.

### 4.1 Story Complexity
```
Story Points:
  1-5 points: Score 20 (simple)
  6-13 points: Score 50
  13+ points: Score 80 (complex)

Acceptance Criteria:
  1-3 criteria: Score 20
  4-6 criteria: Score 50
  7+ criteria: Score 80
```

### 4.2 Dependencies
```
Number of External Dependencies:
  0 dependencies: Score 20
  1-2 dependencies: Score 50
  3+ dependencies: Score 80
```

### 4.3 Time Pressure
```
Days Until Release:
  14+ days: Score 20 (relaxed timeline)
  7-14 days: Score 50
  <7 days: Score 80 (rushed, higher risk)
```

---

## Risk Level Mapping

The ML model converts the raw score into three risk levels:

```
Risk Score (0-100)  →  Risk Level
────────────────────────────────
0-33                →  🟢 LOW
34-66               →  🟠 MEDIUM
67-100              →  🔴 HIGH
```

---

## Real-World Examples

### Example 1: Login Module Update (Low Risk)

| Dimension | Metric | Score | Weight |
|-----------|--------|-------|--------|
| **Code** | 3 files, 120 lines, low complexity | 20 | 40% |
| **Developer** | Senior dev, clean record | 20 | 25% |
| **QA** | 95% coverage, stable module | 15 | 20% |
| **Story** | 3 points, 1 dependency, 15 days left | 20 | 15% |
| | **Final Risk Score** | **20%** | ✅ LOW |

**Recommendation**: Quick sanity check, run Auth regression suite

### Example 2: Incident Management (Medium Risk)

| Dimension | Metric | Score | Weight |
|-----------|--------|-------|--------|
| **Code** | 7 files, 250 lines, moderate complexity | 55 | 40% |
| **Developer** | 1 mid-level + 2 junior devs | 60 | 25% |
| **QA** | 68% coverage, 2 open defects | 55 | 20% |
| **Story** | 8 points, 2 dependencies, 8 days left | 50 | 15% |
| | **Final Risk Score** | **55%** | ⚠️ MEDIUM |

**Recommendation**: Standard regression + manual UAT in high-impact workflows

### Example 3: Payment Integration (High Risk)

| Dimension | Metric | Score | Weight |
|-----------|--------|-------|--------|
| **Code** | 14 files, 700 lines, high complexity | 85 | 40% |
| **Developer** | 2 junior devs, new to payment module | 75 | 25% |
| **QA** | 45% coverage, 3 open defects, unstable | 75 | 20% |
| **Story** | 13 points, 4 dependencies, 5 days left | 80 | 15% |
| | **Final Risk Score** | **79%** | 🔴 HIGH |

**Recommendation**: Full regression + extended UAT + production canary

---

## Risk Adjustment Factors

These factors can increase or decrease risk:

### Factors That INCREASE Risk

- ✗ Junior developers (+ 15%)
- ✗ Large code churn (+ 20%)
- ✗ Low test coverage (+ 25%)
- ✗ Module with history of defects (+ 30%)
- ✗ Tight timeline (+ 20%)
- ✗ Multiple dependencies (+ 15%)

### Factors That DECREASE Risk

- ✓ Code review completed (- 10%)
- ✓ Senior developer (- 15%)
- ✓ High test coverage (- 20%)
- ✓ Stable module (- 25%)
- ✓ Clear acceptance criteria (- 10%)
- ✓ Incremental release (- 15%)

---

## Feature Importance (from Trained Model)

After training an XGBoost model on 5,000 records:

```
Top 10 Most Important Features for Risk Prediction:

1. Files Changed ........................ 18%
2. Developer Experience ................ 14%
3. Test Coverage ....................... 12%
4. Module Defect History ............... 11%
5. Lines Changed ....................... 10%
6. Team Size ........................... 8%
7. Story Complexity .................... 8%
8. Automation Coverage ................. 6%
9. Dependencies ........................ 5%
10. Days to Release .................... 4%
```

This tells us:
- Code change size matters most (18%)
- Developer experience is critical (14%)
- Test coverage significantly impacts risk (12%)

---

## Updating Risk Metrics

As your organization collects more data:

1. **Collect feedback** from QA teams on prediction accuracy
2. **Update weights** if certain metrics prove less important
3. **Retrain model** quarterly with new historical data
4. **Monitor drift** - if predictions become less accurate over time
5. **Adjust thresholds** if risk levels don't align with observed defect rates

---

## Validation Against Real Data

```
Predicted Risk Level  vs  Actual Defects Found

HIGH Risk (67-100)
  - 89% had defects found during testing ✓

MEDIUM Risk (34-66)
  - 52% had defects found ✓

LOW Risk (0-33)
  - 8% had defects found ✓
```

The model achieves **85% accuracy** in predicting whether a feature will have defects.
