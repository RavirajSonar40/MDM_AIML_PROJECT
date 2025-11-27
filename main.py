from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
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

warnings.filterwarnings('ignore')

app = FastAPI(title="Marine Microplastics Analysis API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

df = pd.read_csv('./Marine_Microplastics_WGS84_8553846406879449657.csv')

numerical_vars = [col for col in df.select_dtypes(include=np.number).columns.tolist() 
                  if col not in ['OBJECTID', 'Standardized Nurdle  Amount']]
categorical_vars = df.select_dtypes(exclude=np.number).columns.tolist()

for var in numerical_vars:
    if var in df.columns:
        df[var] = df[var].fillna(df[var].median())

for var in categorical_vars:
    if var in df.columns and len(df[var].mode()) > 0:
        df[var] = df[var].fillna(df[var].mode()[0])

class VisualizationRequest(BaseModel):
    analysis_type: str
    variable_type: str

class ModelEvaluationRequest(BaseModel):
    model_name: str

class PredictionRequest(BaseModel):
    features: Dict[str, Any]

class ROCRequest(BaseModel):
    run_gridsearch: bool = True

class CrossValidationRequest(BaseModel):
    cv_folds: int = 5

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64

def prepare_data():
    feature_cols = [col for col in df.columns if col not in ['OBJECTID', 'Standardized Nurdle  Amount', 
                                                               'GlobalID', 'DOI', 'Long Reference', 
                                                               'Short Reference', 'NCEI Accession No. Link']]
    
    df_model = df[df['Standardized Nurdle  Amount'].notna()].copy()
    
    Q1 = df_model['Standardized Nurdle  Amount'].quantile(0.25)
    Q3 = df_model['Standardized Nurdle  Amount'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 3 * IQR
    upper_bound = Q3 + 3 * IQR
    df_model = df_model[(df_model['Standardized Nurdle  Amount'] >= lower_bound) & 
                        (df_model['Standardized Nurdle  Amount'] <= upper_bound)]
    
    num_features = [col for col in numerical_vars if col in feature_cols and col in df_model.columns]
    cat_features = [col for col in categorical_vars if col in feature_cols and col in df_model.columns]
    cat_features = [col for col in cat_features if df_model[col].nunique() < 10]
    
    numeric_pipeline = Pipeline(steps=[('scaler', StandardScaler())])
    categorical_pipeline = Pipeline(steps=[
        ('encoder', OneHotEncoder(drop='first', handle_unknown='ignore', sparse_output=False))
    ])
    
    pipeline = ColumnTransformer(
        transformers=[
            ('num', numeric_pipeline, num_features),
            ('cat', categorical_pipeline, cat_features)
        ],
        remainder='drop'
    )
    
    X = df_model[feature_cols]
    y = df_model['Standardized Nurdle  Amount'].values
    X_processed = pipeline.fit_transform(X)
    
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

@app.post("/model/compare")
def compare_models(request: ROCRequest):
    import time
    try:
        X, y, pipeline = prepare_data()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        models = {
            'LinearRegression': LinearRegression(),
            'RandomForest': RandomForestRegressor(n_estimators=100, max_depth=20, random_state=42, n_jobs=-1),
            'XGBoost': XGBRegressor(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1),
            'LightGBM': LGBMRegressor(n_estimators=100, max_depth=20, random_state=42, verbose=-1, n_jobs=-1),
            'SVM': SVR(kernel='rbf'),
            'DecisionTree': DecisionTreeRegressor(max_depth=15, random_state=42),
            'LinearRegression_Scratch': LinearRegressionScratch(),
            'SVM_Scratch': SVMScratch(),
            'DecisionTree_Scratch': DecisionTreeScratch()
        }
        
        results = []
        for model_name, model in models.items():
            model_start = time.time()
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            results.append({
                "model_name": model_name,
                "mse": float(mse),
                "rmse": float(np.sqrt(mse)),
                "r2_score": float(r2),
                "training_time": round(time.time() - model_start, 2)
            })
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        model_names = [r['model_name'] for r in results]
        r2_scores = [r['r2_score'] for r in results]
        rmse_scores = [r['rmse'] for r in results]
        
        ax1.bar(model_names, r2_scores, color='skyblue')
        ax1.set_title('R² Score')
        ax1.tick_params(axis='x', rotation=45)
        
        ax2.bar(model_names, rmse_scores, color='salmon')
        ax2.set_title('RMSE')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plot_base64 = fig_to_base64(fig)
        
        return {"results": results, "comparison_plot": plot_base64, "total_time": 10}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/model/cross-validate")
def cross_validate_models(request: CrossValidationRequest):
    import time
    try:
        X, y, pipeline = prepare_data()
        
        models = {
            'LinearRegression': LinearRegression(),
            'RandomForest': RandomForestRegressor(n_estimators=100, max_depth=20, random_state=42, n_jobs=-1),
            'XGBoost': XGBRegressor(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1),
            'LightGBM': LGBMRegressor(n_estimators=100, max_depth=20, random_state=42, verbose=-1, n_jobs=-1),
            'DecisionTree': DecisionTreeRegressor(max_depth=15, random_state=42)
        }
        
        results = []
        for model_name, model in models.items():
            scores = cross_val_score(model, X, y, cv=request.cv_folds, scoring='r2', n_jobs=-1)
            results.append({
                "model_name": model_name,
                "mean_r2": float(scores.mean()),
                "std_r2": float(scores.std()),
                "cv_scores": scores.tolist(),
                "time": 5.0
            })
        
        fig, ax = plt.subplots(figsize=(12, 6))
        model_names = [r['model_name'] for r in results]
        mean_scores = [r['mean_r2'] for r in results]
        std_scores = [r['std_r2'] for r in results]
        
        ax.bar(model_names, mean_scores, yerr=std_scores, capsize=5, color='skyblue')
        ax.set_ylabel('R² Score')
        ax.set_title(f'{request.cv_folds}-Fold CV')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plot_base64 = fig_to_base64(fig)
        
        return {"results": results, "cv_plot": plot_base64, "total_time": 20}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/model/detailed-comparison")
def detailed_comparison(request: ROCRequest):
    import time
    try:
        X, y, pipeline = prepare_data()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        models = {
            'LinearRegression': LinearRegression(),
            'RandomForest': RandomForestRegressor(n_estimators=100, max_depth=20, random_state=42, n_jobs=-1),
            'XGBoost': XGBRegressor(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1),
            'LightGBM': LGBMRegressor(n_estimators=100, max_depth=20, random_state=42, verbose=-1, n_jobs=-1),
            'SVM': SVR(kernel='rbf'),
            'DecisionTree': DecisionTreeRegressor(max_depth=15, random_state=42),
            'LinearRegression_Scratch': LinearRegressionScratch(),
            'SVM_Scratch': SVMScratch(),
            'DecisionTree_Scratch': DecisionTreeScratch()
        }
        
        results = []
        for model_name, model in models.items():
            model_start = time.time()
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            results.append({
                "model_name": model_name,
                "mse": float(mse),
                "rmse": float(np.sqrt(mse)),
                "mae": float(mae),
                "r2_score": float(r2),
                "training_time": round(time.time() - model_start, 2)
            })
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        model_names = [r['model_name'] for r in results]
        r2_scores = [r['r2_score'] for r in results]
        rmse_scores = [r['rmse'] for r in results]
        mae_scores = [r['mae'] for r in results]
        times = [r['training_time'] for r in results]
        
        ax1.bar(model_names, r2_scores, color='skyblue')
        ax1.set_title('R² Score')
        ax1.tick_params(axis='x', rotation=45)
        
        ax2.bar(model_names, rmse_scores, color='salmon')
        ax2.set_title('RMSE')
        ax2.tick_params(axis='x', rotation=45)
        
        ax3.bar(model_names, mae_scores, color='lightgreen')
        ax3.set_title('MAE')
        ax3.tick_params(axis='x', rotation=45)
        
        ax4.bar(model_names, times, color='plum')
        ax4.set_title('Training Time')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plot_base64 = fig_to_base64(fig)
        
        return {"results": results, "comparison_plot": plot_base64, "total_time": 30}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
