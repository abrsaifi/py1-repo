import React, { useEffect, useState } from 'react'
import { adminAPI } from '@shared/api/api'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import '../styles/admin.css'

const StorageManagement = () => {
  const [payload, setPayload] = useState({
    stats: {
      totalStorageUsed: '0 B',
      tempFileCount: 0,
      avgFileSize: '0 B',
      cleanupSchedule: 'Not configured',
    },
    buckets: [],
  })
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [lastUpdated, setLastUpdated] = useState('')

  useEffect(() => {
    loadStorageOverview()
  }, [])

  const loadStorageOverview = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await adminAPI.getStorageOverview()
      setPayload(response.data || { stats: {}, buckets: [] })
      setLastUpdated(response.data?.generatedAt || '')
    } catch (err) {
      console.error('Failed to load storage overview:', err)
      setError(err.message || 'Failed to load storage overview')
    } finally {
      setLoading(false)
    }
  }

  const handleManualCleanup = async () => {
    try {
      setActionLoading('cleanup')
      setMessage('')
      const response = await adminAPI.cleanupStorageUploads({})
      setMessage(response.data?.message || 'Cleanup completed.')
      await loadStorageOverview()
    } catch (err) {
      console.error('Failed to clean upload staging:', err)
      setError(err.message || 'Failed to clean upload staging')
    } finally {
      setActionLoading('')
    }
  }

  const handleReconcileStorage = async () => {
    try {
      setActionLoading('reconcile')
      setMessage('')
      const response = await adminAPI.reconcileStorageReferences()
      setMessage(response.data?.message || 'Storage reconciliation completed.')
      await loadStorageOverview()
    } catch (err) {
      console.error('Failed to reconcile storage references:', err)
      setError(err.message || 'Failed to reconcile storage references')
    } finally {
      setActionLoading('')
    }
  }

  const stats = payload.stats || {}

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="💾" size={24} /> Files & Storage</h2>
      <p className="section-subtitle">
        Live storage usage and cleanup controls
        {lastUpdated ? ` • Last updated ${lastUpdated.replace('T', ' ').slice(0, 19)}` : ''}
      </p>

      {error && <div className="alert-banner error">{error}</div>}
      {message && <div className="alert-banner success">{message}</div>}

      <div className="admin-stats-grid">
        <div className="admin-stat-card metric-primary">
          <UniversalIcon icon="💿" size={32} />
          <div className="stat-content">
            <h3>Total Storage Used</h3>
            <p className="stat-value">{stats.totalStorageUsed || '0 B'}</p>
            <p className="stat-detail">Tracked application storage</p>
          </div>
        </div>

        <div className="admin-stat-card metric-warning">
          <UniversalIcon icon="📋" size={32} />
          <div className="stat-content">
            <h3>Upload Staging Files</h3>
            <p className="stat-value">{stats.tempFileCount || 0}</p>
            <p className="stat-detail">Chunked upload artifacts</p>
          </div>
        </div>

        <div className="admin-stat-card metric-info">
          <UniversalIcon icon="📊" size={32} />
          <div className="stat-content">
            <h3>Average File Size</h3>
            <p className="stat-value">{stats.avgFileSize || '0 B'}</p>
            <p className="stat-detail">Across tracked files</p>
          </div>
        </div>

        <div className="admin-stat-card metric-success">
          <UniversalIcon icon="📅" size={32} />
          <div className="stat-content">
            <h3>Cleanup Schedule</h3>
            <p className="stat-value">{stats.cleanupSchedule || 'Not configured'}</p>
            <p className="stat-detail">Upload staging retention</p>
          </div>
        </div>
      </div>

      <div className="quick-actions" style={{ marginTop: '30px', marginBottom: '30px' }}>
        <button className="action-button primary" onClick={handleManualCleanup} disabled={actionLoading === 'cleanup' || loading} title="Purge stale upload staging directories">
          <UniversalIcon icon="🧹" size={14} /> {actionLoading === 'cleanup' ? 'Cleaning...' : 'Cleanup Upload Staging'}
        </button>
        <button className="action-button primary" onClick={handleReconcileStorage} disabled={actionLoading === 'reconcile' || loading} title="Clear stale conversion file references">
          <UniversalIcon icon="🗑️" size={14} /> {actionLoading === 'reconcile' ? 'Reconciling...' : 'Clear Stale References'}
        </button>
        <button className="action-button primary" onClick={loadStorageOverview} disabled={loading} title="Refresh storage metrics">
          <UniversalIcon icon="🔄" size={14} /> {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      <div className="admin-section-content">
        <h3>Storage Areas</h3>

        <div className="jobs-table-wrapper">
          <table className="jobs-table">
            <thead>
              <tr>
                <th>Area ID</th>
                <th>Name</th>
                <th>Used Space</th>
                <th>File Count</th>
                <th>Stale Records</th>
                <th>Cleanup Candidates</th>
                <th>Last Updated</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {(payload.buckets || []).map((bucket) => (
                <tr key={bucket.id} className={`job-row ${bucket.status}`}>
                  <td className="job-id"><code>{bucket.id}</code></td>
                  <td>
                    <strong>{bucket.name}</strong>
                    <div className="timestamp">{bucket.path || 'Path unavailable'}</div>
                  </td>
                  <td>
                    <span className="format-badge" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
                      {bucket.usedLabel}
                    </span>
                  </td>
                  <td><strong>{bucket.files}</strong></td>
                  <td>{bucket.orphaned}</td>
                  <td>{bucket.cleanupCandidates}</td>
                  <td className="timestamp">{bucket.lastUpdated ? bucket.lastUpdated.replace('T', ' ').slice(0, 19) : 'No activity'}</td>
                  <td>
                    <span className="status-badge" style={{ backgroundColor: bucket.status === 'healthy' ? '#11998e' : '#f6ad55', color: 'white' }}>
                      {bucket.status}
                    </span>
                  </td>
                </tr>
              ))}
              {!loading && (!payload.buckets || payload.buckets.length === 0) && (
                <tr>
                  <td colSpan="8">No storage areas available</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default StorageManagement