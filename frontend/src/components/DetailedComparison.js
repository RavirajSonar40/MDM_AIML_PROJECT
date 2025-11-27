import React, { useState } from 'react';
import axios from 'axios';

function DetailedComparison({ apiUrl }) {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runComparison = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post(`${apiUrl}/model/detailed-comparison`, {
        run_gridsearch: false
      });
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error running comparison');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Detailed Model Comparison</h2>
      <p style={{ color: '#666', marginBottom: '1.5rem' }}>
        Comprehensive comparison with multiple metrics and visualizations
      </p>

      <button className="btn" onClick={runComparison} disabled={loading}>
        {loading ? 'Comparing...' : '📊 Run Detailed Comparison'}
      </button>

      {error && <div className="error">{error}</div>}

      {loading && (
        <div>
          <div className="spinner"></div>
          <p className="loading">Running detailed comparison...</p>
        </div>
      )}

      {results && (
        <div>
          <h3 style={{ marginTop: '2rem' }}>Comparison Results</h3>
          
          <div style={{ overflowX: 'auto', marginTop: '1.5rem' }}>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse',
              background: 'white',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              borderRadius: '8px'
            }}>
              <thead>
                <tr style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                  <th style={{ padding: '1rem', textAlign: 'left' }}>Model</th>
                  <th style={{ padding: '1rem', textAlign: 'right' }}>R² Score</th>
                  <th style={{ padding: '1rem', textAlign: 'right' }}>RMSE</th>
                  <th style={{ padding: '1rem', textAlign: 'right' }}>MAE</th>
                  <th style={{ padding: '1rem', textAlign: 'right' }}>⏱️ Time (s)</th>
                </tr>
              </thead>
              <tbody>
                {results.results.map((result, index) => (
                  <tr key={index} style={{
                    borderBottom: '1px solid #e0e0e0',
                    background: index % 2 === 0 ? '#f8f9fa' : 'white'
                  }}>
                    <td style={{ padding: '1rem', fontWeight: '500' }}>{result.model_name}</td>
                    <td style={{ padding: '1rem', textAlign: 'right', color: '#667eea', fontWeight: '600' }}>
                      {result.r2_score.toFixed(4)}
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'right' }}>{result.rmse.toFixed(2)}</td>
                    <td style={{ padding: '1rem', textAlign: 'right' }}>{result.mae.toFixed(2)}</td>
                    <td style={{ padding: '1rem', textAlign: 'right', color: '#ff6b6b', fontWeight: '500' }}>
                      {result.training_time}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {results.total_time && (
            <div style={{ background: '#f0f7ff', padding: '1rem', borderRadius: '8px', marginTop: '1rem', textAlign: 'center' }}>
              <strong>⏱️ Total Time:</strong> {results.total_time}s
            </div>
          )}

          <div className="image-container">
            <h4 style={{ color: '#1e3c72', marginBottom: '1rem' }}>Comprehensive Metrics Comparison</h4>
            <img 
              src={`data:image/png;base64,${results.comparison_plot}`} 
              alt="Detailed comparison plot"
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default DetailedComparison;
