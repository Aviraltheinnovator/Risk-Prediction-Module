# How to Run the Risk Prediction Module in Jupyter Notebook

## 📋 Complete Step-by-Step Guide

---

## Part 1: Setup (5 minutes)

### Step 1: Install Jupyter

```bash
pip install jupyter notebook
```

### Step 2: Navigate to Project Directory

```bash
cd Risk-Prediction-Module
```

### Step 3: Launch Jupyter

```bash
jupyter notebook
```

Your browser will open at `http://localhost:8888`

### Step 4: Open the Notebook

Click on `Risk_Prediction_Notebook.ipynb` in the file browser.

---

## Part 2: Run the Notebook (15-20 minutes)

### The notebook contains 22 steps organized in 8 parts:

#### **PART 1: Data Loading & Exploration (Steps 1-5)**
- Cell 1: Install dependencies
- Cell 2: Import libraries
- Cell 3: Create training dataset
- Cell 4: Exploratory data analysis
- Cell 5: Visualize distributions

**⏱️ Time: 2-3 minutes**

#### **PART 2: Data Preprocessing (Steps 6-7)**
- Cell 6: Prepare data for ML
- Cell 7: Train/test split

**⏱️ Time: 1 minute**

#### **PART 3: Model Training (Steps 8-12)**
- Cell 8: Train Random Forest
- Cell 9: Evaluate performance
- Cell 10: Classification report
- Cell 11: Visualize results
- Cell 12: Feature importance

**⏱️ Time: 3-5 minutes**

#### **PART 4: Making Predictions (Steps 13-15)**
- Cell 13: Define prediction functions
- Cell 14: Example predictions (Low, Medium, High risk)
- Cell 15: Batch predictions

**⏱️ Time: 2-3 minutes**

#### **PART 5: Git Integration (Step 16)**
- Cell 16: Git repository analysis (optional)

**⏱️ Time: 1 minute**

#### **PART 6: Save & Export (Steps 17-19)**
- Cell 17: Save trained model
- Cell 18: Load saved model
- Cell 19: Export predictions to CSV

**⏱️ Time: 2 minutes**

#### **PART 7: Summary (Steps 20-21)**
- Cell 20: Summary dashboard
- Cell 21: Comprehensive visualization

**⏱️ Time: 2-3 minutes**

#### **PART 8: Usage Guide (Step 22)**
- Cell 22: How to use for your own data

---

## Part 3: How to Run Each Cell

### Method 1: Run Cells Sequentially (Recommended)

1. Click on the first cell
2. Press `Shift + Enter` to run and move to next cell
3. Continue until all cells are complete

### Method 2: Run All Cells at Once

- Click: `Cell` → `Run All`

### Method 3: Run Individual Cells

- Click on a cell
- Press `Ctrl + Enter` to run (stay in same cell)

---

## Part 4: Understanding the Output

### After Each Major Step, You'll See:

**Step 3 Output:**
```
📊 Dataset created!

Shape: (85, 14)

First 5 rows:
[DataFrame display]

Risk distribution:
Low      28
Medium   35
High     22
```

**Step 9 Output:**
```
MODEL EVALUATION METRICS
============================================================

📊 TRAINING SET PERFORMANCE:
  Accuracy:  0.9286
  Precision: 0.9302
  Recall:    0.9286
  F1-Score:  0.9289

📊 TEST SET PERFORMANCE:
  Accuracy:  0.8571
  Precision: 0.8667
  Recall:    0.8571
  F1-Score:  0.8571
```

**Step 14 Output:**
```
======================================================================
EXAMPLE 1: LOW RISK - Authentication Service Update
======================================================================

🎯 Risk Score: 15%
📊 Risk Level: Low

📈 Confidence:
   Low: 87.3%
   Medium: 8.5%
   High: 4.2%

📋 Recommendation:
   Testing Level: Quick sanity check
   Test Suites: ['Smoke tests']
   Manual Testing: False
   Deployment: Direct to production
   Time Estimate: 15-30 minutes
```

---

## Part 5: Common Issues & Solutions

### Issue 1: "Module not found" Error

**Problem:**
```
ModuleNotFoundError: No module named 'pandas'
```

**Solution:**
- Run Cell 1 again (Install dependencies)
- Or manually: `pip install pandas numpy scikit-learn matplotlib seaborn`

### Issue 2: Kernel Crashes

**Problem:**
```
Kernel died, restarting...
```

**Solution:**
1. Click: `Kernel` → `Restart`
2. Run cells from the beginning
3. Make sure you have enough RAM (2GB+)

### Issue 3: Git Not Found

**Problem:**
```
GitPython not installed. Skipping git analysis.
```

**Solution:**
- Run: `pip install GitPython radon` in terminal
- This is optional; notebook works without it

### Issue 4: Matplotlib Not Displaying

**Problem:**
```
Plots don't show in notebook
```

**Solution:**
Add this cell at the beginning:
```python
%matplotlib inline
import matplotlib.pyplot as plt
```

---

## Part 6: Customizing for Your Data

### Replace Step 3 (Create Dataset) with Your Data:

**Option A: Load from CSV**

```python
# Instead of generating data, load your own
df = pd.read_csv('your_data.csv')

# Make sure it has these columns:
# - module
# - files_changed
# - lines_added
# - lines_deleted
# - complexity_score
# - developer_experience
# - team_size
# - past_defect_rate
# - test_coverage
# - automation_coverage
# - regression_failures
# - story_points
# - dependencies
# - days_to_release
# - risk_label (target variable)
```

**Option B: Load from Database**

```python
import sqlalchemy

engine = sqlalchemy.create_engine('mysql://user:password@localhost/database')
df = pd.read_sql('SELECT * FROM features', engine)
```

**Option C: Load from API**

```python
import requests

response = requests.get('https://api.example.com/features')
df = pd.DataFrame(response.json())
```

---

## Part 7: Exporting & Using Results

### After Running Complete Notebook:

**Files Created:**
- `models/risk_prediction_model.pkl` - Trained model (5MB)
- `test_predictions.csv` - All predictions (can be opened in Excel)

### Use the Model in Python:

```python
# In a separate Python script
import pickle
import numpy as np

# Load model
with open('models/risk_prediction_model.pkl', 'rb') as f:
    model_data = pickle.load(f)

model = model_data['model']
encoders = model_data['label_encoders']

# Make prediction
features = np.array([...]).reshape(1, -1)  # Your data
prediction = model.predict(features)
```

### Convert to Python Script:

```bash
# In terminal
jupyter nbconvert --to script Risk_Prediction_Notebook.ipynb

# Run as Python script
python Risk_Prediction_Notebook.py
```

---

## Part 8: Advanced Usage

### Run Notebook from Command Line:

```bash
jupyter nbconvert --to notebook --execute Risk_Prediction_Notebook.ipynb
```

### Generate HTML Report:

```bash
jupyter nbconvert --to html Risk_Prediction_Notebook.ipynb
# Creates: Risk_Prediction_Notebook.html
```

### Schedule Automatic Runs:

```bash
# Using cron (Linux/Mac)
0 8 * * * cd /path/to/project && jupyter nbconvert --to notebook --execute Risk_Prediction_Notebook.ipynb

# Using Windows Task Scheduler
# Create task that runs: jupyter nbconvert --execute Risk_Prediction_Notebook.ipynb
```

---

## Part 9: Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Run cell | Shift + Enter |
| Run cell (stay) | Ctrl + Enter |
| Insert cell below | Alt + Enter |
| Delete cell | Ctrl + Shift + X |
| Cut cell | Ctrl + X |
| Paste cell | Ctrl + V |
| Restart kernel | Ctrl + Shift + R |
| Clear output | Ctrl + Shift + O |
| Help | Shift + Tab (in function) |

---

## Part 10: Troubleshooting Outputs

### If predictions seem wrong:

1. Check if model trained correctly (Cell 9)
2. Verify feature values are reasonable
3. Check feature encoding (print encoders)
4. Try with different random_state

### If accuracy is low:

1. More training data needed
2. Try different features
3. Tune hyperparameters in Cell 8
4. Try different model (XGBoost, etc.)

### If slow:

1. Reduce dataset size
2. Disable visualizations temporarily
3. Use smaller train/test split
4. Check RAM usage

---

## Part 11: Next Steps After Running

1. **✅ Modify features**: Change cell 3 to use your actual data
2. **✅ Tune model**: Adjust parameters in cell 8
3. **✅ Add visualizations**: Create custom plots in cells
4. **✅ Export model**: Use cell 17 output
5. **✅ Deploy**: Use model in production (cell 18)

---

## Part 12: Full Example Workflow

### Complete workflow from start to finish:

```python
# 1. Run all cells (Shift + Enter for each)
# 2. Check output in Cell 9 - your accuracy should be > 75%
# 3. Look at predictions in Cell 14
# 4. Export model in Cell 17
# 5. Verify CSV export in Cell 19
# 6. Now you have:
#    - Trained model
#    - Predictions
#    - Visualizations
#    - Summary report
```

---

## Part 13: FAQ

**Q: Can I modify the notebook?**
A: Yes! It's fully customizable. Add cells, modify code, experiment freely.

**Q: How long does it take to run?**
A: Complete notebook: 15-20 minutes
   Just training: 5 minutes
   Just predictions: 2 minutes

**Q: Can I use my own data?**
A: Yes! Replace Cell 3 with your CSV loading code.

**Q: Will the model improve?**
A: Yes! Retrain monthly with new data + actual outcomes.

**Q: Can I share the notebook?**
A: Yes! Share the .ipynb file. Others can run it on their machine.

**Q: How do I debug errors?**
A: Click cell with error, press Ctrl+Shift+O to see output, read error message.

---

## Summary

✅ **Complete notebook implementation**
✅ **22 steps covering full ML pipeline**
✅ **Real data generation + visualization**
✅ **Model training + evaluation**
✅ **3 prediction examples**
✅ **Export capabilities**
✅ **Full customization support**

**Start running now: `jupyter notebook` → Open `Risk_Prediction_Notebook.ipynb` → Press `Shift+Enter`!**
