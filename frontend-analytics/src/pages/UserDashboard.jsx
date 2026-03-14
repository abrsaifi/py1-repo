import React, { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import { useNavigate } from 'react-router-dom'
import { useToast } from '../components/Toast'
import '../styles/user-dashboard-v2.css'

const DEFAULT_STATS = {
  totalConversions: 0,
  averageConversionTime: 0,
  mostUsedTool: 'No conversions yet',
  filesProcessed: 0,
  successRate: 0,
  monthlyConversions: 0,
  storageUsed: 0,
  storageTotal: 5,
}

const DEFAULT_INSIGHTS = {
  totalConversionsTrend: { text: 'No change vs previous period', direction: 'flat' },
  averageConversionTimeTrend: { text: 'No change vs previous period', direction: 'flat' },
  successRateTrend: { text: 'No change vs previous period', direction: 'flat' },
  monthlyConversionsTrend: { text: 'No change vs previous period', direction: 'flat' },
  filesProcessedTrend: { text: 'No change vs previous period', direction: 'flat' },
}

const UserDashboard = () => {
  const navigate = useNavigate()
  const auth = useAuth()
  const { addToast } = useToast()
  const [activeTab, setActiveTab] = useState('overview')
  const [searchQuery, setSearchQuery] = useState('')
  const [filterFormat, setFilterFormat] = useState('all')
  const [conversions, setConversions] = useState([])
  const [stats, setStats] = useState(DEFAULT_STATS)
  const [insights, setInsights] = useState(DEFAULT_INSIGHTS)
  const [storageBreakdown, setStorageBreakdown] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const loadDashboard = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/dashboard/user', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to load dashboard')
      }

      const payload = await response.json()
      setStats({ ...DEFAULT_STATS, ...(payload.stats || {}) })
      setInsights({ ...DEFAULT_INSIGHTS, ...(payload.insights || {}) })
      setConversions(payload.conversions || [])
      setStorageBreakdown(payload.storageBreakdown || [])
      setError(null)
    } catch (loadError) {
      console.error('Failed to load user dashboard:', loadError)
      setError(loadError.message)
    } finally {
      setLoading(false)
    }
  }

  const downloadFile = async (url, fallbackName) => {
    try {
      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
        },
      })

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}))
        throw new Error(payload.error || 'Download failed')
      }

      const blob = await response.blob()
      const objectUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = objectUrl
      link.download = fallbackName
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(objectUrl)
      addToast({ type: 'success', title: 'Download started', message: fallbackName })
    } catch (downloadError) {
      addToast({ type: 'error', title: 'Download failed', message: downloadError.message })
    }
  }

  const downloadConversion = (conversion) => {
    if (!conversion.can_download) {
      addToast({ type: 'warning', title: 'File unavailable', message: 'This conversion output is no longer available for download' })
      return
    }

    downloadFile(`/api/dashboard/conversions/${conversion.id}/download`, conversion.filename)
  }

  const downloadAllConversions = () => {
    downloadFile('/api/dashboard/conversions/download-all', 'docpro-conversions.zip')
  }

  const cleanupOldFiles = async () => {
    try {
      const response = await fetch('/api/dashboard/conversions/cleanup-old', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
        },
        body: JSON.stringify({ older_than_days: 7 }),
      })

      const payload = await response.json().catch(() => ({}))
      if (!response.ok) {
        throw new Error(payload.error || 'Cleanup failed')
      }

      setConversions((current) => current.map((item) => ({ ...item, can_download: false })))
      addToast({ type: 'success', title: 'Storage cleaned', message: payload.message || 'Old files removed' })
      loadDashboard()
    } catch (cleanupError) {
      addToast({ type: 'error', title: 'Cleanup failed', message: cleanupError.message })
    }
  }

  useEffect(() => {
    if (!auth.isAuthenticated || !auth.user) {
      navigate('/login', { replace: true })
    }
  }, [auth.isAuthenticated, auth.user, navigate])

  useEffect(() => {
    if (!auth.isAuthenticated) {
      return
    }

    loadDashboard()
  }, [auth.isAuthenticated])

  const filteredConversions = conversions.filter(c =>
    (c.filename.toLowerCase().includes(searchQuery.toLowerCase()) || searchQuery === '') &&
    (filterFormat === 'all' || c.from.toLowerCase() === filterFormat.toLowerCase())
  )

  const navItems = [
    { id: 'overview', icon: '▦', label: 'Overview' },
    { id: 'history', icon: '☰', label: 'History' },
    { id: 'storage', icon: '◉', label: 'Storage' },
    { id: 'performance', icon: '↗', label: 'Performance' },
  ]

  const storagePercent = stats.storageTotal ? ((stats.storageUsed / stats.storageTotal) * 100).toFixed(1) : '0.0'

  if (loading) {
    return <div className="udb-root"><div className="udb-content">Loading dashboard...</div></div>
  }

  if (error) {
    return <div className="udb-root"><div className="udb-content">{error}</div></div>
  }

  return (
    <div className="udb-root">

      {/* ── Body: Sidebar + Main ─────────────────────── */}
      <div className="udb-body">

        {/* Sidebar */}
        <aside className="udb-sidebar">
          {/* Profile card */}
          <div className="udb-profile-card">
            <div className="udb-pc-avatar">
              {auth.user?.username?.[0]?.toUpperCase() || 'U'}
            </div>
            <div className="udb-pc-name">{auth.user?.username}</div>
            <div className="udb-pc-email">{auth.user?.email || 'user@docpro.app'}</div>
            <span className="udb-plan-badge">Pro Plan</span>
          </div>

          {/* Navigation */}
          <nav className="udb-sidenav">
            {navItems.map(item => (
              <button
                key={item.id}
                className={`udb-sidenav-item${activeTab === item.id ? ' active' : ''}`}
                onClick={() => setActiveTab(item.id)}
              >
                <span className="udb-si-icon">{item.icon}</span>
                <span>{item.label}</span>
              </button>
            ))}
          </nav>

          {/* Storage widget */}
          <div className="udb-storage-widget">
            <div className="udb-sw-header">
              <span>Storage</span>
              <span className="udb-sw-value">{stats.storageUsed} / {stats.storageTotal} GB</span>
            </div>
            <div className="udb-sw-bar">
              <div className="udb-sw-fill" style={{ width: `${storagePercent}%` }} />
            </div>
            <div className="udb-sw-pct">{storagePercent}% used</div>
          </div>

          {/* Quick links */}
          <div className="udb-quick-links">
            <div className="udb-ql-title">Quick Links</div>
            <button className="udb-ql-item" onClick={() => navigate('/')}>📄 Convert a File</button>
            <button className="udb-ql-item" onClick={() => navigate('/dashboard/account')}>🔑 API Keys</button>
            <button className="udb-ql-item" onClick={() => navigate('/settings')}>⚙️ Settings</button>
          </div>
        </aside>

        {/* Main content */}
        <main className="udb-main">

          {/* ── OVERVIEW TAB ── */}
          {activeTab === 'overview' && (
            <div className="udb-content">

              <div className="udb-stats-grid">
                <div className="udb-stat-card" data-color="blue">
                  <div className="udb-sc-label">Total Conversions</div>
                  <div className="udb-sc-value">{stats.totalConversions}</div>
                  <div className={`udb-sc-trend ${insights.totalConversionsTrend.direction === 'down' ? 'down' : 'up'}`}>{insights.totalConversionsTrend.text}</div>
                </div>
                <div className="udb-stat-card" data-color="violet">
                  <div className="udb-sc-label">Avg. Speed</div>
                  <div className="udb-sc-value">{stats.averageConversionTime}s</div>
                  <div className={`udb-sc-trend ${insights.averageConversionTimeTrend.direction === 'down' ? 'down' : 'up'}`}>{insights.averageConversionTimeTrend.text}</div>
                </div>
                <div className="udb-stat-card" data-color="emerald">
                  <div className="udb-sc-label">Success Rate</div>
                  <div className="udb-sc-value">{stats.successRate}%</div>
                  <div className={`udb-sc-trend ${insights.successRateTrend.direction === 'down' ? 'down' : 'up'}`}>{insights.successRateTrend.text}</div>
                </div>
                <div className="udb-stat-card" data-color="amber">
                  <div className="udb-sc-label">This Month</div>
                  <div className="udb-sc-value">{stats.monthlyConversions}</div>
                  <div className={`udb-sc-trend ${insights.monthlyConversionsTrend.direction === 'down' ? 'down' : 'up'}`}>{insights.monthlyConversionsTrend.text}</div>
                </div>
              </div>

              <div className="udb-section">
                <div className="udb-section-head">
                  <h2 className="udb-section-title">Recent Conversions</h2>
                  <button className="udb-link-btn" onClick={() => setActiveTab('history')}>View all →</button>
                </div>
                <div className="udb-conv-list">
                  {conversions.slice(0, 5).map(c => (
                    <div key={c.id} className="udb-conv-row">
                      <span className="udb-conv-file-icon">📄</span>
                      <div className="udb-conv-info">
                        <div className="udb-conv-name">{c.filename}</div>
                        <div className="udb-conv-meta">
                          <span className="udb-fmt">{c.from}</span>
                          <span className="udb-arrow">→</span>
                          <span className="udb-fmt">{c.to}</span>
                          <span className="udb-sep">·</span>
                          <span>{c.size}</span>
                          <span className="udb-sep">·</span>
                          <span>{c.duration}s</span>
                        </div>
                      </div>
                      <div className="udb-conv-date">{c.date}</div>
                      <span className="udb-status-pill">✓ Done</span>
                      <button className="udb-dl-btn" title="Download" onClick={() => downloadConversion(c)} disabled={!c.can_download}>↓</button>
                    </div>
                  ))}
                </div>
              </div>

              <div className="udb-section">
                <h2 className="udb-section-title">Quick Actions</h2>
                <div className="udb-action-grid">
                  {[
                    { icon: '➕', title: 'New Conversion', desc: 'Convert any file format', action: () => navigate('/') },
                    { icon: '📖', title: 'Documentation', desc: 'Browse tools and usage guides', action: () => navigate('/tools') },
                    { icon: '💬', title: 'Support', desc: 'Email the support team', action: () => { addToast({ type: 'info', title: 'Opening support', message: 'Launching your mail client for support@docpro.app' }); window.location.href = 'mailto:support@docpro.app' } },
                    { icon: '🔌', title: 'API Access', desc: 'Manage API keys and access', action: () => navigate('/dashboard/account') },
                  ].map((a, i) => (
                    <button key={i} className="udb-action-card" onClick={a.action}>
                      <span className="udb-ac-icon">{a.icon}</span>
                      <span className="udb-ac-title">{a.title}</span>
                      <span className="udb-ac-desc">{a.desc}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* ── HISTORY TAB ── */}
          {activeTab === 'history' && (
            <div className="udb-content">
              <div className="udb-section">
                <h2 className="udb-section-title">Conversion History</h2>

                <div className="udb-history-controls">
                  <input
                    type="text"
                    className="udb-search"
                    placeholder="🔍  Search by filename…"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                  />
                  <select
                    className="udb-filter"
                    value={filterFormat}
                    onChange={e => setFilterFormat(e.target.value)}
                  >
                    <option value="all">All Formats</option>
                    <option value="pdf">PDF</option>
                    <option value="jpg">JPG</option>
                    <option value="xlsx">XLSX</option>
                    <option value="pptx">PPTX</option>
                  </select>
                </div>

                {filteredConversions.length === 0 ? (
                  <div className="udb-empty">
                    <div className="udb-empty-icon">🔍</div>
                    <div>No matching conversions</div>
                    <div className="udb-empty-sub">Try adjusting your filters</div>
                  </div>
                ) : (
                  <div className="udb-table">
                    <div className="udb-table-head">
                      <span>File</span>
                      <span>Format</span>
                      <span>Date & Time</span>
                      <span>Size</span>
                      <span>Duration</span>
                      <span></span>
                    </div>
                    {filteredConversions.map(c => (
                      <div key={c.id} className="udb-table-row">
                        <span className="udb-table-file">{c.filename}</span>
                        <span>{c.from} → {c.to}</span>
                        <span>{c.date} {c.time}</span>
                        <span>{c.size}</span>
                        <span>{c.duration}s</span>
                        <button className="udb-dl-btn" title="Download" onClick={() => downloadConversion(c)} disabled={!c.can_download}>↓</button>
                      </div>
                    ))}
                  </div>
                )}
                <div className="udb-table-footer">
                  Showing {filteredConversions.length} of {conversions.length} conversions
                </div>
              </div>
            </div>
          )}

          {/* ── STORAGE TAB ── */}
          {activeTab === 'storage' && (
            <div className="udb-content">
              <div className="udb-section">
                <h2 className="udb-section-title">Storage Management</h2>

                <div className="udb-storage-card">
                  <div className="udb-storage-info">
                    <span className="udb-storage-used">{stats.storageUsed} GB</span>
                    <span className="udb-storage-of">of {stats.storageTotal} GB used</span>
                  </div>
                  <div className="udb-storage-bar-lg">
                    <div className="udb-storage-fill-lg" style={{ width: `${storagePercent}%` }} />
                  </div>
                  <div className="udb-storage-pct">{storagePercent}%</div>
                </div>

                <div className="udb-breakdown-grid">
                  {(storageBreakdown.length ? storageBreakdown : [
                    { label: 'No files yet', size: '0 B', pct: 0 },
                  ]).map((item, index) => (
                    <div key={item.label} className="udb-breakdown-item">
                      <div className="udb-bd-color" style={{ background: ['#6366f1', '#06b6d4', '#10b981', '#f59e0b'][index % 4] }} />
                      <div className="udb-bd-info">
                        <span>{item.label}</span>
                        <span className="udb-bd-size">{item.size}</span>
                      </div>
                      <div className="udb-bd-bar">
                        <div style={{ width: `${item.pct}%`, background: ['#6366f1', '#06b6d4', '#10b981', '#f59e0b'][index % 4], height: '100%', borderRadius: '4px' }} />
                      </div>
                    </div>
                  ))}
                </div>

                <div className="udb-storage-actions">
                  <button className="udb-btn-secondary" onClick={cleanupOldFiles}>🗑️ Clear Old Files</button>
                  <button className="udb-btn-secondary" onClick={downloadAllConversions} disabled={!conversions.some(item => item.can_download)}>📥 Download All</button>
                  <button className="udb-new-btn" onClick={() => navigate('/billing')}>⭐ Upgrade Storage</button>
                </div>
              </div>
            </div>
          )}

          {/* ── PERFORMANCE TAB ── */}
          {activeTab === 'performance' && (
            <div className="udb-content">
              <div className="udb-section">
                <h2 className="udb-section-title">Performance Metrics</h2>
                <div className="udb-perf-grid">
                  {[
                    { title: 'Avg. Conversion Speed', value: `${stats.averageConversionTime}s`, trend: insights.averageConversionTimeTrend.text, up: insights.averageConversionTimeTrend.direction !== 'down' },
                    { title: 'Success Rate', value: `${stats.successRate}%`, trend: insights.successRateTrend.text, up: insights.successRateTrend.direction !== 'down' },
                    { title: 'Files Processed', value: stats.filesProcessed, trend: insights.filesProcessedTrend.text, up: insights.filesProcessedTrend.direction === 'up' ? true : insights.filesProcessedTrend.direction === 'down' ? false : null },
                    { title: 'Monthly Activity', value: stats.monthlyConversions, trend: insights.monthlyConversionsTrend.text, up: insights.monthlyConversionsTrend.direction !== 'down' },
                  ].map((m, i) => (
                    <div key={i} className="udb-perf-card">
                      <div className="udb-perf-title">{m.title}</div>
                      <div className="udb-perf-value">{m.value}</div>
                      <div className={`udb-perf-trend ${m.up === true ? 'up' : m.up === false ? 'down' : ''}`}>
                        {m.trend}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

        </main>
      </div>
    </div>
  )
}

export default UserDashboard
