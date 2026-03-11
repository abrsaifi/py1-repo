import React, { useState, useEffect } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'

const SystemMonitoring = () => {
  const [metrics, setMetrics] = useState({
    cpuUsage: 35,
    memoryUsage: 62,
    diskUsage: 45,
    apiResponseTime: 145,
    activeUsers: 28,
    requestsPerSecond: 42,
    errorRate: 0.5,
    uptime: 99.98
  })

  const [systemStatus, setSystemStatus] = useState({
    database: 'healthy',
    api: 'healthy',
    cache: 'healthy',
    storage: 'healthy'
  })

  const [alerts, setAlerts] = useState([
    { id: 1, type: 'warning', message: 'Memory usage exceeded 60%', time: '5 minutes ago' },
    { id: 2, type: 'info', message: 'Scheduled backup completed successfully', time: '2 hours ago' },
    { id: 3, type: 'error', message: 'API endpoint /reports experiencing slow response times', time: '1 hour ago' }
  ])

  useEffect(() => {
    const interval = setInterval(() => {
      updateMetrics()
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  const updateMetrics = () => {
    setMetrics(prev => ({
      ...prev,
      cpuUsage: Math.max(20, Math.min(80, prev.cpuUsage + (Math.random() - 0.5) * 10)),
      memoryUsage: Math.max(40, Math.min(90, prev.memoryUsage + (Math.random() - 0.5) * 5)),
      diskUsage: Math.max(30, Math.min(70, prev.diskUsage + (Math.random() - 0.5) * 3)),
      apiResponseTime: Math.max(100, Math.min(500, prev.apiResponseTime + (Math.random() - 0.5) * 50)),
      requestsPerSecond: Math.max(30, Math.min(100, prev.requestsPerSecond + (Math.random() - 0.5) * 20)),
      errorRate: Math.max(0, Math.min(5, prev.errorRate + (Math.random() - 0.5) * 1))
    }))
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
      case 'warning':
        return '#ff9800'
      case 'critical':
        return '#f44336'
      default:
        return '#9e9e9e'
    }
  }

  const dismissAlert = (id) => {
    setAlerts(alerts.filter(alert => alert.id !== id))
  }

  return (
    <div className="system-monitoring">
      <div className="management-header">
        <h2><UniversalIcon icon="📡" size={24} /> System Monitoring</h2>
        <div className="header-actions">
          <span className="refresh-indicator"><UniversalIcon icon="🜢" size={14} /> Live</span>
        </div>
      </div>

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
          <div className="metric-value">{metrics.uptime.toFixed(2)}%</div>
          <p className="metric-detail">Last 30 days</p>
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
                <p className="status-text">{status.charAt(0).toUpperCase() + status.slice(1)}</p>
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
                  <p className="alert-time">{alert.time}</p>
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
