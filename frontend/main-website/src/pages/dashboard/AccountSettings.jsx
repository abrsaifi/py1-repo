import React, { useState } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import { useNavigate } from 'react-router-dom'
import '../../styles/dashboard.css'

const AccountSettings = () => {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('security')
  const [message, setMessage] = useState('')

  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })

  const [twoFactor, setTwoFactor] = useState(false)
  const [sessions, setSessions] = useState([
    {
      id: 1,
      device: 'Chrome on Windows',
      location: 'San Francisco, CA',
      ip: '192.168.1.100',
      lastActive: '2 minutes ago',
      isCurrent: true
    },
    {
      id: 2,
      device: 'Safari on iPhone',
      location: 'San Francisco, CA',
      ip: '203.0.113.45',
      lastActive: '2 hours ago',
      isCurrent: false
    },
    {
      id: 3,
      device: 'Firefox on Mac',
      location: 'New York, NY',
      ip: '192.168.1.50',
      lastActive: '1 day ago',
      isCurrent: false
    }
  ])

  const [apiKeys, setApiKeys] = useState([
    {
      id: 1,
      name: 'Production API Key',
      key: 'sk_prod_xxxxxxxxxxxxxxxx',
      created: '2024-01-15',
      lastUsed: '2024-03-06',
      active: true
    },
    {
      id: 2,
      name: 'Test API Key',
      key: 'sk_test_yyyyyyyyyyyyyyyy',
      created: '2024-02-01',
      lastUsed: '2024-03-05',
      active: true
    }
  ])

  const [connectedApps, setConnectedApps] = useState([
    { id: 1, name: 'Zapier', icon: '⚙️', connected: true, lastUsed: '2024-03-05' },
    { id: 2, name: 'IFTTT', icon: '🔗', connected: false, lastUsed: 'Never' },
    { id: 3, name: 'Slack', icon: '💬', connected: true, lastUsed: '2024-03-04' }
  ])

  const handlePasswordChange = () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setMessage('Passwords do not match')
      return
    }
    if (passwordData.newPassword.length < 8) {
      setMessage('Password must be at least 8 characters')
      return
    }
    setMessage('Password changed successfully!')
    setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' })
    setTimeout(() => setMessage(''), 3000)
  }

  const handleLogoutSession = (sessionId) => {
    setSessions(sessions.filter(s => s.id !== sessionId))
    setMessage('Session logged out')
    setTimeout(() => setMessage(''), 2000)
  }

  const handleCopyApiKey = (key) => {
    navigator.clipboard.writeText(key)
    setMessage('API key copied to clipboard')
    setTimeout(() => setMessage(''), 2000)
  }

  const handleToggleTwoFactor = () => {
    setTwoFactor(!twoFactor)
    setMessage(twoFactor ? '✅ 2FA disabled' : '✅ 2FA enabled')
    setTimeout(() => setMessage(''), 2000)
  }

  return (
    <div className="user-dashboard">
      {/* Settings Navigation - Outside Container */}
      <nav className="nav-container settings-nav">
        <button 
          className={`nav-tab ${activeTab === 'security' ? 'active' : ''}`}
          onClick={() => setActiveTab('security')}
        >
          <UniversalIcon icon="🔒" size={16} /> Security
        </button>
        <button 
          className={`nav-tab ${activeTab === 'sessions' ? 'active' : ''}`}
          onClick={() => setActiveTab('sessions')}
        >
          <UniversalIcon icon="📱" size={16} /> Sessions
        </button>
        <button 
          className={`nav-tab ${activeTab === 'api' ? 'active' : ''}`}
          onClick={() => setActiveTab('api')}
        >
          <UniversalIcon icon="🔌" size={16} /> API Keys
        </button>
        <button 
          className={`nav-tab ${activeTab === 'apps' ? 'active' : ''}`}
          onClick={() => setActiveTab('apps')}
        >
          <UniversalIcon icon="🔗" size={16} /> Connected Apps
        </button>
        <button 
          className={`nav-tab ${activeTab === 'privacy' ? 'active' : ''}`}
          onClick={() => setActiveTab('privacy')}
        >
          <UniversalIcon icon="👁" size={16} /> Privacy
        </button>
        <div style={{ marginLeft: 'auto' }} />
      </nav>

      <div className="settings-container">
        {message && <div className="alert-success-minimal">{message}</div>}

        {/* Content */}
        <div className="settings-content">
          {/* Security Tab */}
          {activeTab === 'security' && (
            <section className="settings-section">
              <h2>Password & Security</h2>

              {/* Change Password */}
              <div className="setting-card">
                <div className="card-header">
                  <h3>Change Password</h3>
                  <span className="card-desc">Update your password regularly for better security</span>
                </div>
                <div className="form-group full">
                  <label>Current Password</label>
                  <input 
                    type="password"
                    value={passwordData.currentPassword}
                    onChange={(e) => setPasswordData({...passwordData, currentPassword: e.target.value})}
                    placeholder="Enter current password"
                  />
                </div>
                <div className="form-group full">
                  <label>New Password</label>
                  <input 
                    type="password"
                    value={passwordData.newPassword}
                    onChange={(e) => setPasswordData({...passwordData, newPassword: e.target.value})}
                    placeholder="Enter new password (min 8 characters)"
                  />
                </div>
                <div className="form-group full">
                  <label>Confirm Password</label>
                  <input 
                    type="password"
                    value={passwordData.confirmPassword}
                    onChange={(e) => setPasswordData({...passwordData, confirmPassword: e.target.value})}
                    placeholder="Confirm new password"
                  />
                </div>
                <button className="btn-primary" onClick={handlePasswordChange}>
                  Update Password
                </button>
              </div>

              {/* Two-Factor Authentication */}
              <div className="setting-card">
                <div className="card-header">
                  <h3>Two-Factor Authentication</h3>
                  <span className="card-desc">Add an extra layer of security to your account</span>
                </div>
                <div className="setting-item">
                  <div>
                    <div className="setting-title">Enable 2FA</div>
                    <div className="setting-desc">Require authentication code on login</div>
                  </div>
                  <input 
                    type="checkbox" 
                    checked={twoFactor}
                    onChange={handleToggleTwoFactor}
                  />
                </div>
                {twoFactor && (
                  <div className="info-box">
                    <UniversalIcon icon="ℹ" size={16} /> You will receive authentication codes via SMS or authenticator app
                  </div>
                )}
              </div>

              {/* Login History */}
              <div className="setting-card">
                <div className="card-header">
                  <h3>Recent Login Activity</h3>
                  <span className="card-desc">Review your recent account access</span>
                </div>
                <div className="login-history">
                  <div className="history-item">
                    <div className="history-info">
                      <div className="history-device"><UniversalIcon icon="✅" size={14} /> Chrome on Windows</div>
                      <div className="history-location">San Francisco, CA • 192.168.1.1</div>
                      <div className="history-time">Today at 2:30 PM</div>
                    </div>
                    <span className="badge success">Current</span>
                  </div>
                  <div className="history-item">
                    <div className="history-info">
                      <div className="history-device">Safari on iPhone</div>
                      <div className="history-location">San Francisco, CA • 203.0.113.45</div>
                      <div className="history-time">Today at 10:15 AM</div>
                    </div>
                    <span className="badge">Successful</span>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Sessions Tab */}
          {activeTab === 'sessions' && (
            <section className="settings-section">
              <h2>Active Sessions</h2>
              <div className="session-list">
                {sessions.map((session) => (
                  <div key={session.id} className="session-card">
                    <div className="session-info">
                      <div className="session-device">{session.device}</div>
                      <div className="session-meta">
                        <UniversalIcon icon="📍" size={14} /> {session.location} • {session.ip}
                      </div>
                      <div className="session-time">Last active: {session.lastActive}</div>
                      {session.isCurrent && <span className="badge success">Current Device</span>}
                    </div>
                    {!session.isCurrent && (
                      <button 
                        className="btn-secondary small"
                        onClick={() => handleLogoutSession(session.id)}
                      >
                        Logout
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* API Keys Tab */}
          {activeTab === 'api' && (
            <section className="settings-section">
              <h2>API Keys</h2>
              <p className="section-desc">Use API keys to authenticate with our API</p>
              
              <button className="btn-primary" style={{ marginBottom: '20px' }}>
                + Generate New API Key
              </button>

              <div className="api-keys-list">
                {apiKeys.map((apiKey) => (
                  <div key={apiKey.id} className="api-key-card">
                    <div className="api-key-info">
                      <div className="api-key-name">{apiKey.name}</div>
                      <div className="api-key-value" onClick={() => handleCopyApiKey(apiKey.key)}>
                        {apiKey.key.substring(0, 15)}...{' '}
                        <span className="copy-hint">Click to copy</span>
                      </div>
                      <div className="api-key-meta">
                        Created: {apiKey.created} • Last used: {apiKey.lastUsed}
                      </div>
                    </div>
                    <div className="api-key-actions">
                      <span className={`badge ${apiKey.active ? 'success' : 'danger'}`}>
                        {apiKey.active ? 'Active' : 'Inactive'}
                      </span>
                      <button className="btn-secondary small">Delete</button>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Connected Apps Tab */}
          {activeTab === 'apps' && (
            <section className="settings-section">
              <h2>Connected Applications</h2>
              <p className="section-desc">Manage third-party app integrations</p>

              <div className="apps-list">
                {connectedApps.map((app) => (
                  <div key={app.id} className="app-card">
                    <div className="app-info">
                      <div className="app-icon">{app.icon}</div>
                      <div>
                        <div className="app-name">{app.name}</div>
                        <div className="app-status">
                          {app.connected ? 
                            `Connected • Last used: ${app.lastUsed}` : 
                            `Not connected`
                          }
                        </div>
                      </div>
                    </div>
                    <button className="btn-secondary small">
                      {app.connected ? 'Disconnect' : 'Connect'}
                    </button>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Privacy Tab */}
          {activeTab === 'privacy' && (
            <section className="settings-section">
              <h2>Privacy & Data</h2>

              <div className="setting-card">
                <div className="card-header">
                  <h3>Data Sharing</h3>
                  <span className="card-desc">Control how your data is used</span>
                </div>
                <div className="privacy-options">
                  <div className="privacy-option">
                    <div>
                      <div className="privacy-title">Analytics</div>
                      <div className="privacy-desc">Help us improve with usage analytics</div>
                    </div>
                    <input type="checkbox" defaultChecked />
                  </div>
                  <div className="privacy-option">
                    <div>
                      <div className="privacy-title">Marketing</div>
                      <div className="privacy-desc">Allow promotional communications</div>
                    </div>
                    <input type="checkbox" defaultChecked />
                  </div>
                  <div className="privacy-option">
                    <div>
                      <div className="privacy-title">Personalization</div>
                      <div className="privacy-desc">Customize experience based on activity</div>
                    </div>
                    <input type="checkbox" defaultChecked />
                  </div>
                </div>
              </div>

              <div className="setting-card danger">
                <div className="card-header">
                  <h3>Delete Account</h3>
                  <span className="card-desc">Permanently remove your account and data</span>
                </div>
                <p className="danger-text">
                  <UniversalIcon icon="⚠️" size={16} /> This action cannot be undone. All your data will be permanently deleted.
                </p>
                <button className="btn-danger">Delete Account</button>
              </div>
            </section>
          )}
        </div>
      </div>

      <style>{`
        .user-dashboard {
          display: flex;
          flex-direction: column;
        }

        .settings-nav {
          display: flex;
          flex-direction: row;
          flex-wrap: wrap;
          gap: 16px;
          padding: 0 20px;
          margin: 0;
          background: white;
          border-bottom: 2px solid #e0e0e0;
          align-items: center;
          width: 100%;
          order: -1;
        }

        .settings-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 30px 20px;
          width: 100%;
        }

        .alert-success-minimal {
          display: flex;
          align-items: center;
          padding: 12px 16px;
          margin-bottom: 20px;
          background-color: #d1fae5;
          color: #065f46;
          border-radius: 6px;
          font-size: 14px;
          font-weight: 500;
          animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .nav-tab {
          padding: 12px 16px;
          background: none;
          border: none;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          color: #666;
          border-bottom: 2px solid transparent;
          transition: all 0.2s ease;
          white-space: nowrap;
        }

        .nav-tab:hover {
          color: #333;
        }

        .nav-tab.active {
          color: #3b82f6;
          border-bottom-color: #3b82f6;
        }

        .settings-content {
          background: white;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }

        .settings-section {
          padding: 30px;
        }

        .settings-section h2 {
          margin: 0 0 25px 0;
          font-size: 22px;
          color: #1a1a1a;
        }

        .section-desc {
          color: #666;
          margin-bottom: 20px;
        }

        .setting-card {
          padding: 20px;
          background: #f9f9f9;
          border-radius: 8px;
          margin-bottom: 20px;
          border: 1px solid #e0e0e0;
        }

        .setting-card.danger {
          border-color: #ffcdd2;
          background: #fff5f5;
        }

        .card-header h3 {
          margin: 0 0 4px 0;
          color: #1a1a1a;
        }

        .card-desc {
          font-size: 13px;
          color: #666;
        }

        .form-group {
          margin-bottom: 16px;
        }

        .form-group label {
          display: block;
          font-weight: 600;
          margin-bottom: 6px;
          color: #333;
          font-size: 14px;
        }

        .form-group input {
          width: 100%;
          padding: 10px 12px;
          border: 1px solid #ddd;
          border-radius: 6px;
          font-size: 14px;
          font-family: inherit;
          transition: all 0.2s ease;
        }

        .form-group input:focus {
          outline: none;
          border-color: #667eea;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .setting-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 0;
          border-bottom: 1px solid #e0e0e0;
        }

        .setting-item:last-child {
          border-bottom: none;
        }

        .setting-title {
          font-weight: 600;
          color: #333;
        }

        .setting-desc {
          font-size: 13px;
          color: #666;
          margin-top: 2px;
        }

        .info-box {
          background: #e3f2fd;
          border-left: 4px solid #2196f3;
          padding: 12px;
          border-radius: 4px;
          margin-top: 12px;
          color: #1565c0;
          font-size: 13px;
        }

        .login-history {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .history-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px;
          background: white;
          border-radius: 6px;
          border: 1px solid #e0e0e0;
        }

        .history-device {
          font-weight: 600;
          color: #333;
        }

        .history-location {
          font-size: 12px;
          color: #666;
          margin: 4px 0;
        }

        .history-time {
          font-size: 12px;
          color: #999;
        }

        .session-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .session-card {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px;
          background: white;
          border: 1px solid #e0e0e0;
          border-radius: 8px;
        }

        .session-device {
          font-weight: 600;
          color: #333;
        }

        .session-meta {
          font-size: 12px;
          color: #666;
          margin: 4px 0;
        }

        .session-time {
          font-size: 12px;
          color: #999;
        }

        .api-keys-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .api-key-card {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px;
          background: white;
          border: 1px solid #e0e0e0;
          border-radius: 8px;
        }

        .api-key-name {
          font-weight: 600;
          color: #333;
          margin-bottom: 4px;
        }

        .api-key-value {
          font-family: monospace;
          color: #667eea;
          cursor: pointer;
          font-size: 13px;
          padding: 4px 8px;
          background: #f5f5f5;
          border-radius: 4px;
          margin-bottom: 4px;
          display: inline-block;
          transition: all 0.2s ease;
        }

        .api-key-value:hover {
          background: #e0e0e0;
        }

        .copy-hint {
          opacity: 0.6;
          font-size: 11px;
        }

        .api-key-meta {
          font-size: 12px;
          color: #666;
        }

        .apps-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .app-card {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px;
          background: white;
          border: 1px solid #e0e0e0;
          border-radius: 8px;
        }

        .app-info {
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .app-icon {
          font-size: 32px;
        }

        .app-name {
          font-weight: 600;
          color: #333;
        }

        .app-status {
          font-size: 13px;
          color: #666;
          margin-top: 2px;
        }

        .privacy-options {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .privacy-option {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 0;
          border-bottom: 1px solid #e0e0e0;
        }

        .privacy-option:last-child {
          border-bottom: none;
        }

        .privacy-title {
          font-weight: 600;
          color: #333;
        }

        .privacy-desc {
          font-size: 13px;
          color: #666;
          margin-top: 2px;
        }

        .badge {
          display: inline-block;
          padding: 4px 12px;
          border-radius: 4px;
          font-size: 11px;
          font-weight: bold;
          background: #e0e0e0;
          color: #333;
        }

        .badge.success {
          background: #c8e6c9;
          color: #2e7d32;
        }

        .badge.danger {
          background: #ffcdd2;
          color: #c62828;
        }

        .danger-text {
          color: #c62828;
          font-weight: 500;
          margin: 12px 0;
        }

        .btn-danger {
          background: #ef5350;
          color: white;
          border: none;
          padding: 10px 16px;
          border-radius: 6px;
          cursor: pointer;
          font-weight: bold;
          transition: all 0.2s ease;
        }

        .btn-danger:hover {
          background: #e53935;
        }

        .btn-secondary.small {
          padding: 8px 12px;
          font-size: 13px;
        }

        @media (max-width: 768px) {
          .settings-container {
            padding: 20px 12px;
          }

          .settings-nav {
            gap: 8px;
            padding: 0 12px;
            flex-wrap: wrap;
          }

          .nav-tab {
            padding: 10px 12px;
            font-size: 13px;
          }

          .settings-section {
            padding: 20px;
          }

          .session-card,
          .app-card,
          .api-key-card {
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
          }

          .api-key-actions {
            display: flex;
            gap: 8px;
            align-self: flex-end;
          }
        }
      `}</style>
    </div>
  )
}

export default AccountSettings
