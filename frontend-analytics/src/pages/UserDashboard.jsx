import React, { useState, useEffect } from 'react'
import { UniversalIcon } from '../utils/UniversalIcon'
import { useNavigate } from 'react-router-dom'
import '../styles/dashboard.css'

const UserDashboard = () => {
  const navigate = useNavigate()
  const [user, setUser] = useState({
    name: 'John Doe',
    email: 'john@example.com',
    avatar: '👤',
    plan: 'Pro',
    conversionsThisMonth: 42,
    filesProcessed: 156,
    totalStorage: 2.3 // GB
  })
  
  const [stats, setStats] = useState({
    totalConversions: 156,
    conversionsSaved: 2456, // MB saved
    averageConversionTime: 3.2, // seconds
    mostUsedTool: 'PDF to DOCX'
  })

  const [recentConversions, setRecentConversions] = useState([
    {
      id: 1,
      filename: 'document.pdf',
      from: 'PDF',
      to: 'DOCX',
      date: '2024-03-06',
      time: '14:30',
      status: 'completed',
      size: '2.4 MB'
    },
    {
      id: 2,
      filename: 'photo.jpg',
      from: 'JPG',
      to: 'PNG',
      date: '2024-03-06',
      time: '10:15',
      status: 'completed',
      size: '1.8 MB'
    },
    {
      id: 3,
      filename: 'spreadsheet.xlsx',
      from: 'XLSX',
      to: 'PDF',
      date: '2024-03-05',
      time: '16:45',
      status: 'completed',
      size: '0.8 MB'
    },
    {
      id: 4,
      filename: 'presentation.pptx',
      from: 'PPTX',
      to: 'PDF',
      date: '2024-03-05',
      time: '09:20',
      status: 'completed',
      size: '5.2 MB'
    },
    {
      id: 5,
      filename: 'image-batch.zip',
      from: 'Multiple',
      to: 'PDF',
      date: '2024-03-04',
      time: '13:10',
      status: 'completed',
      size: '15.6 MB'
    }
  ])

  const [activeTab, setActiveTab] = useState('overview')

  const handleLogout = () => {
    // Clear authentication and redirect
    navigate('/login')
  }

  const handleViewHistory = () => {
    navigate('/dashboard/history')
  }

  const handleUploadNew = () => {
    navigate('/convert')
  }

  return (
    <div className="user-dashboard">
      {/* Navigation Tabs */}
      <div className="dashboard-nav">
        <div className="nav-container">
          <button 
            className={`nav-tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button 
            className={`nav-tab ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            Conversion History
          </button>
          <button 
            className={`nav-tab ${activeTab === 'storage' ? 'active' : ''}`}
            onClick={() => setActiveTab('storage')}
          >
            Storage
          </button>
          <button 
            className="new-conversion-btn"
            onClick={handleUploadNew}
          >
            <UniversalIcon icon="fas fa-plus" size={20} /> New Conversion
          </button>
        </div>
      </div>

      <div className="dashboard-container">
        {/* Sidebar */}
        <aside className="dashboard-sidebar">
          <div className="sidebar-card">
            <div className="card-header">Current Plan</div>
            <div className="plan-badge pro">{user.plan}</div>
            <p className="plan-desc">Full access to all converters</p>
            <button className="btn-secondary">Manage Plan</button>
          </div>

          <div className="sidebar-card">
            <div className="card-header">Storage Used</div>
            <div className="storage-bar">
              <div className="storage-fill" style={{ width: `${(user.totalStorage / 100) * 100}%` }}></div>
            </div>
            <p className="storage-text">{user.totalStorage.toFixed(1)} GB / 100 GB</p>
            <button className="btn-link">Upgrade Storage</button>
          </div>

          <div className="sidebar-card">
            <div className="card-header">Quick Links</div>
            <ul className="quick-links">
              <li><a href="#help"><UniversalIcon icon="📖" size={18} /> Help Center</a></li>
              <li><a href="#docs"><UniversalIcon icon="📚" size={18} /> Documentation</a></li>
              <li><a href="#support"><UniversalIcon icon="ud83d\udde8" size={18} /> Contact Support</a></li>
              <li><a href="#api"><UniversalIcon icon="🔌" size={18} /> API Docs</a></li>
            </ul>
          </div>
        </aside>

        {/* Main Content */}
        <main className="dashboard-main">
          {activeTab === 'overview' && (
            <>
              {/* Stats Grid */}
              <section className="stats-grid">
                <div className="stat-card">
                  <UniversalIcon icon="📋" size={32} />
                  <div className="stat-content">
                    <div className="stat-value">{stats.totalConversions}</div>
                    <div className="stat-label">Total Conversions</div>
                  </div>
                </div>

                <div className="stat-card">
                  <UniversalIcon icon="💾" size={32} />
                  <div className="stat-content">
                    <div className="stat-value">{stats.conversionsSaved} MB</div>
                    <div className="stat-label">Space Saved</div>
                  </div>
                </div>

                <div className="stat-card">
                  <UniversalIcon icon="⚡" size={32} />
                  <div className="stat-content">
                    <div className="stat-value">{stats.averageConversionTime}s</div>
                    <div className="stat-label">Avg. Speed</div>
                  </div>
                </div>

                <div className="stat-card">
                  <UniversalIcon icon="🏆" size={32} />
                  <div className="stat-content">
                    <div className="stat-value">{stats.mostUsedTool}</div>
                    <div className="stat-label">Most Used</div>
                  </div>
                </div>
              </section>

              {/* Recent Activity */}
              <section className="recent-activity">
                <div className="section-header">
                  <h2>Recent Conversions</h2>
                  <button className="btn-link" onClick={handleViewHistory}>
                    View All →
                  </button>
                </div>

                <div className="conversion-list">
                  {recentConversions.slice(0, 5).map((conversion) => (
                    <div key={conversion.id} className="conversion-item">
                      <div className="conversion-icon">
                        {conversion.status === 'completed' ? <UniversalIcon icon="✅" size={18} /> : <UniversalIcon icon="⏳" size={18} />}
                      </div>
                      <div className="conversion-info">
                        <div className="conversion-name">{conversion.filename}</div>
                        <div className="conversion-meta">
                          {conversion.from} → {conversion.to} • {conversion.size}
                        </div>
                      </div>
                      <div className="conversion-time">
                        <div className="time">{conversion.time}</div>
                        <div className="date">{conversion.date}</div>
                      </div>
                      <button className="btn-icon">↓</button>
                    </div>
                  ))}
                </div>
              </section>

              {/* Premium Features */}
              <section className="premium-features">
                <h2>Premium Features</h2>
                <div className="features-grid">
                  <div className="feature-box">
                    <UniversalIcon icon="🚀" size={48} />
                    <h3>Priority Processing</h3>
                    <p>Get lightning-fast conversion speeds</p>
                  </div>
                  <div className="feature-box">
                    <UniversalIcon icon="📁" size={48} />
                    <h3>Unlimited Storage</h3>
                    <p>Convert and store unlimited files</p>
                  </div>
                  <div className="feature-box">
                    <UniversalIcon icon="🔄" size={48} />
                    <h3>Batch Conversion</h3>
                    <p>Convert multiple files at once</p>
                  </div>
                  <div className="feature-box">
                    <UniversalIcon icon="📧" size={48} />
                    <h3>Email Delivery</h3>
                    <p>Get your files via email</p>
                  </div>
                </div>
              </section>
            </>
          )}

          {activeTab === 'history' && (
            <section className="history-section">
              <h2>Conversion History</h2>
              <div className="history-filters">
                <input 
                  type="text" 
                  placeholder="Search conversions..."
                  className="search-input"
                />
                <select className="filter-select">
                  <option>All Formats</option>
                  <option>PDF</option>
                  <option>Image</option>
                  <option>Document</option>
                </select>
              </div>

              <div className="conversion-list full-width">
                {recentConversions.map((conversion) => (
                  <div key={conversion.id} className="conversion-item">
                    <div className="conversion-icon">
                      {conversion.status === 'completed' ? '✅' : '⏳'}
                    </div>
                    <div className="conversion-info">
                      <div className="conversion-name">{conversion.filename}</div>
                      <div className="conversion-meta">
                        {conversion.from} → {conversion.to} • {conversion.size}
                      </div>
                    </div>
                    <div className="conversion-time">
                      <div className="time">{conversion.time}</div>
                      <div className="date">{conversion.date}</div>
                    </div>
                    <button className="btn-icon">↓</button>
                  </div>
                ))}
              </div>
            </section>
          )}

          {activeTab === 'storage' && (
            <section className="storage-section">
              <h2>Storage Management</h2>
              <div className="storage-details">
                <div className="storage-main">
                  <div className="storage-chart">
                    <div className="storage-ring">
                      <svg viewBox="0 0 100 100">
                        <circle cx="50" cy="50" r="45" fill="none" stroke="#e0e0e0" strokeWidth="8" />
                        <circle 
                          cx="50" 
                          cy="50" 
                          r="45" 
                          fill="none" 
                          stroke="#667eea" 
                          strokeWidth="8"
                          strokeDasharray={`${(user.totalStorage / 100) * 283} 283`}
                        />
                      </svg>
                      <div className="storage-percent">{((user.totalStorage / 100) * 100).toFixed(0)}%</div>
                    </div>
                  </div>

                  <div className="storage-breakdown">
                    <div className="breakdown-item">
                      <span className="breakdown-label">Documents</span>
                      <span className="breakdown-value">0.8 GB</span>
                    </div>
                    <div className="breakdown-item">
                      <span className="breakdown-label">Images</span>
                      <span className="breakdown-value">0.9 GB</span>
                    </div>
                    <div className="breakdown-item">
                      <span className="breakdown-label">PDFs</span>
                      <span className="breakdown-value">0.6 GB</span>
                    </div>
                  </div>
                </div>

                <div className="storage-actions">
                  <button className="btn-secondary">Clear Old Files</button>
                  <button className="btn-secondary">Download All</button>
                  <button className="btn-primary">Upgrade to 1TB</button>
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
