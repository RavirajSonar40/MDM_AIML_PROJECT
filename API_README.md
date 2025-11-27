# Marine Microplastics Analysis API

FastAPI backend for analyzing the Maine microplastic dataset.

## Features

- **Data Endpoints**: Get dataset information, sample data, and statistics
- **Visualization**: Generate univariate and bivariate plots
- **Model Evaluation**: Evaluate different regression models (Linear Regression, Random Forest, XGBoost, LightGBM)
- **Model Comparison**: Compare multiple models side-by-side
- **Predictions**: Make predictions on microplastic concentrations

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the API

Start the server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Root
- `GET /` - API information and available endpoints

### Data Endpoints
- `GET /data/info` - Get dataset information (rows, columns, data types, missing values)
- `GET /data/sample?n=10` - Get sample data (default 10 rows)
- `GET /data/statistics` - Get statistical summary of numerical columns

### Visualization
- `POST /visualize` - Generate visualizations
  ```json
  {
    "analysis_type": "Univariate",  // or "Bivariate"
    "variable_type": "Continuous"   // or "Categorical"
  }
  ```

### Model Endpoints
- `POST /model/evaluate` - Evaluate a specific model
  ```json
  {
    "model_name": "RandomForest"  // LinearRegression, RandomForest, XGBoost, LightGBM
  }
  ```

- `POST /model/compare` - Compare all models
  ```json
  {
    "run_gridsearch": true
  }
  ```

- `POST /predict` - Make predictions
  ```json
  {
    "features": {
      "Latitude (degree)": 40.93,
      "Longitude(degree)": -70.65,
      "Ocean Bottom Depth (m)": 100,
      ...
    }
  }
  ```

### Health Check
- `GET /health` - Health check endpoint

## Interactive Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Example Usage

### Using cURL

```bash
# Get dataset info
curl http://localhost:8000/data/info

# Get sample data
curl http://localhost:8000/data/sample?n=5

# Generate visualization
curl -X POST http://localhost:8000/visualize \
  -H "Content-Type: application/json" \
  -d '{"analysis_type": "Univariate", "variable_type": "Continuous"}'

# Evaluate model
curl -X POST http://localhost:8000/model/evaluate \
  -H "Content-Type: application/json" \
  -d '{"model_name": "RandomForest"}'

# Compare models
curl -X POST http://localhost:8000/model/compare \
  -H "Content-Type: application/json" \
  -d '{"run_gridsearch": true}'
```

### Using Python

```python
import requests

# Get dataset info
response = requests.get("http://localhost:8000/data/info")
print(response.json())

# Generate visualization
response = requests.post(
    "http://localhost:8000/visualize",
    json={
        "analysis_type": "Univariate",
        "variable_type": "Continuous"
    }
)
plots = response.json()

# Evaluate model
response = requests.post(
    "http://localhost:8000/model/evaluate",
    json={"model_name": "RandomForest"}
)
results = response.json()
print(f"R² Score: {results['metrics']['r2_score']}")
```

## Dataset

The API uses the `Marine_Microplastics_WGS84_8553846406879449657.csv` dataset containing information about microplastic concentrations in marine environments.

## Models

The API supports the following regression models:
- **Linear Regression**: Simple baseline model
- **Random Forest**: Ensemble method using decision trees
- **XGBoost**: Gradient boosting framework
- **LightGBM**: Fast gradient boosting framework

## Response Format

All visualization and model evaluation endpoints return base64-encoded PNG images that can be displayed in web applications.

Example:
```json
{
  "plots": [
    {
      "variable": "Latitude (degree)",
      "plot": "iVBORw0KGgoAAAANSUhEUgAA..."
    }
  ]
}
```

To display in HTML:
```html
<img src="data:image/png;base64,{plot_data}" />
```
