import React, { useState, useEffect } from 'react'
import { UniversalIcon } from '../utils/UniversalIcon'
import '../styles/admin.css'

const WorkerMonitoring = () => {
  const [workers, setWorkers] = useState([
    { id: 'WORKER-001', name: 'Worker-01', queue: 5, status: 'active', avgTime: '2.3s', errors: 0, memory: '645 MB', lastHeartbeat: '2026-03-06 14:50' },
    { id: 'WORKER-002', name: 'Worker-02', queue: 3, status: 'active', avgTime: '1.8s', errors: 0, memory: '512 MB', lastHeartbeat: '2026-03-06 14:50' },
    { id: 'WORKER-003', name: 'Worker-03', queue: 8, status: 'busy', avgTime: '3.1s', errors: 2, memory: '782 MB', lastHeartbeat: '2026-03-06 14:49' },
    { id: 'WORKER-004', name: 'Worker-04', queue: 0, status: 'idle', avgTime: '0.0s', errors: 0, memory: '342 MB', lastHeartbeat: '2026-03-06 14:48' },
    { id: 'WORKER-005', name: 'Worker-05', queue: 6, status: 'active', avgTime: '2.5s', errors: 1, memory: '698 MB', lastHeartbeat: '2026-03-06 14:50' },
  ])

  const [stats, setStats] = useState({
    activeWorkers: 4,
    queueSize: 22,
    avgProcessingTime: '2.3s',
    workerErrors: 3,
    memoryUsage: '2.98 GB / 4.00 GB'
  })


  useEffect(() => {
    const interval = setInterval(() => {
      setWorkers(prev => prev.map(w => {
        const currentMB = parseInt(w.memory)
        const newMB = Math.max(300, Math.min(800, currentMB + Math.floor(Math.random() * 100) - 50))
        const newTime = (Math.random() * 4 + 1).toFixed(1)
        return {
          ...w,
          queue: Math.max(0, w.queue + Math.floor(Math.random() * 4) - 1),
          memory: newMB + ' MB',
          avgTime: newTime + 's'
        }
      }))

      const totalQueue = Math.floor(Math.random() * 30) + 10
      const totalMB = Math.min(3900, Math.max(2500, Math.floor(Math.random() * 4000)))
      const procTime = (Math.random() * 3 + 1).toFixed(1)
      const memUsage = (totalMB / 1024).toFixed(2)
      
      setStats(prev => ({
        ...prev,
        queueSize: totalQueue,
        avgProcessingTime: procTime + 's',
        memoryUsage: memUsage + ' GB / 4.00 GB'
      }))
    }, 3000)
    
    return () => clearInterval(interval)
  }, [])


  const handleRestartWorker = (workerId) => {
    alert(`Restarting worker: ${workerId}`)
  }

  const handleScaleWorkerPool = () => {
    alert('Opening worker scaling interface...')
  }

  const handleViewLogs = (workerId) => {
    alert(`Viewing logs for worker: ${workerId}`)
  }

  const getStatusBadge = (status) => {
    const badges = {
      active: { color: '#11998e', text: '✅ Active' },
      busy: { color: '#4099ff', text: '⚙️ Busy' },
      idle: { color: '#718096', text: '😴 Idle' },
      error: { color: '#eb3349', text: '❌ Error' }
    }
    return badges[status] || badges.idle
  }

  const getMemoryColor = (memStr) => {
    const mb = parseInt(memStr)
    if (mb > 700) return '#eb3349'
    if (mb > 600) return '#f97316'
    return '#11998e'
  }

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="⚙️" size={24} /> Workers</h2>
      <p className="section-subtitle">Monitor background processing - Critical for Celery workers</p>

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
            <p className="stat-value">{stats.avgProcessingTime}</p>
            <p className="stat-detail">Per task</p>
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
            <p className="stat-value">{stats.memoryUsage}</p>
            <p className="stat-detail">System RAM</p>
          </div>
        </div>
      </div>

      <div className="quick-actions" style={{ marginTop: '30px', marginBottom: '30px' }}>
        <button className="action-button primary" onClick={handleScaleWorkerPool} title="Add or remove workers">
          <UniversalIcon icon="📈" size={16} /> Scale Worker Pool
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
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {workers.map(worker => {
                const statusInfo = getStatusBadge(worker.status)
                const memoryColor = getMemoryColor(worker.memory)
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
                    <td>{worker.avgTime}</td>
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
                        {worker.memory}
                      </span>
                    </td>
                    <td className="timestamp">{worker.lastHeartbeat}</td>
                    <td className="actions">
                      <button 
                        className="action-btn retry" 
                        onClick={() => handleRestartWorker(worker.id)} 
                        title="Restart Worker"
                      >
                        <UniversalIcon icon="🔄" size={14} />
                      </button>
                      <button 
                        className="action-btn cancel" 
                        onClick={() => handleViewLogs(worker.id)} 
                        title="View Logs"
                      >
                        <UniversalIcon icon="📋" size={14} />
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {workers.length === 0 && (
          <div className="no-data">
            <p>No workers available</p>
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

export default WorkerMonitoring
