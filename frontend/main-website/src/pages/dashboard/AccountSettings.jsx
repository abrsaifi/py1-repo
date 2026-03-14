import React, { useEffect, useState } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import { useToast } from '@shared/components/Toast'
import { useNavigate } from 'react-router-dom'
import '../../styles/dashboard.css'

const AccountSettings = () => {
  const navigate = useNavigate()
  const { addToast } = useToast()
  const [activeTab, setActiveTab] = useState('security')
  const [loading, setLoading] = useState(true)
  const [billingProfile, setBillingProfile] = useState({
    card: {
      brand: '',
      last4: '',
      expiry_month: '',
      expiry_year: '',
      holder: '',
      status: '',
    },
    billingAddressForm: {
      name: '',
      line1: '',
      line2: '',
      country: '',
    },
    taxInfoForm: {
      taxId: '',
      taxExemption: 'Not applicable',
    },
  })

  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })

  const [twoFactor, setTwoFactor] = useState(false)
  const [sessions, setSessions] = useState([])
  const [apiKeys, setApiKeys] = useState([])
  const [connectedApps, setConnectedApps] = useState([])
  const [privacySettings, setPrivacySettings] = useState({
    analytics_opt_in: true,
    marketing_opt_in: true,
    personalization_opt_in: true,
    deletion_requested_at: null,
  })

  const getAuthHeaders = (includeJson = false) => {
    const headers = {
      Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
    }

    if (includeJson) {
      headers['Content-Type'] = 'application/json'
    }

    return headers
  }

  const formatDateLabel = (value) => {
    if (!value) {
      return 'Never'
    }

    const parsed = new Date(value)
    if (Number.isNaN(parsed.getTime())) {
      return value
    }

    return parsed.toISOString().slice(0, 10)
  }

  const loadAccountSettings = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/account/settings', {
        headers: getAuthHeaders(),
      })
      const payload = await response.json()

      if (!response.ok) {
        throw new Error(payload.error || 'Failed to load account settings')
      }

      setTwoFactor(Boolean(payload.preferences?.two_factor_enabled))
      setPrivacySettings({
        analytics_opt_in: Boolean(payload.preferences?.analytics_opt_in ?? true),
        marketing_opt_in: Boolean(payload.preferences?.marketing_opt_in ?? true),
        personalization_opt_in: Boolean(payload.preferences?.personalization_opt_in ?? true),
        deletion_requested_at: payload.preferences?.deletion_requested_at || null,
      })
      setSessions(payload.sessions || [])
      setApiKeys(payload.api_keys || [])
      setConnectedApps(payload.connected_apps || [])
      setBillingProfile(payload.billing_profile || {
        card: { brand: '', last4: '', expiry_month: '', expiry_year: '', holder: '', status: '' },
        billingAddressForm: { name: '', line1: '', line2: '', country: '' },
        taxInfoForm: { taxId: '', taxExemption: 'Not applicable' },
      })
    } catch (error) {
      addToast({ type: 'error', title: 'Settings unavailable', message: error.message })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAccountSettings()
  }, [])

  const updatePreferences = async (nextValues, successMessage) => {
    const response = await fetch('/api/account/preferences', {
      method: 'POST',
      headers: getAuthHeaders(true),
      body: JSON.stringify(nextValues),
    })
    const payload = await response.json()

    if (!response.ok) {
      throw new Error(payload.error || 'Failed to update preferences')
    }

    if (Object.prototype.hasOwnProperty.call(nextValues, 'two_factor_enabled')) {
      setTwoFactor(Boolean(nextValues.two_factor_enabled))
    }

    setPrivacySettings((current) => ({
      ...current,
      ...payload.preferences,
    }))

    addToast({ type: 'success', title: 'Preferences updated', message: successMessage })
  }

  const handlePasswordChange = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      addToast({ type: 'error', title: 'Password update failed', message: 'Passwords do not match' })
      return
    }
    if (passwordData.newPassword.length < 8) {
      addToast({ type: 'error', title: 'Password update failed', message: 'Password must be at least 8 characters' })
      return
    }

    try {
      const response = await fetch('/api/account/change-password', {
        method: 'POST',
        headers: getAuthHeaders(true),
        body: JSON.stringify({
          current_password: passwordData.currentPassword,
          new_password: passwordData.newPassword,
        }),
      })
      const payload = await response.json()

      if (!response.ok) {
        throw new Error(payload.error || 'Failed to update password')
      }

      addToast({ type: 'success', title: 'Password updated', message: payload.message || 'Your password was changed successfully' })
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' })
    } catch (error) {
      addToast({ type: 'error', title: 'Password update failed', message: error.message })
    }
  }

  const handleLogoutSession = async (sessionId) => {
    try {
      const response = await fetch(`/api/account/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      })
      const payload = await response.json()

      if (!response.ok) {
        throw new Error(payload.error || 'Failed to end session')
      }

      setSessions((current) => current.filter((session) => session.id !== sessionId))
      addToast({ type: 'success', title: 'Session ended', message: payload.message || 'The selected session has been logged out' })
    } catch (error) {
      addToast({ type: 'error', title: 'Session update failed', message: error.message })
    }
  }

  const handleCopyApiKey = (key) => {
    if (!key) {
      addToast({ type: 'info', title: 'Full key unavailable', message: 'Only newly generated keys can be copied in full. Store new keys when they are created.' })
      return
    }
    navigator.clipboard.writeText(key)
    addToast({ type: 'success', title: 'API key copied', message: 'The API key has been copied to your clipboard' })
  }

  const handleToggleTwoFactor = async () => {
    try {
      await updatePreferences(
        { two_factor_enabled: !twoFactor },
        twoFactor ? 'Two-factor authentication disabled' : 'Two-factor authentication enabled'
      )
    } catch (error) {
      addToast({ type: 'error', title: 'Security update failed', message: error.message })
    }
  }

  const handleGenerateApiKey = async () => {
    try {
      const response = await fetch('/api/account/api-keys', {
        method: 'POST',
        headers: getAuthHeaders(true),
        body: JSON.stringify({ name: `Generated Key ${apiKeys.length + 1}` }),
      })
      const payload = await response.json()

      if (!response.ok) {
        throw new Error(payload.error || 'Failed to generate API key')
      }

      setApiKeys((current) => [{ ...payload.api_key, last_used: 'Never' }, ...current])
      addToast({ type: 'success', title: 'API key generated', message: 'A new API key has been created. Copy it now and store it securely.' })
    } catch (error) {
      addToast({ type: 'error', title: 'API key generation failed', message: error.message })
    }
  }

  const handleDeleteApiKey = async (keyId) => {
    try {
      const response = await fetch(`/api/account/api-keys/${keyId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      })
      const payload = await response.json()

      if (!response.ok) {
        throw new Error(payload.error || 'Failed to delete API key')
      }

      setApiKeys((current) => current.filter((key) => key.id !== keyId))
      addToast({ type: 'success', title: 'API key deleted', message: payload.message || 'The API key was removed' })
    } catch (error) {
      addToast({ type: 'error', title: 'API key deletion failed', message: error.message })
    }
  }

  const handleToggleConnectedApp = async (appId) => {
    try {
      const response = await fetch(`/api/account/apps/${appId}/toggle`, {
        method: 'POST',
        headers: getAuthHeaders(),
      })
      const payload = await response.json()

      if (!response.ok) {
        throw new Error(payload.error || 'Failed to update integration')
      }

      setConnectedApps((current) => current.map((app) => (
        app.id === appId ? payload.connected_app : app
      )))
      addToast({ type: 'success', title: 'Integration updated', message: payload.message || 'Connected application status changed' })
    } catch (error) {
      addToast({ type: 'error', title: 'Integration update failed', message: error.message })
    }
  }

  const handlePrivacyToggle = async (field) => {
    const nextValue = !privacySettings[field]
    try {
      await updatePreferences({ [field]: nextValue }, 'Privacy preferences saved')
    } catch (error) {
      addToast({ type: 'error', title: 'Privacy update failed', message: error.message })
    }
  }

  const handleDeleteAccount = async () => {
    try {
      const response = await fetch('/api/account/delete-request', {
        method: 'POST',
        headers: getAuthHeaders(),
      })
      const payload = await response.json()

      if (!response.ok) {
        throw new Error(payload.error || 'Failed to request account deletion')
      }

      setPrivacySettings((current) => ({
        ...current,
        deletion_requested_at: payload.requested_at,
      }))
      addToast({ type: 'warning', title: 'Deletion requested', message: payload.message || 'Support will follow up shortly.' })
      navigate('/dashboard')
    } catch (error) {
      addToast({ type: 'error', title: 'Deletion request failed', message: error.message })
    }
  }

  const updateBillingProfileSection = (section, field, value) => {
    setBillingProfile((current) => ({
      ...current,
      [section]: {
        ...current[section],
        [field]: value,
      },
    }))
  }

  const handleSaveBillingProfile = async () => {
    try {
      const response = await fetch('/api/account/billing-profile', {
        method: 'POST',
        headers: getAuthHeaders(true),
        body: JSON.stringify({
          card: billingProfile.card,
          billingAddress: billingProfile.billingAddressForm,
          taxInfo: billingProfile.taxInfoForm,
        }),
      })
      const payload = await response.json()

      if (!response.ok) {
        throw new Error(payload.error || 'Failed to update billing profile')
      }

      setBillingProfile(payload.billing_profile || billingProfile)
      addToast({ type: 'success', title: 'Billing profile updated', message: payload.message || 'Your billing details were saved.' })
    } catch (error) {
      addToast({ type: 'error', title: 'Billing update failed', message: error.message })
    }
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
          className={`nav-tab ${activeTab === 'billing' ? 'active' : ''}`}
          onClick={() => setActiveTab('billing')}
        >
          <UniversalIcon icon="💳" size={16} /> Billing
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
        {/* Content */}
        <div className="settings-content">
          {loading && (
            <section className="settings-section">
              <h2>Loading account settings...</h2>
              <p className="section-desc">Fetching security, API, and privacy data.</p>
            </section>
          )}

          {/* Security Tab */}
          {!loading && activeTab === 'security' && (
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
          {!loading && activeTab === 'sessions' && (
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
                      {session.is_current && <span className="badge success">Current Device</span>}
                    </div>
                    {!session.is_current && (
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
          {!loading && activeTab === 'api' && (
            <section className="settings-section">
              <h2>API Keys</h2>
              <p className="section-desc">Use API keys to authenticate with our API</p>
              
              <button className="btn-primary" style={{ marginBottom: '20px' }} onClick={handleGenerateApiKey}>
                + Generate New API Key
              </button>

              <div className="api-keys-list">
                {apiKeys.map((apiKey) => (
                  <div key={apiKey.id} className="api-key-card">
                    <div className="api-key-info">
                      <div className="api-key-name">{apiKey.name}</div>
                      <div className="api-key-value" onClick={() => handleCopyApiKey(apiKey.key)}>
                        {(apiKey.key || apiKey.key_preview || 'Unavailable')}{' '}
                        <span className="copy-hint">Click to copy</span>
                      </div>
                      <div className="api-key-meta">
                        Created: {formatDateLabel(apiKey.created_at)} • Last used: {apiKey.last_used || 'Never'}
                      </div>
                    </div>
                    <div className="api-key-actions">
                      <span className={`badge ${apiKey.is_active ? 'success' : 'danger'}`}>
                        {apiKey.is_active ? 'Active' : 'Inactive'}
                      </span>
                      <button className="btn-secondary small" onClick={() => handleDeleteApiKey(apiKey.id)}>Delete</button>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Connected Apps Tab */}
          {!loading && activeTab === 'apps' && (
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
                    <button className="btn-secondary small" onClick={() => handleToggleConnectedApp(app.id)}>
                      {app.connected ? 'Disconnect' : 'Connect'}
                    </button>
                  </div>
                ))}
              </div>
            </section>
          )}

          {!loading && activeTab === 'billing' && (
            <section className="settings-section">
              <h2>Billing Details</h2>
              <p className="section-desc">Manage the payment summary, billing address, and tax information shown on your subscriber dashboard.</p>

              <div className="setting-card">
                <div className="card-header">
                  <h3>Payment Method Summary</h3>
                  <span className="card-desc">Stored locally until a billing provider is connected</span>
                </div>
                <div className="form-group full">
                  <label>Card Brand</label>
                  <input value={billingProfile.card.brand} onChange={(e) => updateBillingProfileSection('card', 'brand', e.target.value)} placeholder="Visa" />
                </div>
                <div className="form-group full">
                  <label>Last 4 Digits</label>
                  <input value={billingProfile.card.last4} onChange={(e) => updateBillingProfileSection('card', 'last4', e.target.value.replace(/\D/g, '').slice(-4))} placeholder="4242" />
                </div>
                <div className="form-group full">
                  <label>Card Holder</label>
                  <input value={billingProfile.card.holder} onChange={(e) => updateBillingProfileSection('card', 'holder', e.target.value)} placeholder="Jane Doe" />
                </div>
                <div className="form-group full">
                  <label>Expiry Month</label>
                  <input value={billingProfile.card.expiry_month} onChange={(e) => updateBillingProfileSection('card', 'expiry_month', e.target.value.replace(/\D/g, '').slice(0, 2))} placeholder="03" />
                </div>
                <div className="form-group full">
                  <label>Expiry Year</label>
                  <input value={billingProfile.card.expiry_year} onChange={(e) => updateBillingProfileSection('card', 'expiry_year', e.target.value.replace(/\D/g, '').slice(0, 4))} placeholder="2027" />
                </div>
                <div className="form-group full">
                  <label>Status Note</label>
                  <input value={billingProfile.card.status} onChange={(e) => updateBillingProfileSection('card', 'status', e.target.value)} placeholder="Primary payment method on file." />
                </div>
              </div>

              <div className="setting-card">
                <div className="card-header">
                  <h3>Billing Address</h3>
                  <span className="card-desc">Used in the subscriber billing summary and invoice context</span>
                </div>
                <div className="form-group full">
                  <label>Name</label>
                  <input value={billingProfile.billingAddressForm.name} onChange={(e) => updateBillingProfileSection('billingAddressForm', 'name', e.target.value)} placeholder="Jane Doe" />
                </div>
                <div className="form-group full">
                  <label>Address Line 1</label>
                  <input value={billingProfile.billingAddressForm.line1} onChange={(e) => updateBillingProfileSection('billingAddressForm', 'line1', e.target.value)} placeholder="123 Main Street" />
                </div>
                <div className="form-group full">
                  <label>Address Line 2</label>
                  <input value={billingProfile.billingAddressForm.line2} onChange={(e) => updateBillingProfileSection('billingAddressForm', 'line2', e.target.value)} placeholder="Suite 400" />
                </div>
                <div className="form-group full">
                  <label>Country</label>
                  <input value={billingProfile.billingAddressForm.country} onChange={(e) => updateBillingProfileSection('billingAddressForm', 'country', e.target.value)} placeholder="United States" />
                </div>
              </div>

              <div className="setting-card">
                <div className="card-header">
                  <h3>Tax Information</h3>
                  <span className="card-desc">Keep VAT, GST, or exemption metadata with the account</span>
                </div>
                <div className="form-group full">
                  <label>Tax ID</label>
                  <input value={billingProfile.taxInfoForm.taxId} onChange={(e) => updateBillingProfileSection('taxInfoForm', 'taxId', e.target.value)} placeholder="VAT-123456" />
                </div>
                <div className="form-group full">
                  <label>Tax Exemption</label>
                  <input value={billingProfile.taxInfoForm.taxExemption} onChange={(e) => updateBillingProfileSection('taxInfoForm', 'taxExemption', e.target.value)} placeholder="Not applicable" />
                </div>
              </div>

              <button className="btn-primary" onClick={handleSaveBillingProfile}>Save Billing Details</button>
            </section>
          )}

          {/* Privacy Tab */}
          {!loading && activeTab === 'privacy' && (
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
                    <input type="checkbox" checked={privacySettings.analytics_opt_in} onChange={() => handlePrivacyToggle('analytics_opt_in')} />
                  </div>
                  <div className="privacy-option">
                    <div>
                      <div className="privacy-title">Marketing</div>
                      <div className="privacy-desc">Allow promotional communications</div>
                    </div>
                    <input type="checkbox" checked={privacySettings.marketing_opt_in} onChange={() => handlePrivacyToggle('marketing_opt_in')} />
                  </div>
                  <div className="privacy-option">
                    <div>
                      <div className="privacy-title">Personalization</div>
                      <div className="privacy-desc">Customize experience based on activity</div>
                    </div>
                    <input type="checkbox" checked={privacySettings.personalization_opt_in} onChange={() => handlePrivacyToggle('personalization_opt_in')} />
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
                {privacySettings.deletion_requested_at && (
                  <p className="section-desc">Deletion requested on {formatDateLabel(privacySettings.deletion_requested_at)}.</p>
                )}
                <button className="btn-danger" onClick={handleDeleteAccount}>Delete Account</button>
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
