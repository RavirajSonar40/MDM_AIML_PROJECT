# Marine Microplastics Frontend

Modern React dashboard for Marine Microplastics Analysis API.

## Features

- 📊 **Data Overview**: View dataset statistics and information
- 📈 **Visualizations**: Generate univariate and bivariate plots
- 🤖 **Model Evaluation**: Evaluate individual ML models
- ⚖️ **Model Comparison**: Compare all models side-by-side

## Installation

1. Install dependencies:
```bash
npm install
```

## Running the Application

1. Make sure the FastAPI backend is running on `http://localhost:8000`

2. Start the React development server:
```bash
npm start
```

3. Open your browser and navigate to `http://localhost:3000`

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── DataInfo.js
│   │   ├── Visualization.js
│   │   ├── ModelEvaluation.js
│   │   └── ModelComparison.js
│   ├── App.js
│   ├── App.css
│   ├── index.js
│   └── index.css
├── package.json
└── README.md
```

## Components

### DataInfo
Displays dataset overview including:
- Total rows and columns
- Numerical and categorical variables
- Data types and statistics

### Visualization
Generate visualizations with options for:
- Analysis type (Univariate/Bivariate)
- Variable type (Continuous/Categorical)

### ModelEvaluation
Evaluate individual models:
- Linear Regression
- Random Forest
- XGBoost
- LightGBM

View metrics: R² Score, RMSE, MAE, MSE

### ModelComparison
Compare all models simultaneously with:
- Side-by-side metrics table
- Visual comparison charts

## Technologies Used

- React 18
- Axios for API calls
- CSS3 with modern gradients and animations
- Responsive design

## API Configuration

The API URL is configured in `App.js`:
```javascript
const API_URL = 'http://localhost:8000';
```

Change this if your backend runs on a different port.

## Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` folder.
