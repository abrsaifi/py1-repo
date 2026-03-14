import React, { useState, useEffect } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'

const SystemMonitoring = () => {
  const [metrics, setMetrics] = useState({
    cpuUsage: 0,
    memoryUsage: 0,
    diskUsage: 0,
    apiResponseTime: 0,
    activeUsers: 0,
    requestsPerSecond: 0,
    errorRate: 0,
    uptimeSeconds: 0,
  })

  const [systemStatus, setSystemStatus] = useState({
    database: 'unknown',
    api: 'unknown',
    cache: 'unknown',
    workers: 'unknown',
    storage: 'unknown'
  })

  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [lastUpdated, setLastUpdated] = useState('')

  useEffect(() => {
    loadSystemHealth()
    const interval = setInterval(() => {
      loadSystemHealth()
    }, 15000)
    return () => clearInterval(interval)
  }, [])

  const loadSystemHealth = async () => {
    try {
      setError('')
      const response = await fetch('/api/admin/health', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` },
      })

      const payload = await response.json().catch(() => ({}))
      if (!response.ok) {
        throw new Error(payload.error || 'Failed to load system health')
      }

      setMetrics({
        cpuUsage: Number(payload.metrics?.cpuUsage || 0),
        memoryUsage: Number(payload.metrics?.memoryUsage || 0),
        diskUsage: Number(payload.metrics?.diskUsage || 0),
        apiResponseTime: Number(payload.metrics?.apiResponseTime || 0),
        activeUsers: Number(payload.metrics?.activeUsers || 0),
        requestsPerSecond: Number(payload.metrics?.requestsPerSecond || 0),
        errorRate: Number(payload.metrics?.errorRate || 0),
        uptimeSeconds: Number(payload.metrics?.uptimeSeconds || 0),
      })
      setSystemStatus({
        database: payload.components?.database?.status || 'unknown',
        api: payload.components?.api?.status || 'unknown',
        cache: payload.components?.cache?.status || 'unknown',
        workers: payload.components?.workers?.status || 'unknown',
        storage: payload.components?.storage?.status || 'unknown',
      })
      setAlerts(payload.alerts || [])
      setLastUpdated(payload.timestamp || '')
    } catch (loadError) {
      console.error('Failed to load system health:', loadError)
      setError(loadError.message || 'Failed to load system health')
    } finally {
      setLoading(false)
    }
  }

  const getHealthStatus = (value, thresholds) => {
    if (value > thresholds.critical) return 'critical'
    if (value > thresholds.warning) return 'warning'
    return 'healthy'
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return '#4caf50'
      case 'degraded':
      case 'warning':
      case 'unknown':
      case 'not_configured':
        return '#ff9800'
      case 'offline':
      case 'unhealthy':
      case 'critical':
        return '#f44336'
      default:
        return '#9e9e9e'
    }
  }

  const dismissAlert = (id) => {
    setAlerts(alerts.filter(alert => alert.id !== id))
  }

  const formatUptime = (uptimeSeconds) => {
    const totalSeconds = Number(uptimeSeconds || 0)
    const days = Math.floor(totalSeconds / 86400)
    const hours = Math.floor((totalSeconds % 86400) / 3600)
    const minutes = Math.floor((totalSeconds % 3600) / 60)
    if (days > 0) return `${days}d ${hours}h`
    if (hours > 0) return `${hours}h ${minutes}m`
    return `${minutes}m`
  }

  return (
    <div className="system-monitoring">
      <div className="management-header">
        <h2><UniversalIcon icon="📡" size={24} /> System Monitoring</h2>
        <div className="header-actions">
          <span className="refresh-indicator"><UniversalIcon icon="🜢" size={14} /> {loading ? 'Loading' : 'Live'}</span>
        </div>
      </div>

      {error ? (
        <div className="no-data" style={{ marginBottom: '20px', border: '1px solid #fed7d7', background: '#fff5f5', color: '#c53030' }}>
          <p>{error}</p>
        </div>
      ) : null}

      {lastUpdated ? (
        <p className="section-subtitle" style={{ marginTop: '-6px' }}>Last updated: {lastUpdated.replace('T', ' ').slice(0, 19)}</p>
      ) : null}

      <div className="monitoring-grid">
        <div className="metric-card">
          <h4>CPU Usage</h4>
          <div className="metric-value">{metrics.cpuUsage.toFixed(1)}%</div>
          <div className="metric-bar">
            <div
              className="bar-fill"
              style={{
                width: `${metrics.cpuUsage}%`,
                backgroundColor: getStatusColor(
                  getHealthStatus(metrics.cpuUsage, { warning: 70, critical: 90 })
                )
              }}
            />
          </div>
          <p className="metric-status">
            {getHealthStatus(metrics.cpuUsage, { warning: 70, critical: 90 }) === 'healthy' ? <><UniversalIcon icon="✓" size={14} /> Normal</> : <><UniversalIcon icon="⚠️" size={14} /> High</>}
          </p>
        </div>

        <div className="metric-card">
          <h4>Memory Usage</h4>
          <div className="metric-value">{metrics.memoryUsage.toFixed(1)}%</div>
          <div className="metric-bar">
            <div
              className="bar-fill"
              style={{
                width: `${metrics.memoryUsage}%`,
                backgroundColor: getStatusColor(
                  getHealthStatus(metrics.memoryUsage, { warning: 75, critical: 90 })
                )
              }}
            />
          </div>
          <p className="metric-status">
            {getHealthStatus(metrics.memoryUsage, { warning: 75, critical: 90 }) === 'healthy' ? <><UniversalIcon icon="✓" size={14} /> Normal</> : <><UniversalIcon icon="⚠️" size={14} /> High</>}
          </p>
        </div>

        <div className="metric-card">
          <h4>Disk Usage</h4>
          <div className="metric-value">{metrics.diskUsage.toFixed(1)}%</div>
          <div className="metric-bar">
            <div
              className="bar-fill"
              style={{
                width: `${metrics.diskUsage}%`,
                backgroundColor: getStatusColor(
                  getHealthStatus(metrics.diskUsage, { warning: 80, critical: 95 })
                )
              }}
            />
          </div>
          <p className="metric-status">
            {getHealthStatus(metrics.diskUsage, { warning: 80, critical: 95 }) === 'healthy' ? <><UniversalIcon icon="✓" size={14} /> Normal</> : <><UniversalIcon icon="⚠️" size={14} /> High</>}
          </p>
        </div>

        <div className="metric-card">
          <h4>API Response Time</h4>
          <div className="metric-value">{metrics.apiResponseTime.toFixed(0)}ms</div>
          <div className="metric-bar">
            <div
              className="bar-fill"
              style={{
                width: `${Math.min(100, (metrics.apiResponseTime / 500) * 100)}%`,
                backgroundColor: getStatusColor(
                  getHealthStatus(metrics.apiResponseTime, { warning: 300, critical: 500 })
                )
              }}
            />
          </div>
          <p className="metric-status">
            {getHealthStatus(metrics.apiResponseTime, { warning: 300, critical: 500 }) === 'healthy' ? <><UniversalIcon icon="✓" size={14} /> Fast</> : <><UniversalIcon icon="⚠️" size={14} /> Slow</>}
          </p>
        </div>

        <div className="metric-card">
          <h4>Active Users</h4>
          <div className="metric-value">{metrics.activeUsers}</div>
          <p className="metric-detail">Currently connected</p>
        </div>

        <div className="metric-card">
          <h4>Requests/Second</h4>
          <div className="metric-value">{metrics.requestsPerSecond.toFixed(1)}</div>
          <p className="metric-detail">Average throughput</p>
        </div>

        <div className="metric-card">
          <h4>Error Rate</h4>
          <div className="metric-value">{metrics.errorRate.toFixed(2)}%</div>
          <div className="metric-bar">
            <div
              className="bar-fill"
              style={{
                width: `${Math.min(100, metrics.errorRate * 20)}%`,
                backgroundColor: getStatusColor(
                  getHealthStatus(metrics.errorRate, { warning: 1, critical: 5 })
                )
              }}
            />
          </div>
          <p className="metric-status">
            {getHealthStatus(metrics.errorRate, { warning: 1, critical: 5 }) === 'healthy' ? <><UniversalIcon icon="✓" size={14} /> Healthy</> : <><UniversalIcon icon="⚠️" size={14} /> Errors</>}
          </p>
        </div>

        <div className="metric-card">
          <h4>System Uptime</h4>
          <div className="metric-value">{formatUptime(metrics.uptimeSeconds)}</div>
          <p className="metric-detail">Process uptime</p>
        </div>
      </div>

      <div className="monitoring-section">
        <h3>Service Status</h3>
        <div className="services-grid">
          {Object.entries(systemStatus).map(([service, status]) => (
            <div key={service} className="service-card">
              <div
                className="status-indicator"
                style={{ backgroundColor: getStatusColor(status) }}
              />
              <div className="service-info">
                <h5>{service.charAt(0).toUpperCase() + service.slice(1)}</h5>
                <p className="status-text">{status.replace('_', ' ')}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="monitoring-section">
        <h3>System Alerts</h3>
        <div className="alerts-list">
          {alerts.length > 0 ? (
            alerts.map(alert => (
              <div key={alert.id} className={`alert-item alert-${alert.type}`}>
                <div className="alert-icon">
                  {alert.type === 'error' && <UniversalIcon icon="❌" size={16} />}
                  {alert.type === 'warning' && <UniversalIcon icon="⚠️" size={16} />}
                  {alert.type === 'info' && <UniversalIcon icon="ℹ" size={16} />}
                </div>
                <div className="alert-content">
                  <p className="alert-message">{alert.message}</p>
                  <p className="alert-time">{String(alert.time || '').replace('T', ' ').slice(0, 19)}</p>
                </div>
                <button
                  className="alert-close"
                  onClick={() => dismissAlert(alert.id)}
                >
                  ×
                </button>
              </div>
            ))
          ) : (
            <p className="no-alerts"><UniversalIcon icon="✓" size={14} /> No active alerts</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default SystemMonitoring
