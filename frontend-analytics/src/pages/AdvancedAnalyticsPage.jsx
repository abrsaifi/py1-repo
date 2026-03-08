import React, { useState, useEffect } from 'react'
import { UniversalIcon } from '../utils/UniversalIcon'
import CustomReportBuilder from './CustomReportBuilder'
import StatisticalAnalysis from './StatisticalAnalysis'
import PredictiveAnalytics from './PredictiveAnalytics'
import AdvancedDataViz from './AdvancedDataViz'
import { analyticsAPI } from '../services/api'
import '../styles/advanced-analytics.css'

const AdvancedAnalyticsPage = ({ onTitleChange }) => {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [analyticsData, setAnalyticsData] = useState({
    totalDataPoints: 0,
    analysisRuntime: 0,
    insights: []
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    onTitleChange?.('Advanced Analytics')
    loadAnalyticsData()
  }, [onTitleChange])

  const loadAnalyticsData = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await analyticsAPI.getDashboard()
      
      if (response.data && response.data.data) {
        const dashboardData = response.data.data
        setAnalyticsData({
          totalDataPoints: dashboardData.kpis?.total_data_points?.value || 15420,
          analysisRuntime: dashboardData.kpis?.analysis_runtime?.value || 2.34,
          insights: dashboardData.insights?.map(i => i.description) || []
        })
      }
    } catch (err) {
      console.error('Failed to load analytics dashboard:', err)
      setError('Failed to load analytics data')
      // Fallback to mock data on error
      setAnalyticsData({
        totalDataPoints: 15420,
        analysisRuntime: 2.34,
        insights: [
          'Trend shows 23% increase over last 30 days',
          'Anomaly detected: 2 standard deviations at 2024-03-02',
          'Forecast suggests 5.2% growth next month',
          'Correlation identified between metrics A and B (r=0.87)'
        ]
      })
    } finally {
      setLoading(false)
    }
  }

  const renderContent = () => {
    if (loading && activeTab === 'dashboard') {
      return (
        <div className="loading-container">
          <div className="spinner">⏳</div>
          <p>Loading analytics data...</p>
        </div>
      )
    }

    if (error && activeTab === 'dashboard') {
      return (
        <div className="error-container">
          <p className="error-message"><UniversalIcon icon="⚠️" size={18} /> {error}</p>
          <button onClick={loadAnalyticsData}>Retry</button>
        </div>
      )
    }

    switch (activeTab) {
      case 'dashboard':
        return <AnalyticsDashboard data={analyticsData} />
      case 'reports':
        return <CustomReportBuilder />
      case 'statistics':
        return <StatisticalAnalysis />
      case 'predictive':
        return <PredictiveAnalytics />
      case 'visualization':
        return <AdvancedDataViz />
      default:
        return <AnalyticsDashboard data={analyticsData} />
    }
  }

  return (
    <div className="advanced-analytics-page">
      <div className="analytics-header">
        <h1>📊 Advanced Analytics</h1>
        <p>Comprehensive data analysis, visualization, and reporting tools</p>
      </div>

      <div className="analytics-tabs">
        <button
          className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          📈 Dashboard
        </button>
        <button
          className={`tab-btn ${activeTab === 'reports' ? 'active' : ''}`}
          onClick={() => setActiveTab('reports')}
        >
          📝 Report Builder
        </button>
        <button
          className={`tab-btn ${activeTab === 'statistics' ? 'active' : ''}`}
          onClick={() => setActiveTab('statistics')}
        >
          📊 Statistics
        </button>
        <button
          className={`tab-btn ${activeTab === 'predictive' ? 'active' : ''}`}
          onClick={() => setActiveTab('predictive')}
        >
          🔮 Predictive
        </button>
        <button
          className={`tab-btn ${activeTab === 'visualization' ? 'active' : ''}`}
          onClick={() => setActiveTab('visualization')}
        >
          🎨 Visualization
        </button>
      </div>

      <div className="analytics-content">
        {renderContent()}
      </div>
    </div>
  )
}

const AnalyticsDashboard = ({ data }) => {
  return (
    <div className="analytics-dashboard">
      <div className="insights-grid">
        <div className="insight-card">
          <div className="insight-icon"><UniversalIcon icon="📊" size={48} /></div>
          <h3>Data Points Analyzed</h3>
          <p className="insight-value">{data.totalDataPoints.toLocaleString()}</p>
          <p className="insight-detail">Across all datasets</p>
        </div>

        <div className="insight-card">
          <div className="insight-icon"><UniversalIcon icon="⚡" size={48} /></div>
          <h3>Analysis Time</h3>
          <p className="insight-value">{data.analysisRuntime}s</p>
          <p className="insight-detail">Average processing time</p>
        </div>

        <div className="insight-card">
          <div className="insight-icon">💡</div>
          <h3>Key Insights Generated</h3>
          <p className="insight-value">{data.insights.length}</p>
          <p className="insight-detail">Automated discoveries</p>
        </div>

        <div className="insight-card">
          <div className="insight-icon"><UniversalIcon icon="✅" size={48} /></div>
          <h3>Analysis Tools</h3>
          <p className="insight-value">5</p>
          <p className="insight-detail">Available modules</p>
        </div>
      </div>

      <div className="insights-feed">
        <h2>Key Insights</h2>
        <div className="insights-list">
          {data.insights.map((insight, idx) => (
            <div key={idx} className="insight-item">
              <span className="insight-marker">💡</span>
              <p>{insight}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="analytics-guide">
        <h2>Getting Started with Advanced Analytics</h2>
        <div className="guide-grid">
          <div className="guide-card">
            <h4>📝 Build Custom Reports</h4>
            <p>Create fully customized reports with your own metrics, filters, and visualizations.</p>
          </div>
          <div className="guide-card">
            <h4>📊 Statistical Analysis</h4>
            <p>Perform detailed statistical analysis including variance, correlation, and regression.</p>
          </div>
          <div className="guide-card">
            <h4>🔮 Predictive Analytics</h4>
            <p>Forecast future trends and identify anomalies in your data with ML models.</p>
          </div>
          <div className="guide-card">
            <h4>🎨 Advanced Visualizations</h4>
            <p>Create stunning interactive charts and visualizations for data exploration.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AdvancedAnalyticsPage
