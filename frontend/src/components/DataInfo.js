import React from 'react';

function DataInfo({ dataInfo, loading }) {
  if (loading) {
    return (
      <div className="card">
        <div className="spinner"></div>
        <p className="loading">Loading data information...</p>
      </div>
    );
  }

  if (!dataInfo) {
    return (
      <div className="card">
        <p className="loading">No data available</p>
      </div>
    );
  }

  return (
    <div>
      <h2 style={{ marginBottom: '2rem' }}>Dataset Overview</h2>
      <div className="grid">
        <div className="stat-card">
          <h3>Total Rows</h3>
          <p>{dataInfo.total_rows?.toLocaleString()}</p>
        </div>
        <div className="stat-card">
          <h3>Total Columns</h3>
          <p>{dataInfo.total_columns}</p>
        </div>
        <div className="stat-card">
          <h3>Numerical Variables</h3>
          <p>{dataInfo.numerical_variables?.length}</p>
        </div>
        <div className="stat-card">
          <h3>Categorical Variables</h3>
          <p>{dataInfo.categorical_variables?.length}</p>
        </div>
      </div>

      <div style={{ marginTop: '3rem' }}>
        <h3 style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>Numerical Variables</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {dataInfo.numerical_variables?.map((variable, index) => (
            <span key={index} style={{
              background: 'rgba(100, 255, 218, 0.1)',
              padding: '0.5rem 1rem',
              borderRadius: '20px',
              fontSize: '0.9rem',
              color: 'var(--accent-glow)',
              border: '1px solid var(--glass-border)'
            }}>
              {variable}
            </span>
          ))}
        </div>
      </div>

      <div style={{ marginTop: '2rem' }}>
        <h3 style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>Categorical Variables</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {dataInfo.categorical_variables?.map((variable, index) => (
            <span key={index} style={{
              background: 'rgba(189, 52, 254, 0.1)',
              padding: '0.5rem 1rem',
              borderRadius: '20px',
              fontSize: '0.9rem',
              color: 'var(--accent-purple)',
              border: '1px solid var(--glass-border)'
            }}>
              {variable}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

export default DataInfo;
