import React, { useState } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'

const PredictiveAnalytics = () => {
  const [selectedMetric, setSelectedMetric] = useState('revenue')
  const [forecastResults, setForecastResults] = useState(null)
  const [anomalies, setAnomalies] = useState([])

  const metrics = [
    { id: 'revenue', name: 'Revenue' },
    { id: 'users', name: 'Active Users' },
    { id: 'conversion', name: 'Conversion Rate' },
    { id: 'engagement', name: 'Engagement Score' }
  ]

  const generateForecast = () => {
    // Generate mock forecast data
    const historicalData = Array.from({ length: 30 }, (_, i) => ({
      date: new Date(Date.now() - (30 - i) * 24 * 60 * 60 * 1000).toLocaleDateString(),
      actual: Math.floor(Math.random() * 5000) + 3000,
      trend: i * 50 + 3000
    }))

    const forecastData = Array.from({ length: 14 }, (_, i) => ({
      date: new Date(Date.now() + (i + 1) * 24 * 60 * 60 * 1000).toLocaleDateString(),
      forecast: Math.floor(Math.random() * 5000) + 3500,
      lowerBound: Math.floor(Math.random() * 4500) + 3000,
      upperBound: Math.floor(Math.random() * 6000) + 4000,
      confidence: 0.95
    }))

    const mockAnomalies = [
      { date: '2024-02-15', value: 1200, severity: 'critical', reason: '2.5 std devs below mean' },
      { date: '2024-02-28', value: 8900, severity: 'warning', reason: '1.8 std devs above mean' }
    ]

    setForecastResults({
      historical: historicalData,
      forecast: forecastData,
      accuracy: 0.92,
      model: 'ARIMA(1,1,1)',
      mae: 234.5,
      rmse: 312.8
    })

    setAnomalies(mockAnomalies)
  }

  return (
    <div className="predictive-analytics">
      <div className="forecast-controls">
        <div className="control-group">
          <label>Select Metric to Forecast</label>
          <select
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value)}
            className="form-input"
          >
            {metrics.map(m => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </select>
        </div>
        <button className="btn-primary" onClick={generateForecast}>
          <UniversalIcon icon="🔮" size={16} /> Generate Forecast
        </button>
      </div>

      {forecastResults && (
        <div className="forecast-results">
          {/* Model Performance */}
          <section className="forecast-section">
            <h2><UniversalIcon icon="📊" size={24} /> Model Performance</h2>
            <div className="performance-grid">
              <div className="metric-card">
                <h4>Accuracy</h4>
                <p className="metric-large">{(forecastResults.accuracy * 100).toFixed(1)}%</p>
              </div>
              <div className="metric-card">
                <h4>Model</h4>
                <p className="metric-values">{forecastResults.model}</p>
              </div>
              <div className="metric-card">
                <h4>MAE</h4>
                <p className="metric-large">{forecastResults.mae.toFixed(1)}</p>
              </div>
              <div className="metric-card">
                <h4>RMSE</h4>
                <p className="metric-large">{forecastResults.rmse.toFixed(1)}</p>
              </div>
            </div>
          </section>

          {/* Forecast Data */}
          <section className="forecast-section">
            <h2><UniversalIcon icon="📈" size={24} /> 14-Day Forecast</h2>
            <div className="forecast-table">
              <div className="table-header">
                <span>Date</span>
                <span>Forecast</span>
                <span>Lower Bound</span>
                <span>Upper Bound</span>
                <span>Confidence</span>
              </div>
              {forecastResults.forecast.map((item, idx) => (
                <div key={`forecast-${idx}-${item.date}`} className="table-row">
                  <span>{item.date}</span>
                  <span className="forecast-value">{item.forecast}</span>
                  <span>{item.lowerBound}</span>
                  <span>{item.upperBound}</span>
                  <span className="confidence-badge">
                    {(item.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>
          </section>

          {/* Trend Analysis */}
          <section className="forecast-section">
            <h2><UniversalIcon icon="📊" size={24} /> Trend Analysis</h2>
            <div className="trend-items">
              <div className="trend-item">
                <h4>Uptrend Detected</h4>
                <p><UniversalIcon icon="📈" size={18} /> Positive trend with +2.5% growth per day</p>
              </div>
              <div className="trend-item">
                <h4>Seasonality</h4>
                <p><UniversalIcon icon="📅" size={18} /> Weekly pattern detected (7-day cycle)</p>
              </div>
              <div className="trend-item">
                <h4>Volatility</h4>
                <p><UniversalIcon icon="📊" size={18} /> Moderate volatility (σ = 312.8)</p>
              </div>
              <div className="trend-item">
                <h4>Forecast Confidence</h4>
                <p><UniversalIcon icon="✓" size={18} /> High confidence interval (95%)</p>
              </div>
            </div>
          </section>

          {/* Anomaly Detection */}
          {anomalies.length > 0 && (
            <section className="forecast-section">
              <h2><UniversalIcon icon="🚨" size={24} /> Anomalies Detected</h2>
              <div className="anomalies-list">
                {anomalies.map((anomaly, idx) => (
                  <div key={`anomaly-${idx}-${anomaly.date}`} className={`anomaly-item severity-${anomaly.severity}`}>
                    <div className="anomaly-icon">
                      {anomaly.severity === 'critical' ? <UniversalIcon icon="🔴" size={18} /> : <UniversalIcon icon="🜢" size={18} />}
                    </div>
                    <div className="anomaly-details">
                      <h4>{anomaly.date}</h4>
                      <p>Value: {anomaly.value} - {anomaly.reason}</p>
                    </div>
                    <span className="anomaly-severity">{anomaly.severity}</span>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Recommendations */}
          <section className="forecast-section">
            <h2><UniversalIcon icon="💡" size={24} /> AI-Generated Recommendations</h2>
            <div className="recommendations">
              <div className="recommendation-item">
                <span className="icon"><UniversalIcon icon="✓" size={16} /></span>
                <p><strong>Growth Expected:</strong> The forecast shows consistent growth. Consider planning resources accordingly.</p>
              </div>
              <div className="recommendation-item">
                <span className="icon"><UniversalIcon icon="⚠️" size={16} /></span>
                <p><strong>Monitor Volatility:</strong> Increased volatility detected. Set up alerts at forecast bounds.</p>
              </div>
              <div className="recommendation-item">
                <span className="icon"><UniversalIcon icon="📊" size={16} /></span>
                <p><strong>Seasonal Pattern:</strong> Weekly patterns identified. Optimize operations based on weekly cycles.</p>
              </div>
              <div className="recommendation-item">
                <span className="icon"><UniversalIcon icon="🎯" size={16} /></span>
                <p><strong>Target Setting:</strong> Based on forecast, realistic target for next month: 4,250 (±450)</p>
              </div>
            </div>
          </section>

          <div className="export-section">
            <button className="btn-primary"><UniversalIcon icon="📟" size={14} /> Export Forecast</button>
            <button className="btn-secondary"><UniversalIcon icon="📧" size={14} /> Email Forecast</button>
            <button className="btn-secondary"><UniversalIcon icon="ud83d\udcbe" size={14} /> Save Model</button>
          </div>
        </div>
      )}

      {!forecastResults && (
        <div className="empty-state">
          <p>Select a metric and click "Generate Forecast" to see predictions</p>
        </div>
      )}
    </div>
  )
}

export default PredictiveAnalytics
