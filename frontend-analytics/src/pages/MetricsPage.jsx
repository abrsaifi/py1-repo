import { useState, useEffect } from 'react'
import { metricsAPI } from '../services/api'
import MetricCard from '../components/MetricCard'
import DataTable from '../components/DataTable'
import BarChart from '../components/BarChart'
import { UniversalIcon } from '../utils/UniversalIcon'
import '../styles/pages.css'

export const MetricsPage = ({ onTitleChange }) => {
  const [metrics, setMetrics] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedMetric, setSelectedMetric] = useState(null)
  const [filterType, setFilterType] = useState('all')

  useEffect(() => {
    onTitleChange('Metrics')
    fetchMetrics()
  }, [onTitleChange])

  const fetchMetrics = async () => {
    try {
      setLoading(true)
      // Mock data for demo
      setMetrics([
        {
          id: '1',
          name: 'Total Requests',
          type: 'system',
          current: 24532,
          previous: 21890,
          change: 12.1,
        },
        {
          id: '2',
          name: 'API Response Time',
          type: 'service',
          current: 145,
          previous: 152,
          change: -4.6,
        },
        {
          id: '3',
          name: 'Error Rate',
          type: 'system',
          current: 0.85,
          previous: 1.02,
          change: -16.7,
        },
        {
          id: '4',
          name: 'Active Users',
          type: 'business',
          current: 1420,
          previous: 1250,
          change: 13.6,
        },
        {
          id: '5',
          name: 'Cache Hit Rate',
          type: 'service',
          current: 94.2,
          previous: 92.5,
          change: 1.8,
        },
      ])
    } catch (error) {
      console.error('Failed to fetch metrics:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredMetrics = filterType === 'all' 
    ? metrics 
    : metrics.filter(m => m.type === filterType)

  const columns = [
    { key: 'name', label: 'Metric Name', sortable: true },
    { key: 'type', label: 'Type', sortable: true },
    { key: 'current', label: 'Current Value', sortable: true },
    { key: 'previous', label: 'Previous Value', sortable: true },
    {
      key: 'change',
      label: 'Change',
      sortable: true,
      render: (value) => `${value > 0 ? '+' : ''}${value.toFixed(1)}%`,
    },
  ]

  return (
    <div className="metrics-page">
      <div className="page-header">
        <div>
          <h2>All Metrics</h2>
          <p>Monitor and analyze system performance</p>
        </div>
        <button className="btn btn-primary">
          <UniversalIcon icon="fas fa-plus" size={20} /> New Metric
        </button>
      </div>

      <div className="metrics-controls">
        <div className="filter-group">
          <select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
            <option value="all">All Types</option>
            <option value="system">System Metrics</option>
            <option value="service">Service Metrics</option>
            <option value="business">Business Metrics</option>
          </select>
        </div>
      </div>

      <div className="metrics-grid">
        {filteredMetrics.slice(0, 4).map(metric => (
          <MetricCard
            key={metric.id}
            title={metric.name}
            value={metric.current}
            trend={Math.round(metric.change)}
            icon="chart-bar"
            color={Math.round(metric.change) > 0 ? 'green' : 'red'}
          />
        ))}
      </div>

      <DataTable
        title="Detailed Metrics"
        columns={columns}
        data={filteredMetrics}
        loading={loading}
        onRowClick={setSelectedMetric}
      />

      {selectedMetric && (
        <div className="metric-detail-modal">
          <div className="modal-content">
            <h3>{selectedMetric.name}</h3>
            <p>Type: {selectedMetric.type}</p>
            <p>Current: {selectedMetric.current}</p>
            <button className="btn btn-secondary" onClick={() => setSelectedMetric(null)}>
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default MetricsPage
