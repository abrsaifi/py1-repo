import { useState, useEffect } from 'react'
import { alertsAPI } from '../services/api'
import DataTable from '../components/DataTable'
import { UniversalIcon } from '../utils/UniversalIcon'
import '../styles/pages.css'

export const AlertsPage = ({ onTitleChange }) => {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [newAlert, setNewAlert] = useState({
    name: '',
    metric: '',
    condition: 'greater_than',
    threshold: '',
    severity: 'warning',
  })

  useEffect(() => {
    onTitleChange('Alerts')
    fetchAlerts()
  }, [onTitleChange])

  const fetchAlerts = async () => {
    try {
      setLoading(true)
      // Mock data
      setAlerts([
        {
          id: '1',
          name: 'High CPU Usage',
          metric: 'CPU Usage',
          threshold: '85%',
          severity: 'high',
          status: 'active',
          lastTriggered: '2026-03-04 10:30',
        },
        {
          id: '2',
          name: 'Database Connection Pool Low',
          metric: 'Available Connections',
          threshold: '< 10',
          severity: 'warning',
          status: 'active',
          lastTriggered: '2026-03-04 09:15',
        },
        {
          id: '3',
          name: 'API Response Time High',
          metric: 'Response Time (P95)',
          threshold: '> 500ms',
          severity: 'medium',
          status: 'inactive',
          lastTriggered: '2026-03-03 14:22',
        },
      ])
    } catch (error) {
      console.error('Failed to fetch alerts:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateAlert = async (e) => {
    e.preventDefault()
    try {
      await alertsAPI.create(newAlert)
      setNewAlert({
        name: '',
        metric: '',
        condition: 'greater_than',
        threshold: '',
        severity: 'warning',
      })
      setShowForm(false)
      fetchAlerts()
    } catch (error) {
      console.error('Failed to create alert:', error)
    }
  }

  const columns = [
    { key: 'name', label: 'Alert Name', sortable: true },
    { key: 'metric', label: 'Metric', sortable: true },
    { key: 'threshold', label: 'Threshold', sortable: true },
    { key: 'severity', label: 'Severity', sortable: true },
    { key: 'status', label: 'Status', sortable: true },
    { key: 'lastTriggered', label: 'Last Triggered', sortable: true },
  ]

  return (
    <div className="alerts-page">
      <div className="page-header">
        <div>
          <h2>Alerts & Notifications</h2>
          <p>Configure and manage system alerts</p>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => setShowForm(!showForm)}
        >
          <UniversalIcon icon="fas fa-plus" size={20} /> Create Alert
        </button>
      </div>

      {showForm && (
        <div className="form-card">
          <h3>Create New Alert</h3>
          <form onSubmit={handleCreateAlert}>
            <div className="form-group">
              <label>Alert Name*</label>
              <input
                type="text"
                value={newAlert.name}
                onChange={(e) => setNewAlert({ ...newAlert, name: e.target.value })}
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Metric*</label>
                <select
                  value={newAlert.metric}
                  onChange={(e) => setNewAlert({ ...newAlert, metric: e.target.value })}
                  required
                >
                  <option value="">Select a metric</option>
                  <option value="cpu">CPU Usage</option>
                  <option value="memory">Memory Usage</option>
                  <option value="response-time">Response Time</option>
                  <option value="requests">Request Rate</option>
                </select>
              </div>

              <div className="form-group">
                <label>Condition</label>
                <select
                  value={newAlert.condition}
                  onChange={(e) => setNewAlert({ ...newAlert, condition: e.target.value })}
                >
                  <option value="greater_than">Greater Than</option>
                  <option value="less_than">Less Than</option>
                  <option value="equals">Equals</option>
                </select>
              </div>

              <div className="form-group">
                <label>Threshold*</label>
                <input
                  type="text"
                  value={newAlert.threshold}
                  onChange={(e) => setNewAlert({ ...newAlert, threshold: e.target.value })}
                  placeholder="e.g., 85%"
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label>Severity</label>
              <select
                value={newAlert.severity}
                onChange={(e) => setNewAlert({ ...newAlert, severity: e.target.value })}
              >
                <option value="info">Info</option>
                <option value="warning">Warning</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn btn-success">
                Create Alert
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
        title="All Alerts"
        columns={columns}
        data={alerts}
        loading={loading}
      />
    </div>
  )
}

export default AlertsPage
