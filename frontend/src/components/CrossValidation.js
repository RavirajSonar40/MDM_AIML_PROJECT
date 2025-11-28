import React, { useState } from 'react';
import axios from 'axios';

function CrossValidation({ apiUrl }) {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runCrossValidation = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post(`${apiUrl}/model/cross-validate`, {});
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
          <div style={{ background: 'var(--nav-bg)', padding: '1.5rem', borderRadius: '8px', marginTop: '2rem', border: '1px solid var(--glass-border)', textAlign: 'center' }}>
            <h3 style={{ color: 'var(--accent-glow)', margin: '0 0 0.5rem 0' }}>
              🏆 Best Cross-Validation: {results.best_cv_folds}-Fold
            </h3>
            <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
              Determined by highest average R² score across all models
            </p>
          </div>

          <h3 style={{ marginTop: '2rem' }}>Model Performance ({results.best_cv_folds}-Fold CV)</h3>

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
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h3 style={{ marginTop: '2rem' }}>Cross-Validation Comparison</h3>
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
                  <th style={{ padding: '1rem', textAlign: 'left' }}>CV Folds</th>
                  <th style={{ padding: '1rem', textAlign: 'right' }}>Avg R² Score</th>
                </tr>
              </thead>
              <tbody>
                {results.cv_comparison.map((cv, index) => (
                  <tr key={index} style={{
                    borderBottom: '1px solid var(--glass-border)',
                    background: cv.cv_folds === results.best_cv_folds ? 'rgba(0, 255, 0, 0.1)' : (index % 2 === 0 ? 'var(--nav-bg)' : 'transparent'),
                    color: 'var(--text-primary)'
                  }}>
                    <td style={{ padding: '1rem', fontWeight: cv.cv_folds === results.best_cv_folds ? '700' : '500' }}>
                      {cv.cv_folds}-Fold {cv.cv_folds === results.best_cv_folds && '🏆'}
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'right', color: cv.cv_folds === results.best_cv_folds ? 'var(--accent-glow)' : 'var(--text-primary)', fontWeight: cv.cv_folds === results.best_cv_folds ? '700' : '500', fontFamily: 'Source Code Pro, monospace' }}>
                      {cv.average_r2.toFixed(4)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {results.total_time && (
            <div style={{ background: 'var(--nav-bg)', padding: '1rem', borderRadius: '8px', marginTop: '1rem', textAlign: 'center', border: '1px solid var(--glass-border)', color: 'var(--accent-glow)' }}>
              <strong>⏱️ Total Analysis Time:</strong> {results.total_time}s
            </div>
          )}

          <div className="image-container">
            <h4 style={{ marginBottom: '1rem' }}>Cross-Validation Fold Comparison</h4>
            <img
              src={`data:image/png;base64,${results.cv_plot}`}
              alt="Cross-validation comparison plot"
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default CrossValidation;
