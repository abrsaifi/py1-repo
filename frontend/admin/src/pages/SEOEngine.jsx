import React, { useState } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import '../styles/admin.css'

const SEOEngine = () => {
  const [stats, setStats] = useState({
    totalPages: 342,
    indexedPages: 289,
    pendingPages: 53,
    publishingSchedule: '24/7 Auto',
    keywordExpansion: '94%'
  })

  const [pages, setPages] = useState([
    { id: 'PAGE-001', title: 'PDF to Word Converter', status: 'indexed', indexed: '2026-02-15', keywords: 45, traffic: 3240, nextUpdate: '2026-03-13' },
    { id: 'PAGE-002', title: 'Image to PDF Converter', status: 'indexed', indexed: '2026-02-10', keywords: 32, traffic: 1892, nextUpdate: '2026-03-10' },
    { id: 'PAGE-003', title: 'Excel to CSV Converter', status: 'indexed', indexed: '2026-01-28', keywords: 28, traffic: 1456, nextUpdate: '2026-02-25' },
    { id: 'PAGE-004', title: 'Document Converter Guide', status: 'pending', indexed: null, keywords: 18, traffic: 0, nextUpdate: '2026-03-12' },
    { id: 'PAGE-005', title: 'Video Compression Tool', status: 'pending', indexed: null, keywords: 22, traffic: 0, nextUpdate: '2026-03-08' },
  ])

  const handleGeneratePages = () => {
    alert('Generating new SEO pages...')
    setStats(prev => ({ ...prev, totalPages: prev.totalPages + 5, pendingPages: prev.pendingPages + 5 }))
  }

  const handleSubmitSitemap = () => {
    alert('Submitting sitemap to Google, Bing, and other search engines...')
  }

  const handleReindexPages = () => {
    alert('Reindexing all pages in search engines...')
  }

  const getStatusBadge = (status) => {
    const badges = {
      indexed: { color: '#11998e', text: '✅ Indexed' },
      indexing: { color: '#4099ff', text: '⏳ Indexing' },
      pending: { color: '#fa709a', text: '📋 Pending' }
    }
    return badges[status] || badges.pending
  }

  const getStatusRowColor = (status) => {
    const colors = {
      indexed: 'indexed',
      indexing: 'processing', 
      pending: 'failed'
    }
    return colors[status] || 'pending'
  }

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="🔍" size={24} /> SEO Engine</h2>
      <p className="section-subtitle">Control your SEO page generator system - Manages 300+ landing pages</p>

      <div className="admin-stats-grid">
        <div className="admin-stat-card metric-primary">
          <UniversalIcon icon="📄" size={32} />
          <div className="stat-content">
            <h3>Total SEO Pages</h3>
            <p className="stat-value">{stats.totalPages}</p>
            <p className="stat-detail">Landing pages created</p>
          </div>
        </div>

        <div className="admin-stat-card metric-success">
          <UniversalIcon icon="✅" size={32} />
          <div className="stat-content">
            <h3>Indexed Pages</h3>
            <p className="stat-value">{stats.indexedPages}</p>
            <p className="stat-detail">In search engines</p>
          </div>
        </div>

        <div className="admin-stat-card metric-warning">
          <UniversalIcon icon="📋" size={32} />
          <div className="stat-content">
            <h3>Pending Pages</h3>
            <p className="stat-value">{stats.pendingPages}</p>
            <p className="stat-detail">Awaiting indexing</p>
          </div>
        </div>

        <div className="admin-stat-card metric-info">
          <UniversalIcon icon="📅" size={32} />
          <div className="stat-content">
            <h3>Publishing Schedule</h3>
            <p className="stat-value">{stats.publishingSchedule}</p>
            <p className="stat-detail">Continuous updates</p>
          </div>
        </div>

        <div className="admin-stat-card metric-revenue">
          <UniversalIcon icon="🔑" size={32} />
          <div className="stat-content">
            <h3>Keyword Expansion</h3>
            <p className="stat-value">{stats.keywordExpansion}</p>
            <p className="stat-detail">Coverage complete</p>
          </div>
        </div>
      </div>

      <div className="quick-actions" style={{ marginTop: '30px', marginBottom: '30px' }}>
        <button className="action-button primary" onClick={handleGeneratePages} title="Generate new SEO pages">
          <UniversalIcon icon="➕" size={16} /> Generate New Pages
        </button>
        <button className="action-button primary" onClick={handleSubmitSitemap} title="Submit sitemap to search engines">
          <UniversalIcon icon="🗺️" size={16} /> Submit Sitemap
        </button>
        <button className="action-button primary" onClick={handleReindexPages} title="Reindex all pages">
          <UniversalIcon icon="🔄" size={16} /> Reindex Pages
        </button>
      </div>

      <div className="admin-section-content">
        <h3>SEO Pages Status</h3>

        <div className="jobs-table-wrapper">
          <table className="jobs-table">
            <thead>
              <tr>
                <th>Page ID</th>
                <th>Title</th>
                <th>Status</th>
                <th>Indexed Date</th>
                <th>Keywords</th>
                <th>Traffic</th>
                <th>Next Update</th>
              </tr>
            </thead>
            <tbody>
              {pages.map(page => {
                const statusInfo = getStatusBadge(page.status)
                return (
                  <tr key={page.id} className={`job-row ${getStatusRowColor(page.status)}`}>
                    <td className="job-id"><code>{page.id}</code></td>
                    <td><strong>{page.title}</strong></td>
                    <td>
                      <span className="status-badge" style={{ backgroundColor: statusInfo.color }}>
                        {statusInfo.text}
                      </span>
                    </td>
                    <td className="timestamp">{page.indexed || '—'}</td>
                    <td><strong>{page.keywords}</strong> keywords</td>
                    <td><strong>{page.traffic.toLocaleString()}</strong> visits</td>
                    <td className="timestamp">{page.nextUpdate}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {pages.length === 0 && (
          <div className="no-data">
            <p>No SEO pages yet. Click "Generate New Pages" to start.</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default SEOEngine
