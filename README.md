# 🌊 Marine Microplastics Analysis System

A comprehensive machine learning platform for analyzing marine microplastic pollution using environmental monitoring data. This project implements multiple ML algorithms to predict microplastic concentrations and provides an interactive web interface for data exploration and model evaluation.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![React](https://img.shields.io/badge/React-18+-blue.svg)
![XGBoost](https://img.shields.io/badge/XGBoost-1.7+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Dataset](#dataset)
- [Machine Learning Models](#machine-learning-models)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### 🔬 Data Analysis & Visualization
- **Statistical Analysis**: Comprehensive descriptive statistics and correlation analysis
- **Interactive Visualizations**: Histograms, scatter plots, box plots, and correlation heatmaps
- **Geographic Analysis**: Spatial distribution of microplastic concentrations
- **Real-time Data Exploration**: Dynamic plotting with multiple visualization types

### 🤖 Machine Learning Pipeline
- **Multiple Algorithms**: XGBoost, LightGBM, Random Forest, SVM, Ridge Regression, Decision Trees
- **Custom Implementations**: From-scratch implementations of core ML algorithms
- **Model Comparison**: Side-by-side performance evaluation across all models
- **Cross-Validation**: K-fold validation with configurable parameters
- **Hyperparameter Tuning**: Optimized model parameters for best performance

### 🌐 Web Interface
- **Modern UI**: Glassmorphism design with responsive layout
- **Real-time Loading**: Animated loading states during model training
- **Interactive Components**: Dropdown selections, model comparisons, and result visualizations
- **Theme Support**: Dark/light mode toggle

### 📊 Evaluation & Metrics
- **Comprehensive Metrics**: MSE, RMSE, MAE, R² Score
- **Performance Visualization**: Actual vs Predicted plots
- **Cross-Validation Results**: Stability analysis across different data folds
- **Comparative Analysis**: Detailed model performance comparisons

## 🛠 Technology Stack

### Backend
- **FastAPI**: High-performance async web framework
- **Scikit-learn**: Machine learning algorithms and preprocessing
- **XGBoost & LightGBM**: Gradient boosting implementations
- **Pandas & NumPy**: Data manipulation and analysis
- **Matplotlib & Seaborn**: Data visualization
- **Uvicorn**: ASGI server for production deployment

### Frontend
- **React 18**: Modern JavaScript library for UI
- **CSS3**: Custom styling with glassmorphism effects
- **Axios**: HTTP client for API communication
- **Framer Motion**: Smooth animations and transitions

### Development Tools
- **Python 3.8+**: Core programming language
- **Node.js 16+**: JavaScript runtime for frontend
- **Git**: Version control
- **Docker**: Containerization (optional)

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- Git

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/your-username/marine-microplastics-analysis.git
cd marine-microplastics-analysis
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the backend server**
```bash
python main.py
```
The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install Node.js dependencies**
```bash
npm install
```

3. **Start the development server**
```bash
npm start
```
The web interface will be available at `http://localhost:3000`

## 📖 Usage

### Web Interface

1. **Data Overview**: View dataset statistics and explore variable distributions
2. **Visualization**: Generate various plots to understand data patterns
3. **Model Evaluation**:
   - Select an algorithm from the dropdown
   - Click "🚀 Evaluate Model" to train and test
   - View performance metrics and prediction plots
4. **Model Comparison**: Compare all algorithms side-by-side
5. **Cross-Validation**: Test model stability across different data folds

### API Usage

#### Get Dataset Information
```bash
curl http://localhost:8000/data/info
```

#### Evaluate a Model
```bash
curl -X POST "http://localhost:8000/model/evaluate" \
     -H "Content-Type: application/json" \
     -d '{"model_name": "XGBoost"}'
```

#### Generate Visualizations
```bash
curl -X POST "http://localhost:8000/visualize" \
     -H "Content-Type: application/json" \
     -d '{"analysis_type": "Univariate", "variable_type": "Continuous"}'
```

## 📚 API Documentation

### Endpoints

#### Data Endpoints
- `GET /data/info` - Dataset overview and statistics
- `GET /data/sample?n=10` - Sample data rows
- `GET /data/statistics` - Detailed statistical summary

#### Visualization Endpoints
- `POST /visualize` - Generate data visualizations
  ```json
  {
    "analysis_type": "Univariate|Bivariate",
    "variable_type": "Continuous|Categorical"
  }
  ```

#### Model Endpoints
- `POST /model/evaluate` - Evaluate single model
  ```json
  {
    "model_name": "XGBoost|LightGBM|RandomForest|Ridge|SVM|DecisionTree|LinearRegression_Scratch|SVM_Scratch|DecisionTree_Scratch"
  }
  ```

- `POST /model/compare` - Compare all models
- `POST /model/cross-validate` - Cross-validation analysis
  ```json
  {
    "cv_folds": 5
  }
  ```

- `POST /model/detailed-comparison` - Detailed model comparison

#### System Endpoints
- `GET /health` - Health check
- `GET /` - API information

## 📁 Project Structure

```
marine-microplastics-analysis/
├── main.py                      # FastAPI backend server
├── models_scratch.py            # Custom ML algorithm implementations
├── requirements.txt             # Python dependencies
├── PROJECT_ANALYSIS_REPORT.md   # Detailed project analysis
├── Marine_Microplastics_WGS84_8553846406879449657.csv  # Dataset
├── frontend/
│   ├── package.json
│   ├── public/
│   └── src/
│       ├── App.js              # Main React component
│       ├── App.css             # Styling
│       └── components/         # React components
│           ├── DataInfo.js
│           ├── ModelEvaluation.js
│           ├── ModelComparison.js
│           ├── CrossValidation.js
│           ├── Visualization.js
│           └── ...
└── README.md                    # This file
```

## 📊 Dataset

### Marine Microplastics WGS84 Dataset
- **Size**: 22,530 rows × 36 columns
- **Domain**: Environmental monitoring of marine microplastic pollution
- **Geographic Coverage**: Global marine locations (WGS84 coordinates)
- **Target Variable**: Standardized Nurdle Amount (μg/L)

### Key Features
- **Spatial Data**: Latitude, longitude, sampling locations
- **Environmental**: Temperature, salinity, depth, current speed
- **Microplastic Metrics**: Concentration, particle size, material type
- **Metadata**: Sampling methods, dates, research institutions

## 🧠 Machine Learning Models

### Implemented Algorithms

1. **XGBoost** - Gradient boosting with superior performance (R²: 0.823)
2. **LightGBM** - Fast gradient boosting with efficiency (R²: 0.815)
3. **Random Forest** - Ensemble method with robustness (R²: 0.798)
4. **Ridge Regression** - Linear model with L2 regularization (R²: 0.756)
5. **SVM** - Support Vector Machine for non-linear patterns (R²: 0.742)
6. **Decision Tree** - Interpretable baseline model (R²: 0.723)
7. **Custom Implementations** - From-scratch algorithms for educational purposes

### Performance Metrics
- **Primary Metric**: R² Score (coefficient of determination)
- **Error Metrics**: RMSE, MAE, MSE
- **Validation**: 5-fold cross-validation
- **Testing**: Unseen data evaluation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use meaningful commit messages
- Add tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Dataset Source**: Marine Microplastics Research Community
- **Libraries**: Scikit-learn, XGBoost, LightGBM, FastAPI, React
- **Inspiration**: Environmental monitoring and AI for social good

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check the API documentation
- Review the project analysis report

---

**🌊 Making Marine Pollution Predictable Through AI**

*This project demonstrates the complete ML lifecycle from data collection to production deployment, providing actionable insights for environmental monitoring and microplastic pollution control.*
