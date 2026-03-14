import { useState, useEffect } from 'react'
import { adminAPI } from '@shared/api/api'
import DataTable from '@shared/components/DataTable'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import '../styles/pages.css'

export const AlertsPage = ({ onTitleChange }) => {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedAlert, setSelectedAlert] = useState(null)
  const [lastUpdated, setLastUpdated] = useState('')

  useEffect(() => {
    onTitleChange('Alerts')
    fetchAlerts()
  }, [onTitleChange])

  const fetchAlerts = async () => {
    try {
      setLoading(true)
      const response = await adminAPI.getAnalyticsOverview({ days: 7 })
      setAlerts(response.data?.alerts || [])
      setLastUpdated(response.data?.generatedAt || '')
    } catch (error) {
      console.error('Failed to fetch alerts:', error)
      setAlerts([])
    } finally {
      setLoading(false)
    }
  }

  const columns = [
    { key: 'name', label: 'Alert Name', sortable: true },
    { key: 'metric', label: 'Signal', sortable: true },
    { key: 'threshold', label: 'Severity', sortable: true },
    { key: 'status', label: 'Status', sortable: true },
    { key: 'lastTriggered', label: 'Last Triggered', sortable: true },
  ]

  return (
    <div className="alerts-page">
      <div className="page-header">
        <div>
          <h2>Alerts & Notifications</h2>
          <p>
            Live alerts derived from current admin health and worker telemetry
            {lastUpdated ? ` • Last updated ${lastUpdated.replace('T', ' ').slice(0, 19)}` : ''}
          </p>
        </div>
        <button className="btn btn-primary" onClick={fetchAlerts}>
          <UniversalIcon icon="fas fa-refresh" size={20} /> Refresh Alerts
        </button>
      </div>

      <DataTable
        title="Active Alerts"
        columns={columns}
        data={alerts}
        loading={loading}
        onRowClick={setSelectedAlert}
      />

      {selectedAlert && (
        <div className="metric-detail-modal" onClick={() => setSelectedAlert(null)}>
          <div className="modal-content" onClick={(event) => event.stopPropagation()}>
            <h3>{selectedAlert.name}</h3>
            <p>Status: {selectedAlert.status}</p>
            <p>Severity: {selectedAlert.threshold}</p>
            <p>{selectedAlert.metric}</p>
            <p>Last triggered: {selectedAlert.lastTriggered || 'Live signal'}</p>
            <button className="btn btn-secondary" onClick={() => setSelectedAlert(null)}>
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default AlertsPage