import React, { useState, useEffect } from 'react'
import { UniversalIcon } from '../utils/UniversalIcon'
import { useAuth } from '../hooks/useAuth'
import { useNavigate } from 'react-router-dom'
import '../styles/dashboard.css'

const UserDashboard = () => {
  const navigate = useNavigate()
  const auth = useAuth()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')
  const [searchQuery, setSearchQuery] = useState('')
  const [filterFormat, setFilterFormat] = useState('all')
  const [showProfile, setShowProfile] = useState(false)

  // Real API state
  const [user, setUser] = useState(null)
  const [stats, setStats] = useState({
    totalConversions: 0,
    conversionsSaved: 0,
    averageConversionTime: 0,
    mostUsedTool: 'N/A'
  })
  const [conversions, setConversions] = useState([])

  // Fetch user data and stats from API
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        
        // Check if user is authenticated by checking localStorage first (source of truth)
        const storedToken = localStorage.getItem('token')
        const storedUser = localStorage.getItem('user')
        
        // Handle both null and string 'undefined' / 'null'
        if (!storedToken || !storedUser || storedUser === 'undefined' || storedUser === 'null') {
          // No token found - user is not authenticated
          navigate('/login', { replace: true })
          return
        }
        
        const token = storedToken
        
        // Fetch user profile from /me endpoint
        const meResponse = await fetch('http://localhost:5000/api/auth/me', {
          method: 'GET',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          credentials: 'include'
        })

        if (!meResponse.ok) {
          if (meResponse.status === 401) {
            // Token expired or invalid, clear storage and redirect to login
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            navigate('/login', { replace: true })
            return
          }
          throw new Error('Failed to fetch user data')
        }

        const userData = await meResponse.json()
        setUser({
          id: userData.user_id,
          username: userData.username,
          email: userData.email,
          plan: 'Pro',
          conversionsThisMonth: 42,
          filesProcessed: 156,
          totalStorage: 2.3
        })

        // For now, use mock conversion data - will integrate with real API later
        const mockConversions = [
          { id: 1, filename: 'document.pdf', from: 'PDF', to: 'DOCX', date: '2024-03-06', time: '14:30', status: 'completed', size: '2.4 MB' },
          { id: 2, filename: 'photo.jpg', from: 'JPG', to: 'PNG', date: '2024-03-06', time: '10:15', status: 'completed', size: '1.8 MB' },
          { id: 3, filename: 'spreadsheet.xlsx', from: 'XLSX', to: 'PDF', date: '2024-03-05', time: '16:45', status: 'completed', size: '0.8 MB' }
        ]
        setConversions(mockConversions)

        setStats({
          totalConversions: 156,
          conversionsSaved: 2456,
          averageConversionTime: 3.2,
          mostUsedTool: 'PDF to DOCX'
        })

        setError(null)
      } catch (err) {
        console.error('Error fetching dashboard data:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    // Only run on component mount, not on every re-render
    fetchData()
  }, [])

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
    <div className="user-dashboard refined">
      {/* Top Navigation Bar */}
      <nav className="dashboard-topnav">
        <div className="topnav-left">
          <h1>Dashboard</h1>
        </div>
        <div className="topnav-right">
          <button className="btn-primary" onClick={handleNewConversion}>
            ➕ New Conversion
          </button>
          <div className="profile-menu-wrapper">
            <button 
              className="profile-button"
              onClick={() => setShowProfile(!showProfile)}
              title="Profile menu"
            >
              <span className="profile-icon">👤</span>
              {user && <span className="profile-name">{user.username}</span>}
            </button>
            
            {showProfile && (
              <div className="profile-dropdown">
                <div className="profile-info">
                  <p><strong>{user?.username}</strong></p>
                  <p className="text-muted">{user?.email}</p>
                </div>
                <hr />
                <button className="dropdown-item" onClick={() => navigate('/settings')}>
                  ⚙️ Settings
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

      {/* Navigation Tabs */}
      <div className="dashboard-nav sticky">
        <div className="nav-container">
          <button 
            className={`nav-tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
            role="tab"
            aria-selected={activeTab === 'overview'}
          >
            📊 Overview
          </button>
          <button 
            className={`nav-tab ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
            role="tab"
            aria-selected={activeTab === 'history'}
          >
            📜 History
          </button>
          <button 
            className={`nav-tab ${activeTab === 'storage' ? 'active' : ''}`}
            onClick={() => setActiveTab('storage')}
            role="tab"
            aria-selected={activeTab === 'storage'}
          >
            💾 Storage
          </button>
        </div>
      </div>

      <div className="dashboard-container">
        {/* Compact Sidebar */}
        <aside className="dashboard-sidebar compact">
          <div className="sidebar-card">
            <div className="card-header">Current Plan</div>
            <div className="plan-badge pro">{user?.plan || 'Free'}</div>
            <p className="plan-desc">Full access to all converters</p>
            <button className="btn-link text-sm">Upgrade →</button>
          </div>

          <div className="sidebar-card">
            <div className="card-header">Storage</div>
            <div className="storage-bar">
              <div className="storage-fill" style={{ width: '23%' }}></div>
            </div>
            <p className="storage-text" style={{ fontSize: '0.875rem' }}>2.3 GB / 100 GB</p>
          </div>

          <div className="sidebar-card">
            <div className="card-header">Quick Stats</div>
            <div className="mini-stat">
              <span className="label">Conversions</span>
              <span className="value">{stats.totalConversions}</span>
            </div>
            <div className="mini-stat">
              <span className="label">This Month</span>
              <span className="value">{user?.conversionsThisMonth || 0}</span>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="dashboard-main">
          {activeTab === 'overview' && (
            <>
              {/* Stats Grid - Simplified */}
              <section className="stats-grid compact">
                <div className="stat-card">
                  <div className="stat-icon">📋</div>
                  <div className="stat-content">
                    <div className="stat-value">{stats.totalConversions}</div>
                    <div className="stat-label">Total Conversions</div>
                  </div>
                </div>

                <div className="stat-card">
                  <div className="stat-icon">💾</div>
                  <div className="stat-content">
                    <div className="stat-value">{(stats.conversionsSaved / 1024).toFixed(1)} GB</div>
                    <div className="stat-label">Space Saved</div>
                  </div>
                </div>

                <div className="stat-card">
                  <div className="stat-icon">⚡</div>
                  <div className="stat-content">
                    <div className="stat-value">{stats.averageConversionTime}s</div>
                    <div className="stat-label">Avg. Speed</div>
                  </div>
                </div>

                <div className="stat-card">
                  <div className="stat-icon">🏆</div>
                  <div className="stat-content">
                    <div className="stat-value text-sm">{stats.mostUsedTool}</div>
                    <div className="stat-label">Top Tool</div>
                  </div>
                </div>
              </section>

              {/* Recent Activity - Cleaner */}
              <section className="recent-activity">
                <div className="section-header">
                  <h2>📌 Recent Conversions</h2>
                  <button className="btn-link" onClick={() => setActiveTab('history')}>
                    View All →
                  </button>
                </div>

                {conversions.length === 0 ? (
                  <div className="empty-state">
                    <p>📂 No conversions yet</p>
                    <button className="btn-primary" onClick={handleNewConversion}>
                      Start Your First Conversion
                    </button>
                  </div>
                ) : (
                  <div className="conversion-list">
                    {conversions.slice(0, 5).map((conversion) => (
                      <div key={conversion.id} className="conversion-item">
                        <div className="conversion-left">
                          <span className="status-badge">{conversion.status === 'completed' ? '✅' : '⏳'}</span>
                          <div className="conversion-details">
                            <div className="conversion-name">{conversion.filename}</div>
                            <div className="conversion-meta">
                              {conversion.from} → {conversion.to} ({conversion.size})
                            </div>
                          </div>
                        </div>
                        <div className="conversion-right">
                          <div className="conversion-time text-muted">
                            {conversion.date} {conversion.time}
                          </div>
                          <button 
                            className="btn-icon"
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

              {/* Quick Actions - Simplified */}
              <section className="quick-actions">
                <h3>❓ Need Help?</h3>
                <div className="actions-grid">
                  <a href="#docs" className="action-card">
                    <span className="action-icon">📖</span>
                    <span>Documentation</span>
                  </a>
                  <a href="#support" className="action-card">
                    <span className="action-icon">💬</span>
                    <span>Contact Support</span>
                  </a>
                  <a href="#api" className="action-card">
                    <span className="action-icon">🔌</span>
                    <span>API Reference</span>
                  </a>
                  <a href="#upgrade" className="action-card">
                    <span className="action-icon">⭐</span>
                    <span>Upgrade Plan</span>
                  </a>
                </div>
              </section>
            </>
          )}

          {activeTab === 'history' && (
            <section className="history-section">
              <h2>📜 Conversion History</h2>
              
              {/* Enhanced Filters */}
              <div className="history-controls">
                <div className="search-box">
                  <input 
                    type="text" 
                    placeholder="🔍 Search by filename..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="search-input"
                    aria-label="Search conversions"
                  />
                </div>
                <select 
                  value={filterFormat}
                  onChange={(e) => setFilterFormat(e.target.value)}
                  className="filter-select"
                  aria-label="Filter by format"
                >
                  <option value="all">All Formats</option>
                  <option value="pdf">PDF</option>
                  <option value="jpg">JPG</option>
                  <option value="xlsx">XLSX</option>
                  <option value="pptx">PPTX</option>
                </select>
              </div>

              {/* Filtered List */}
              {filteredConversions.length === 0 ? (
                <div className="empty-state">
                  <p>🔍 No conversions found</p>
                  <p className="text-muted">Try adjusting your filters</p>
                </div>
              ) : (
                <div className="conversion-list">
                  {filteredConversions.map((conversion) => (
                    <div key={conversion.id} className="conversion-item">
                      <div className="conversion-left">
                        <span className="status-badge">{conversion.status === 'completed' ? '✅' : '⏳'}</span>
                        <div className="conversion-details">
                          <div className="conversion-name">{conversion.filename}</div>
                          <div className="conversion-meta">
                            {conversion.from} → {conversion.to} ({conversion.size})
                          </div>
                        </div>
                      </div>
                      <div className="conversion-right">
                        <div className="conversion-time text-muted">
                          {conversion.date} {conversion.time}
                        </div>
                        <button 
                          className="btn-icon"
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
              
              <div className="history-footer text-muted text-center">
                Showing {filteredConversions.length} of {conversions.length} conversions
              </div>
            </section>
          )}

          {activeTab === 'storage' && (
            <section className="storage-section">
              <h2>💾 Storage Management</h2>
              <div className="storage-details">
                <div className="storage-main">
                  <div className="storage-info">
                    <div className="storage-bar large">
                      <div className="storage-fill" style={{ width: '23%' }}></div>
                    </div>
                    <p className="storage-text">2.3 GB / 100 GB (23% used)</p>
                    
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
                  <button className="btn-primary">⭐ Upgrade to 1TB</button>
                </div>

                <div className="storage-note">
                  <p><strong>💡 Tip:</strong> Keep your storage organized by regularly deleting old conversions you no longer need.</p>
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
