import React, { useState } from 'react'
import { UniversalIcon } from '../utils/UniversalIcon'
import '../styles/admin.css'

const APIMonitoring = () => {
  // CONVERSION METRICS
  const [conversionMetrics] = useState({
    successRate: 98.2,
    avgProcessingTime: 2.3,
    queueDelay: 1.8
  })

  // USER METRICS
  const [userMetrics] = useState({
    newUsersPerDay: 47,
    activeUsers: 234,
    retention: 87.3
  })

  // INFRASTRUCTURE METRICS
  const [infraMetrics] = useState({
    cpuUsage: 62,
    memoryUsage: 48,
    diskIO: 34
  })

  const [stats] = useState({
    totalRequests: 45230,
    avgResponseTime: 145,
    errorRate: 0.85,
    rateLimitViolations: 12
  })

  const [endpoints] = useState([
    { endpoint: '/api/convert', requests: 12450, avgTime: 120, errors: 2, status: 'healthy' },
    { endpoint: '/api/batch-convert', requests: 8340, avgTime: 180, errors: 1, status: 'healthy' },
    { endpoint: '/api/upload', requests: 5600, avgTime: 85, errors: 0, status: 'healthy' },
    { endpoint: '/api/analytics', requests: 18840, avgTime: 45, errors: 12, status: 'warning' }
  ])

  const [rateLimits] = useState([
    { ip: '192.168.1.100', requests: 5000, limit: 1000, status: 'blocked' },
    { ip: '203.45.67.89', requests: 450, limit: 1000, status: 'warning' },
    { ip: '105.23.12.45', requests: 890, limit: 1000, status: 'healthy' }
  ])

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="📈" size={24} /> Advanced Analytics Metrics</h2>
      <p className="section-subtitle">Comprehensive conversion, user, and infrastructure tracking</p>

      {/* CONVERSION METRICS SECTION */}
      <h3 style={{ marginTop: '24px', marginBottom: '12px', fontWeight: '600' }}><UniversalIcon icon="🔄" size={20} /> Conversion Metrics</h3>
      <div className="admin-stats-grid">
        <div className="admin-stat-card metric-success">
          <UniversalIcon icon="✅" size={32} />
          <div className="stat-content">
            <h3>Success Rate</h3>
            <p className="stat-value">{conversionMetrics.successRate}%</p>
            <p className="stat-detail">Successful conversions</p>
          </div>
        </div>

        <div className="admin-stat-card metric-primary">
          <UniversalIcon icon="⚡" size={32} />
          <div className="stat-content">
            <h3>Avg Processing</h3>
            <p className="stat-value">{conversionMetrics.avgProcessingTime}s</p>
            <p className="stat-detail">Average time per job</p>
          </div>
        </div>

        <div className="admin-stat-card metric-warning">
          <UniversalIcon icon="⏱️" size={32} />
          <div className="stat-content">
            <h3>Queue Delay</h3>
            <p className="stat-value">{conversionMetrics.queueDelay}s</p>
            <p className="stat-detail">Average wait time</p>
          </div>
        </div>
      </div>

      {/* USER METRICS SECTION */}
      <h3 style={{ marginTop: '24px', marginBottom: '12px', fontWeight: '600' }}><UniversalIcon icon="👥" size={20} /> User Metrics</h3>
      <div className="admin-stats-grid">
        <div className="admin-stat-card metric-info">
          <UniversalIcon icon="🆕" size={32} />
          <div className="stat-content">
            <h3>New Users/Day</h3>
            <p className="stat-value">{userMetrics.newUsersPerDay}</p>
            <p className="stat-detail">Daily signups</p>
          </div>
        </div>

        <div className="admin-stat-card metric-info">
          <UniversalIcon icon="🟢" size={32} />
          <div className="stat-content">
            <h3>Active Users</h3>
            <p className="stat-value">{userMetrics.activeUsers}</p>
            <p className="stat-detail">Currently active</p>
          </div>
        </div>

        <div className="admin-stat-card metric-success">
          <UniversalIcon icon="📊" size={32} />
          <div className="stat-content">
            <h3>Retention Rate</h3>
            <p className="stat-value">{userMetrics.retention}%</p>
            <p className="stat-detail">30-day retention</p>
          </div>
        </div>
      </div>

      {/* INFRASTRUCTURE METRICS SECTION */}
      <h3 style={{ marginTop: '24px', marginBottom: '12px', fontWeight: '600' }}><UniversalIcon icon="🖥️" size={20} /> Infrastructure Metrics</h3>
      <div className="admin-stats-grid">
        <div className="admin-stat-card metric-danger">
          <UniversalIcon icon="💾" size={32} />
          <div className="stat-content">
            <h3>CPU Usage</h3>
            <p className="stat-value">{infraMetrics.cpuUsage}%</p>
            <p className="stat-detail">Active processing</p>
          </div>
        </div>

        <div className="admin-stat-card metric-warning">
          <UniversalIcon icon="🧠" size={32} />
          <div className="stat-content">
            <h3>Memory Usage</h3>
            <p className="stat-value">{infraMetrics.memoryUsage}%</p>
            <p className="stat-detail">RAM utilization</p>
          </div>
        </div>

        <div className="admin-stat-card metric-info">
          <UniversalIcon icon="💿" size={32} />
          <div className="stat-content">
            <h3>Disk I/O</h3>
            <p className="stat-value">{infraMetrics.diskIO}%</p>
            <p className="stat-detail">I/O operations</p>
          </div>
        </div>
      </div>

      <div className="admin-section-content">
        <h3>Endpoint Performance</h3>
        <div className="table-list">
          {endpoints.map((endpoint, idx) => (
            <div key={idx} className="list-item">
              <div className="item-info">
                <p className="item-name">{endpoint.endpoint}</p>
                <p className="item-detail">{endpoint.requests.toLocaleString()} requests • {endpoint.avgTime}ms avg • {endpoint.errors} errors</p>
              </div>
              <div className="item-stat">
                <span className={`status-badge status-${endpoint.status}`}>{endpoint.status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="admin-section-content">
        <h3>Rate Limit Violations</h3>
        <div className="table-list">
          {rateLimits.map((item, idx) => (
            <div key={idx} className="list-item">
              <div className="item-info">
                <p className="item-name">{item.ip}</p>
                <p className="item-detail">{item.requests} requests (limit: {item.limit})</p>
              </div>
              <div className="item-stat">
                <span className={`status-badge status-${item.status}`}>{item.status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default APIMonitoring
