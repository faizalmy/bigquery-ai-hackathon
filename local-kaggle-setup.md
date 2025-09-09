# Running Kaggle Notebooks Locally

## Overview
This guide shows you how to set up a local environment to run Kaggle notebooks on your machine, including data download, environment setup, and notebook execution.

## Prerequisites
- Python 3.7+ installed
- pip package manager
- Git (optional, for version control)

## Step 1: Set Up Python Virtual Environment

### Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv kaggle-env

# Activate virtual environment
# On macOS/Linux:
source kaggle-env/bin/activate
# On Windows:
# kaggle-env\Scripts\activate
```

### Install Required Packages
```bash
# Install essential packages
pip install jupyter notebook
pip install pandas numpy matplotlib seaborn
pip install scikit-learn
pip install kaggle

# Optional: Install additional ML libraries
pip install xgboost lightgbm
pip install plotly
pip install openpyxl  # for Excel files
```

## Step 2: Set Up Kaggle API

### Get API Credentials
1. Go to [Kaggle Account Settings](https://www.kaggle.com/account)
2. Scroll to "API" section
3. Click "Create New API Token"
4. Download `kaggle.json` file

### Configure API
```bash
# Create kaggle directory
mkdir -p ~/.kaggle

# Copy your kaggle.json file to the directory
cp ~/Downloads/kaggle.json ~/.kaggle/

# Set proper permissions
chmod 600 ~/.kaggle/kaggle.json
```

### Test API Connection
```bash
# Test the API
kaggle competitions list
```

## Step 3: Download Competition Data

### Download Titanic Data
```bash
# Navigate to your project directory
cd /Users/faizal/Sites/kaggle/titanic

# Download the competition data
kaggle competitions download -c titanic

# Extract the files
unzip titanic.zip

# List downloaded files
ls -la
```

### Expected Files
- `train.csv` - Training data (891 passengers)
- `test.csv` - Test data (418 passengers)
- `gender_submission.csv` - Sample submission

## Step 4: Set Up Jupyter Notebook

### Start Jupyter Server
```bash
# Start Jupyter notebook server
jupyter notebook

# Or use JupyterLab (more modern interface)
pip install jupyterlab
jupyter lab
```

### Create New Notebook
1. Open browser to `http://localhost:8888`
2. Click "New" → "Python 3"
3. Rename notebook to `titanic-analysis.ipynb`

## Step 5: Basic Notebook Structure

### Cell 1: Import Libraries
```python
# Import essential libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

# Set display options
pd.set_option('display.max_columns', None)
plt.style.use('seaborn-v0_8')
```

### Cell 2: Load Data
```python
# Load the data
train_data = pd.read_csv('train.csv')
test_data = pd.read_csv('test.csv')

# Display basic information
print("Training data shape:", train_data.shape)
print("Test data shape:", test_data.shape)
print("\nTraining data info:")
print(train_data.info())
```

### Cell 3: Data Exploration
```python
# Display first few rows
print("First 5 rows of training data:")
print(train_data.head())

# Check for missing values
print("\nMissing values in training data:")
print(train_data.isnull().sum())

# Basic statistics
print("\nBasic statistics:")
print(train_data.describe())
```

### Cell 4: Data Visualization
```python
# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Survival by gender
train_data.groupby('Sex')['Survived'].mean().plot(kind='bar', ax=axes[0,0])
axes[0,0].set_title('Survival Rate by Gender')

# Survival by class
train_data.groupby('Pclass')['Survived'].mean().plot(kind='bar', ax=axes[0,1])
axes[0,1].set_title('Survival Rate by Class')

# Age distribution
train_data['Age'].hist(bins=30, ax=axes[1,0])
axes[1,0].set_title('Age Distribution')

# Survival by age groups
train_data['AgeGroup'] = pd.cut(train_data['Age'], bins=[0, 12, 18, 35, 60, 100], labels=['Child', 'Teen', 'Adult', 'Middle', 'Senior'])
train_data.groupby('AgeGroup')['Survived'].mean().plot(kind='bar', ax=axes[1,1])
axes[1,1].set_title('Survival Rate by Age Group')

plt.tight_layout()
plt.show()
```

### Cell 5: Data Preprocessing
```python
# Handle missing values
train_data['Age'].fillna(train_data['Age'].median(), inplace=True)
test_data['Age'].fillna(test_data['Age'].median(), inplace=True)

train_data['Embarked'].fillna(train_data['Embarked'].mode()[0], inplace=True)
test_data['Embarked'].fillna(test_data['Embarked'].mode()[0], inplace=True)

# Feature engineering
def extract_title(name):
    return name.split(',')[1].split('.')[0].strip()

train_data['Title'] = train_data['Name'].apply(extract_title)
test_data['Title'] = test_data['Name'].apply(extract_title)

# Create family size feature
train_data['FamilySize'] = train_data['SibSp'] + train_data['Parch'] + 1
test_data['FamilySize'] = test_data['SibSp'] + test_data['Parch'] + 1

print("Feature engineering completed!")
```

### Cell 6: Model Training
```python
# Select features
features = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare", "Embarked", "FamilySize"]
X = pd.get_dummies(train_data[features])
X_test = pd.get_dummies(test_data[features])

# Ensure both datasets have the same columns
X_test = X_test.reindex(columns=X.columns, fill_value=0)

y = train_data["Survived"]

# Split data for validation
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=1)
model.fit(X_train, y_train)

# Make predictions
val_predictions = model.predict(X_val)
accuracy = accuracy_score(y_val, val_predictions)
print(f"Validation Accuracy: {accuracy:.4f}")
```

### Cell 7: Make Predictions and Submit
```python
# Make predictions on test set
predictions = model.predict(X_test)

# Create submission file
output = pd.DataFrame({
    'PassengerId': test_data.PassengerId,
    'Survived': predictions
})

# Save submission
output.to_csv('submission.csv', index=False)
print("Submission file created: submission.csv")
print(f"Predictions: {predictions.sum()} survivors out of {len(predictions)} passengers")
```

## Step 6: Advanced Setup Options

### Using Conda Environment
```bash
# Create conda environment
conda create -n kaggle-env python=3.9
conda activate kaggle-env

# Install packages
conda install jupyter pandas numpy matplotlib seaborn scikit-learn
pip install kaggle
```

### Using Docker (Optional)
```dockerfile
# Dockerfile
FROM jupyter/scipy-notebook:latest

USER root
RUN pip install kaggle

USER jovyan
WORKDIR /home/jovyan/work
```

### VS Code Integration
```bash
# Install VS Code extensions
code --install-extension ms-python.python
code --install-extension ms-toolsai.jupyter
```

## Step 7: Project Structure

```
titanic/
├── kaggle-env/                 # Virtual environment
├── data/                       # Data files
│   ├── train.csv
│   ├── test.csv
│   └── gender_submission.csv
├── notebooks/                  # Jupyter notebooks
│   ├── titanic-analysis.ipynb
│   └── titanic-advanced.ipynb
├── src/                        # Python scripts
│   ├── data_preprocessing.py
│   ├── feature_engineering.py
│   └── model_training.py
├── submissions/                # Submission files
│   └── submission.csv
├── requirements.txt            # Dependencies
└── README.md                   # Project documentation
```

## Step 8: Create Requirements File

```bash
# Generate requirements.txt
pip freeze > requirements.txt
```

### requirements.txt content:
```
jupyter==1.0.0
pandas==2.0.3
numpy==1.24.3
matplotlib==3.7.2
seaborn==0.12.2
scikit-learn==1.3.0
kaggle==1.7.4.5
xgboost==1.7.6
lightgbm==4.0.0
```

## Step 9: Running Scripts

### Create Python Script
```python
# titanic_analysis.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

def main():
    # Load data
    train_data = pd.read_csv('data/train.csv')
    test_data = pd.read_csv('data/test.csv')

    # Your analysis code here
    print("Analysis completed!")

if __name__ == "__main__":
    main()
```

### Run Script
```bash
python titanic_analysis.py
```

## Step 10: Best Practices

### Version Control
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit: Titanic analysis setup"
```

### Environment Management
```bash
# Create .env file for sensitive data
echo "KAGGLE_USERNAME=your_username" > .env
echo "KAGGLE_KEY=your_api_key" >> .env
```

### Documentation
- Use markdown cells in notebooks for documentation
- Add docstrings to functions
- Keep a README.md with setup instructions

## Troubleshooting

### Common Issues

1. **Kaggle API not working**:
   ```bash
   # Check credentials
   ls -la ~/.kaggle/
   # Should show kaggle.json with 600 permissions
   ```

2. **Import errors**:
   ```bash
   # Reinstall packages
   pip install --upgrade pandas numpy scikit-learn
   ```

3. **Jupyter not starting**:
   ```bash
   # Check if port is in use
   lsof -i :8888
   # Use different port
   jupyter notebook --port 8889
   ```

### Performance Tips
- Use `%time` magic command to measure execution time
- Use `%%time` for entire cell timing
- Profile memory usage with `%memit`

## Next Steps
1. Set up your local environment
2. Download the Titanic data
3. Create your first notebook
4. Experiment with different models
5. Submit your predictions to Kaggle

---

*This guide provides everything you need to run Kaggle notebooks locally with a professional setup.*
