import React, { useEffect, useState } from 'react'
import { adminAPI } from '@shared/api/api'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import '../styles/admin.css'

const APIMonitoring = () => {
  const [payload, setPayload] = useState({
    conversionMetrics: { successRate: 0, avgProcessingTime: 0, queueDepth: 0 },
    userMetrics: { newUsersPerDay: 0, activeUsers: 0, retention: 0 },
    infraMetrics: { cpuUsage: 0, memoryUsage: 0, diskUsage: 0 },
    stats: { requestRate: 0, avgResponseTime: 0, errorRate: 0, activeApiKeys: 0, totalApiKeys: 0 },
    endpoints: [],
    apiKeys: [],
    rateLimitPolicies: [],
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [lastUpdated, setLastUpdated] = useState('')

  useEffect(() => {
    loadApiMonitoring()
    const intervalId = window.setInterval(() => {
      loadApiMonitoring(false)
    }, 15000)

    return () => window.clearInterval(intervalId)
  }, [])

  const loadApiMonitoring = async (showLoader = true) => {
    try {
      if (showLoader) {
        setLoading(true)
      }
      setError('')
      const response = await adminAPI.getApiMonitoring()
      setPayload(response.data || {})
      setLastUpdated(response.data?.generatedAt || '')
    } catch (err) {
      console.error('Failed to load API monitoring:', err)
      setError(err.message || 'Failed to load API monitoring')
    } finally {
      if (showLoader) {
        setLoading(false)
      }
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      healthy: '#11998e',
      active: '#11998e',
      warning: '#f6ad55',
      degraded: '#f6ad55',
      critical: '#eb3349',
      offline: '#eb3349',
      expired: '#718096',
      inactive: '#718096',
    }
    return colors[status] || '#4099ff'
  }

  const conversionMetrics = payload.conversionMetrics || {}
  const userMetrics = payload.userMetrics || {}
  const infraMetrics = payload.infraMetrics || {}
  const stats = payload.stats || {}

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="📈" size={24} /> API Monitoring</h2>
      <p className="section-subtitle">
        Live conversion, user, infrastructure, and API consumer telemetry
        {lastUpdated ? ` • Last updated ${lastUpdated.replace('T', ' ').slice(0, 19)}` : ''}
      </p>

      {error && <div className="alert-banner error">{error}</div>}

      <div className="quick-actions" style={{ marginBottom: '24px' }}>
        <button className="action-button primary" onClick={() => loadApiMonitoring()} disabled={loading}>
          <UniversalIcon icon="📈" size={14} /> {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      <h3 style={{ marginTop: '24px', marginBottom: '12px', fontWeight: '600' }}><UniversalIcon icon="🔄" size={20} /> Conversion Metrics</h3>
      <div className="admin-stats-grid">
        <div className="admin-stat-card metric-success">
          <UniversalIcon icon="✅" size={32} />
          <div className="stat-content">
            <h3>Success Rate</h3>
            <p className="stat-value">{conversionMetrics.successRate || 0}%</p>
            <p className="stat-detail">Last 24 hours</p>
          </div>
        </div>

        <div className="admin-stat-card metric-primary">
          <UniversalIcon icon="⚡" size={32} />
          <div className="stat-content">
            <h3>Avg Processing</h3>
            <p className="stat-value">{conversionMetrics.avgProcessingTime || 0}s</p>
            <p className="stat-detail">Completed conversions</p>
          </div>
        </div>

        <div className="admin-stat-card metric-warning">
          <UniversalIcon icon="⏱️" size={32} />
          <div className="stat-content">
            <h3>Queue Depth</h3>
            <p className="stat-value">{conversionMetrics.queueDepth || 0}</p>
            <p className="stat-detail">Pending worker tasks</p>
          </div>
        </div>
      </div>

      <h3 style={{ marginTop: '24px', marginBottom: '12px', fontWeight: '600' }}><UniversalIcon icon="👥" size={20} /> User Metrics</h3>
      <div className="admin-stats-grid">
        <div className="admin-stat-card metric-info">
          <UniversalIcon icon="🆕" size={32} />
          <div className="stat-content">
            <h3>New Users/Day</h3>
            <p className="stat-value">{userMetrics.newUsersPerDay || 0}</p>
            <p className="stat-detail">Registered in the last 24h</p>
          </div>
        </div>

        <div className="admin-stat-card metric-info">
          <UniversalIcon icon="🟢" size={32} />
          <div className="stat-content">
            <h3>Active Users</h3>
            <p className="stat-value">{userMetrics.activeUsers || 0}</p>
            <p className="stat-detail">Sessions active in 30m</p>
          </div>
        </div>

        <div className="admin-stat-card metric-success">
          <UniversalIcon icon="📊" size={32} />
          <div className="stat-content">
            <h3>30-Day Retention</h3>
            <p className="stat-value">{userMetrics.retention || 0}%</p>
            <p className="stat-detail">Returning eligible users</p>
          </div>
        </div>
      </div>

      <h3 style={{ marginTop: '24px', marginBottom: '12px', fontWeight: '600' }}><UniversalIcon icon="🖥️" size={20} /> Infrastructure Metrics</h3>
      <div className="admin-stats-grid">
        <div className="admin-stat-card metric-danger">
          <UniversalIcon icon="💾" size={32} />
          <div className="stat-content">
            <h3>CPU Usage</h3>
            <p className="stat-value">{infraMetrics.cpuUsage || 0}%</p>
            <p className="stat-detail">Process CPU load</p>
          </div>
        </div>

        <div className="admin-stat-card metric-warning">
          <UniversalIcon icon="🧠" size={32} />
          <div className="stat-content">
            <h3>Memory Usage</h3>
            <p className="stat-value">{infraMetrics.memoryUsage || 0}%</p>
            <p className="stat-detail">Process memory load</p>
          </div>
        </div>

        <div className="admin-stat-card metric-info">
          <UniversalIcon icon="💿" size={32} />
          <div className="stat-content">
            <h3>Disk Usage</h3>
            <p className="stat-value">{infraMetrics.diskUsage || 0}%</p>
            <p className="stat-detail">Application disk usage</p>
          </div>
        </div>
      </div>

      <div className="admin-section-content">
        <h3>Service Endpoints</h3>
        <div className="table-list">
          {(payload.endpoints || []).map((endpoint, idx) => (
            <div key={`endpoint-${idx}-${endpoint.endpoint}`} className="list-item">
              <div className="item-info">
                <p className="item-name">{endpoint.endpoint}</p>
                <p className="item-detail">{endpoint.requests} signal • {endpoint.avgTime}ms avg • {endpoint.errors} issues • {endpoint.detail}</p>
              </div>
              <div className="item-stat">
                <span className="status-badge" style={{ backgroundColor: getStatusColor(endpoint.status), color: 'white' }}>{endpoint.status}</span>
              </div>
            </div>
          ))}
          {!loading && (!payload.endpoints || payload.endpoints.length === 0) && <p>No endpoint telemetry available.</p>}
        </div>
      </div>

      <div className="admin-section-content">
        <h3>API Consumers</h3>
        <div className="jobs-table-wrapper">
          <table className="jobs-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Key Preview</th>
                <th>Plan</th>
                <th>Usage Count</th>
                <th>Last Used</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {(payload.apiKeys || []).map((apiKey) => (
                <tr key={apiKey.id} className={`job-row ${apiKey.status}`}>
                  <td><strong>{apiKey.name}</strong></td>
                  <td><code>{apiKey.keyPreview}</code></td>
                  <td>{apiKey.plan}</td>
                  <td>{apiKey.usageCount}</td>
                  <td className="timestamp">{apiKey.lastUsedAt ? apiKey.lastUsedAt.replace('T', ' ').slice(0, 19) : 'Never'}</td>
                  <td>
                    <span className="status-badge" style={{ backgroundColor: getStatusColor(apiKey.status), color: 'white' }}>
                      {apiKey.status}
                    </span>
                  </td>
                </tr>
              ))}
              {!loading && (!payload.apiKeys || payload.apiKeys.length === 0) && (
                <tr>
                  <td colSpan="6">No API keys have been created yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="admin-section-content">
        <h3>Rate Limit Policies</h3>
        <div className="table-list">
          {(payload.rateLimitPolicies || []).map((policy) => (
            <div key={policy.plan} className="list-item">
              <div className="item-info">
                <p className="item-name">{policy.plan}</p>
                <p className="item-detail">{policy.requestsPerMinute}/min • {policy.requestsPerHour}/hour • {policy.requestsPerDay}/day • {policy.concurrentConversions} concurrent conversions</p>
              </div>
            </div>
          ))}
          {!loading && (!payload.rateLimitPolicies || payload.rateLimitPolicies.length === 0) && <p>No rate limit policies available.</p>}
        </div>
      </div>
    </div>
  )
}

export default APIMonitoring