import React, { useState } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import '../styles/admin.css'

const SecurityManagement = () => {
  const [stats, setStats] = useState({
    blockedIPs: 12,
    rateLimitViolations: 47,
    suspiciousPatterns: 8,
    malwareDetections: 2
  })

  const [blockedIPs, setBlockedIPs] = useState([
    { id: 'BLK-001', ip: '192.168.1.105', reason: 'Brute force attack', blockedDate: '2026-03-06 14:30', severity: 'critical' },
    { id: 'BLK-002', ip: '203.45.67.89', reason: 'Rate limit exceeded', blockedDate: '2026-03-06 13:15', severity: 'high' },
    { id: 'BLK-003', ip: '158.92.134.56', reason: 'Suspicious pattern', blockedDate: '2026-03-06 10:45', severity: 'medium' },
    { id: 'BLK-004', ip: '172.16.45.200', reason: 'Malware signature detected', blockedDate: '2026-03-05 22:10', severity: 'critical' },
    { id: 'BLK-005', ip: '210.100.88.34', reason: 'SQL injection attempt', blockedDate: '2026-03-05 18:20', severity: 'high' },
  ])

  const [violations, setViolations] = useState([
    { id: 'VIO-001', ip: '10.20.30.40', endpoint: '/api/convert', count: 2847, limit: 1000, timestamp: '2026-03-06 14:50', status: 'active' },
    { id: 'VIO-002', ip: '192.168.50.10', endpoint: '/api/upload', count: 1567, limit: 500, timestamp: '2026-03-06 14:35', status: 'active' },
    { id: 'VIO-003', ip: '172.30.20.15', endpoint: '/api/health', count: 892, limit: 5000, timestamp: '2026-03-06 14:20', status: 'resolved' },
  ])

  const [rateLimit, setRateLimit] = useState({
    defaultLimit: 1000,
    windowSize: '1 hour',
    burstAllowance: 200
  })

  const [showRateLimitForm, setShowRateLimitForm] = useState(false)

  const handleBlockIP = () => {
    const newIP = prompt('Enter IP address to block:')
    if (newIP) {
      alert(`Blocking IP: ${newIP}`)
      const newBlock = {
        id: `BLK-${String(blockedIPs.length + 1).padStart(3, '0')}`,
        ip: newIP,
        reason: 'Manual block',
        blockedDate: new Date().toLocaleString(),
        severity: 'medium'
      }
      setBlockedIPs([newBlock, ...blockedIPs])
      setStats(prev => ({ ...prev, blockedIPs: prev.blockedIPs + 1 }))
    }
  }

  const handleUnblockIP = (ipId) => {
    alert(`Unblocking IP: ${ipId}`)
    setBlockedIPs(blockedIPs.filter(ip => ip.id !== ipId))
    setStats(prev => ({ ...prev, blockedIPs: Math.max(0, prev.blockedIPs - 1) }))
  }

  const handleChangeRateLimit = () => {
    alert('Updating rate limits to: ' + rateLimit.defaultLimit + ' requests per ' + rateLimit.windowSize)
    setShowRateLimitForm(false)
  }

  const getSeverityColor = (severity) => {
    const colors = {
      critical: '#eb3349',
      high: '#f97316',
      medium: '#f6ad55',
      low: '#11998e'
    }
    return colors[severity] || '#718096'
  }

  const getStatusColor = (status) => {
    return status === 'active' ? '#eb3349' : '#11998e'
  }

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="🔒" size={24} /> Security</h2>
      <p className="section-subtitle">Security monitoring panel - IP blocking & rate limiting</p>

      <div className="admin-stats-grid">
        <div className="admin-stat-card metric-danger">
          <UniversalIcon icon="🚫" size={32} />
          <div className="stat-content">
            <h3>Blocked IPs</h3>
            <p className="stat-value">{stats.blockedIPs}</p>
            <p className="stat-detail">Currently blocked</p>
          </div>
        </div>

        <div className="admin-stat-card metric-warning">
          <UniversalIcon icon="⚠️" size={32} />
          <div className="stat-content">
            <h3>Rate Limit Violations</h3>
            <p className="stat-value">{stats.rateLimitViolations}</p>
            <p className="stat-detail">Last 24 hours</p>
          </div>
        </div>

        <div className="admin-stat-card metric-info">
          <UniversalIcon icon="🔍" size={32} />
          <div className="stat-content">
            <h3>Suspicious Upload Patterns</h3>
            <p className="stat-value">{stats.suspiciousPatterns}</p>
            <p className="stat-detail">Detected today</p>
          </div>
        </div>

        <div className="admin-stat-card metric-danger">
          <UniversalIcon icon="🦠" size={32} />
          <div className="stat-content">
            <h3>Malware Detections</h3>
            <p className="stat-value">{stats.malwareDetections}</p>
            <p className="stat-detail">In last 7 days</p>
          </div>
        </div>
      </div>

      <div className="quick-actions" style={{ marginTop: '30px', marginBottom: '30px' }}>
        <button className="action-button primary" onClick={handleBlockIP} title="Add new IP to block list">
          <UniversalIcon icon="🚫" size={14} /> Block IP
        </button>
        <button className="action-button primary" onClick={() => setShowRateLimitForm(!showRateLimitForm)} title="Adjust rate limits">
          <UniversalIcon icon="⚙️" size={14} /> Change Rate Limits
        </button>
      </div>

      {showRateLimitForm && (
        <div className="filter-controls" style={{ marginBottom: '30px' }}>
          <label>Default Rate Limit (requests per hour):</label>
          <input 
            type="number" 
            value={rateLimit.defaultLimit} 
            onChange={(e) => setRateLimit({...rateLimit, defaultLimit: parseInt(e.target.value)})}
            style={{ padding: '8px 12px', border: '1px solid #cbd5e0', borderRadius: '6px', width: '150px' }}
          />
          <label style={{ marginLeft: '20px' }}>Burst Allowance:</label>
          <input 
            type="number" 
            value={rateLimit.burstAllowance} 
            onChange={(e) => setRateLimit({...rateLimit, burstAllowance: parseInt(e.target.value)})}
            style={{ padding: '8px 12px', border: '1px solid #cbd5e0', borderRadius: '6px', width: '150px' }}
          />
          <button 
            className="action-button primary" 
            onClick={handleChangeRateLimit}
            style={{ marginLeft: '20px' }}
          >
            Apply Changes
          </button>
        </div>
      )}

      <div className="admin-section-content">
        <h3>Blocked IPs</h3>

        <div className="jobs-table-wrapper">
          <table className="jobs-table">
            <thead>
              <tr>
                <th>Block ID</th>
                <th>IP Address</th>
                <th>Reason</th>
                <th>Severity</th>
                <th>Blocked Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {blockedIPs.map(block => (
                <tr key={block.id} className="job-row">
                  <td className="job-id"><code>{block.id}</code></td>
                  <td><strong>{block.ip}</strong></td>
                  <td>{block.reason}</td>
                  <td>
                    <span className="status-badge" style={{ backgroundColor: getSeverityColor(block.severity) }}>
                      {block.severity.toUpperCase()}
                    </span>
                  </td>
                  <td className="timestamp">{block.blockedDate}</td>
                  <td className="actions">
                    <button 
                      className="action-btn logs" 
                      onClick={() => handleUnblockIP(block.id)} 
                      title="Unblock IP"
                    >
                      <UniversalIcon icon="🔓" size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {blockedIPs.length === 0 && (
          <div className="no-data">
            <p>No blocked IPs</p>
          </div>
        )}
      </div>

      <div className="admin-section-content" style={{ marginTop: '40px' }}>
        <h3>Rate Limit Violations</h3>

        <div className="jobs-table-wrapper">
          <table className="jobs-table">
            <thead>
              <tr>
                <th>Violation ID</th>
                <th>IP Address</th>
                <th>Endpoint</th>
                <th>Request Count</th>
                <th>Limit</th>
                <th>Status</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {violations.map(vio => (
                <tr key={vio.id} className="job-row">
                  <td className="job-id"><code>{vio.id}</code></td>
                  <td><strong>{vio.ip}</strong></td>
                  <td><code>{vio.endpoint}</code></td>
                  <td><strong>{vio.count.toLocaleString()}</strong></td>
                  <td>{vio.limit.toLocaleString()}</td>
                  <td>
                    <span className="status-badge" style={{ backgroundColor: getStatusColor(vio.status) }}>
                      {vio.status.toUpperCase()}
                    </span>
                  </td>
                  <td className="timestamp">{vio.timestamp}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {violations.length === 0 && (
          <div className="no-data">
            <p>No rate limit violations</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default SecurityManagement
