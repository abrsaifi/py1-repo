import { useState, useEffect } from 'react'
import { adminAPI } from '@shared/api/api'
import MetricCard from '@shared/components/MetricCard'
import DataTable from '@shared/components/DataTable'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
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
      const response = await adminAPI.getAnalyticsOverview({ days: 7 })
      setMetrics(response.data?.metricRows || [])
    } catch (error) {
      console.error('Failed to fetch metrics:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredMetrics = filterType === 'all'
    ? metrics
    : metrics.filter((metric) => metric.type === filterType)

  const columns = [
    { key: 'name', label: 'Metric Name', sortable: true },
    { key: 'type', label: 'Type', sortable: true },
    { key: 'current', label: 'Current Value', sortable: true },
    { key: 'previous', label: 'Previous Value', sortable: true },
    { key: 'changeLabel', label: 'Change', sortable: true },
  ]

  const displayMetrics = filteredMetrics.map((metric) => ({
    ...metric,
    current: `${metric.current} ${metric.unit || ''}`.trim(),
    previous: `${metric.previous} ${metric.unit || ''}`.trim(),
    changeLabel: `${metric.change > 0 ? '+' : ''}${Number(metric.change || 0).toFixed(1)}%`,
  }))

  return (
    <div className="metrics-page">
      <div className="page-header">
        <div>
          <h2>All Metrics</h2>
          <p>Monitor and analyze live system performance</p>
        </div>
        <button className="btn btn-primary" onClick={fetchMetrics}>
          <UniversalIcon icon="fas fa-refresh" size={20} /> Refresh Metrics
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
            unit={metric.unit}
            trend={Math.round(metric.change)}
            icon="chart-bar"
            color={metric.change >= 0 ? 'green' : 'red'}
          />
        ))}
      </div>

      <DataTable
        title="Detailed Metrics"
        columns={columns}
        data={displayMetrics}
        loading={loading}
        onRowClick={(row) => {
          const metric = filteredMetrics.find((item) => item.id === row.id)
          setSelectedMetric(metric || row)
        }}
      />

      {selectedMetric && (
        <div className="metric-detail-modal" onClick={() => setSelectedMetric(null)}>
          <div className="modal-content" onClick={(event) => event.stopPropagation()}>
            <h3>{selectedMetric.name}</h3>
            <p>Type: {selectedMetric.type}</p>
            <p>Current: {selectedMetric.current} {selectedMetric.unit}</p>
            <p>Previous: {selectedMetric.previous} {selectedMetric.unit}</p>
            <p>Change: {selectedMetric.change > 0 ? '+' : ''}{Number(selectedMetric.change || 0).toFixed(1)}%</p>
            <p>{selectedMetric.description || 'No additional context available.'}</p>
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