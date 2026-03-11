import React, { useState, useEffect } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import { useAuth } from '@shared/hooks/useAuth'
import { useNavigate } from 'react-router-dom'
import '../../styles/dashboard.css'

const UserDashboard = () => {
  const navigate = useNavigate()
  const auth = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')
  const [searchQuery, setSearchQuery] = useState('')
  const [filterFormat, setFilterFormat] = useState('all')
  const [showProfile, setShowProfile] = useState(false)
  const [conversions, setConversions] = useState([])
  const [showNotifications, setShowNotifications] = useState(false)
  const [stats, setStats] = useState({
    totalConversions: 156,
    conversionsSaved: 2456,
    averageConversionTime: 3.2,
    mostUsedTool: 'PDF to DOCX',
    filesProcessed: 250,
    successRate: 99.2,
    monthlyConversions: 42,
    storageUsed: 2.3,
    storageTotal: 100
  })
  const [profile, setProfile] = useState({
    joinDate: '2024-01-15',
    plan: 'Pro',
    nextBillingDate: '2024-04-15',
    conversionsThisMonth: 42,
    tasksCompleted: 156
  })

  // Redirect if not authenticated - check immediately without loading state to prevent flicker
  useEffect(() => {
    if (!auth.isAuthenticated || !auth.user) {
      navigate('/login', { replace: true })
    }
  }, [auth.isAuthenticated, auth.user, navigate])

  // Fetch stats and conversion history from API
  useEffect(() => {
    if (!auth.isAuthenticated) return // Skip if not authenticated
    
    const fetchStats = async () => {
      try {
        setLoading(true)
        
        // Mock conversion data
        const mockConversions = [
          { id: 1, filename: 'document.pdf', from: 'PDF', to: 'DOCX', date: '2024-03-06', time: '14:30', status: 'completed', size: '2.4 MB', duration: 2.1 },
          { id: 2, filename: 'photo.jpg', from: 'JPG', to: 'PNG', date: '2024-03-06', time: '10:15', status: 'completed', size: '1.8 MB', duration: 1.5 },
          { id: 3, filename: 'spreadsheet.xlsx', from: 'XLSX', to: 'PDF', date: '2024-03-05', time: '16:45', status: 'completed', size: '0.8 MB', duration: 3.8 },
          { id: 4, filename: 'presentation.pptx', from: 'PPTX', to: 'PDF', date: '2024-03-05', time: '14:20', status: 'completed', size: '4.2 MB', duration: 5.2 },
          { id: 5, filename: 'image.png', from: 'PNG', to: 'JPG', date: '2024-03-04', time: '09:30', status: 'completed', size: '0.6 MB', duration: 0.8 },
        ]
        setConversions(mockConversions)
        setError(null)
      } catch (err) {
        console.error('Error fetching dashboard stats:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [auth.isAuthenticated])

  const handleNewConversion = () => {
    navigate('/')
  }

  const downloadConversion = (filename) => {
    console.log('Downloading:', filename)
    // Implement download logic
  }

  const filteredConversions = conversions.filter(c => 
    (c.filename.toLowerCase().includes(searchQuery.toLowerCase()) || searchQuery === '') &&
    (filterFormat === 'all' || c.from.toLowerCase() === filterFormat.toLowerCase())
  )

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
            <span className="notification-badge">3</span>
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
                <button className="dropdown-item" onClick={() => navigate('/api-keys')}>
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
            <div className="notification-item">
              <span className="notification-icon">✅</span>
              <div>
                <p className="notification-title">Conversion Completed</p>
                <p className="notification-meta">Your PDF conversion finished in 2.1s</p>
              </div>
            </div>
            <div className="notification-item">
              <span className="notification-icon">💾</span>
              <div>
                <p className="notification-title">Storage Warning</p>
                <p className="notification-meta">You've used 2.3GB of 100GB storage</p>
              </div>
            </div>
            <div className="notification-item">
              <span className="notification-icon">🎉</span>
              <div>
                <p className="notification-title">Achievement Unlocked</p>
                <p className="notification-meta">You've completed 150 conversions!</p>
              </div>
            </div>
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
              <p className="plan-desc">Full access to all converters</p>
              <div className="plan-features">
                <div className="feature">✅ Unlimited conversions</div>
                <div className="feature">✅ 100GB storage</div>
                <div className="feature">✅ Priority support</div>
              </div>
            </div>
            <button className="btn-link btn-block">Upgrade Plan →</button>
          </div>

          {/* Storage Card */}
          <div className="sidebar-card storage-card">
            <div className="card-header">💾 Storage</div>
            <div className="storage-visual">
              <div className="storage-bar">
                <div className="storage-fill" style={{ width: `${(stats.storageUsed / stats.storageTotal) * 100}%` }}></div>
              </div>
              <p className="storage-text">{stats.storageUsed} GB / {stats.storageTotal} GB</p>
              <p className="storage-percent">{((stats.storageUsed / stats.storageTotal) * 100).toFixed(0)}% used</p>
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
                      <div className="stat-change positive">↑ 12 this month</div>
                    </div>
                  </div>

                  <div className="stat-card premium">
                    <div className="stat-header">
                      <span className="stat-icon">⚡</span>
                      <span className="stat-label">Avg Speed</span>
                    </div>
                    <div className="stat-content">
                      <div className="stat-value">{stats.averageConversionTime}s</div>
                      <div className="stat-change positive">↑ Faster than last week</div>
                    </div>
                  </div>

                  <div className="stat-card premium">
                    <div className="stat-header">
                      <span className="stat-icon">💾</span>
                      <span className="stat-label">Storage Saved</span>
                    </div>
                    <div className="stat-content">
                      <div className="stat-value">{(stats.conversionsSaved / 1024).toFixed(1)} GB</div>
                      <div className="stat-change positive">↑ Growing daily</div>
                    </div>
                  </div>

                  <div className="stat-card premium">
                    <div className="stat-header">
                      <span className="stat-icon">🏆</span>
                      <span className="stat-label">Most Used</span>
                    </div>
                    <div className="stat-content">
                      <div className="stat-value text-sm">{stats.mostUsedTool}</div>
                      <div className="stat-change">{stats.filesProcessed} files</div>
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
                            onClick={() => downloadConversion(conversion.filename)}
                            title="Download file"
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
                  <a href="#docs" className="action-card">
                    <span className="action-icon">📖</span>
                    <span className="action-title">Documentation</span>
                    <span className="action-desc">Learn how to use</span>
                  </a>
                  <a href="#support" className="action-card">
                    <span className="action-icon">💬</span>
                    <span className="action-title">Contact Support</span>
                    <span className="action-desc">Get help fast</span>
                  </a>
                  <a href="#api" className="action-card">
                    <span className="action-icon">🔌</span>
                    <span className="action-title">API Reference</span>
                    <span className="action-desc">Integrate with API</span>
                  </a>
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
                          onClick={() => downloadConversion(conversion.filename)}
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
                      <div className="storage-fill" style={{ width: `${(stats.storageUsed / stats.storageTotal) * 100}%` }}></div>
                    </div>
                    <p className="storage-text">{stats.storageUsed} GB / {stats.storageTotal} GB ({((stats.storageUsed / stats.storageTotal) * 100).toFixed(0)}% used)</p>
                    
                    <div className="storage-breakdown">
                      <div className="breakdown-item">
                        <div className="breakdown-bar documents"></div>
                        <div className="breakdown-label">Documents (0.8 GB)</div>
                      </div>
                      <div className="breakdown-item">
                        <div className="breakdown-bar images"></div>
                        <div className="breakdown-label">Images (0.9 GB)</div>
                      </div>
                      <div className="breakdown-item">
                        <div className="breakdown-bar pdfs"></div>
                        <div className="breakdown-label">PDFs (0.6 GB)</div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="storage-actions">
                  <button className="btn-secondary">🗑️ Clear Old Files</button>
                  <button className="btn-secondary">📥 Download All</button>
                  <button className="btn-primary">⭐ Upgrade Storage</button>
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
                  <div className="metric-trend positive">↓ 0.5s faster than last week</div>
                </div>
                <div className="performance-card">
                  <h3>Success Rate</h3>
                  <div className="metric-display">{stats.successRate}%</div>
                  <div className="metric-trend positive">↑ 0.3% improvement</div>
                </div>
                <div className="performance-card">
                  <h3>Total Files Processed</h3>
                  <div className="metric-display">{stats.filesProcessed}</div>
                  <div className="metric-trend">→ Steady performance</div>
                </div>
                <div className="performance-card">
                  <h3>This Month Activity</h3>
                  <div className="metric-display">{profile.conversionsThisMonth}</div>
                  <div className="metric-trend positive">↑ 42% vs last month</div>
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
