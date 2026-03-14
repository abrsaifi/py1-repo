import React, { useState, useEffect } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import '../styles/admin.css'

const WorkerMonitoring = () => {
  const [workers, setWorkers] = useState([])

  const [stats, setStats] = useState({
    activeWorkers: 0,
    queueSize: 0,
    avgProcessingTimeMs: 0,
    workerErrors: 0,
    memoryUsageMb: 0,
  })

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')


  useEffect(() => {
    loadWorkers()
    const interval = setInterval(() => {
      loadWorkers()
    }, 15000)
    
    return () => clearInterval(interval)
  }, [])


  const loadWorkers = async () => {
    try {
      setError('')
      const response = await fetch('/api/admin/workers', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` },
      })
      const payload = await response.json().catch(() => ({}))
      if (!response.ok) {
        throw new Error(payload.error || 'Failed to load worker status')
      }

      setWorkers(payload.workers || [])
      setStats({
        activeWorkers: Number(payload.stats?.activeWorkers || 0),
        queueSize: Number(payload.stats?.queueSize || 0),
        avgProcessingTimeMs: Number(payload.stats?.avgProcessingTimeMs || 0),
        workerErrors: Number(payload.stats?.workerErrors || 0),
        memoryUsageMb: Number(payload.stats?.memoryUsageMb || 0),
      })
      setMessage(payload.message || '')
    } catch (loadError) {
      console.error('Failed to load worker monitoring:', loadError)
      setError(loadError.message || 'Failed to load worker status')
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      active: { color: '#11998e', text: '✅ Active' },
      busy: { color: '#4099ff', text: '⚙️ Busy' },
      idle: { color: '#718096', text: '😴 Idle' },
      offline: { color: '#eb3349', text: '❌ Offline' },
      error: { color: '#eb3349', text: '❌ Error' }
    }
    return badges[status] || badges.idle
  }

  const getMemoryColor = (mb) => {
    if (mb > 700) return '#eb3349'
    if (mb > 600) return '#f97316'
    return '#11998e'
  }

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="⚙️" size={24} /> Workers</h2>
      <p className="section-subtitle">Monitor background processing - Critical for Celery workers</p>

      {error ? (
        <div className="no-data" style={{ marginBottom: '20px', border: '1px solid #fed7d7', background: '#fff5f5', color: '#c53030' }}>
          <p>{error}</p>
        </div>
      ) : null}

      {message ? (
        <p className="section-subtitle" style={{ marginTop: '-4px' }}>{message}</p>
      ) : null}

      <div className="admin-stats-grid">
        <div className="admin-stat-card metric-primary">
          <UniversalIcon icon="🖥️" size={32} />
          <div className="stat-content">
            <h3>Active Workers</h3>
            <p className="stat-value">{stats.activeWorkers}</p>
            <p className="stat-detail">Processing jobs</p>
          </div>
        </div>

        <div className="admin-stat-card metric-info">
          <UniversalIcon icon="📋" size={32} />
          <div className="stat-content">
            <h3>Queue Size</h3>
            <p className="stat-value">{stats.queueSize}</p>
            <p className="stat-detail">Jobs waiting</p>
          </div>
        </div>

        <div className="admin-stat-card metric-success">
          <UniversalIcon icon="⏱️" size={32} />
          <div className="stat-content">
            <h3>Avg Processing Time</h3>
            <p className="stat-value">{stats.avgProcessingTimeMs.toFixed(0)} ms</p>
            <p className="stat-detail">Recent request baseline</p>
          </div>
        </div>

        <div className="admin-stat-card metric-danger">
          <UniversalIcon icon="⚠️" size={32} />
          <div className="stat-content">
            <h3>Worker Errors</h3>
            <p className="stat-value">{stats.workerErrors}</p>
            <p className="stat-detail">Errors in last hour</p>
          </div>
        </div>

        <div className="admin-stat-card metric-warning">
          <UniversalIcon icon="💾" size={32} />
          <div className="stat-content">
            <h3>Memory Usage</h3>
            <p className="stat-value">{(stats.memoryUsageMb / 1024).toFixed(2)} GB</p>
            <p className="stat-detail">Worker RSS total</p>
          </div>
        </div>
      </div>

      <div className="quick-actions" style={{ marginTop: '30px', marginBottom: '30px' }}>
        <button className="action-button primary" onClick={loadWorkers} title="Refresh worker status" disabled={loading}>
          <UniversalIcon icon="📈" size={16} /> {loading ? 'Loading...' : 'Refresh Worker Status'}
        </button>
      </div>

      <div className="admin-section-content">
        <h3>Worker Status</h3>

        <div className="jobs-table-wrapper">
          <table className="jobs-table">
            <thead>
              <tr>
                <th>Worker ID</th>
                <th>Name</th>
                <th>Status</th>
                <th>Queue</th>
                <th>Avg Processing</th>
                <th>Errors</th>
                <th>Memory</th>
                <th>Last Heartbeat</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="8">Loading worker status...</td>
                </tr>
              ) : workers.length > 0 ? (
                workers.map(worker => {
                  const statusInfo = getStatusBadge(worker.status)
                  const memoryColor = getMemoryColor(worker.memoryMb)
                  return (
                    <tr key={worker.id} className={`job-row ${worker.status}`}>
                      <td className="job-id"><code>{worker.id}</code></td>
                      <td><strong>{worker.name}</strong></td>
                      <td>
                        <span className="status-badge" style={{ backgroundColor: statusInfo.color }}>
                          {statusInfo.text}
                        </span>
                      </td>
                      <td><strong>{worker.queue}</strong> tasks</td>
                      <td>{worker.avgTimeMs != null ? `${Number(worker.avgTimeMs).toFixed(0)} ms` : 'N/A'}</td>
                      <td>
                        {worker.errors > 0 ? (
                          <span className="status-badge" style={{ backgroundColor: '#eb3349', color: 'white' }}>
                            <UniversalIcon icon="⚠️" size={14} /> {worker.errors}
                          </span>
                        ) : (
                          <span style={{ color: '#11998e', fontWeight: '600' }}><UniversalIcon icon="✓" size={14} /> 0</span>
                        )}
                      </td>
                      <td>
                        <span className="format-badge" style={{ background: `linear-gradient(135deg, ${memoryColor} 0%, ${adjustBrightness(memoryColor, -20)} 100%)`, color: 'white' }}>
                          {worker.memoryMb ? `${worker.memoryMb.toFixed(0)} MB` : 'N/A'}
                        </span>
                      </td>
                      <td className="timestamp">{worker.lastHeartbeat ? worker.lastHeartbeat.replace('T', ' ').slice(0, 19) : 'N/A'}</td>
                    </tr>
                  )
                })
              ) : (
                <tr>
                  <td colSpan="8">No workers available</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
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

export default WorkerMonitoring
