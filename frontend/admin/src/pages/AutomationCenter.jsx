import React, { useEffect, useState } from 'react'
import { adminAPI } from '@shared/api/api'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import '../styles/admin.css'

const AutomationCenter = () => {
  const [payload, setPayload] = useState({
    stats: {
      activeWorkflows: 0,
      seoAutomation: 0,
      emailAutomation: 0,
      alertAutomation: 0,
      pausedWorkflows: 0,
      failedWorkflows: 0,
    },
    workflows: [],
  })
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [selectedWorkflow, setSelectedWorkflow] = useState(null)
  const [workflowLogs, setWorkflowLogs] = useState([])
  const [logsLoading, setLogsLoading] = useState(false)

  useEffect(() => {
    loadAutomationOverview()
  }, [])

  const loadAutomationOverview = async (showLoader = true) => {
    try {
      if (showLoader) {
        setLoading(true)
      }
      setError('')
      const response = await adminAPI.getAutomationOverview()
      setPayload(response.data || { stats: {}, workflows: [] })
    } catch (err) {
      console.error('Failed to load automation overview:', err)
      setError(err.response?.data?.error || err.message || 'Failed to load automation overview')
    } finally {
      if (showLoader) {
        setLoading(false)
      }
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      running: '#11998e',
      failed: '#eb3349',
      paused: '#f6ad55'
    }
    return colors[status] || '#718096'
  }

  const getTypeColor = (type) => {
    const colors = {
      'SEO': '#667eea',
      'Email': '#11998e',
      'Alert': '#f97316'
    }
    return colors[type] || '#718096'
  }

  const handleToggleWorkflow = async (workflow) => {
    try {
      setActionLoading(workflow.id)
      setMessage('')
      setError('')

      const response = workflow.status === 'running'
        ? await adminAPI.pauseAutomationWorkflow(workflow.id)
        : await adminAPI.resumeAutomationWorkflow(workflow.id)

      setMessage(response.data?.message || 'Workflow updated.')
      await loadAutomationOverview(false)
      if (selectedWorkflow?.id === workflow.id) {
        await handleViewLogs(workflow)
      }
    } catch (err) {
      console.error('Failed to update workflow:', err)
      setError(err.response?.data?.error || err.message || 'Failed to update workflow')
    } finally {
      setActionLoading('')
    }
  }

  const handleViewLogs = async (workflow) => {
    try {
      setSelectedWorkflow(workflow)
      setLogsLoading(true)
      const response = await adminAPI.getAutomationWorkflowLogs(workflow.id)
      setWorkflowLogs(response.data?.logs || [])
    } catch (err) {
      console.error('Failed to load workflow logs:', err)
      setError(err.response?.data?.error || err.message || 'Failed to load workflow logs')
      setWorkflowLogs([])
    } finally {
      setLogsLoading(false)
    }
  }

  const stats = payload.stats || {}
  const workflows = payload.workflows || []

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="⚙️" size={24} /> Automation</h2>
      <p className="section-subtitle">Persisted automation workflows for SEO, email, and alert operations</p>

      {error && <div className="alert-banner error">{error}</div>}
      {message && <div className="alert-banner success">{message}</div>}

      <div className="quick-actions" style={{ marginBottom: '24px' }}>
        <button className="action-button primary" onClick={() => loadAutomationOverview()} disabled={loading}>
          <UniversalIcon icon="🔄" size={14} /> {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      <div className="admin-stats-grid">
        <div className="admin-stat-card metric-primary">
          <UniversalIcon icon="🔄" size={32} />
          <div className="stat-content">
            <h3>Active Workflows</h3>
            <p className="stat-value">{stats.activeWorkflows}</p>
            <p className="stat-detail">Total automated processes</p>
          </div>
        </div>

        <div className="admin-stat-card metric-info">
          <UniversalIcon icon="🔍" size={32} />
          <div className="stat-content">
            <h3>SEO Automation</h3>
            <p className="stat-value">{stats.seoAutomation}</p>
            <p className="stat-detail">Page generation & indexing</p>
          </div>
        </div>

        <div className="admin-stat-card metric-success">
          <UniversalIcon icon="📧" size={32} />
          <div className="stat-content">
            <h3>Email Automation</h3>
            <p className="stat-value">{stats.emailAutomation}</p>
            <p className="stat-detail">Notifications & newsletters</p>
          </div>
        </div>

        <div className="admin-stat-card metric-warning">
          <UniversalIcon icon="🔔" size={32} />
          <div className="stat-content">
            <h3>Alert Automation</h3>
            <p className="stat-value">{stats.alertAutomation}</p>
            <p className="stat-detail">Notifications & monitoring</p>
          </div>
        </div>
      </div>

      <div className="admin-stats-grid" style={{ marginTop: '20px' }}>
        <div className="admin-stat-card metric-info">
          <UniversalIcon icon="⏸️" size={32} />
          <div className="stat-content">
            <h3>Paused Workflows</h3>
            <p className="stat-value">{stats.pausedWorkflows || 0}</p>
            <p className="stat-detail">Awaiting operator action</p>
          </div>
        </div>

        <div className="admin-stat-card metric-danger">
          <UniversalIcon icon="❌" size={32} />
          <div className="stat-content">
            <h3>Failed Workflows</h3>
            <p className="stat-value">{stats.failedWorkflows || 0}</p>
            <p className="stat-detail">Require retry or investigation</p>
          </div>
        </div>
      </div>

      <div className="admin-section-content">
        <h3>Automation Workflows</h3>

        <div className="jobs-table-wrapper">
          <table className="jobs-table">
            <thead>
              <tr>
                <th>Workflow ID</th>
                <th>Name</th>
                <th>Type</th>
                <th>Status</th>
                <th>Executions</th>
                <th>Last Run</th>
                <th>Next Run</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {workflows.map(wf => (
                <tr key={wf.id} className={`job-row ${wf.status}`}>
                  <td className="job-id"><code>{wf.id}</code></td>
                  <td>
                    <strong>{wf.name}</strong>
                    <div className="timestamp">{wf.description || 'No description available'}</div>
                  </td>
                  <td>
                    <span className="format-badge" style={{ background: `linear-gradient(135deg, ${getTypeColor(wf.type)} 0%, ${adjustBrightness(getTypeColor(wf.type), -20)} 100%)`, color: 'white' }}>
                      {wf.type}
                    </span>
                  </td>
                  <td>
                    <span className="status-badge" style={{ backgroundColor: getStatusColor(wf.status) }}>
                      {wf.status === 'running' && <><UniversalIcon icon="▶️" size={14} /> RUNNING</>}
                      {wf.status === 'failed' && <><UniversalIcon icon="❌" size={14} /> FAILED</>}
                      {wf.status === 'paused' && <><UniversalIcon icon="⏸️" size={14} /> PAUSED</>}
                    </span>
                  </td>
                  <td><strong>{wf.executions.toLocaleString()}</strong></td>
                  <td className="timestamp">{wf.lastRun || 'Never'}</td>
                  <td className="timestamp">{wf.nextRun || 'Not scheduled'}</td>
                  <td className="actions">
                    {wf.status === 'running' ? (
                      <button 
                        className="action-btn" 
                        style={{ background: '#f6ad55', color: 'white' }}
                        onClick={() => handleToggleWorkflow(wf)} 
                        disabled={actionLoading === wf.id}
                        title="Pause Workflow"
                      >
                        <UniversalIcon icon="⏸️" size={14} />
                      </button>
                    ) : (
                      <button 
                        className="action-btn retry" 
                        onClick={() => handleToggleWorkflow(wf)} 
                        disabled={actionLoading === wf.id}
                        title="Resume Workflow"
                      >
                        <UniversalIcon icon="▶️" size={14} />
                      </button>
                    )}
                    <button 
                      className="action-btn logs" 
                      onClick={() => handleViewLogs(wf)} 
                      title="View Logs"
                    >
                      <UniversalIcon icon="📋" size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {workflows.length === 0 && (
          <div className="no-data">
            <p>No workflows configured</p>
          </div>
        )}
      </div>

      {selectedWorkflow && (
        <div className="modal-overlay">
          <div className="modal-content modal-large">
            <div className="modal-header">
              <h3>{selectedWorkflow.name} Logs</h3>
              <button className="close-btn" onClick={() => setSelectedWorkflow(null)}>×</button>
            </div>
            <div className="modal-body">
              {logsLoading ? (
                <p>Loading logs...</p>
              ) : workflowLogs.length > 0 ? (
                <div className="table-list">
                  {workflowLogs.map((entry) => (
                    <div key={entry.id} className="list-item">
                      <div className="item-info">
                        <p className="item-name">{entry.message}</p>
                        <p className="item-detail">{entry.timestampLabel || entry.timestamp} • {entry.level}</p>
                      </div>
                      <div className="item-stat">
                        <span className="status-badge" style={{ backgroundColor: getStatusColor(entry.status === 'failed' ? 'failed' : selectedWorkflow.status), color: 'white' }}>
                          {entry.status || entry.level}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p>No workflow logs available.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Helper function to adjust brightness of hex colors
const adjustBrightness = (color, percent) => {
  const num = parseInt(color.replace("#", ""), 16);
  const amt = Math.round(2.55 * percent);
  const R = Math.max(0, Math.min(255, (num >> 16) + amt));
  const G = Math.max(0, Math.min(255, (num >> 8 & 0x00FF) + amt));
  const B = Math.max(0, Math.min(255, (num & 0x0000FF) + amt));
  return "#" + (0x1000000 + R * 0x10000 + G * 0x100 + B).toString(16).slice(1);
}

export default AutomationCenter
