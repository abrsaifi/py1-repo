import { useState, useEffect } from 'react'
import { metricsAPI } from '@shared/api/api'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import MetricCard from '@shared/components/MetricCard'
import LineChart from '@shared/components/LineChart'
import BarChart from '@shared/components/BarChart'
import '../styles/pages.css'

export const DashboardPage = ({ onTitleChange }) => {
  const [metrics, setMetrics] = useState([])
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('24h')

  useEffect(() => {
    onTitleChange('Dashboard')
    fetchMetrics()
  }, [onTitleChange])

  const fetchMetrics = async () => {
    try {
      setLoading(true)
      const response = await metricsAPI.getSystemMetrics()
      // Mock data for demo
      setMetrics([
        {
          _id: '1',
          metric_name: 'Total Requests',
          value: 24532,
          unit: 'requests',
          aggregation_level: 'daily',
          trend: 12,
        },
        {
          _id: '2',
          metric_name: 'API Response Time',
          value: 145,
          unit: 'ms',
          aggregation_level: 'hourly',
          trend: -5,
        },
        {
          _id: '3',
          metric_name: 'Error Rate',
          value: 0.85,
          unit: '%',
          aggregation_level: 'hourly',
          trend: -2,
        },
        {
          _id: '4',
          metric_name: 'Database Connections',
          value: 128,
          unit: 'active',
          aggregation_level: 'real-time',
          trend: 3,
        },
      ])
    } catch (error) {
      console.error('Failed to fetch metrics:', error)
    } finally {
      setLoading(false)
    }
  }

  const lineChartData = {
    labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
    datasets: [
      {
        label: 'Requests',
        data: [3500, 4200, 3800, 5100, 4600, 5200],
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
      },
    ],
  }

  const barChartData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Daily Requests',
        data: [120000, 135000, 128000, 152000, 148000, 95000, 82000],
        backgroundColor: '#8b5cf6',
      },
    ],
  }

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <div>
          <h2>Analytics Overview</h2>
          <p>Real-time metrics and performance data</p>
        </div>
        <div className="filter-controls">
          <select value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
            <option value="1h">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
          <button className="btn btn-primary">
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
            trend={metric.trend}
            icon="chart-line"
            color="blue"
          />
        ))}
      </div>

      <div className="charts-section">
        <div className="chart-container">
          <LineChart
            title="Request Volume Over Time"
            labels={lineChartData.labels}
            datasets={lineChartData.datasets}
          />
        </div>

        <div className="chart-container">
          <BarChart
            title="Daily Request Distribution"
            labels={barChartData.labels}
            datasets={barChartData.datasets}
          />
        </div>
      </div>

      <div className="alerts-preview">
        <h3>Recent Alerts</h3>
        <div className="alert-item">
          <div className="alert-icon warning">
            <UniversalIcon icon="fas fa-exclamation-triangle" size={20} />
          </div>
          <div className="alert-content">
            <h4>High CPU Usage Detected</h4>
            <p>CPU usage exceeded 85% threshold</p>
            <span className="alert-time">2 minutes ago</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
