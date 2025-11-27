import React, { useState } from 'react';
import axios from 'axios';

function CrossValidation({ apiUrl }) {
  const [cvFolds, setCvFolds] = useState(5);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runCrossValidation = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post(`${apiUrl}/model/cross-validate`, {
        cv_folds: cvFolds
      });
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error running cross-validation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Cross-Validation Analysis</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
        Evaluate model performance using k-fold cross-validation
      </p>

      <div className="select-group">
        <label>Number of Folds</label>
        <div className="select-wrapper">
          <select value={cvFolds} onChange={(e) => setCvFolds(Number(e.target.value))}>
            <option value={3}>3-Fold</option>
            <option value={5}>5-Fold</option>
            <option value={10}>10-Fold</option>
          </select>
        </div>
      </div>

      <button className="btn" onClick={runCrossValidation} disabled={loading}>
        {loading ? 'Running CV...' : '🔄 Run Cross-Validation'}
      </button>

      {error && <div className="error">{error}</div>}

      {loading && (
        <div>
          <div className="spinner"></div>
          <p className="loading">Running cross-validation...</p>
        </div>
      )}

      {results && (
        <div>
          <h3 style={{ marginTop: '2rem' }}>{cvFolds}-Fold CV Results</h3>

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
                  <th style={{ padding: '1rem', textAlign: 'right' }}>Mean R²</th>
                  <th style={{ padding: '1rem', textAlign: 'right' }}>Std Dev</th>
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
                      {result.mean_r2.toFixed(4)}
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'right' }}>±{result.std_r2.toFixed(4)}</td>
                    <td style={{ padding: '1rem', textAlign: 'right', color: '#ff6b6b', fontWeight: '500' }}>
                      {result.time}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {results.total_time && (
            <div style={{ background: 'var(--nav-bg)', padding: '1rem', borderRadius: '8px', marginTop: '1rem', textAlign: 'center', border: '1px solid var(--glass-border)', color: 'var(--accent-glow)' }}>
              <strong>⏱️ Total CV Time:</strong> {results.total_time}s
            </div>
          )}

          <div className="image-container">
            <h4 style={{ marginBottom: '1rem' }}>Cross-Validation Scores</h4>
            <img
              src={`data:image/png;base64,${results.cv_plot}`}
              alt="Cross-validation plot"
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default CrossValidation;
