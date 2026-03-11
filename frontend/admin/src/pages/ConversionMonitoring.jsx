import React, { useState, useEffect } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import '../styles/admin.css'
import { FormatBadge, StatusBadge, getStatusIcon } from '@shared/utils/badgeIcons'

const ConversionMonitoring = () => {
  const [stats, setStats] = useState({
    queueSize: 27,
    runningJobs: 5,
    failedJobs: 2,
    totalToday: 3204,
    successRate: 98.2,
    avgTime: 1.8
  })

  const [filterType, setFilterType] = useState('all') // all, failed, large, slow
  const [jobs, setJobs] = useState([
    { id: 'JOB-001234', user: 'User 123', inputFormat: 'PDF', outputFormat: 'DOCX', fileSize: '2.5 MB', status: 'completed', processingTime: '1.2s', workerNode: 'Worker-03', createdAt: '2026-03-06 14:32' },
    { id: 'JOB-001235', user: 'User 441', inputFormat: 'JPG', outputFormat: 'PNG', fileSize: '4.8 MB', status: 'processing', processingTime: '0.5s', workerNode: 'Worker-01', createdAt: '2026-03-06 14:35' },
    { id: 'JOB-001236', user: 'User 892', inputFormat: 'DOC', outputFormat: 'PDF', fileSize: '1.2 MB', status: 'failed', processingTime: '2.1s', workerNode: 'Worker-02', createdAt: '2026-03-06 14:28' },
    { id: 'JOB-001237', user: 'User 567', inputFormat: 'XLSX', outputFormat: 'CSV', fileSize: '0.8 MB', status: 'completed', processingTime: '0.8s', workerNode: 'Worker-04', createdAt: '2026-03-06 14:30' },
    { id: 'JOB-001238', user: 'User 234', inputFormat: 'PNG', outputFormat: 'WebP', fileSize: '12.5 MB', status: 'processing', processingTime: '3.2s', workerNode: 'Worker-05', createdAt: '2026-03-06 14:25' },
    { id: 'JOB-001239', user: 'User 678', inputFormat: 'PPTX', outputFormat: 'PDF', fileSize: '8.3 MB', status: 'failed', processingTime: '5.8s', workerNode: 'Worker-01', createdAt: '2026-03-06 14:20' },
  ])

  useEffect(() => {
    const loadStats = setInterval(() => {
      setStats(prev => ({
        ...prev,
        queueSize: Math.max(0, prev.queueSize + Math.floor(Math.random() * 5) - 2),
        runningJobs: Math.floor(Math.random() * 8) + 2,
        totalToday: prev.totalToday + Math.floor(Math.random() * 10)
      }))
    }, 3000)
    
    return () => clearInterval(loadStats)
  }, [])

  const getFilteredJobs = () => {
    switch(filterType) {
      case 'failed':
        return jobs.filter(job => job.status === 'failed')
      case 'large':
        return jobs.filter(job => {
          const size = parseFloat(job.fileSize)
          return size > 5
        })
      case 'slow':
        return jobs.filter(job => {
          const time = parseFloat(job.processingTime)
          return time > 2
        })
      default:
        return jobs
    }
  }

  const handleRetry = (jobId) => {
    alert(`Retrying job: ${jobId}`)
  }

  const handleCancel = (jobId) => {
    alert(`Cancelling job: ${jobId}`)
  }

  const handleViewLogs = (jobId) => {
    alert(`Viewing logs for job: ${jobId}`)
  }

  const getStatusBadge = (status) => {
    const badges = {
      completed: { color: '#11998e', text: '✅ Completed' },
      processing: { color: '#4099ff', text: '⏳ Processing' },
      failed: { color: '#eb3349', text: '❌ Failed' },
      queued: { color: '#fa709a', text: '📋 Queued' }
    }
    return badges[status] || badges.queued
  }

  const filteredJobs = getFilteredJobs()

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="🔁" size={24} /> Conversions</h2>
      <p className="section-subtitle">Operational view of all jobs</p>

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
            <p className="stat-value">{stats.avgTime}s</p>
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
        
        <div className="filter-controls">
          <label>Filter:</label>
          <select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
            <option value="all">All Jobs ({jobs.length})</option>
            <option value="failed">Failed Jobs ({jobs.filter(j => j.status === 'failed').length})</option>
            <option value="large">Large Files ({jobs.filter(j => parseFloat(j.fileSize) > 5).length})</option>
            <option value="slow">Slow Conversions ({jobs.filter(j => parseFloat(j.processingTime) > 2).length})</option>
          </select>
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
              {filteredJobs.map(job => {
                const statusInfo = getStatusBadge(job.status)
                return (
                  <tr key={job.id} className={`job-row ${job.status}`}>
                    <td className="job-id"><code>{job.id}</code></td>
                    <td>{job.user}</td>
                    <td>
                      <FormatBadge format={job.inputFormat} />
                    </td>
                    <td>
                      <FormatBadge format={job.outputFormat} />
                    </td>
                    <td>{job.fileSize}</td>
                    <td>
                      <StatusBadge status={job.status} text={statusInfo.text} style={{ backgroundColor: statusInfo.color }} />
                    </td>
                    <td>{job.processingTime}</td>
                    <td><code>{job.workerNode}</code></td>
                    <td className="timestamp">{job.createdAt}</td>
                    <td className="actions">
                      <button className="action-btn retry" onClick={() => handleRetry(job.id)} title="Retry"><UniversalIcon icon="↻" size={14} /></button>
                      <button className="action-btn cancel" onClick={() => handleCancel(job.id)} title="Cancel"><UniversalIcon icon="✗" size={14} /></button>
                      <button className="action-btn logs" onClick={() => handleViewLogs(job.id)} title="Logs"><UniversalIcon icon="📋" size={14} /></button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {filteredJobs.length === 0 && (
          <div className="no-data">
            <p>No jobs match the selected filter</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default ConversionMonitoring
