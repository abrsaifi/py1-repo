import React, { useState, useEffect } from 'react'
import { UniversalIcon } from '../utils/UniversalIcon'
import { useAuditLogger } from '../services/auditLogger'

const ActivityFeed = () => {
  const { getLogs } = useAuditLogger()
  const [activities, setActivities] = useState([])
  const [filterType, setFilterType] = useState('all')
  const [expandedId, setExpandedId] = useState(null)

  useEffect(() => {
    loadActivities()
    // Refresh every 10 seconds
    const interval = setInterval(loadActivities, 10000)
    return () => clearInterval(interval)
  }, [])

  const loadActivities = () => {
    const logs = getLogs({
      limit: 50,
      sortBy: 'timestamp',
      sortOrder: 'desc'
    })
    setActivities(logs)
  }

  const getActivityIcon = (action) => {
    if (action.includes('login')) return '🔓'
    if (action.includes('logout')) return '🔒'
    if (action.includes('created')) return '✨'
    if (action.includes('updated')) return '✏️'
    if (action.includes('deleted')) return '🗑️'
    if (action.includes('report')) return '📊'
    if (action.includes('exported')) return '📥'
    if (action.includes('access-denied')) return '🚫'
    if (action.includes('error')) return '❌'
    return '📌'
  }

  const getActivityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return '#d32f2f'
      case 'warning':
        return '#f57c00'
      case 'info':
        return '#1976d2'
      default:
        return '#388e3c'
    }
  }

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMinutes = Math.floor((now - date) / 60000)

    if (diffMinutes < 1) return 'Just now'
    if (diffMinutes < 60) return `${diffMinutes}m ago`
    if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)}h ago`
    return date.toLocaleDateString()
  }

  const filteredActivities = filterType === 'all'
    ? activities
    : activities.filter(a => a.severity === filterType)

  const activityStats = {
    today: activities.filter(a => {
      const aDate = new Date(a.timestamp).toDateString()
      const today = new Date().toDateString()
      return aDate === today
    }).length,
    critical: activities.filter(a => a.severity === 'critical').length,
    warnings: activities.filter(a => a.severity === 'warning').length
  }

  return (
    <div className="activity-feed">
      <div className="management-header">
        <h2><UniversalIcon icon="📋" size={24} /> Activity Feed</h2>
        <div className="refresh-indicator">
          <span className="pulse"><UniversalIcon icon="🜢" size={14} /></span> Live Updates
        </div>
      </div>

      <div className="activity-stats">
        <div className="stat-badge">
          <span>Activities Today</span>
          <span className="badge-value">{activityStats.today}</span>
        </div>
        <div className="stat-badge">
          <span>Critical Events</span>
          <span className="badge-value" style={{ color: '#d32f2f' }}>
            {activityStats.critical}
          </span>
        </div>
        <div className="stat-badge">
          <span>Warnings</span>
          <span className="badge-value" style={{ color: '#f57c00' }}>
            {activityStats.warnings}
          </span>
        </div>
      </div>

      <div className="filter-tabs">
        <button
          className={`filter-tab ${filterType === 'all' ? 'active' : ''}`}
          onClick={() => setFilterType('all')}
        >
          All Activities
        </button>
        <button
          className={`filter-tab ${filterType === 'critical' ? 'active' : ''}`}
          onClick={() => setFilterType('critical')}
        >
          Critical
        </button>
        <button
          className={`filter-tab ${filterType === 'warning' ? 'active' : ''}`}
          onClick={() => setFilterType('warning')}
        >
          Warnings
        </button>
        <button
          className={`filter-tab ${filterType === 'info' ? 'active' : ''}`}
          onClick={() => setFilterType('info')}
        >
          Info
        </button>
      </div>

      <div className="activity-list">
        {filteredActivities.length > 0 ? (
          filteredActivities.map(activity => (
            <div
              key={activity.id}
              className={`activity-item severity-${activity.severity}`}
            >
              <div className="activity-marker" />
              
              <div className="activity-icon">
                {getActivityIcon(activity.action)}
              </div>

              <div className="activity-content">
                <div className="activity-header">
                  <h4 className="activity-action">{activity.action}</h4>
                  <span className="activity-time">{formatTimestamp(activity.timestamp)}</span>
                </div>

                <div className="activity-details">
                  <span className="activity-user"><UniversalIcon icon="👤" size={14} /> {activity.userId}</span>
                  {activity.resourceName && (
                    <span className="activity-resource"><UniversalIcon icon="📦" size={14} /> {activity.resourceName}</span>
                  )}
                  <span
                    className="activity-severity"
                    style={{ backgroundColor: getActivityColor(activity.severity) }}
                  >
                    {activity.severity}
                  </span>
                  <span className={`activity-status status-${activity.status}`}>
                    {activity.status}
                  </span>
                </div>

                {activity.details && (
                  <button
                    className="expand-details"
                    onClick={() => setExpandedId(expandedId === activity.id ? null : activity.id)}
                  >
                    {expandedId === activity.id ? <><UniversalIcon icon="▼" size={14} /> Hide Details</> : <><UniversalIcon icon="▶" size={14} /> Show Details</>}
                  </button>
                )}

                {expandedId === activity.id && (
                  <div className="activity-expanded">
                    <pre>{JSON.stringify(activity, null, 2)}</pre>
                  </div>
                )}
              </div>

              {activity.ipAddress && (
                <div className="activity-ip">
                  <span title={activity.ipAddress}><UniversalIcon icon="🌐" size={14} /></span>
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="no-activities">
            <p><UniversalIcon icon="📭" size={16} /> No activities found</p>
          </div>
        )}
      </div>

      <div className="activity-footer">
        <p>Showing {filteredActivities.length} activities • Auto-refreshing every 10 seconds</p>
      </div>
    </div>
  )
}

export default ActivityFeed
