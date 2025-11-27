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
      <div className="card">
        <h2>Dataset Overview</h2>
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
      </div>

      <div className="card">
        <h3>Numerical Variables</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {dataInfo.numerical_variables?.map((variable, index) => (
            <span key={index} style={{
              background: '#e3f2fd',
              padding: '0.5rem 1rem',
              borderRadius: '20px',
              fontSize: '0.9rem',
              color: '#1976d2'
            }}>
              {variable}
            </span>
          ))}
        </div>
      </div>

      <div className="card">
        <h3>Categorical Variables</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {dataInfo.categorical_variables?.map((variable, index) => (
            <span key={index} style={{
              background: '#f3e5f5',
              padding: '0.5rem 1rem',
              borderRadius: '20px',
              fontSize: '0.9rem',
              color: '#7b1fa2'
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
