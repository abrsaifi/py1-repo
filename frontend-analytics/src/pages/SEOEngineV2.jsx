import React, { useEffect, useState } from 'react'
import { UniversalIcon } from '../utils/UniversalIcon'
import '../styles/admin.css'

function SEOEngine() {
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    totalPages: 0,
    indexedPages: 0,
    pendingPages: 0,
    publishingSchedule: 'Scheduled Daily',
    keywordExpansion: '0%',
  })
  const [pages, setPages] = useState([])

  const loadSEOData = async () => {
    try {
      setLoading(true)
      const [summaryResponse, pagesResponse] = await Promise.all([
        fetch('/api/seo/summary', { headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` } }),
        fetch('/api/seo/pages', { headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` } }),
      ])

      if (!summaryResponse.ok || !pagesResponse.ok) {
        throw new Error('Failed to load SEO data')
      }

      const summaryData = await summaryResponse.json()
      const pagesData = await pagesResponse.json()
      setStats(summaryData.summary || {})
      setPages(pagesData.pages || [])
    } catch (error) {
      console.error('Failed to load SEO data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSEOData()
  }, [])

  const postAction = async (url, message) => {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
        },
      })
      if (!response.ok) {
        throw new Error('Request failed')
      }
      const payload = await response.json()
      alert(payload.message || message)
      loadSEOData()
    } catch (error) {
      console.error('SEO action failed:', error)
      alert('Action failed')
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      indexed: { color: '#11998e', text: '✅ Indexed' },
      indexing: { color: '#4099ff', text: '⏳ Indexing' },
      pending: { color: '#fa709a', text: '📋 Pending' },
    }
    return badges[status] || badges.pending
  }

  const getStatusRowColor = (status) => {
    const colors = {
      indexed: 'indexed',
      indexing: 'processing',
      pending: 'failed',
    }
    return colors[status] || 'pending'
  }

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="🔍" size={24} /> SEO Engine</h2>
      <p className="section-subtitle">Live SEO summary from CMS pages and tool metadata</p>

      <div className="admin-stats-grid">
        <div className="admin-stat-card metric-primary">
          <UniversalIcon icon="📄" size={32} />
          <div className="stat-content">
            <h3>Total SEO Pages</h3>
            <p className="stat-value">{loading ? '...' : stats.totalPages}</p>
            <p className="stat-detail">CMS + tool pages</p>
          </div>
        </div>
        <div className="admin-stat-card metric-success">
          <UniversalIcon icon="✅" size={32} />
          <div className="stat-content">
            <h3>Indexed Pages</h3>
            <p className="stat-value">{loading ? '...' : stats.indexedPages}</p>
            <p className="stat-detail">Published/indexable pages</p>
          </div>
        </div>
        <div className="admin-stat-card metric-warning">
          <UniversalIcon icon="📋" size={32} />
          <div className="stat-content">
            <h3>Pending Pages</h3>
            <p className="stat-value">{loading ? '...' : stats.pendingPages}</p>
            <p className="stat-detail">Draft or not yet indexable</p>
          </div>
        </div>
        <div className="admin-stat-card metric-info">
          <UniversalIcon icon="📅" size={32} />
          <div className="stat-content">
            <h3>Publishing Schedule</h3>
            <p className="stat-value">{stats.publishingSchedule}</p>
            <p className="stat-detail">Current refresh cadence</p>
          </div>
        </div>
        <div className="admin-stat-card metric-revenue">
          <UniversalIcon icon="🔑" size={32} />
          <div className="stat-content">
            <h3>Keyword Expansion</h3>
            <p className="stat-value">{stats.keywordExpansion}</p>
            <p className="stat-detail">Indexed share</p>
          </div>
        </div>
      </div>

      <div className="quick-actions" style={{ marginTop: '30px', marginBottom: '30px' }}>
        <button className="action-button primary" onClick={() => postAction('/api/seo/actions/generate', 'SEO summary refreshed')}>
          <UniversalIcon icon="➕" size={16} /> Refresh Summary
        </button>
        <button className="action-button primary" onClick={() => postAction('/api/seo/actions/submit-sitemap', 'Sitemap submission queued')}>
          <UniversalIcon icon="🗺️" size={16} /> Submit Sitemap
        </button>
        <button className="action-button primary" onClick={() => postAction('/api/seo/actions/reindex', 'Reindex request queued')}>
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
              {pages.map((page) => {
                const statusInfo = getStatusBadge(page.status)
                return (
                  <tr key={page.id} className={`job-row ${getStatusRowColor(page.status)}`}>
                    <td className="job-id"><code>{page.id}</code></td>
                    <td><strong>{page.title}</strong></td>
                    <td><span className="status-badge" style={{ backgroundColor: statusInfo.color }}>{statusInfo.text}</span></td>
                    <td className="timestamp">{page.indexed || '—'}</td>
                    <td><strong>{page.keywords}</strong> keywords</td>
                    <td><strong>{Number(page.traffic || 0).toLocaleString()}</strong> visits</td>
                    <td className="timestamp">{page.nextUpdate}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
        {!loading && pages.length === 0 && <div className="no-data"><p>No SEO pages found yet.</p></div>}
      </div>
    </div>
  )
}

export default SEOEngine
