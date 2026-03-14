import React, { useState, useEffect } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import '../styles/admin.css'
import { FormatBadge, StatusBadge } from '@shared/utils/badgeIcons'

const ConversionMonitoring = () => {
  const [stats, setStats] = useState({
    queueSize: 0,
    runningJobs: 0,
    failedJobs: 0,
    totalToday: 0,
    successRate: 0,
    avgProcessingSeconds: 0,
  })

  const [filterType, setFilterType] = useState('all')
  const [jobs, setJobs] = useState([])
  const [filterCounts, setFilterCounts] = useState({ all: 0, failed: 0, large: 0, slow: 0 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedJob, setSelectedJob] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)

  useEffect(() => {
    loadMonitoring()
    const intervalId = window.setInterval(() => {
      loadMonitoring(false)
    }, 15000)

    return () => window.clearInterval(intervalId)
  }, [])

  const loadMonitoring = async (showLoader = true) => {
    try {
      if (showLoader) {
        setLoading(true)
      }
      setError('')

      const response = await fetch('/api/admin/conversions/monitoring?limit=100', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
        },
      })

      const payload = await response.json()
      if (!response.ok) {
        throw new Error(payload.error || 'Failed to load conversion monitoring')
      }

      setStats(payload.stats || {
        queueSize: 0,
        runningJobs: 0,
        failedJobs: 0,
        totalToday: 0,
        successRate: 0,
        avgProcessingSeconds: 0,
      })
      setJobs(payload.jobs || [])
      setFilterCounts(payload.filters || { all: 0, failed: 0, large: 0, slow: 0 })
      setLastUpdated(payload.generatedAt || null)
    } catch (err) {
      console.error('Failed to load conversion monitoring:', err)
      setError(err.message || 'Failed to load conversion monitoring')
    } finally {
      if (showLoader) {
        setLoading(false)
      }
    }
  }

  const getFilteredJobs = () => {
    switch (filterType) {
      case 'failed':
        return jobs.filter(job => job.status === 'failed')
      case 'large':
        return jobs.filter(job => job.isLarge)
      case 'slow':
        return jobs.filter(job => job.isSlow)
      default:
        return jobs
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      completed: { color: '#11998e', text: '✅ Completed' },
      processing: { color: '#4099ff', text: '⏳ Processing' },
      failed: { color: '#eb3349', text: '❌ Failed' },
      cancelled: { color: '#718096', text: '⛔ Cancelled' },
      queued: { color: '#fa709a', text: '📋 Queued' }
    }
    return badges[status] || badges.queued
  }

  const filteredJobs = getFilteredJobs()

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="🔁" size={24} /> Conversions</h2>
      <p className="section-subtitle">
        Operational view of real conversion jobs
        {lastUpdated ? ` • Last updated ${lastUpdated.replace('T', ' ').slice(0, 19)}` : ''}
      </p>

      {error && <div className="alert-banner error">{error}</div>}

      <div className="admin-stats-grid">
        <div className="admin-stat-card metric-info">
          <UniversalIcon icon="📋" size={32} />
          <div className="stat-content">
            <h3>Queue Size</h3>
            <p className="stat-value">{stats.queueSize}</p>
            <p className="stat-detail">Jobs waiting</p>
          </div>
        </div>

        <div className="admin-stat-card metric-primary">
          <UniversalIcon icon="⚙️" size={32} />
          <div className="stat-content">
            <h3>Running Jobs</h3>
            <p className="stat-value">{stats.runningJobs}</p>
            <p className="stat-detail">Currently processing</p>
          </div>
        </div>

        <div className="admin-stat-card metric-danger">
          <UniversalIcon icon="❌" size={32} />
          <div className="stat-content">
            <h3>Failed Jobs</h3>
            <p className="stat-value">{stats.failedJobs}</p>
            <p className="stat-detail">Needs attention</p>
          </div>
        </div>

        <div className="admin-stat-card metric-success">
          <UniversalIcon icon="✅" size={32} />
          <div className="stat-content">
            <h3>Success Rate</h3>
            <p className="stat-value">{stats.successRate}%</p>
            <p className="stat-detail">Today</p>
          </div>
        </div>

        <div className="admin-stat-card metric-warning">
          <UniversalIcon icon="⏱️" size={32} />
          <div className="stat-content">
            <h3>Avg Processing</h3>
            <p className="stat-value">{stats.avgProcessingSeconds}s</p>
            <p className="stat-detail">Average time</p>
          </div>
        </div>

        <div className="admin-stat-card metric-revenue">
          <UniversalIcon icon="📊" size={32} />
          <div className="stat-content">
            <h3>Conversions Today</h3>
            <p className="stat-value">{stats.totalToday}</p>
            <p className="stat-detail">Total completed</p>
          </div>
        </div>
      </div>

      <div className="admin-section-content">
        <h3>Job Management</h3>
        <div className="filter-controls" style={{ justifyContent: 'space-between', alignItems: 'center', gap: '12px' }}>
          <div className="filter-controls">
            <label>Filter:</label>
            <select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
              <option value="all">All Jobs ({filterCounts.all})</option>
              <option value="failed">Failed Jobs ({filterCounts.failed})</option>
              <option value="large">Large Files ({filterCounts.large})</option>
              <option value="slow">Slow Conversions ({filterCounts.slow})</option>
            </select>
          </div>
          <button className="action-button primary" onClick={() => loadMonitoring()} disabled={loading}>
            <UniversalIcon icon="📈" size={16} /> {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>

        <div className="jobs-table-wrapper">
          <table className="jobs-table">
            <thead>
              <tr>
                <th>Job ID</th>
                <th>User</th>
                <th>Input</th>
                <th>Output</th>
                <th>File Size</th>
                <th>Status</th>
                <th>Time</th>
                <th>Worker</th>
                <th>Created At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr>
                  <td colSpan="10" className="timestamp">Loading conversion activity...</td>
                </tr>
              )}
              {filteredJobs.map(job => {
                const statusInfo = getStatusBadge(job.status)
                return (
                  <tr key={job.id} className={`job-row ${job.status}`}>
                    <td className="job-id"><code>{job.displayId}</code></td>
                    <td>{job.user}</td>
                    <td>
                      <FormatBadge format={job.inputFormat} />
                    </td>
                    <td>
                      <FormatBadge format={job.outputFormat} />
                    </td>
                    <td>{job.fileSizeLabel}</td>
                    <td>
                      <StatusBadge status={job.status} text={statusInfo.text} style={{ backgroundColor: statusInfo.color }} />
                    </td>
                    <td>{job.processingTimeLabel}</td>
                    <td><code>{job.workerNode}</code></td>
                    <td className="timestamp">{job.createdAt}</td>
                    <td className="actions">
                      <button className="action-btn logs" onClick={() => setSelectedJob(job)} title="Inspect">
                        <UniversalIcon icon="📋" size={14} />
                      </button>
                    </td>
                  </tr>
                )
              })}
              {!loading && filteredJobs.length === 0 && (
                <tr>
                  <td colSpan="10" className="timestamp">No jobs match the selected filter</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {selectedJob && (
        <div className="metric-detail-modal" onClick={() => setSelectedJob(null)}>
          <div className="modal-content" onClick={(event) => event.stopPropagation()}>
            <h3>{selectedJob.displayId}</h3>
            <p><strong>User:</strong> {selectedJob.user}</p>
            <p><strong>File:</strong> {selectedJob.filename || 'Unknown file'}</p>
            <p><strong>Output:</strong> {selectedJob.outputFilename || 'Pending'}</p>
            <p><strong>Status:</strong> {selectedJob.status}</p>
            <p><strong>Worker:</strong> {selectedJob.workerNode}</p>
            <p><strong>Created:</strong> {selectedJob.createdAt || 'Unknown'}</p>
            <p><strong>Processing Time:</strong> {selectedJob.processingTimeLabel}</p>
            <p><strong>Error:</strong> {selectedJob.errorMessage || 'No error details recorded'}</p>
            <button className="btn btn-secondary" onClick={() => setSelectedJob(null)}>
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default ConversionMonitoring
