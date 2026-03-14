import { useState, useEffect } from 'react'
import { adminAPI } from '@shared/api/api'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import MetricCard from '@shared/components/MetricCard'
import LineChart from '@shared/components/LineChart'
import BarChart from '@shared/components/BarChart'
import '../styles/pages.css'

export const DashboardPage = ({ onTitleChange }) => {
  const [metrics, setMetrics] = useState([])
  const [requestVolume, setRequestVolume] = useState({ labels: [], datasets: [] })
  const [dailyDistribution, setDailyDistribution] = useState({ labels: [], datasets: [] })
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('7d')
  const [lastUpdated, setLastUpdated] = useState('')

  useEffect(() => {
    onTitleChange('Dashboard')
  }, [onTitleChange])

  useEffect(() => {
    fetchMetrics()
  }, [timeRange])

  const fetchMetrics = async () => {
    try {
      setLoading(true)
      const days = timeRange === '1h' ? 1 : timeRange === '24h' ? 1 : timeRange === '7d' ? 7 : 30
      const response = await adminAPI.getAnalyticsOverview({ days })
      const payload = response.data || {}
      setMetrics(payload.metrics || [])
      setRequestVolume(payload.charts?.requestVolume || { labels: [], datasets: [] })
      setDailyDistribution(payload.charts?.dailyDistribution || { labels: [], datasets: [] })
      setAlerts(payload.alerts || [])
      setLastUpdated(payload.generatedAt || '')
    } catch (error) {
      console.error('Failed to fetch dashboard analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <div>
          <h2>Analytics Overview</h2>
          <p>
            Real-time metrics and performance data
            {lastUpdated ? ` • Last updated ${lastUpdated.replace('T', ' ').slice(0, 19)}` : ''}
          </p>
        </div>
        <div className="filter-controls">
          <select value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
            <option value="1h">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
          <button className="btn btn-primary" onClick={fetchMetrics}>
            <UniversalIcon icon="fas fa-refresh" size={16} /> Refresh
          </button>
        </div>
      </div>

      <div className="metrics-grid">
        {metrics.map(metric => (
          <MetricCard
            key={metric._id}
            title={metric.metric_name}
            value={metric.value}
            unit={metric.unit}
            trend={Math.round(metric.trend || 0)}
            icon="chart-line"
            color="blue"
          />
        ))}
      </div>

      <div className="charts-section">
        <div className="chart-container">
          <LineChart
            title="Conversion Volume Over Time"
            labels={requestVolume.labels}
            datasets={requestVolume.datasets}
          />
        </div>

        <div className="chart-container">
          <BarChart
            title="Completed Conversion Distribution"
            labels={dailyDistribution.labels}
            datasets={dailyDistribution.datasets}
          />
        </div>
      </div>

      <div className="alerts-preview">
        <h3>Recent Alerts</h3>
        {loading && <p>Loading dashboard alerts...</p>}
        {!loading && alerts.length === 0 && <p>No active alerts.</p>}
        {!loading && alerts.map((alert) => (
          <div className="alert-item" key={alert.id}>
            <div className={`alert-icon ${alert.severity || 'warning'}`}>
              <UniversalIcon icon="fas fa-exclamation-triangle" size={20} />
            </div>
            <div className="alert-content">
              <h4>{alert.name}</h4>
              <p>{alert.metric}</p>
              <span className="alert-time">{alert.lastTriggered || 'Live signal'}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default DashboardPage