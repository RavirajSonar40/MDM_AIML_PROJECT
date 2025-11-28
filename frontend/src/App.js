import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import './App.css';
import DataInfo from './components/DataInfo';
import Visualization from './components/Visualization';
import ModelEvaluation from './components/ModelEvaluation';
import ModelComparison from './components/ModelComparison';
import CrossValidation from './components/CrossValidation';
import CustomCursor from './components/CustomCursor';
import ParticleBackground from './components/ParticleBackground';

const API_URL = '';  // API is served from the same domain in production

function App() {
  const [activeTab, setActiveTab] = useState('data');
  const [dataInfo, setDataInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    fetchDataInfo();
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

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
      <CustomCursor />
      <ParticleBackground />

      <button className="theme-toggle" onClick={toggleTheme} title="Toggle Theme">
        {theme === 'dark' ? '☀️' : '🌙'}
      </button>

      <div className="aurora-bg">
        <div className="aurora-blob blob-1"></div>
        <div className="aurora-blob blob-2"></div>
        <div className="aurora-blob blob-3"></div>
      </div>

      <div className="bubbles">
        <div className="bubble"></div>
        <div className="bubble"></div>
        <div className="bubble"></div>
        <div className="bubble"></div>
        <div className="bubble"></div>
        <div className="bubble"></div>
      </div>

      <div className="content-wrapper">
        <header className="hero-header">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, ease: "easeOut" }}
          >
            <div className="hero-subtitle">Marine Microplastics Analysis</div>
            <h1 className="hero-title">
              OCEAN<br />ANALYTICS
            </h1>
          </motion.div>
        </header>

        <div className="nav-container">
          <nav className="nav-tabs">
            {['data', 'visualize', 'evaluate', 'compare', 'cv'].map((tab) => (
              <button
                key={tab}
                className={activeTab === tab ? 'tab active' : 'tab'}
                onClick={() => setActiveTab(tab)}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </nav>
        </div>

        <main className="main-content">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.95 }}
              transition={{ duration: 0.4 }}
            >
              <div className="card-3d">
                {activeTab === 'data' && <DataInfo dataInfo={dataInfo} loading={loading} />}
                {activeTab === 'visualize' && <Visualization apiUrl={API_URL} />}
                {activeTab === 'evaluate' && <ModelEvaluation apiUrl={API_URL} />}
                {activeTab === 'compare' && <ModelComparison apiUrl={API_URL} />}
                {activeTab === 'cv' && <CrossValidation apiUrl={API_URL} />}
              </div>
            </motion.div>
          </AnimatePresence>
        </main>

        <footer style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>
          <p>Designed for Advanced Analytics</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
