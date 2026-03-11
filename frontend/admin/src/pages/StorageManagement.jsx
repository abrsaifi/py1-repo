import React, { useState } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import '../styles/admin.css'

const StorageManagement = () => {
  const [stats, setStats] = useState({
    totalStorageUsed: '487.2 GB',
    tempFileCount: 3847,
    avgFileSize: '24.5 MB',
    cleanupSchedule: 'Daily at 2:00 AM'
  })

  const [storageData] = useState([
    { id: 'BUCKET-001', name: 'Uploads', used: '285 GB', files: 12450, lastCleanup: '2026-03-06 02:15', orphans: 123 },
    { id: 'BUCKET-002', name: 'Temporary', used: '98 GB', files: 3847, lastCleanup: '2026-03-06 02:15', orphans: 456 },
    { id: 'BUCKET-003', name: 'Processing', used: '67 GB', files: 2891, lastCleanup: '2026-03-05 22:30', orphans: 234 },
    { id: 'BUCKET-004', name: 'Archives', used: '37.2 GB', files: 1205, lastCleanup: '2026-03-04 14:45', orphans: 12 },
  ])

  const handleManualCleanup = () => {
    alert('Starting manual cleanup of temporary files...')
  }

  const handleDeleteOrphanFiles = () => {
    alert('Scanning and deleting orphaned files...')
  }

  const handleInspectBucket = (bucketName) => {
    alert(`Inspecting storage bucket: ${bucketName}`)
  }

  const getStoragePercentage = (used, total) => {
    const usedNum = parseFloat(used)
    const totalNum = parseFloat(total)
    return Math.round((usedNum / totalNum) * 100)
  }

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="💾" size={24} /> Files & Storage</h2>
      <p className="section-subtitle">Manage temporary files and storage buckets</p>

      <div className="admin-stats-grid">
        <div className="admin-stat-card metric-primary">
          <UniversalIcon icon="💿" size={32} />
          <div className="stat-content">
            <h3>Total Storage Used</h3>
            <p className="stat-value">{stats.totalStorageUsed}</p>
            <p className="stat-detail">1.2 TB available</p>
          </div>
        </div>

        <div className="admin-stat-card metric-warning">
          <UniversalIcon icon="📋" size={32} />
          <div className="stat-content">
            <h3>Temporary File Count</h3>
            <p className="stat-value">{stats.tempFileCount}</p>
            <p className="stat-detail">Pending cleanup</p>
          </div>
        </div>

        <div className="admin-stat-card metric-info">
          <UniversalIcon icon="📊" size={32} />
          <div className="stat-content">
            <h3>Average File Size</h3>
            <p className="stat-value">{stats.avgFileSize}</p>
            <p className="stat-detail">Mean across all files</p>
          </div>
        </div>

        <div className="admin-stat-card metric-success">
          <UniversalIcon icon="📅" size={32} />
          <div className="stat-content">
            <h3>Storage Cleanup Schedule</h3>
            <p className="stat-value">{stats.cleanupSchedule}</p>
            <p className="stat-detail">Automatic cleanup</p>
          </div>
        </div>
      </div>

      <div className="quick-actions" style={{ marginTop: '30px', marginBottom: '30px' }}>
        <button className="action-button primary" onClick={handleManualCleanup} title="Run cleanup now">
          <UniversalIcon icon="🧹" size={14} /> Manual Cleanup
        </button>
        <button className="action-button primary" onClick={handleDeleteOrphanFiles} title="Delete orphaned files">
          <UniversalIcon icon="🗑️" size={14} /> Delete Orphan Files
        </button>
      </div>

      <div className="admin-section-content">
        <h3>Storage Buckets</h3>

        <div className="jobs-table-wrapper">
          <table className="jobs-table">
            <thead>
              <tr>
                <th>Bucket ID</th>
                <th>Bucket Name</th>
                <th>Used Space</th>
                <th>File Count</th>
                <th>Orphaned Files</th>
                <th>Last Cleanup</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {storageData.map(bucket => {
                const percentage = getStoragePercentage(bucket.used, '1024')
                return (
                  <tr key={bucket.id} className="job-row">
                    <td className="job-id"><code>{bucket.id}</code></td>
                    <td><strong>{bucket.name}</strong></td>
                    <td>
                      <span className="format-badge" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
                        {bucket.used}
                      </span>
                    </td>
                    <td><strong>{bucket.files.toLocaleString()}</strong></td>
                    <td>
                      {bucket.orphans > 0 ? (
                        <span className="status-badge" style={{ backgroundColor: '#f97316', color: 'white' }}>
                          <UniversalIcon icon="⚠️" size={14} /> {bucket.orphans}
                        </span>
                      ) : (
                        <span style={{ color: '#11998e', fontWeight: '600' }}><UniversalIcon icon="✓" size={14} /> 0</span>
                      )}
                    </td>
                    <td className="timestamp">{bucket.lastCleanup}</td>
                    <td className="actions">
                      <button 
                        className="action-btn logs" 
                        onClick={() => handleInspectBucket(bucket.name)} 
                        title="Inspect Bucket"
                      >
                        <UniversalIcon icon="🔍" size={14} />
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {storageData.length === 0 && (
          <div className="no-data">
            <p>No storage buckets available</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default StorageManagement
