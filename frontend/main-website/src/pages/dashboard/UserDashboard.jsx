import React, { useState, useEffect } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import { useAuth } from '@shared/hooks/useAuth'
import { useToast } from '@shared/components/Toast'
import { useNavigate } from 'react-router-dom'
import '../../styles/dashboard.css'

const DEFAULT_STATS = {
  totalConversions: 0,
  conversionsSaved: 0,
  averageConversionTime: 0,
  mostUsedTool: 'No conversions yet',
  filesProcessed: 0,
  successRate: 0,
  monthlyConversions: 0,
  storageUsed: 0,
  storageTotal: 5,
}

const DEFAULT_PROFILE = {
  joinDate: 'N/A',
  plan: 'Free',
  nextBillingDate: 'N/A',
  conversionsThisMonth: 0,
  tasksCompleted: 0,
}

const DEFAULT_NOTIFICATIONS = []
const DEFAULT_INSIGHTS = {
  totalConversionsTrend: { text: 'No change vs previous period', direction: 'flat' },
  averageConversionTimeTrend: { text: 'No change vs previous period', direction: 'flat' },
  successRateTrend: { text: 'No change vs previous period', direction: 'flat' },
  monthlyConversionsTrend: { text: 'No change vs previous period', direction: 'flat' },
  filesProcessedTrend: { text: 'No change vs previous period', direction: 'flat' },
  conversionsSavedTrend: { text: 'No completed conversions yet', direction: 'flat' },
  mostUsedToolDetail: 'Waiting for conversion activity',
}
const DEFAULT_PLAN_DETAILS = {
  name: 'Free',
  description: 'Essential tools for occasional conversions.',
  features: ['5 GB storage quota', '100 conversions per month', 'Community support'],
}

const UserDashboard = () => {
  const navigate = useNavigate()
  const auth = useAuth()
  const { addToast } = useToast()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')
  const [searchQuery, setSearchQuery] = useState('')
  const [filterFormat, setFilterFormat] = useState('all')
  const [showProfile, setShowProfile] = useState(false)
  const [conversions, setConversions] = useState([])
  const [showNotifications, setShowNotifications] = useState(false)
  const [notifications, setNotifications] = useState(DEFAULT_NOTIFICATIONS)
  const [stats, setStats] = useState(DEFAULT_STATS)
  const [profile, setProfile] = useState(DEFAULT_PROFILE)
  const [insights, setInsights] = useState(DEFAULT_INSIGHTS)
  const [planDetails, setPlanDetails] = useState(DEFAULT_PLAN_DETAILS)
  const [storageBreakdown, setStorageBreakdown] = useState([])

  const fetchStats = async () => {
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
      setProfile({ ...DEFAULT_PROFILE, ...(payload.profile || {}) })
      setInsights({ ...DEFAULT_INSIGHTS, ...(payload.insights || {}) })
      setPlanDetails({ ...DEFAULT_PLAN_DETAILS, ...(payload.planDetails || {}) })
      setConversions(payload.conversions || [])
      setNotifications(payload.notifications || DEFAULT_NOTIFICATIONS)
      setStorageBreakdown(payload.storageBreakdown || [])
      setError(null)
    } catch (err) {
      console.error('Error fetching dashboard stats:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Redirect if not authenticated - check immediately without loading state to prevent flicker
  useEffect(() => {
    if (!auth.isAuthenticated || !auth.user) {
      navigate('/login', { replace: true })
    }
  }, [auth.isAuthenticated, auth.user, navigate])

  // Fetch stats and conversion history from API
  useEffect(() => {
    if (!auth.isAuthenticated) return // Skip if not authenticated

    fetchStats()
  }, [auth.isAuthenticated])

  const handleNewConversion = () => {
    navigate('/')
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
      fetchStats()
    } catch (cleanupError) {
      addToast({ type: 'error', title: 'Cleanup failed', message: cleanupError.message })
    }
  }

  const filteredConversions = conversions.filter(c => 
    (c.filename.toLowerCase().includes(searchQuery.toLowerCase()) || searchQuery === '') &&
    (filterFormat === 'all' || c.from.toLowerCase() === filterFormat.toLowerCase())
  )

  const storagePercent = stats.storageTotal ? ((stats.storageUsed / stats.storageTotal) * 100) : 0

  if (loading) {
    return (
      <div className="user-dashboard loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading your dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="user-dashboard error">
        <div className="error-container">
          <h2>⚠️ Error Loading Dashboard</h2>
          <p>{error}</p>
          <button className="btn-primary" onClick={() => window.location.reload()}>
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="user-dashboard enhanced">
      {/* Enhanced Top Navigation Bar */}
      <nav className="dashboard-topnav v2">
        <div className="topnav-left">
          <h1>🎯 Dashboard</h1>
          <div className="breadcrumb">
            <span>Home</span>
            <span className="divider">/</span>
            <span className="active">{activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}</span>
          </div>
        </div>
        <div className="topnav-right">
          <button className="btn-icon notification-btn" onClick={() => setShowNotifications(!showNotifications)}>
            🔔
            <span className="notification-badge">{notifications.length}</span>
          </button>
          <button className="btn-primary" onClick={handleNewConversion}>
            ➕ New Conversion
          </button>
          <div className="profile-menu-wrapper">
            <button 
              className="profile-button"
              onClick={() => setShowProfile(!showProfile)}
              title="Profile menu"
            >
              <span className="profile-avatar">{auth.user?.username?.[0]?.toUpperCase() || '👤'}</span>
              <span className="profile-name">{auth.user?.username}</span>
            </button>
            
            {showProfile && (
              <div className="profile-dropdown">
                <div className="profile-header">
                  <div className="profile-avatar-large">{auth.user?.username?.[0]?.toUpperCase() || '👤'}</div>
                  <div>
                    <p className="profile-name-large"><strong>{auth.user?.username}</strong></p>
                    <p className="text-muted">{auth.user?.email}</p>
                  </div>
                </div>
                <hr />
                <button className="dropdown-item" onClick={() => navigate('/profile')}>
                  👤 View Profile
                </button>
                <button className="dropdown-item" onClick={() => navigate('/settings')}>
                  ⚙️ Settings
                </button>
                <button className="dropdown-item" onClick={() => navigate('/billing')}>
                  💳 Billing
                </button>
                <button className="dropdown-item" onClick={() => navigate('/dashboard/account')}>
                  🔑 API Keys
                </button>
                <hr />
                <button className="dropdown-item logout" onClick={auth.logout}>
                  🚪 Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </nav>

      {/* Notifications Panel */}
      {showNotifications && (
        <div className="notifications-panel">
          <div className="notifications-header">
            <h3>Notifications</h3>
            <button className="btn-icon" onClick={() => setShowNotifications(false)}>✕</button>
          </div>
          <div className="notifications-list">
            {notifications.map((notification) => (
              <div className="notification-item" key={notification.id}>
                <span className="notification-icon">{notification.icon}</span>
                <div>
                  <p className="notification-title">{notification.title}</p>
                  <p className="notification-meta">{notification.meta}</p>
                </div>
              </div>
            ))}
            {notifications.length === 0 && (
              <div className="notification-item">
                <span className="notification-icon">📭</span>
                <div>
                  <p className="notification-title">No notifications yet</p>
                  <p className="notification-meta">Your latest conversion activity will appear here.</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Enhanced Navigation Tabs */}
      <div className="dashboard-nav sticky v2">
        <div className="nav-container">
          <button 
            className={`nav-tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
            title="Overview dashboard"
          >
            📊 Overview
          </button>
          <button 
            className={`nav-tab ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
            title="Conversion history"
          >
            📜 History
          </button>
          <button 
            className={`nav-tab ${activeTab === 'storage' ? 'active' : ''}`}
            onClick={() => setActiveTab('storage')}
            title="Storage management"
          >
            💾 Storage
          </button>
          <button 
            className={`nav-tab ${activeTab === 'performance' ? 'active' : ''}`}
            onClick={() => setActiveTab('performance')}
            title="Performance metrics"
          >
            ⚡ Performance
          </button>
        </div>
      </div>

      <div className="dashboard-container v2">
        {/* Enhanced Sidebar */}
        <aside className="dashboard-sidebar v2">
          {/* Profile Card */}
          <div className="sidebar-card profile-card">
            <div className="profile-section">
              <div className="avatar-large">{auth.user?.username?.[0]?.toUpperCase() || '👤'}</div>
              <h3>{auth.user?.username}</h3>
              <p className="text-muted">{auth.user?.email}</p>
              <div className="profile-badge pro">{profile.plan} Plan</div>
            </div>
            <div className="profile-details">
              <div className="detail-item">
                <span className="label">Member Since</span>
                <span className="value">{profile.joinDate}</span>
              </div>
              <div className="detail-item">
                <span className="label">Next Billing</span>
                <span className="value">{profile.nextBillingDate}</span>
              </div>
            </div>
            <button className="btn-secondary btn-block">Edit Profile</button>
          </div>

          {/* Plan Card */}
          <div className="sidebar-card plan-card">
            <div className="card-header">📋 Current Plan</div>
            <div className="plan-info">
              <div className="plan-badge pro">{profile.plan}</div>
              <p className="plan-desc">{planDetails.description}</p>
              <div className="plan-features">
                {planDetails.features.map((feature) => (
                  <div className="feature" key={feature}>✅ {feature}</div>
                ))}
              </div>
            </div>
            <button className="btn-link btn-block">Upgrade Plan →</button>
          </div>

          {/* Storage Card */}
          <div className="sidebar-card storage-card">
            <div className="card-header">💾 Storage</div>
            <div className="storage-visual">
              <div className="storage-bar">
                <div className="storage-fill" style={{ width: `${storagePercent}%` }}></div>
              </div>
              <p className="storage-text">{stats.storageUsed} GB / {stats.storageTotal} GB</p>
              <p className="storage-percent">{storagePercent.toFixed(0)}% used</p>
            </div>
          </div>

          {/* Quick Stats Card */}
          <div className="sidebar-card stats-card">
            <div className="card-header">📈 This Month</div>
            <div className="quick-stat">
              <div className="stat-number">{profile.conversionsThisMonth}</div>
              <div className="stat-label">Conversions</div>
            </div>
            <div className="quick-stat">
              <div className="stat-number">{stats.successRate}%</div>
              <div className="stat-label">Success Rate</div>
            </div>
          </div>
        </aside>

        {/* Enhanced Main Content */}
        <main className="dashboard-main v2">
          {activeTab === 'overview' && (
            <>
              {/* Hero Stats Section */}
              <section className="stats-section hero-stats">
                <h2 className="section-title">Your Activity Overview</h2>
                <div className="stats-grid v2">
                  <div className="stat-card premium">
                    <div className="stat-header">
                      <span className="stat-icon">📋</span>
                      <span className="stat-label">Total Conversions</span>
                    </div>
                    <div className="stat-content">
                      <div className="stat-value">{stats.totalConversions}</div>
                      <div className={`stat-change ${insights.totalConversionsTrend.direction === 'down' ? 'negative' : 'positive'}`}>{insights.totalConversionsTrend.text}</div>
                    </div>
                  </div>

                  <div className="stat-card premium">
                    <div className="stat-header">
                      <span className="stat-icon">⚡</span>
                      <span className="stat-label">Avg Speed</span>
                    </div>
                    <div className="stat-content">
                      <div className="stat-value">{stats.averageConversionTime}s</div>
                      <div className={`stat-change ${insights.averageConversionTimeTrend.direction === 'down' ? 'negative' : 'positive'}`}>{insights.averageConversionTimeTrend.text}</div>
                    </div>
                  </div>

                  <div className="stat-card premium">
                    <div className="stat-header">
                      <span className="stat-icon">💾</span>
                      <span className="stat-label">Storage Saved</span>
                    </div>
                    <div className="stat-content">
                      <div className="stat-value">{(stats.conversionsSaved / 1024).toFixed(1)} GB</div>
                      <div className={`stat-change ${insights.conversionsSavedTrend.direction === 'down' ? 'negative' : 'positive'}`}>{insights.conversionsSavedTrend.text}</div>
                    </div>
                  </div>

                  <div className="stat-card premium">
                    <div className="stat-header">
                      <span className="stat-icon">🏆</span>
                      <span className="stat-label">Most Used</span>
                    </div>
                    <div className="stat-content">
                      <div className="stat-value text-sm">{stats.mostUsedTool}</div>
                      <div className="stat-change">{insights.mostUsedToolDetail}</div>
                    </div>
                  </div>
                </div>
              </section>

              {/* Recent Activity */}
              <section className="recent-activity v2">
                <div className="section-header">
                  <h2>📌 Recent Conversions</h2>
                  <button className="btn-link" onClick={() => setActiveTab('history')}>
                    View All →
                  </button>
                </div>

                {conversions.length === 0 ? (
                  <div className="empty-state">
                    <span className="empty-icon">📂</span>
                    <p>No conversions yet</p>
                    <button className="btn-primary" onClick={handleNewConversion}>
                      Start Your First Conversion
                    </button>
                  </div>
                ) : (
                  <div className="conversion-list v2">
                    {conversions.slice(0, 5).map((conversion) => (
                      <div key={conversion.id} className="conversion-item v2">
                        <div className="conversion-left">
                          <span className="file-icon">📄</span>
                          <div className="conversion-details">
                            <div className="conversion-name">{conversion.filename}</div>
                            <div className="conversion-meta">
                              <span className="format-badge">{conversion.from}</span>
                              <span className="arrow">→</span>
                              <span className="format-badge">{conversion.to}</span>
                              <span className="spacer">•</span>
                              <span className="size">{conversion.size}</span>
                            </div>
                          </div>
                        </div>
                        <div className="conversion-right">
                          <div className="conversion-time">{conversion.date}</div>
                          <button 
                            className="btn-icon download"
                            onClick={() => downloadConversion(conversion)}
                            title="Download file"
                            disabled={!conversion.can_download}
                          >
                            ⬇️
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </section>

              {/* Quick Actions */}
              <section className="quick-actions v2">
                <h2 className="section-title">⚡ Quick Actions</h2>
                <div className="actions-grid v2">
                  <button className="action-card" onClick={handleNewConversion}>
                    <span className="action-icon">➕</span>
                    <span className="action-title">New Conversion</span>
                    <span className="action-desc">Start converting</span>
                  </button>
                  <button className="action-card" onClick={() => navigate('/tools')}>
                    <span className="action-icon">📖</span>
                    <span className="action-title">Documentation</span>
                    <span className="action-desc">Browse tools and usage guides</span>
                  </button>
                  <button className="action-card" onClick={() => { addToast({ type: 'info', title: 'Opening support', message: 'Launching your mail client for support@docpro.app' }); window.location.href = 'mailto:support@docpro.app' }}>
                    <span className="action-icon">💬</span>
                    <span className="action-title">Contact Support</span>
                    <span className="action-desc">Email the support team</span>
                  </button>
                  <button className="action-card" onClick={() => navigate('/dashboard/account')}>
                    <span className="action-icon">🔌</span>
                    <span className="action-title">API Reference</span>
                    <span className="action-desc">Manage API keys and access</span>
                  </button>
                </div>
              </section>
            </>
          )}

          {activeTab === 'history' && (
            <section className="history-section v2">
              <h2>📜 Conversion History</h2>
              
              <div className="history-controls">
                <div className="search-box">
                  <input 
                    type="text" 
                    placeholder="🔍 Search by filename..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="search-input"
                  />
                </div>
                <select 
                  value={filterFormat}
                  onChange={(e) => setFilterFormat(e.target.value)}
                  className="filter-select"
                >
                  <option value="all">All Formats</option>
                  <option value="pdf">PDF</option>
                  <option value="jpg">JPG</option>
                  <option value="xlsx">XLSX</option>
                  <option value="pptx">PPTX</option>
                </select>
              </div>

              {filteredConversions.length === 0 ? (
                <div className="empty-state">
                  <p>🔍 No conversions found</p>
                  <p className="text-muted">Try adjusting your filters</p>
                </div>
              ) : (
                <div className="conversion-table">
                  <div className="table-header">
                    <div className="col-file">File</div>
                    <div className="col-format">Format</div>
                    <div className="col-date">Date</div>
                    <div className="col-size">Size</div>
                    <div className="col-duration">Duration</div>
                    <div className="col-actions">Actions</div>
                  </div>
                  {filteredConversions.map((conversion) => (
                    <div key={conversion.id} className="table-row">
                      <div className="col-file">{conversion.filename}</div>
                      <div className="col-format">{conversion.from} → {conversion.to}</div>
                      <div className="col-date">{conversion.date} {conversion.time}</div>
                      <div className="col-size">{conversion.size}</div>
                      <div className="col-duration">{conversion.duration}s</div>
                      <div className="col-actions">
                        <button 
                          className="btn-icon"
                          onClick={() => downloadConversion(conversion)}
                          disabled={!conversion.can_download}
                        >
                          ⬇️
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              <div className="history-footer">
                Showing {filteredConversions.length} of {conversions.length} conversions
              </div>
            </section>
          )}

          {activeTab === 'storage' && (
            <section className="storage-section v2">
              <h2>💾 Storage Management</h2>
              <div className="storage-details">
                <div className="storage-main">
                  <div className="storage-info">
                    <div className="storage-bar large">
                      <div className="storage-fill" style={{ width: `${storagePercent}%` }}></div>
                    </div>
                    <p className="storage-text">{stats.storageUsed} GB / {stats.storageTotal} GB ({storagePercent.toFixed(0)}% used)</p>
                    
                    <div className="storage-breakdown">
                      {(storageBreakdown.length ? storageBreakdown : [{ label: 'No files yet', size: '0 B', pct: 0 }]).map((item, index) => (
                        <div className="breakdown-item" key={item.label}>
                          <div className={`breakdown-bar ${['documents', 'images', 'pdfs'][index] || 'documents'}`} style={{ width: `${item.pct}%` }}></div>
                          <div className="breakdown-label">{item.label} ({item.size})</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="storage-actions">
                  <button className="btn-secondary" onClick={cleanupOldFiles}>🗑️ Clear Old Files</button>
                  <button className="btn-secondary" onClick={downloadAllConversions} disabled={!conversions.some(item => item.can_download)}>📥 Download All</button>
                  <button className="btn-primary" onClick={() => navigate('/billing')}>⭐ Upgrade Storage</button>
                </div>

                <div className="storage-note">
                  <p><strong>💡 Tip:</strong> Keep your storage organized by regularly deleting old conversions you no longer need.</p>
                </div>
              </div>
            </section>
          )}

          {activeTab === 'performance' && (
            <section className="performance-section v2">
              <h2>⚡ Performance Metrics</h2>
              <div className="performance-grid">
                <div className="performance-card">
                  <h3>Average Conversion Speed</h3>
                  <div className="metric-display">{stats.averageConversionTime}s</div>
                  <div className={`metric-trend ${insights.averageConversionTimeTrend.direction === 'down' ? 'negative' : 'positive'}`}>{insights.averageConversionTimeTrend.text}</div>
                </div>
                <div className="performance-card">
                  <h3>Success Rate</h3>
                  <div className="metric-display">{stats.successRate}%</div>
                  <div className={`metric-trend ${insights.successRateTrend.direction === 'down' ? 'negative' : 'positive'}`}>{insights.successRateTrend.text}</div>
                </div>
                <div className="performance-card">
                  <h3>Total Files Processed</h3>
                  <div className="metric-display">{stats.filesProcessed}</div>
                  <div className="metric-trend">{insights.filesProcessedTrend.text}</div>
                </div>
                <div className="performance-card">
                  <h3>This Month Activity</h3>
                  <div className="metric-display">{profile.conversionsThisMonth}</div>
                  <div className={`metric-trend ${insights.monthlyConversionsTrend.direction === 'down' ? 'negative' : 'positive'}`}>{insights.monthlyConversionsTrend.text}</div>
                </div>
              </div>
            </section>
          )}
        </main>
      </div>
    </div>
  )
}

export default UserDashboard
