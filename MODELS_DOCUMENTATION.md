# Models Documentation

## Overview
This project includes **9 different machine learning models** for marine microplastics prediction:

### Sklearn Library Models (5)
1. **Linear Regression** - Simple linear model
2. **Random Forest** - Ensemble of decision trees
3. **XGBoost** - Gradient boosting framework
4. **LightGBM** - Fast gradient boosting
5. **SVM (Support Vector Machine)** - Support Vector Regression with RBF kernel
6. **Decision Tree** - Single decision tree regressor

### From-Scratch Implementations (3)
7. **Linear Regression (Scratch)** - Custom implementation using normal equation
8. **SVM (Scratch)** - Custom SVM using gradient descent
9. **Decision Tree (Scratch)** - Custom decision tree with MSE splitting

---

## Model Details

### 1. Linear Regression (sklearn)
- **Library**: scikit-learn
- **Type**: Linear model
- **Use Case**: Baseline model, fast training
- **Pros**: Simple, interpretable, fast
- **Cons**: Assumes linear relationships

### 2. Random Forest
- **Library**: scikit-learn
- **Type**: Ensemble method
- **Parameters**: 100 estimators
- **Pros**: Handles non-linearity, robust to outliers
- **Cons**: Can overfit, slower prediction

### 3. XGBoost
- **Library**: XGBoost
- **Type**: Gradient boosting
- **Parameters**: 100 estimators
- **Pros**: High accuracy, handles missing values
- **Cons**: Requires tuning, slower training

### 4. LightGBM
- **Library**: LightGBM
- **Type**: Gradient boosting
- **Parameters**: 100 estimators
- **Pros**: Very fast, memory efficient
- **Cons**: Can overfit on small datasets

### 5. SVM (sklearn)
- **Library**: scikit-learn
- **Type**: Support Vector Regression
- **Kernel**: RBF (Radial Basis Function)
- **Pros**: Effective in high dimensions
- **Cons**: Slow on large datasets

### 6. Decision Tree (sklearn)
- **Library**: scikit-learn
- **Type**: Tree-based model
- **Parameters**: max_depth=10
- **Pros**: Easy to interpret, handles non-linearity
- **Cons**: Prone to overfitting

### 7. Linear Regression (Scratch)
- **Implementation**: Custom using Normal Equation
- **Formula**: θ = (X^T X)^(-1) X^T y
- **Method**: Closed-form solution
- **Pros**: Exact solution, no hyperparameters
- **Cons**: Computationally expensive for large datasets

### 8. SVM (Scratch)
- **Implementation**: Custom using Gradient Descent
- **Method**: Hinge loss optimization
- **Parameters**: 
  - learning_rate=0.001
  - lambda_param=0.01
  - n_iters=1000
- **Pros**: Educational, customizable
- **Cons**: Slower than sklearn, simplified implementation

### 9. Decision Tree (Scratch)
- **Implementation**: Custom recursive tree building
- **Splitting Criterion**: Mean Squared Error (MSE)
- **Parameters**:
  - max_depth=10
  - min_samples_split=2
- **Method**: Greedy recursive splitting
- **Pros**: Full control over algorithm
- **Cons**: Slower than optimized libraries

---

## API Usage

### Evaluate Single Model
```bash
curl -X POST http://localhost:8000/model/evaluate \
  -H "Content-Type: application/json" \
  -d '{"model_name": "SVM"}'
```

Available model names:
- `LinearRegression`
- `RandomForest`
- `XGBoost`
- `LightGBM`
- `SVM`
- `DecisionTree`
- `LinearRegression_Scratch`
- `SVM_Scratch`
- `DecisionTree_Scratch`

### Compare All Models
```bash
curl -X POST http://localhost:8000/model/compare \
  -H "Content-Type: application/json" \
  -d '{"run_gridsearch": false}'
```

---

## Metrics Explained

### R² Score (Coefficient of Determination)
- Range: -∞ to 1
- Best: 1 (perfect prediction)
- Interpretation: Proportion of variance explained

### RMSE (Root Mean Squared Error)
- Range: 0 to ∞
- Best: 0 (no error)
- Unit: Same as target variable
- Interpretation: Average prediction error

### MAE (Mean Absolute Error)
- Range: 0 to ∞
- Best: 0 (no error)
- Interpretation: Average absolute error

### MSE (Mean Squared Error)
- Range: 0 to ∞
- Best: 0 (no error)
- Interpretation: Average squared error

---

## Implementation Files

- **main.py** - FastAPI backend with all models
- **models_scratch.py** - Custom implementations
- **frontend/** - React dashboard

---

## Performance Comparison

Use the Model Comparison tab in the frontend to see:
- Side-by-side metrics table
- R² Score bar chart
- RMSE comparison chart

This helps identify the best model for your specific dataset.
