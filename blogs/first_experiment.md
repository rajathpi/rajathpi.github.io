### Code
```python
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report
import warnings
warnings.filterwarnings('ignore')
### Output
```


### Code
```python
# Step 1: Create an imbalanced binary classification dataset
X, y = make_classification(n_samples=1000, n_features=10, n_informative=2, n_redundant=8, 
                           weights=[0.9, 0.1], flip_y=0, random_state=42)

np.unique(y, return_counts=True)
### Output
```




    (array([0, 1]), array([900, 100], dtype=int64))




### Code
```python
# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)
### Output
```


### Code
```python
# Define the model hyperparameters
params = {
    "solver": "lbfgs", "max_iter": 500,
    "multi_class": "auto",
    "random_state": 8888,
}

# Train the model
lr = LogisticRegression(**params)
lr.fit(X_train, y_train)

# Predict on the test set
y_pred = lr.predict(X_test)

report = classification_report(y_test, y_pred)
print(report)
### Output
```

                  precision    recall  f1-score   support
    
               0       0.95      0.97      0.96       270
               1       0.62      0.50      0.56        30
    
        accuracy                           0.92       300
       macro avg       0.79      0.73      0.76       300
    weighted avg       0.91      0.92      0.92       300
    
    


### Code
```python
report_dict = classification_report(y_test, y_pred, output_dict=True)
report_dict
### Output
```




    {'0': {'precision': 0.9456521739130435,
      'recall': 0.9666666666666667,
      'f1-score': 0.956043956043956,
      'support': 270},
     '1': {'precision': 0.625,
      'recall': 0.5,
      'f1-score': 0.5555555555555556,
      'support': 30},
     'accuracy': 0.92,
     'macro avg': {'precision': 0.7853260869565217,
      'recall': 0.7333333333333334,
      'f1-score': 0.7557997557997558,
      'support': 300},
     'weighted avg': {'precision': 0.9135869565217392,
      'recall': 0.92,
      'f1-score': 0.915995115995116,
      'support': 300}}




### Code
```python
import mlflow
### Output
```


### Code
```python
mlflow.set_experiment("First Experiment")
mlflow.set_tracking_uri("http://127.0.0.1:5000/")


# we will log parameters, metrics and model
with mlflow.start_run():
    mlflow.log_params(params)
    mlflow.log_metrics({
        'accuracy': report_dict['accuracy'],
        'recall_class_0': report_dict['0']['recall'],
        'recall_class_1': report_dict['1']['recall'],
        'f1_score_macro': report_dict['macro avg']['f1-score']
    })
    mlflow.sklearn.log_model(lr, "Logistic Regression")
### Output
```

    2025/01/16 09:56:47 WARNING mlflow.models.model: Model logged without a signature and input example. Please set `input_example` parameter when logging the model to auto infer the model signature.
    

    🏃 View run resilient-rat-669 at: http://127.0.0.1:5000/#/experiments/311624381169912091/runs/2ee861134ee241f2b11f4969a983c65c
    🧪 View experiment at: http://127.0.0.1:5000/#/experiments/311624381169912091
    


### Code
```python

### Output
```
