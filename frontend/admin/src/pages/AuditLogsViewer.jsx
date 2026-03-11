import React, { useState, useEffect } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import { useAuditLogger } from '../services/auditLogger'

const AuditLogsViewer = () => {
  const { getLogs, getStatistics, exportLogs } = useAuditLogger()
  const [logs, setLogs] = useState([])
  const [filteredLogs, setFilteredLogs] = useState([])
  const [stats, setStats] = useState(null)
  const [filters, setFilters] = useState({
    userId: '',
    action: '',
    severity: '',
    status: '',
    startDate: '',
    endDate: ''
  })
  const [sortBy, setSortBy] = useState('timestamp')
  const [sortOrder, setSortOrder] = useState('desc')
  const [expandedLog, setExpandedLog] = useState(null)

  useEffect(() => {
    loadLogs()
    loadStats()
  }, [])

  useEffect(() => {
    applyFilters()
  }, [filters, logs, sortBy, sortOrder])

  const loadLogs = () => {
    const allLogs = getLogs({
      limit: 500,
      sortBy: 'timestamp',
      sortOrder: 'desc'
    })
    setLogs(allLogs)
  }

  const loadStats = () => {
    const startDate = new Date()
    startDate.setDate(startDate.getDate() - 30)
    const statsData = getStatistics(startDate.toISOString(), new Date().toISOString())
    setStats(statsData)
  }

  const applyFilters = () => {
    let filtered = [...logs]

    if (filters.userId) {
      filtered = filtered.filter(log => log.userId.toLowerCase().includes(filters.userId.toLowerCase()))
    }

    if (filters.action) {
      filtered = filtered.filter(log => log.action === filters.action)
    }

    if (filters.severity) {
      filtered = filtered.filter(log => log.severity === filters.severity)
    }

    if (filters.status) {
      filtered = filtered.filter(log => log.status === filters.status)
    }

    if (filters.startDate) {
      const startDate = new Date(filters.startDate)
      filtered = filtered.filter(log => new Date(log.timestamp) >= startDate)
    }

    if (filters.endDate) {
      const endDate = new Date(filters.endDate)
      filtered = filtered.filter(log => new Date(log.timestamp) <= endDate)
    }

    // Sorting
    filtered.sort((a, b) => {
      let aVal = a[sortBy]
      let bVal = b[sortBy]

      if (typeof aVal === 'string') {
        aVal = aVal.toLowerCase()
        bVal = bVal.toLowerCase()
      }

      const comparison = aVal < bVal ? -1 : aVal > bVal ? 1 : 0
      return sortOrder === 'asc' ? comparison : -comparison
    })

    setFilteredLogs(filtered)
  }

  const handleExport = () => {
    const data = exportLogs({
      userId: filters.userId,
      action: filters.action,
      severity: filters.severity
    })

    const csv = 'Timestamp,User,Action,Resource,Status,Severity\n' +
      data.map(log =>
        `"${log.timestamp}","${log.userId}","${log.action}","${log.resourceType || ''}","${log.status}","${log.severity}"`
      ).join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
  }

  const handleClearFilters = () => {
    setFilters({
      userId: '',
      action: '',
      severity: '',
      status: '',
      startDate: '',
      endDate: ''
    })
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return '#d32f2f'
      case 'warning':
        return '#f57c00'
      case 'info':
        return '#1976d2'
      default:
        return '#388e3c'
    }
  }

  return (
    <div className="audit-viewer">
      <div className="management-header">
        <h2><UniversalIcon icon="📝" size={24} /> Audit Log Viewer</h2>
        <button className="btn-primary" onClick={handleExport}>
          <UniversalIcon icon="📥" size={16} /> Export CSV
        </button>
      </div>

      {stats && (
        <div className="audit-stats">
          <div className="stat-badge">
            <span className="stat-label">Total Events</span>
            <span className="stat-number">{stats.totalEvents}</span>
          </div>
          <div className="stat-badge">
            <span className="stat-label">Critical</span>
            <span className="stat-number" style={{ color: '#d32f2f' }}>
              {stats.bySeverity.critical || 0}
            </span>
          </div>
          <div className="stat-badge">
            <span className="stat-label">Warnings</span>
            <span className="stat-number" style={{ color: '#f57c00' }}>
              {stats.bySeverity.warning || 0}
            </span>
          </div>
          <div className="stat-badge">
            <span className="stat-label">Info</span>
            <span className="stat-number" style={{ color: '#1976d2' }}>
              {stats.bySeverity.info || 0}
            </span>
          </div>
        </div>
      )}

      <div className="filter-panel">
        <div className="filter-grid">
          <input
            type="text"
            placeholder="Filter by User ID..."
            value={filters.userId}
            onChange={(e) => setFilters(prev => ({ ...prev, userId: e.target.value }))}
            className="form-input"
          />
          <select
            value={filters.action}
            onChange={(e) => setFilters(prev => ({ ...prev, action: e.target.value }))}
            className="form-input"
          >
            <option value="">All Actions</option>
            <option value="user-login">User Login</option>
            <option value="user-logout">User Logout</option>
            <option value="report-created">Report Created</option>
            <option value="report-updated">Report Updated</option>
            <option value="access-denied">Access Denied</option>
            <option value="error">Error</option>
          </select>
          <select
            value={filters.severity}
            onChange={(e) => setFilters(prev => ({ ...prev, severity: e.target.value }))}
            className="form-input"
          >
            <option value="">All Severities</option>
            <option value="critical">Critical</option>
            <option value="warning">Warning</option>
            <option value="info">Info</option>
          </select>
          <input
            type="date"
            value={filters.startDate}
            onChange={(e) => setFilters(prev => ({ ...prev, startDate: e.target.value }))}
            className="form-input"
          />
          <input
            type="date"
            value={filters.endDate}
            onChange={(e) => setFilters(prev => ({ ...prev, endDate: e.target.value }))}
            className="form-input"
          />
          <button className="btn-secondary" onClick={handleClearFilters}>
            Clear Filters
          </button>
        </div>
      </div>

      <div className="audit-table-container">
        <table className="audit-table">
          <thead>
            <tr>
              <th>
                <button
                  onClick={() => {
                    setSortBy('timestamp')
                    setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
                  }}
                  className="sort-btn"
                >
                  Timestamp {sortBy === 'timestamp' && (sortOrder === 'asc' ? '↑' : '↓')}
                </button>
              </th>
              <th>User</th>
              <th>Action</th>
              <th>Resource</th>
              <th>Status</th>
              <th>Severity</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            {filteredLogs.length > 0 ? (
              filteredLogs.map(log => (
                <React.Fragment key={log.id}>
                  <tr
                    className={`audit-row severity-${log.severity}`}
                    onClick={() => setExpandedLog(expandedLog === log.id ? null : log.id)}
                  >
                    <td>{new Date(log.timestamp).toLocaleString()}</td>
                    <td>{log.userId}</td>
                    <td>{log.action}</td>
                    <td>{log.resourceName || log.resourceType || '-'}</td>
                    <td>
                      <span className={`status-badge status-${log.status}`}>
                        {log.status}
                      </span>
                    </td>
                    <td>
                      <span
                        className="severity-badge"
                        style={{ backgroundColor: getSeverityColor(log.severity) }}
                      >
                        {log.severity}
                      </span>
                    </td>
                    <td>
                      <button className="expand-icon">
                        {expandedLog === log.id ? <UniversalIcon icon="▼" size={14} /> : <UniversalIcon icon="▶" size={14} />}
                      </button>
                    </td>
                  </tr>
                  {expandedLog === log.id && (
                    <tr className="audit-details">
                      <td colSpan="7">
                        <pre>{JSON.stringify(log, null, 2)}</pre>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))
            ) : (
              <tr>
                <td colSpan="7" style={{ textAlign: 'center', padding: '20px' }}>
                  No audit logs found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="audit-footer">
        <p>Showing {filteredLogs.length} of {logs.length} logs</p>
      </div>
    </div>
  )
}

export default AuditLogsViewer
