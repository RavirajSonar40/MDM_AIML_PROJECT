import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import DataInfo from './components/DataInfo';
import Visualization from './components/Visualization';
import ModelEvaluation from './components/ModelEvaluation';
import ModelComparison from './components/ModelComparison';
import CrossValidation from './components/CrossValidation';
import DetailedComparison from './components/DetailedComparison';

const API_URL = 'http://localhost:8000';

function App() {
  const [activeTab, setActiveTab] = useState('data');
  const [dataInfo, setDataInfo] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDataInfo();
  }, []);

  const fetchDataInfo = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/data/info`);
      setDataInfo(response.data);
    } catch (error) {
      console.error('Error fetching data info:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="header">
        <div className="header-content">
          <h1>🌊 Marine Microplastics Analysis</h1>
          <p>Advanced ML-powered analysis dashboard</p>
        </div>
      </header>

      <nav className="nav-tabs">
        <button 
          className={activeTab === 'data' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('data')}
        >
          📊 Data Overview
        </button>
        <button 
          className={activeTab === 'visualize' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('visualize')}
        >
          📈 Visualizations
        </button>
        <button 
          className={activeTab === 'evaluate' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('evaluate')}
        >
          🤖 Model Evaluation
        </button>
        <button 
          className={activeTab === 'compare' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('compare')}
        >
          ⚖️ Model Comparison
        </button>
        <button 
          className={activeTab === 'cv' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('cv')}
        >
          🔄 Cross-Validation
        </button>
        <button 
          className={activeTab === 'detailed' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('detailed')}
        >
          📊 Detailed Analysis
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'data' && <DataInfo dataInfo={dataInfo} loading={loading} />}
        {activeTab === 'visualize' && <Visualization apiUrl={API_URL} />}
        {activeTab === 'evaluate' && <ModelEvaluation apiUrl={API_URL} />}
        {activeTab === 'compare' && <ModelComparison apiUrl={API_URL} />}
        {activeTab === 'cv' && <CrossValidation apiUrl={API_URL} />}
        {activeTab === 'detailed' && <DetailedComparison apiUrl={API_URL} />}
      </main>

      <footer className="footer">
        <p>Marine Microplastics Analysis System © 2024</p>
      </footer>
    </div>
  );
}

export default App;
