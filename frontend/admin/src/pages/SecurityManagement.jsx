import React, { useEffect, useState } from 'react'
import { adminAPI } from '@shared/api/api'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import '../styles/admin.css'

const SecurityManagement = () => {
  const [payload, setPayload] = useState({
    stats: {
      blockedIPs: 0,
      rateLimitViolations: 0,
      suspiciousPatterns: 0,
      malwareDetections: 0,
    },
    blockedIPs: [],
    violations: [],
    rateLimit: {
      defaultLimit: 1000,
      windowSize: '1 hour',
      burstAllowance: 200,
      updatedAt: '',
    },
  })
  const [rateLimit, setRateLimit] = useState({
    defaultLimit: 1000,
    windowSize: '1 hour',
    burstAllowance: 200
  })
  const [blockForm, setBlockForm] = useState({ ip: '', reason: 'Manual block', severity: 'medium' })
  const [showRateLimitForm, setShowRateLimitForm] = useState(false)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  useEffect(() => {
    loadSecurityOverview()
  }, [])

  const loadSecurityOverview = async (showLoader = true) => {
    try {
      if (showLoader) {
        setLoading(true)
      }
      setError('')
      const response = await adminAPI.getSecurityOverview()
      const nextPayload = response.data || { stats: {}, blockedIPs: [], violations: [], rateLimit: {} }
      setPayload(nextPayload)
      setRateLimit({
        defaultLimit: nextPayload.rateLimit?.defaultLimit || 1000,
        windowSize: nextPayload.rateLimit?.windowSize || '1 hour',
        burstAllowance: nextPayload.rateLimit?.burstAllowance || 200,
      })
    } catch (err) {
      console.error('Failed to load security overview:', err)
      setError(err.response?.data?.error || err.message || 'Failed to load security overview')
    } finally {
      if (showLoader) {
        setLoading(false)
      }
    }
  }

  const handleBlockIP = async () => {
    try {
      setActionLoading('block-ip')
      setError('')
      setMessage('')
      const response = await adminAPI.createBlockedIp(blockForm)
      setMessage(response.data?.message || 'IP blocked successfully.')
      setBlockForm({ ip: '', reason: 'Manual block', severity: 'medium' })
      await loadSecurityOverview(false)
    } catch (err) {
      console.error('Failed to block IP:', err)
      setError(err.response?.data?.error || err.message || 'Failed to block IP')
    } finally {
      setActionLoading('')
    }
  }

  const handleUnblockIP = async (ipId) => {
    try {
      setActionLoading(ipId)
      setError('')
      setMessage('')
      const response = await adminAPI.deleteBlockedIp(ipId)
      setMessage(response.data?.message || 'IP unblocked successfully.')
      await loadSecurityOverview(false)
    } catch (err) {
      console.error('Failed to unblock IP:', err)
      setError(err.response?.data?.error || err.message || 'Failed to unblock IP')
    } finally {
      setActionLoading('')
    }
  }

  const handleChangeRateLimit = async () => {
    try {
      setActionLoading('rate-limit')
      setError('')
      setMessage('')
      const response = await adminAPI.updateSecurityRateLimit(rateLimit)
      setMessage(response.data?.message || 'Rate limit settings updated.')
      setShowRateLimitForm(false)
      await loadSecurityOverview(false)
    } catch (err) {
      console.error('Failed to update rate limit settings:', err)
      setError(err.response?.data?.error || err.message || 'Failed to update rate limit settings')
    } finally {
      setActionLoading('')
    }
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

  const stats = payload.stats || {}
  const blockedIPs = payload.blockedIPs || []
  const violations = payload.violations || []

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="🔒" size={24} /> Security</h2>
      <p className="section-subtitle">Persisted security controls, block lists, and admin-side rate-limit guardrails</p>

      {error && <div className="alert-banner error">{error}</div>}
      {message && <div className="alert-banner success">{message}</div>}

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
        <button className="action-button primary" onClick={() => setShowRateLimitForm(!showRateLimitForm)} title="Adjust rate limits">
          <UniversalIcon icon="⚙️" size={14} /> Change Rate Limits
        </button>
        <button className="action-button primary" onClick={() => loadSecurityOverview()} disabled={loading} title="Refresh security overview">
          <UniversalIcon icon="🔄" size={14} /> {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      <div className="filter-controls" style={{ marginBottom: '24px', display: 'grid', gridTemplateColumns: '2fr 2fr 1fr auto', gap: '12px', alignItems: 'end' }}>
        <div>
          <label>IP Address</label>
          <input
            type="text"
            value={blockForm.ip}
            onChange={(e) => setBlockForm({ ...blockForm, ip: e.target.value })}
            placeholder="e.g. 203.45.67.89"
            className="form-input"
          />
        </div>
        <div>
          <label>Reason</label>
          <input
            type="text"
            value={blockForm.reason}
            onChange={(e) => setBlockForm({ ...blockForm, reason: e.target.value })}
            className="form-input"
          />
        </div>
        <div>
          <label>Severity</label>
          <select
            value={blockForm.severity}
            onChange={(e) => setBlockForm({ ...blockForm, severity: e.target.value })}
            className="form-input"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
        <button className="action-button primary" onClick={handleBlockIP} disabled={actionLoading === 'block-ip'} title="Add new IP to block list">
          <UniversalIcon icon="🚫" size={14} /> {actionLoading === 'block-ip' ? 'Blocking...' : 'Block IP'}
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
            disabled={actionLoading === 'rate-limit'}
            style={{ marginLeft: '20px' }}
          >
            {actionLoading === 'rate-limit' ? 'Applying...' : 'Apply Changes'}
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
                      disabled={actionLoading === block.id}
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
        <p className="section-subtitle" style={{ marginBottom: '16px' }}>
          Current guardrails: {payload.rateLimit?.defaultLimit || rateLimit.defaultLimit} requests per {payload.rateLimit?.windowSize || rateLimit.windowSize} with burst allowance {payload.rateLimit?.burstAllowance || rateLimit.burstAllowance}
          {payload.rateLimit?.updatedAt ? ` • Updated ${payload.rateLimit.updatedAt}` : ''}
        </p>

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
