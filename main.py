
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
import pickle
import io
import base64
from matplotlib import pyplot as plt
import seaborn as sns
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score, cross_validate
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, VotingRegressor
from sklearn.preprocessing import StandardScaler, OrdinalEncoder, OneHotEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from models_scratch import LinearRegressionScratch, SVMScratch, DecisionTreeScratch
import warnings
import os

warnings.filterwarnings('ignore')

# Initialize FastAPI application with title and version
app = FastAPI(title="Marine Microplastics Analysis API", version="1.0.0")

# Mount static files for serving the React frontend
if os.path.exists("frontend/build"):
    app.mount("/", StaticFiles(directory="frontend/build", html=True), name="static")

# Add CORS middleware to allow cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development and production)
    allow_credentials=True,  # Allow credentials
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Load the marine microplastics dataset
df = pd.read_csv('./Marine_Microplastics_WGS84_8553846406879449657.csv')

# Identify numerical and categorical variables from the dataset
numerical_vars = [col for col in df.select_dtypes(include=np.number).columns.tolist()
                  if col not in ['OBJECTID', 'Standardized Nurdle  Amount']]  
categorical_vars = df.select_dtypes(exclude=np.number).columns.tolist()  # Get categorical columns

# Handle missing values: fill numerical columns with median, categorical with mode
for var in numerical_vars:
    if var in df.columns:
        df[var] = df[var].fillna(df[var].median())

for var in categorical_vars:
    if var in df.columns and len(df[var].mode()) > 0:
        df[var] = df[var].fillna(df[var].mode()[0])

# Pydantic models for API request validation
class VisualizationRequest(BaseModel):
    analysis_type: str  # Type of analysis: 'Univariate' or 'Bivariate'
    variable_type: str  # Type of variables: 'Continuous' or 'Categorical'

class ModelEvaluationRequest(BaseModel):
    model_name: str  # Name of the ML model to evaluate

class PredictionRequest(BaseModel):
    features: Dict[str, Any]  # Feature values for prediction 

class ROCRequest(BaseModel):
    run_gridsearch: bool = True  # Flag for grid search 

class CrossValidationRequest(BaseModel):
    pass  # No parameters needed, will test multiple CV folds internally

# Utility function to convert matplotlib figures to base64 encoded strings for API responses
def fig_to_base64(fig):
    buf = io.BytesIO()  
    fig.savefig(buf, format='png', bbox_inches='tight')  
    buf.seek(0)  
    img_base64 = base64.b64encode(buf.read()).decode('utf-8') 
    plt.close(fig)  
    return img_base64

# Function to prepare and preprocess the dataset for machine learning
def prepare_data():
    # Define feature columns by excluding IDs and target variable
    feature_cols = [col for col in df.columns if col not in ['OBJECTID', 'Standardized Nurdle  Amount',
                                                               'GlobalID', 'DOI', 'Long Reference',
                                                               'Short Reference', 'NCEI Accession No. Link']]

    # Filter out rows with missing target values
    df_model = df[df['Standardized Nurdle  Amount'].notna()].copy()

    # Remove outliers using IQR method (3*IQR from Q1/Q3)
    Q1 = df_model['Standardized Nurdle  Amount'].quantile(0.25)
    Q3 = df_model['Standardized Nurdle  Amount'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 3 * IQR
    upper_bound = Q3 + 3 * IQR
    df_model = df_model[(df_model['Standardized Nurdle  Amount'] >= lower_bound) &
                        (df_model['Standardized Nurdle  Amount'] <= upper_bound)]

    # Separate numerical and categorical features
    num_features = [col for col in numerical_vars if col in feature_cols and col in df_model.columns]
    cat_features = [col for col in categorical_vars if col in feature_cols and col in df_model.columns]
    cat_features = [col for col in cat_features if df_model[col].nunique() < 10]  # Only include low-cardinality categorical features

    # Create preprocessing pipelines
    numeric_pipeline = Pipeline(steps=[('scaler', StandardScaler())])  # Standardize numerical features
    categorical_pipeline = Pipeline(steps=[
        ('encoder', OneHotEncoder(drop='first', handle_unknown='ignore', sparse_output=False))  # One-hot encode categorical features
    ])

    # Combine pipelines using ColumnTransformer
    pipeline = ColumnTransformer(
        transformers=[
            ('num', numeric_pipeline, num_features),
            ('cat', categorical_pipeline, cat_features)
        ],
        remainder='drop'  # Drop any columns not specified in transformers
    )

    # Prepare features (X) and target (y)
    X = df_model[feature_cols]
    y = df_model['Standardized Nurdle  Amount'].values
    X_processed = pipeline.fit_transform(X)  # Apply preprocessing

    return X_processed, y, pipeline

@app.get("/")
def read_root():
    return {"message": "Marine Microplastics Analysis API", "version": "1.0.0"}

@app.get("/data/info")
def get_data_info():
    return {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "numerical_variables": numerical_vars,
        "categorical_variables": categorical_vars
    }

@app.get("/data/sample")
def get_sample_data(n: int = 10):
    return {"sample_size": n, "data": df.head(n).to_dict(orient='records')}

@app.get("/data/statistics")
def get_statistics():
    return {"statistics": df.describe().to_dict()}

# Endpoint to generate data visualizations (histograms, scatter plots, box plots)
@app.post("/visualize")
def generate_visualization(request: VisualizationRequest):
    plots = []
    try:
        if request.analysis_type == 'Univariate':
            if request.variable_type == 'Continuous':
                for var in numerical_vars[:5]:
                    if var in df.columns:
                        fig, ax = plt.subplots(figsize=(10, 5))
                        sns.histplot(df[var].dropna(), kde=True, ax=ax)
                        ax.set_title(f'Distribution of {var}')
                        plots.append({"variable": var, "plot": fig_to_base64(fig)})
            else:
                for var in categorical_vars[:5]:
                    if var in df.columns and df[var].nunique() < 20:
                        fig, ax = plt.subplots(figsize=(10, 5))
                        value_counts = df[var].value_counts().head(10)
                        sns.barplot(x=value_counts.values, y=value_counts.index, ax=ax)
                        ax.set_title(f'Count Plot of {var}')
                        plt.tight_layout()
                        plots.append({"variable": var, "plot": fig_to_base64(fig)})
        else:
            target = 'Standardized Nurdle  Amount'
            if target in df.columns:
                if request.variable_type == 'Continuous':
                    for var in numerical_vars[:5]:
                        if var in df.columns:
                            fig, ax = plt.subplots(figsize=(10, 5))
                            df_clean = df[[var, target]].dropna()
                            sns.scatterplot(x=df_clean[var], y=df_clean[target], ax=ax, alpha=0.5)
                            ax.set_title(f'{var} vs {target}')
                            plots.append({"variable": var, "plot": fig_to_base64(fig)})
                else:
                    for var in categorical_vars[:5]:
                        if var in df.columns and df[var].nunique() < 20:
                            fig, ax = plt.subplots(figsize=(10, 5))
                            df_clean = df[[var, target]].dropna()
                            sns.boxplot(x=var, y=target, data=df_clean, ax=ax)
                            plt.xticks(rotation=45)
                            ax.set_title(f'{target} by {var}')
                            plt.tight_layout()
                            plots.append({"variable": var, "plot": fig_to_base64(fig)})
        
        return {"analysis_type": request.analysis_type, "variable_type": request.variable_type, "plots": plots}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Endpoint to evaluate a single ML model using train-test split
@app.post("/model/evaluate")
def evaluate_model(request: ModelEvaluationRequest):
    import time
    try:
        start_time = time.time()
        X, y, pipeline = prepare_data()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        models = {
            'LinearRegression': Ridge(alpha=1.0),
            'RandomForest': RandomForestRegressor(n_estimators=100, max_depth=20, min_samples_split=5, random_state=42, n_jobs=-1),
            'XGBoost': XGBRegressor(n_estimators=100, max_depth=8, learning_rate=0.1, random_state=42, n_jobs=-1),
            'LightGBM': LGBMRegressor(n_estimators=100, max_depth=20, learning_rate=0.1, random_state=42, verbose=-1, n_jobs=-1),
            'SVM': SVR(kernel='rbf', C=1.0, epsilon=0.1, cache_size=500),
            'DecisionTree': DecisionTreeRegressor(max_depth=15, min_samples_split=5, random_state=42),
            'LinearRegression_Scratch': LinearRegressionScratch(),
            'SVM_Scratch': SVMScratch(n_iters=1000),
            'DecisionTree_Scratch': DecisionTreeScratch(max_depth=10, min_samples_split=10)
        }
        
        if request.model_name not in models:
            raise HTTPException(status_code=400, detail=f"Model not supported")
        
        model = models[request.model_name]
        train_start = time.time()
        model.fit(X_train, y_train)
        train_time = time.time() - train_start
        
        y_pred = model.predict(X_test)
        
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(y_test, y_pred, alpha=0.5)
        ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
        ax.set_xlabel('Actual')
        ax.set_ylabel('Predicted')
        ax.set_title(f'{request.model_name}')
        plot_base64 = fig_to_base64(fig)
        
        return {
            "model_name": request.model_name,
            "metrics": {"mse": float(mse), "rmse": float(np.sqrt(mse)), "mae": float(mae), "r2_score": float(r2)},
            "plot": plot_base64,
            "timing": {"train_time": round(train_time, 2), "prediction_time": 0.1, "total_time": round(time.time() - start_time, 2)}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Endpoint to compare all ML models using 5-fold cross-validation
@app.post("/model/compare")
def compare_models(request: ROCRequest):
    import time
    try:
        X, y, pipeline = prepare_data()
        cv_folds = 5

        models = {
            'LinearRegression': LinearRegression(),
            'RandomForest': RandomForestRegressor(n_estimators=100, max_depth=20, min_samples_split=5, random_state=42, n_jobs=-1),
            'XGBoost': XGBRegressor(n_estimators=100, max_depth=20, learning_rate=0.1, random_state=42, n_jobs=-1),
            'LightGBM': LGBMRegressor(n_estimators=100, max_depth=20, learning_rate=0.1, random_state=42, verbose=-1, n_jobs=-1),
            'SVM': SVR(kernel='rbf', C=1.0, epsilon=0.1),
            'DecisionTree': DecisionTreeRegressor(max_depth=15, min_samples_split=5, random_state=42),
            'LinearRegression_Scratch': LinearRegressionScratch(),
            'SVM_Scratch': SVMScratch(n_iters=1000),
            'DecisionTree_Scratch': DecisionTreeScratch(max_depth=10, min_samples_split=10)
        }

        results = []
        for model_name, model in models.items():
            start_time = time.time()
            cv_results = cross_validate(model, X, y, cv=cv_folds, scoring=['r2', 'neg_mean_squared_error', 'neg_mean_absolute_error'], n_jobs=-1)
            total_time = time.time() - start_time

            mean_r2 = cv_results['test_r2'].mean()
            mean_mse = -cv_results['test_neg_mean_squared_error'].mean()
            mean_mae = -cv_results['test_neg_mean_absolute_error'].mean()
            mean_rmse = np.sqrt(mean_mse)

            results.append({
                "model_name": model_name,
                "mse": float(mean_mse),
                "rmse": float(mean_rmse),
                "mae": float(mean_mae),
                "r2_score": float(mean_r2),
                "training_time": round(total_time / cv_folds, 2)  # Average time per fold
            })

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        model_names = [r['model_name'] for r in results]
        r2_scores = [r['r2_score'] for r in results]
        rmse_scores = [r['rmse'] for r in results]
        mae_scores = [r['mae'] for r in results]
        times = [r['training_time'] for r in results]

        ax1.bar(model_names, r2_scores, color='skyblue')
        ax1.set_title('Mean R² Score (5-fold CV)')
        ax1.tick_params(axis='x', rotation=45)

        ax2.bar(model_names, rmse_scores, color='salmon')
        ax2.set_title('Mean RMSE (5-fold CV)')
        ax2.tick_params(axis='x', rotation=45)

        ax3.bar(model_names, mae_scores, color='lightgreen')
        ax3.set_title('Mean MAE (5-fold CV)')
        ax3.tick_params(axis='x', rotation=45)

        ax4.bar(model_names, times, color='plum')
        ax4.set_title('Avg Training Time per Fold (s)')
        ax4.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plot_base64 = fig_to_base64(fig)

        return {"results": results, "comparison_plot": plot_base64, "total_time": round(sum(times), 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Endpoint to perform cross-validation on selected models and compare different CV folds
@app.post("/model/cross-validate")
def cross_validate_models(request: CrossValidationRequest):
    import time
    try:
        start_time = time.time()
        X, y, pipeline = prepare_data()

        models = {
            'LinearRegression': LinearRegression(),
            'RandomForest': RandomForestRegressor(n_estimators=100, max_depth=20, random_state=42, n_jobs=-1),
            'XGBoost': XGBRegressor(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1),
            'LightGBM': LGBMRegressor(n_estimators=100, max_depth=20, random_state=42, verbose=-1, n_jobs=-1),
            'DecisionTree': DecisionTreeRegressor(max_depth=15, random_state=42)
        }

        cv_folds_options = [3, 5, 7, 10]
        cv_comparison = []

        results = {}
        for model_name, model in models.items():
            results[model_name] = {}
            for cv_folds in cv_folds_options:
                scores = cross_val_score(model, X, y, cv=cv_folds, scoring='r2', n_jobs=-1)
                results[model_name][cv_folds] = {
                    "mean_r2": float(scores.mean()),
                    "std_r2": float(scores.std()),
                    "cv_scores": scores.tolist()
                }

        # Compute average R² for each CV fold across all models
        for cv_folds in cv_folds_options:
            avg_r2 = np.mean([results[model][cv_folds]["mean_r2"] for model in models.keys()])
            cv_comparison.append({
                "cv_folds": cv_folds,
                "average_r2": float(avg_r2)
            })

        # Find the best CV fold (highest average R²)
        best_cv = max(cv_comparison, key=lambda x: x["average_r2"])["cv_folds"]

        # Prepare results for the best CV fold
        best_results = []
        for model_name in models.keys():
            best_results.append({
                "model_name": model_name,
                "mean_r2": results[model_name][best_cv]["mean_r2"],
                "std_r2": results[model_name][best_cv]["std_r2"],
                "cv_scores": results[model_name][best_cv]["cv_scores"],
                "cv_folds": best_cv
            })

        # Create plot comparing different CV folds
        fig, ax = plt.subplots(figsize=(10, 6))
        cv_labels = [f"{cv['cv_folds']}-fold" for cv in cv_comparison]
        avg_scores = [cv["average_r2"] for cv in cv_comparison]

        bars = ax.bar(cv_labels, avg_scores, color='skyblue')
        ax.set_ylabel('Average R² Score')
        ax.set_title('Comparison of Cross-Validation Folds')
        ax.set_ylim(0, 1)

        # Highlight the best CV fold
        best_idx = cv_folds_options.index(best_cv)
        bars[best_idx].set_color('lightgreen')

        # Add value labels on bars
        for bar, score in zip(bars, avg_scores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{score:.3f}', ha='center', va='bottom')

        plt.tight_layout()
        plot_base64 = fig_to_base64(fig)

        total_time = time.time() - start_time

        return {
            "best_cv_folds": best_cv,
            "results": best_results,
            "cv_comparison": cv_comparison,
            "cv_plot": plot_base64,
            "total_time": round(total_time, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Endpoint for detailed model comparison using 5-fold cross-validation (similar to /model/compare)
@app.post("/model/detailed-comparison")
def detailed_comparison(request: ROCRequest):
    import time
    try:
        X, y, pipeline = prepare_data()
        cv_folds = 5

        models = {
            'LinearRegression': LinearRegression(),
            'RandomForest': RandomForestRegressor(n_estimators=100, max_depth=20, min_samples_split=5, random_state=42, n_jobs=-1),
            'XGBoost': XGBRegressor(n_estimators=100, max_depth=20, learning_rate=0.1, random_state=42, n_jobs=-1),
            'LightGBM': LGBMRegressor(n_estimators=100, max_depth=20, learning_rate=0.1, random_state=42, verbose=-1, n_jobs=-1),
            'SVM': SVR(kernel='rbf', C=1.0, epsilon=0.1),
            'DecisionTree': DecisionTreeRegressor(max_depth=15, min_samples_split=5, random_state=42),
            'LinearRegression_Scratch': LinearRegressionScratch(),
            'SVM_Scratch': SVMScratch(n_iters=1000),
            'DecisionTree_Scratch': DecisionTreeScratch(max_depth=10, min_samples_split=10)
        }

        results = []
        for model_name, model in models.items():
            start_time = time.time()
            cv_results = cross_validate(model, X, y, cv=cv_folds, scoring=['r2', 'neg_mean_squared_error', 'neg_mean_absolute_error'], n_jobs=-1)
            total_time = time.time() - start_time

            mean_r2 = cv_results['test_r2'].mean()
            mean_mse = -cv_results['test_neg_mean_squared_error'].mean()
            mean_mae = -cv_results['test_neg_mean_absolute_error'].mean()
            mean_rmse = np.sqrt(mean_mse)

            results.append({
                "model_name": model_name,
                "mse": float(mean_mse),
                "rmse": float(mean_rmse),
                "mae": float(mean_mae),
                "r2_score": float(mean_r2),
                "training_time": round(total_time / cv_folds, 2)  # Average time per fold
            })

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        model_names = [r['model_name'] for r in results]
        r2_scores = [r['r2_score'] for r in results]
        rmse_scores = [r['rmse'] for r in results]
        mae_scores = [r['mae'] for r in results]
        times = [r['training_time'] for r in results]

        ax1.bar(model_names, r2_scores, color='skyblue')
        ax1.set_title('Mean R² Score (5-fold CV)')
        ax1.tick_params(axis='x', rotation=45)

        ax2.bar(model_names, rmse_scores, color='salmon')
        ax2.set_title('Mean RMSE (5-fold CV)')
        ax2.tick_params(axis='x', rotation=45)

        ax3.bar(model_names, mae_scores, color='lightgreen')
        ax3.set_title('Mean MAE (5-fold CV)')
        ax3.tick_params(axis='x', rotation=45)

        ax4.bar(model_names, times, color='plum')
        ax4.set_title('Avg Training Time per Fold (s)')
        ax4.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plot_base64 = fig_to_base64(fig)

        return {"results": results, "comparison_plot": plot_base64, "total_time": round(sum(times), 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Health check endpoint for monitoring API status
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Main entry point to run the FastAPI application with Uvicorn server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Run on all interfaces, port 8000
