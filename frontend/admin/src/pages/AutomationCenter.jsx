import React, { useState } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import '../styles/admin.css'

const AutomationCenter = () => {
  const [stats, setStats] = useState({
    activeWorkflows: 24,
    seoAutomation: 8,
    emailAutomation: 12,
    alertAutomation: 4
  })

  const [workflows, setWorkflows] = useState([
    { id: 'WF-001', name: 'Daily SEO Page Generator', type: 'SEO', status: 'running', executions: 847, lastRun: '2026-03-06 14:50', nextRun: '2026-03-07 00:00' },
    { id: 'WF-002', name: 'Keyword Ranking Checker', type: 'SEO', status: 'running', executions: 156, lastRun: '2026-03-06 14:45', nextRun: '2026-03-06 16:00' },
    { id: 'WF-003', name: 'Sitemap Auto-Submit', type: 'SEO', status: 'running', executions: 52, lastRun: '2026-03-06 02:15', nextRun: '2026-03-07 02:00' },
    { id: 'WF-004', name: 'Conversion Success Email', type: 'Email', status: 'running', executions: 3421, lastRun: '2026-03-06 14:52', nextRun: 'Real-time' },
    { id: 'WF-005', name: 'Daily Report Newsletter', type: 'Email', status: 'running', executions: 24, lastRun: '2026-03-06 08:00', nextRun: '2026-03-07 08:00' },
    { id: 'WF-006', name: 'User Signup Welcome', type: 'Email', status: 'running', executions: 1247, lastRun: '2026-03-06 14:35', nextRun: 'Real-time' },
    { id: 'WF-007', name: 'High Error Rate Alert', type: 'Alert', status: 'running', executions: 12, lastRun: '2026-03-06 13:20', nextRun: 'Real-time' },
    { id: 'WF-008', name: 'Storage Quota Warning', type: 'Alert', status: 'paused', executions: 0, lastRun: '2026-03-04 15:30', nextRun: 'Paused' },
    { id: 'WF-009', name: 'Rate Limit Exceeded Alert', type: 'Alert', status: 'failed', executions: 8, lastRun: '2026-03-06 14:10 (Error)', nextRun: 'Retry: 2026-03-06 15:10' },
    { id: 'WF-010', name: 'Failed Conversion Alert', type: 'Alert', status: 'running', executions: 67, lastRun: '2026-03-06 14:48', nextRun: 'Real-time' },
  ])

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

  const handlePauseWorkflow = (workflowId) => {
    alert(`Pausing workflow: ${workflowId}`)
  }

  const handleResumeWorkflow = (workflowId) => {
    alert(`Resuming workflow: ${workflowId}`)
  }

  const handleViewLogs = (workflowId) => {
    alert(`Opening logs for workflow: ${workflowId}`)
  }

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="⚙️" size={24} /> Automation</h2>
      <p className="section-subtitle">n8n automation workflows - SEO, Email, and Alerts</p>

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
                  <td><strong>{wf.name}</strong></td>
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
                  <td className="timestamp">{wf.lastRun}</td>
                  <td className="timestamp">{wf.nextRun}</td>
                  <td className="actions">
                    {wf.status === 'running' ? (
                      <button 
                        className="action-btn" 
                        style={{ background: '#f6ad55', color: 'white' }}
                        onClick={() => handlePauseWorkflow(wf.id)} 
                        title="Pause Workflow"
                      >
                        <UniversalIcon icon="⏸️" size={14} />
                      </button>
                    ) : (
                      <button 
                        className="action-btn retry" 
                        onClick={() => handleResumeWorkflow(wf.id)} 
                        title="Resume Workflow"
                      >
                        <UniversalIcon icon="▶️" size={14} />
                      </button>
                    )}
                    <button 
                      className="action-btn logs" 
                      onClick={() => handleViewLogs(wf.id)} 
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
