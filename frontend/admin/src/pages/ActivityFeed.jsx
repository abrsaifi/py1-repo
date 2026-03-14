import React, { useEffect, useState } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import { adminAPI } from '@shared/api/api'

const ActivityFeed = () => {
  const [activities, setActivities] = useState([])
  const [stats, setStats] = useState({ today: 0, critical: 0, warnings: 0 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [expandedId, setExpandedId] = useState(null)

  useEffect(() => {
    loadActivities()
    const interval = setInterval(loadActivities, 10000)
    return () => clearInterval(interval)
  }, [])

  const loadActivities = async () => {
    try {
      setError('')
      const response = await adminAPI.getActivityFeed({ limit: 75, period_days: 30 })
      setActivities(response.data.entries || [])
      setStats(response.data.stats || { today: 0, critical: 0, warnings: 0 })
    } catch (loadError) {
      setError(loadError.response?.data?.error || 'Failed to load activity feed')
    } finally {
      setLoading(false)
    }
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
          <span className="badge-value">{stats.today || 0}</span>
        </div>
        <div className="stat-badge">
          <span>Critical Events</span>
          <span className="badge-value" style={{ color: '#d32f2f' }}>
            {stats.critical || 0}
          </span>
        </div>
        <div className="stat-badge">
          <span>Warnings</span>
          <span className="badge-value" style={{ color: '#f57c00' }}>
            {stats.warnings || 0}
          </span>
        </div>
      </div>

      {error && (
        <div className="no-activities">
          <p><UniversalIcon icon="⚠️" size={16} /> {error}</p>
        </div>
      )}

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
        {loading ? (
          <div className="no-activities">
            <p><UniversalIcon icon="⏳" size={16} /> Loading activity feed...</p>
          </div>
        ) : filteredActivities.length > 0 ? (
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
                  <h4 className="activity-action">{activity.action.replace(/-/g, ' ')}</h4>
                  <span className="activity-time">{formatTimestamp(activity.timestamp)}</span>
                </div>

                <div className="activity-details">
                  <span className="activity-user"><UniversalIcon icon="👤" size={14} /> {activity.userName || activity.userId || 'system'}</span>
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
        <p>Showing {filteredActivities.length} live backend events • Auto-refreshing every 10 seconds</p>
      </div>
    </div>
  )
}

export default ActivityFeed
