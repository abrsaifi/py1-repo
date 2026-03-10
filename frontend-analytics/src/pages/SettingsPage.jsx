import { useState, useEffect } from 'react'
import { UniversalIcon } from '../utils/UniversalIcon'
import '../styles/pages.css'

export const SettingsPage = ({ onTitleChange }) => {
  const [activeTab, setActiveTab] = useState('api')
  const [settings, setSettings] = useState({
    apiBaseUrl: localStorage.getItem('apiBaseUrl') || 'http://localhost:5009',
    theme: localStorage.getItem('theme') || 'light',
    autoRefresh: localStorage.getItem('autoRefresh') === 'true',
    refreshInterval: localStorage.getItem('refreshInterval') || '30',
    dateFormat: localStorage.getItem('dateFormat') || 'MM/DD/YYYY',
    timezone: localStorage.getItem('timezone') || 'UTC',
  })

  const [saved, setSaved] = useState(false)

  const handleChange = (field, value) => {
    setSettings(prev => ({
      ...prev,
      [field]: value,
    }))
  }

  const handleSave = () => {
    Object.entries(settings).forEach(([key, value]) => {
      localStorage.setItem(key, value)
    })
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  useEffect(() => {
    onTitleChange('Settings')
  }, [onTitleChange])

  return (
    <div className="settings-page">
      {saved && (
        <div className="alert-success-minimal">
          <UniversalIcon icon="fas fa-check-circle" size={20} /> Saved
        </div>
      )}

      <nav className="nav-container settings-nav">
        <button
          className={`nav-tab ${activeTab === 'api' ? 'active' : ''}`}
          onClick={() => setActiveTab('api')}
        >
          <UniversalIcon icon="🔌" size={18} /> API
        </button>
        <button
          className={`nav-tab ${activeTab === 'display' ? 'active' : ''}`}
          onClick={() => setActiveTab('display')}
        >
          <UniversalIcon icon="🔨" size={18} /> Display
        </button>
        <button
          className={`nav-tab ${activeTab === 'refresh' ? 'active' : ''}`}
          onClick={() => setActiveTab('refresh')}
        >
          <UniversalIcon icon="⟳" size={16} /> Auto-Refresh
        </button>
        <div style={{ marginLeft: 'auto' }} />
      </nav>

      <div className="settings-content">
        {activeTab === 'api' && (
          <div className="settings-card">
            <div className="card-title">API Configuration</div>
            <div className="form-group">
              <label>Base URL</label>
              <input
                type="text"
                value={settings.apiBaseUrl}
                onChange={(e) => handleChange('apiBaseUrl', e.target.value)}
                placeholder="http://localhost:5000"
              />
            </div>
          </div>
        )}

        {activeTab === 'display' && (
          <div className="settings-card">
            <div className="card-title">Display Preferences</div>
            <div className="form-group">
              <label>Theme</label>
              <select
                value={settings.theme}
                onChange={(e) => handleChange('theme', e.target.value)}
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
                <option value="auto">Auto</option>
              </select>
            </div>

            <div className="form-group">
              <label>Date Format</label>
              <select
                value={settings.dateFormat}
                onChange={(e) => handleChange('dateFormat', e.target.value)}
              >
                <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                <option value="YYYY-MM-DD">YYYY-MM-DD</option>
              </select>
            </div>

            <div className="form-group">
              <label>Timezone</label>
              <select
                value={settings.timezone}
                onChange={(e) => handleChange('timezone', e.target.value)}
              >
                <option value="UTC">UTC</option>
                <option value="EST">EST</option>
                <option value="CST">CST</option>
                <option value="MST">MST</option>
                <option value="PST">PST</option>
              </select>
            </div>
          </div>
        )}

        {activeTab === 'refresh' && (
          <div className="settings-card">
            <div className="card-title">Auto-Refresh Settings</div>
            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={settings.autoRefresh}
                  onChange={(e) => handleChange('autoRefresh', e.target.checked)}
                />
                Enable auto-refresh
              </label>
            </div>

            {settings.autoRefresh && (
              <div className="form-group">
                <label>Interval</label>
                <select
                  value={settings.refreshInterval}
                  onChange={(e) => handleChange('refreshInterval', e.target.value)}
                >
                  <option value="15">15 seconds</option>
                  <option value="30">30 seconds</option>
                  <option value="60">1 minute</option>
                  <option value="300">5 minutes</option>
                  <option value="600">10 minutes</option>
                </select>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="settings-footer">
        <button className="btn-save" onClick={handleSave}>
          <UniversalIcon icon="fas fa-save" size={20} /> Save
        </button>
        <button className="btn-reset" onClick={() => window.location.reload()}>
          <UniversalIcon icon="fas fa-redo" size={20} /> Reset
        </button>
      </div>
    </div>
  )
}

export default SettingsPage
