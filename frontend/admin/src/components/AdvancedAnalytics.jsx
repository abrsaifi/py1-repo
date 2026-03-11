import { useState, useMemo } from 'react'
import '../styles/analytics.css'

// Analytics Engine
class AnalyticsEngine {
  static calculateTrend(data, key) {
    if (data.length < 2) return 0
    
    const first = data[0][key]
    const last = data[data.length - 1][key]
    return ((last - first) / first) * 100
  }

  static findAnomalies(data, key, threshold = 2) {
    const values = data.map(d => d[key])
    const mean = values.reduce((a, b) => a + b, 0) / values.length
    const stdDev = Math.sqrt(
      values.reduce((sq, n) => sq + Math.pow(n - mean, 2), 0) / values.length
    )

    return data.map((item, idx) => ({
      ...item,
      isAnomaly: Math.abs(item[key] - mean) > threshold * stdDev,
      zscore: (item[key] - mean) / stdDev
    }))
  }

  static movingAverage(data, key, period = 7) {
    return data.map((item, idx) => {
      const start = Math.max(0, idx - period + 1)
      const subset = data.slice(start, idx + 1)
      const avg = subset.reduce((sum, d) => sum + d[key], 0) / subset.length
      return { ...item, movingAverage: avg }
    })
  }

  static forecast(data, key, periods = 5) {
    if (data.length < 2) return []

    const values = data.map(d => d[key])
    const n = values.length

    // Simple linear regression
    const sumX = (n * (n + 1)) / 2
    const sumY = values.reduce((a, b) => a + b, 0)
    const sumXY = values.reduce((sum, v, i) => sum + v * (i + 1), 0)
    const sumX2 = (n * (n + 1) * (2 * n + 1)) / 6

    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX)
    const intercept = (sumY - slope * sumX) / n

    const forecasts = []
    for (let i = 1; i <= periods; i++) {
      forecasts.push({
        period: n + i,
        value: slope * (n + i) + intercept
      })
    }

    return forecasts
  }

  static percentileChange(data, key, period = 7) {
    const current = data[data.length - 1][key]
    const previous = data[Math.max(0, data.length - period - 1)][key]
    return ((current - previous) / previous) * 100
  }

  static getDistribution(data, key, buckets = 10) {
    const values = data.map(d => d[key])
    const min = Math.min(...values)
    const max = Math.max(...values)
    const bucketSize = (max - min) / buckets

    const distribution = Array(buckets).fill(0)
    values.forEach(value => {
      const bucketIdx = Math.floor((value - min) / bucketSize)
      distribution[Math.min(bucketIdx, buckets - 1)]++
    })

    return distribution
  }
}

// Advanced Analytics Component
export const AdvancedAnalytics = ({ data = [], metric = 'value' }) => {
  const [selectedAnalysis, setSelectedAnalysis] = useState('trend')

  const analytics = useMemo(() => {
    if (!data.length) return {}

    return {
      trend: AnalyticsEngine.calculateTrend(data, metric),
      anomalies: AnalyticsEngine.findAnomalies(data, metric),
      movingAvg: AnalyticsEngine.movingAverage(data, metric),
      forecast: AnalyticsEngine.forecast(data, metric, 7),
      percentileChange: AnalyticsEngine.percentileChange(data, metric),
      distribution: AnalyticsEngine.getDistribution(data, metric)
    }
  }, [data, metric])

  if (!data.length) {
    return <div className="analytics-empty">No data available for analysis</div>
  }

  return (
    <div className="advanced-analytics">
      <div className="analytics-nav">
        <button
          className={`nav-btn ${selectedAnalysis === 'trend' ? 'active' : ''}`}
          onClick={() => setSelectedAnalysis('trend')}
        >
          Trend
        </button>
        <button
          className={`nav-btn ${selectedAnalysis === 'anomalies' ? 'active' : ''}`}
          onClick={() => setSelectedAnalysis('anomalies')}
        >
          Anomalies
        </button>
        <button
          className={`nav-btn ${selectedAnalysis === 'forecast' ? 'active' : ''}`}
          onClick={() => setSelectedAnalysis('forecast')}
        >
          Forecast
        </button>
        <button
          className={`nav-btn ${selectedAnalysis === 'distribution' ? 'active' : ''}`}
          onClick={() => setSelectedAnalysis('distribution')}
        >
          Distribution
        </button>
      </div>

      <div className="analytics-content">
        {selectedAnalysis === 'trend' && (
          <TrendAnalysis
            trend={analytics.trend}
            percentileChange={analytics.percentileChange}
          />
        )}

        {selectedAnalysis === 'anomalies' && (
          <AnomalyAnalysis anomalies={analytics.anomalies} />
        )}

        {selectedAnalysis === 'forecast' && (
          <ForecastAnalysis forecast={analytics.forecast} />
        )}

        {selectedAnalysis === 'distribution' && (
          <DistributionAnalysis distribution={analytics.distribution} />
        )}
      </div>
    </div>
  )
}

const TrendAnalysis = ({ trend, percentileChange }) => (
  <div className="analysis-section">
    <h4>Trend Analysis</h4>
    <div className="metrics-grid">
      <div className="metric-box">
        <label>Overall Trend</label>
        <div className={`metric-value ${trend > 0 ? 'positive' : 'negative'}`}>
          {trend > 0 ? '↑' : '↓'} {Math.abs(trend).toFixed(2)}%
        </div>
      </div>
      <div className="metric-box">
        <label>Weekly Change</label>
        <div className={`metric-value ${percentileChange > 0 ? 'positive' : 'negative'}`}>
          {percentileChange > 0 ? '+' : ''}{percentileChange.toFixed(2)}%
        </div>
      </div>
    </div>
  </div>
)

const AnomalyAnalysis = ({ anomalies }) => {
  const anomalyCount = anomalies.filter(a => a.isAnomaly).length

  return (
    <div className="analysis-section">
      <h4>Anomaly Detection</h4>
      <div className="metric-box">
        <label>Anomalies Detected</label>
        <div className={`metric-value ${anomalyCount > 0 ? 'warning' : 'safe'}`}>
          {anomalyCount} / {anomalies.length}
        </div>
      </div>
      {anomalyCount > 0 && (
        <div className="anomalies-list">
          {anomalies
            .filter(a => a.isAnomaly)
            .map((item, idx) => (
              <div key={`anomaly-${idx}-${item.zscore}`} className="anomaly-item">
                <span className="anomaly-label">Item {idx + 1}</span>
                <span className="anomaly-zscore">Z-Score: {item.zscore.toFixed(2)}</span>
              </div>
            ))}
        </div>
      )}
    </div>
  )
}

const ForecastAnalysis = ({ forecast }) => (
  <div className="analysis-section">
    <h4>7-Day Forecast</h4>
    <div className="forecast-list">
      {forecast.map((item, idx) => (
        <div key={`forecast-${idx}-${item.value}`} className="forecast-item">
          <span className="forecast-period">Day {idx + 1}</span>
          <span className="forecast-value">{item.value.toFixed(2)}</span>
        </div>
      ))}
    </div>
  </div>
)

const DistributionAnalysis = ({ distribution }) => (
  <div className="analysis-section">
    <h4>Value Distribution</h4>
    <div className="distribution-chart">
      {distribution.map((count, idx) => (
        <div key={`dist-${idx}`} className="distribution-bar">
          <div
            className="distribution-fill"
            style={{
              height: `${(count / Math.max(...distribution)) * 100}%`
            }}
          ></div>
          <span className="distribution-label">{idx + 1}</span>
        </div>
      ))}
    </div>
  </div>
)

export default AdvancedAnalytics
