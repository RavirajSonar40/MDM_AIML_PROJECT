import React, { useState } from 'react';
import axios from 'axios';

function Visualization({ apiUrl }) {
  const [analysisType, setAnalysisType] = useState('Univariate');
  const [variableType, setVariableType] = useState('Continuous');
  const [plots, setPlots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const generateVisualization = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post(`${apiUrl}/visualize`, {
        analysis_type: analysisType,
        variable_type: variableType
      });
      setPlots(response.data.plots);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error generating visualization');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Data Visualization</h2>

      <div className="select-group">
        <label>Analysis Type</label>
        <div className="select-wrapper">
          <select value={analysisType} onChange={(e) => setAnalysisType(e.target.value)}>
            <option value="Univariate">Univariate Analysis</option>
            <option value="Bivariate">Bivariate Analysis</option>
          </select>
        </div>
      </div>

      <div className="select-group">
        <label>Variable Type</label>
        <div className="select-wrapper">
          <select value={variableType} onChange={(e) => setVariableType(e.target.value)}>
            <option value="Continuous">Continuous</option>
            <option value="Categorical">Categorical</option>
          </select>
        </div>
      </div>

      <button className="btn" onClick={generateVisualization} disabled={loading}>
        {loading ? 'Generating...' : '📊 Generate Visualizations'}
      </button>

      {error && <div className="error">{error}</div>}

      {loading && (
        <div>
          <div className="spinner"></div>
          <p className="loading">Generating visualizations...</p>
        </div>
      )}

      {plots.length > 0 && (
        <div>
          <h3 style={{ marginTop: '2rem' }}>Results ({plots.length} plots)</h3>
          {plots.map((plot, index) => (
            <div key={index} className="image-container">
              <h4 style={{ marginBottom: '1rem' }}>{plot.variable}</h4>
              <img
                src={`data:image/png;base64,${plot.plot}`}
                alt={`${plot.variable} visualization`}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Visualization;
