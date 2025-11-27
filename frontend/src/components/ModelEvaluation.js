import React, { useState } from 'react';
import axios from 'axios';

function ModelEvaluation({ apiUrl }) {
  const [modelName, setModelName] = useState('RandomForest');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const models = [
    { value: 'LinearRegression', label: 'Linear Regression (sklearn)' },
    { value: 'RandomForest', label: 'Random Forest' },
    { value: 'XGBoost', label: 'XGBoost' },
    { value: 'LightGBM', label: 'LightGBM' },
    { value: 'SVM', label: 'SVM (sklearn)' },
    { value: 'DecisionTree', label: 'Decision Tree (sklearn)' },
    { value: 'LinearRegression_Scratch', label: 'Linear Regression (Scratch)' },
    { value: 'SVM_Scratch', label: 'SVM (Scratch)' },
    { value: 'DecisionTree_Scratch', label: 'Decision Tree (Scratch)' }
  ];

  const evaluateModel = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post(`${apiUrl}/model/evaluate`, {
        model_name: modelName
      });
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error evaluating model');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Model Evaluation</h2>

      <div className="select-group">
        <label>Select Model</label>
        <div className="select-wrapper">
          <select value={modelName} onChange={(e) => setModelName(e.target.value)}>
            {models.map(model => (
              <option key={model.value} value={model.value}>
                {model.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <button className="btn" onClick={evaluateModel} disabled={loading}>
        {loading ? 'Evaluating...' : '🚀 Evaluate Model'}
      </button>

      {error && <div className="error">{error}</div>}

      {loading && (
        <div>
          <div className="spinner"></div>
          <p className="loading">Evaluating model...</p>
        </div>
      )}

      {results && (
        <div>
          <h3 style={{ marginTop: '2rem' }}>Results for {results.model_name}</h3>

          <div className="metrics-grid">
            <div className="metric-item">
              <h4>R² Score</h4>
              <p>{results.metrics.r2_score.toFixed(4)}</p>
            </div>
            <div className="metric-item">
              <h4>RMSE</h4>
              <p>{results.metrics.rmse.toFixed(4)}</p>
            </div>
            <div className="metric-item">
              <h4>MAE</h4>
              <p>{results.metrics.mae.toFixed(4)}</p>
            </div>
            <div className="metric-item">
              <h4>MSE</h4>
              <p>{results.metrics.mse.toFixed(4)}</p>
            </div>
          </div>

          {results.timing && (
            <div style={{ background: 'var(--nav-bg)', padding: '1rem', borderRadius: '8px', marginTop: '1rem', border: '1px solid var(--glass-border)' }}>
              <h4 style={{ color: 'var(--accent-glow)', marginBottom: '0.5rem', fontFamily: 'Source Code Pro, monospace' }}>⏱️ Performance Timing</h4>
              <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
                <div>
                  <strong>Training:</strong> {results.timing.train_time}s
                </div>
                <div>
                  <strong>Prediction:</strong> {results.timing.prediction_time}s
                </div>
                <div>
                  <strong>Total:</strong> {results.timing.total_time}s
                </div>
              </div>
            </div>
          )}

          <div className="image-container">
            <h4 style={{ marginBottom: '1rem' }}>Actual vs Predicted</h4>
            <img
              src={`data:image/png;base64,${results.plot}`}
              alt="Model evaluation plot"
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default ModelEvaluation;
