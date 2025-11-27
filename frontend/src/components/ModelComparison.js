import React, { useState } from 'react';
import axios from 'axios';

function ModelComparison({ apiUrl }) {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const compareModels = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post(`${apiUrl}/model/compare`, {
        run_gridsearch: false
      });
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error comparing models');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Model Comparison</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
        Compare all available models side-by-side
      </p>

      <button className="btn" onClick={compareModels} disabled={loading}>
        {loading ? 'Comparing...' : '⚖️ Compare All Models'}
      </button>

      {error && <div className="error">{error}</div>}

      {loading && (
        <div>
          <div className="spinner"></div>
          <p className="loading">Comparing models...</p>
        </div>
      )}

      {results && (
        <div>
          <h3 style={{ marginTop: '2rem' }}>Comparison Results</h3>

          <div style={{ overflowX: 'auto', marginTop: '1.5rem' }}>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse',
              background: 'var(--card-bg)',
              boxShadow: '0 10px 30px -10px rgba(0, 0, 0, 0.2)',
              borderRadius: '8px',
              border: '1px solid var(--glass-border)'
            }}>
              <thead>
                <tr style={{ background: 'var(--nav-bg)', color: 'var(--accent-glow)' }}>
                  <th style={{ padding: '1rem', textAlign: 'left' }}>Model</th>
                  <th style={{ padding: '1rem', textAlign: 'right' }}>R² Score</th>
                  <th style={{ padding: '1rem', textAlign: 'right' }}>RMSE</th>
                  <th style={{ padding: '1rem', textAlign: 'right' }}>MSE</th>
                  <th style={{ padding: '1rem', textAlign: 'right' }}>⏱️ Time (s)</th>
                </tr>
              </thead>
              <tbody>
                {results.results.map((result, index) => (
                  <tr key={index} style={{
                    borderBottom: '1px solid var(--glass-border)',
                    background: index % 2 === 0 ? 'var(--nav-bg)' : 'transparent',
                    color: 'var(--text-primary)'
                  }}>
                    <td style={{ padding: '1rem', fontWeight: '500' }}>{result.model_name}</td>
                    <td style={{ padding: '1rem', textAlign: 'right', color: 'var(--accent-glow)', fontWeight: '600', fontFamily: 'Source Code Pro, monospace' }}>
                      {result.r2_score.toFixed(4)}
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'right' }}>{result.rmse.toFixed(4)}</td>
                    <td style={{ padding: '1rem', textAlign: 'right' }}>{result.mse.toFixed(4)}</td>
                    <td style={{ padding: '1rem', textAlign: 'right', color: '#ff6b6b', fontWeight: '500' }}>
                      {result.training_time}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {results.total_time && (
            <div style={{ background: 'var(--nav-bg)', padding: '1rem', borderRadius: '8px', marginTop: '1rem', textAlign: 'center', border: '1px solid var(--glass-border)', color: 'var(--accent-glow)' }}>
              <strong>⏱️ Total Comparison Time:</strong> {results.total_time}s
            </div>
          )}

          <div className="image-container">
            <h4 style={{ marginBottom: '1rem' }}>Performance Comparison</h4>
            <img
              src={`data:image/png;base64,${results.comparison_plot}`}
              alt="Model comparison plot"
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default ModelComparison;
