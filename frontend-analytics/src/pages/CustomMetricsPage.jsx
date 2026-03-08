import { useState, useEffect } from 'react'
import { customMetricsAPI } from '../services/api'
import DataTable from '../components/DataTable'
import { UniversalIcon } from '../utils/UniversalIcon'
import '../styles/pages.css'

export const CustomMetricsPage = ({ onTitleChange }) => {
  const [customMetrics, setCustomMetrics] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [newMetric, setNewMetric] = useState({
    name: '',
    formula: '',
    unit: '',
    description: '',
  })

  useEffect(() => {
    onTitleChange('Custom Metrics')
    fetchCustomMetrics()
  }, [onTitleChange])

  const fetchCustomMetrics = async () => {
    try {
      setLoading(true)
      // Mock data
      setCustomMetrics([
        {
          id: '1',
          name: 'Revenue per User',
          formula: 'total_revenue / active_users',
          unit: '$',
          status: 'active',
          lastCalculated: '2026-03-04 10:00',
        },
        {
          id: '2',
          name: 'Conversion Rate',
          formula: 'conversions / visitors * 100',
          unit: '%',
          status: 'active',
          lastCalculated: '2026-03-04 09:30',
        },
        {
          id: '3',
          name: 'Customer Lifetime Value',
          formula: 'avg_transaction * repeat_rate',
          unit: '$',
          status: 'inactive',
          lastCalculated: '2026-03-03 15:00',
        },
      ])
    } catch (error) {
      console.error('Failed to fetch custom metrics:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateMetric = async (e) => {
    e.preventDefault()
    try {
      await customMetricsAPI.create(newMetric)
      setNewMetric({ name: '', formula: '', unit: '', description: '' })
      setShowForm(false)
      fetchCustomMetrics()
    } catch (error) {
      console.error('Failed to create metric:', error)
    }
  }

  const columns = [
    { key: 'name', label: 'Metric Name', sortable: true },
    { key: 'formula', label: 'Formula', sortable: false },
    { key: 'unit', label: 'Unit', sortable: true },
    { key: 'status', label: 'Status', sortable: true },
    { key: 'lastCalculated', label: 'Last Calculated', sortable: true },
  ]

  return (
    <div className="custom-metrics-page">
      <div className="page-header">
        <div>
          <h2>Custom Metrics</h2>
          <p>Create and manage calculated metrics</p>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => setShowForm(!showForm)}
        >
          <UniversalIcon icon="fas fa-plus" size={20} /> New Metric
        </button>
      </div>

      {showForm && (
        <div className="form-card">
          <h3>Create Custom Metric</h3>
          <form onSubmit={handleCreateMetric}>
            <div className="form-group">
              <label>Metric Name*</label>
              <input
                type="text"
                value={newMetric.name}
                onChange={(e) => setNewMetric({ ...newMetric, name: e.target.value })}
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Unit</label>
                <input
                  type="text"
                  value={newMetric.unit}
                  onChange={(e) => setNewMetric({ ...newMetric, unit: e.target.value })}
                  placeholder="e.g., $, %, units"
                />
              </div>
            </div>

            <div className="form-group">
              <label>Formula*</label>
              <textarea
                value={newMetric.formula}
                onChange={(e) => setNewMetric({ ...newMetric, formula: e.target.value })}
                placeholder="e.g., total_revenue / active_users"
                rows="3"
                required
              />
              <small>Use metric names separated by operators (+, -, *, /)</small>
            </div>

            <div className="form-group">
              <label>Description</label>
              <textarea
                value={newMetric.description}
                onChange={(e) => setNewMetric({ ...newMetric, description: e.target.value })}
                rows="3"
              />
            </div>

            <div className="form-actions">
              <button type="submit" className="btn btn-success">
                Create Metric
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setShowForm(false)}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <DataTable
        title="Custom Metrics"
        columns={columns}
        data={customMetrics}
        loading={loading}
      />
    </div>
  )
}

export default CustomMetricsPage
