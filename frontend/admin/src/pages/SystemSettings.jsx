import React, { useState, useEffect } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'

const SystemSettings = () => {
  const [settings, setSettings] = useState({
    appName: 'Analytics Dashboard',
    appVersion: '1.0.0',
    environment: 'production',
    maintenanceMode: false,
    maxLoginAttempts: 5,
    sessionTimeout: 30,
    enableTwoFactor: false,
    enableAuditLogging: true,
    dataRetention: 90,
    backupFrequency: 'daily',
    emailNotifications: true,
    apiRateLimit: 1000,
    maxFileUploadSize: 50,
    // Feature Toggles
    enableConversions: true,
    enableAnalytics: true,
    enableSEO: true,
    enableWorkers: true,
    enableAutomation: true,
    // Integration Settings
    smtpServer: 'smtp.gmail.com',
    smtpPort: 587,
    smtpUsername: '',
    smtpPassword: '',
    enableCloudStorage: false,
    cloudStorageType: 'aws',
    // Branding
    appLogo: 'logo.png',
    appBrandColor: '#667eea',
    appCompanyName: 'Analytics Inc.',
    // Advanced Settings
    enableDebugMode: false,
    enableVerboseLogging: false,
    logLevel: 'info',
    enableMetrics: true,
    enableHealthChecks: true,
    // API Quotas per Subscription Plan
    freeQuota: 100,
    starterQuota: 500,
    proQuota: 5000,
    enterpriseQuota: 'unlimited',
    // User Tier Management
    defaultUserTier: 'free',
    allowTierUpgrade: true,
    autoDowngradeOnQuotaExceed: false,
    // Database
    databaseType: 'postgresql',
    databaseStatus: 'connected',
    enableAutoMigration: true
  })

  const [savedMessage, setSavedMessage] = useState('')
  const [activeSection, setActiveSection] = useState('general')

  useEffect(() => {
    // Load settings from localStorage
    const stored = localStorage.getItem('system-settings')
    if (stored) {
      setSettings(JSON.parse(stored))
    }
  }, [])

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }))
  }

  const handleSaveSettings = () => {
    localStorage.setItem('system-settings', JSON.stringify(settings))
    setSavedMessage('Settings saved successfully!')
    setTimeout(() => setSavedMessage(''), 3000)
  }

  return (
    <div className="system-settings">
      <div className="management-header">
        <h2><UniversalIcon icon="⚙️" size={24} /> System Settings</h2>
        <button className="btn-primary" onClick={handleSaveSettings}>
          <UniversalIcon icon="💾" size={16} /> Save Settings
        </button>
      </div>

      {savedMessage && <div className="success-message">{savedMessage}</div>}

      <div className="settings-container">
        <aside className="settings-menu">
          {[
            { id: 'general', label: 'General', icon: '🔧' },
            { id: 'security', label: 'Security', icon: '🔐' },
            { id: 'performance', label: 'Performance', icon: '⚡' },
            { id: 'notifications', label: 'Notifications', icon: '🔔' },
            { id: 'features', label: 'Features', icon: '✨' },
            { id: 'integrations', label: 'Integrations', icon: '🔗' },
            { id: 'branding', label: 'Branding', icon: '🎨' },
            { id: 'advanced', label: 'Advanced', icon: '🛠️' },
            { id: 'quotas', label: 'API Quotas', icon: '📊' },
            { id: 'tiers', label: 'User Tiers', icon: '👥' },
            { id: 'database', label: 'Database', icon: '🗄️' },
            { id: 'maintenance', label: 'Maintenance', icon: '🔧' }
          ].map(section => (
            <button
              key={section.id}
              className={`settings-menu-item ${activeSection === section.id ? 'active' : ''}`}
              onClick={() => setActiveSection(section.id)}
            >
              <span className="icon"><UniversalIcon icon={section.icon} size={18} /></span>
              <span>{section.label}</span>
            </button>
          ))}
        </aside>

        <main className="settings-content">
          {activeSection === 'general' && (
            <div className="settings-section">
              <h3>General Settings</h3>
              <div className="setting-group">
                <label>Application Name</label>
                <input
                  type="text"
                  value={settings.appName}
                  onChange={(e) => handleSettingChange('appName', e.target.value)}
                  className="form-input"
                />
              </div>
              <div className="setting-group">
                <label>Version</label>
                <input
                  type="text"
                  value={settings.appVersion}
                  readOnly
                  className="form-input"
                  disabled
                />
              </div>
              <div className="setting-group">
                <label>Environment</label>
                <select
                  value={settings.environment}
                  onChange={(e) => handleSettingChange('environment', e.target.value)}
                  className="form-input"
                >
                  <option value="development">Development</option>
                  <option value="staging">Staging</option>
                  <option value="production">Production</option>
                </select>
              </div>
            </div>
          )}

          {activeSection === 'security' && (
            <div className="settings-section">
              <h3>Security Settings</h3>
              <div className="setting-group">
                <label>Max Login Attempts</label>
                <input
                  type="number"
                  value={settings.maxLoginAttempts}
                  onChange={(e) => handleSettingChange('maxLoginAttempts', parseInt(e.target.value))}
                  className="form-input"
                  min="1"
                  max="10"
                />
              </div>
              <div className="setting-group">
                <label>Session Timeout (minutes)</label>
                <input
                  type="number"
                  value={settings.sessionTimeout}
                  onChange={(e) => handleSettingChange('sessionTimeout', parseInt(e.target.value))}
                  className="form-input"
                  min="5"
                  max="480"
                />
              </div>
              <div className="setting-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.enableTwoFactor}
                    onChange={(e) => handleSettingChange('enableTwoFactor', e.target.checked)}
                  />
                  Enable Two-Factor Authentication
                </label>
              </div>
              <div className="setting-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.enableAuditLogging}
                    onChange={(e) => handleSettingChange('enableAuditLogging', e.target.checked)}
                  />
                  Enable Audit Logging
                </label>
              </div>
              <div className="setting-group">
                <label>API Rate Limit (requests/hour)</label>
                <input
                  type="number"
                  value={settings.apiRateLimit}
                  onChange={(e) => handleSettingChange('apiRateLimit', parseInt(e.target.value))}
                  className="form-input"
                  min="100"
                />
              </div>
            </div>
          )}

          {activeSection === 'performance' && (
            <div className="settings-section">
              <h3>Performance Settings</h3>
              <div className="setting-group">
                <label>Data Retention (days)</label>
                <input
                  type="number"
                  value={settings.dataRetention}
                  onChange={(e) => handleSettingChange('dataRetention', parseInt(e.target.value))}
                  className="form-input"
                  min="30"
                  max="3650"
                />
              </div>
              <div className="setting-group">
                <label>Backup Frequency</label>
                <select
                  value={settings.backupFrequency}
                  onChange={(e) => handleSettingChange('backupFrequency', e.target.value)}
                  className="form-input"
                >
                  <option value="hourly">Hourly</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>
              <div className="setting-group">
                <label>Max File Upload Size (MB)</label>
                <input
                  type="number"
                  value={settings.maxFileUploadSize}
                  onChange={(e) => handleSettingChange('maxFileUploadSize', parseInt(e.target.value))}
                  className="form-input"
                  min="1"
                  max="500"
                />
              </div>
            </div>
          )}

          {activeSection === 'notifications' && (
            <div className="settings-section">
              <h3>Notification Settings</h3>
              <div className="setting-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.emailNotifications}
                    onChange={(e) => handleSettingChange('emailNotifications', e.target.checked)}
                  />
                  Enable Email Notifications
                </label>
              </div>
              <div className="setting-info">
                <p>Email notifications will be sent for:</p>
                <ul>
                  <li>Critical system alerts</li>
                  <li>Failed backup notifications</li>
                  <li>Security incidents</li>
                  <li>Scheduled report deliveries</li>
                </ul>
              </div>
            </div>
          )}

          {activeSection === 'maintenance' && (
            <div className="settings-section">
              <h3>Maintenance Settings</h3>
              <div className="setting-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.maintenanceMode}
                    onChange={(e) => handleSettingChange('maintenanceMode', e.target.checked)}
                  />
                  Enable Maintenance Mode
                </label>
              </div>
              <div className="setting-info">
                <p>When enabled, the system will be in maintenance mode and users will see a maintenance message.</p>
              </div>
              <hr />
              <div className="maintenance-actions">
                <h4>Maintenance Tasks</h4>
                <button className="btn-secondary"><UniversalIcon icon="🗑️" size={16} /> Clear Cache</button>
                <button className="btn-secondary"><UniversalIcon icon="🔄" size={16} /> Rebuild Database</button>
                <button className="btn-secondary"><UniversalIcon icon="📊" size={16} /> Generate Report</button>
                <button className="btn-warning"><UniversalIcon icon="⚠️" size={18} /> Reset All Settings</button>
              </div>
            </div>
          )}

          {activeSection === 'features' && (
            <div className="settings-section">
              <h3>Feature Toggles</h3>
              <p className="setting-info-text">Enable or disable major system features globally.</p>
              <div className="setting-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.enableConversions}
                    onChange={(e) => handleSettingChange('enableConversions', e.target.checked)}
                  />
                  Enable Conversions Module
                </label>
                <small>File conversion and format transformation features</small>
              </div>
              <div className="setting-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.enableAnalytics}
                    onChange={(e) => handleSettingChange('enableAnalytics', e.target.checked)}
                  />
                  Enable Analytics Module
                </label>
                <small>Dashboard metrics and reporting</small>
              </div>
              <div className="setting-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.enableSEO}
                    onChange={(e) => handleSettingChange('enableSEO', e.target.checked)}
                  />
                  Enable SEO Engine
                </label>
                <small>SEO page generation and optimization</small>
              </div>
              <div className="setting-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.enableWorkers}
                    onChange={(e) => handleSettingChange('enableWorkers', e.target.checked)}
                  />
                  Enable Background Workers
                </label>
                <small>Celery worker processing and job queuing</small>
              </div>
              <div className="setting-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.enableAutomation}
                    onChange={(e) => handleSettingChange('enableAutomation', e.target.checked)}
                  />
                  Enable Automation (n8n)
                </label>
                <small>Workflow automation and scheduled tasks</small>
              </div>
            </div>
          )}

          {activeSection === 'integrations' && (
            <div className="settings-section">
              <h3>Integration Settings</h3>
              
              <h4 style={{marginTop: '20px'}}><UniversalIcon icon="📧" size={18} /> Email (SMTP)</h4>
              <div className="setting-group">
                <label>SMTP Server</label>
                <input
                  type="text"
                  value={settings.smtpServer}
                  onChange={(e) => handleSettingChange('smtpServer', e.target.value)}
                  className="form-input"
                  placeholder="smtp.gmail.com"
                />
              </div>
              <div className="setting-group">
                <label>SMTP Port</label>
                <input
                  type="number"
                  value={settings.smtpPort}
                  onChange={(e) => handleSettingChange('smtpPort', parseInt(e.target.value))}
                  className="form-input"
                  min="1"
                  max="65535"
                />
              </div>
              <div className="setting-group">
                <label>Username</label>
                <input
                  type="text"
                  value={settings.smtpUsername}
                  onChange={(e) => handleSettingChange('smtpUsername', e.target.value)}
                  className="form-input"
                  placeholder="your-email@example.com"
                />
              </div>
              <div className="setting-group">
                <label>Password</label>
                <input
                  type="password"
                  value={settings.smtpPassword}
                  onChange={(e) => handleSettingChange('smtpPassword', e.target.value)}
                  className="form-input"
                />
              </div>
              <button className="btn-secondary" style={{marginTop: '10px'}}><UniversalIcon icon="✉️" size={16} /> Test Email Connection</button>

              <hr style={{margin: '20px 0'}} />
              
              <h4><UniversalIcon icon="☁️" size={18} /> Cloud Storage</h4>
              <div className="setting-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.enableCloudStorage}
                    onChange={(e) => handleSettingChange('enableCloudStorage', e.target.checked)}
                  />
                  Enable Cloud Storage Integration
                </label>
              </div>
              {settings.enableCloudStorage && (
                <div className="setting-group">
                  <label>Cloud Storage Type</label>
                  <select
                    value={settings.cloudStorageType}
                    onChange={(e) => handleSettingChange('cloudStorageType', e.target.value)}
                    className="form-input"
                  >
                    <option value="aws">AWS S3</option>
                    <option value="azure">Azure Blob</option>
                    <option value="gcs">Google Cloud Storage</option>
                    <option value="minio">MinIO</option>
                  </select>
                </div>
              )}
              <button className="btn-secondary"><UniversalIcon icon="🧪" size={16} /> Test Cloud Connection</button>
            </div>
          )}

          {activeSection === 'branding' && (
            <div className="settings-section">
              <h3>Branding Settings</h3>
              <div className="setting-group">
                <label>Company Name</label>
                <input
                  type="text"
                  value={settings.appCompanyName}
                  onChange={(e) => handleSettingChange('appCompanyName', e.target.value)}
                  className="form-input"
                />
              </div>
              <div className="setting-group">
                <label>Application Logo (URL)</label>
                <input
                  type="text"
                  value={settings.appLogo}
                  onChange={(e) => handleSettingChange('appLogo', e.target.value)}
                  className="form-input"
                  placeholder="https://example.com/logo.png"
                />
              </div>
              <div className="setting-group">
                <label>Brand Color (Hex)</label>
                <div style={{display: 'flex', gap: '10px'}}>
                  <input
                    type="color"
                    value={settings.appBrandColor}
                    onChange={(e) => handleSettingChange('appBrandColor', e.target.value)}
                    className="form-input"
                    style={{width: '60px', cursor: 'pointer'}}
                  />
                  <input
                    type="text"
                    value={settings.appBrandColor}
                    onChange={(e) => handleSettingChange('appBrandColor', e.target.value)}
                    className="form-input"
                    placeholder="#667eea"
                  />
                </div>
              </div>
            </div>
          )}

          {activeSection === 'advanced' && (
            <div className="settings-section">
              <h3>Advanced Settings</h3>
              <div className="setting-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.enableDebugMode}
                    onChange={(e) => handleSettingChange('enableDebugMode', e.target.checked)}
                  />
                  Enable Debug Mode
                </label>
                <small>Enable detailed error messages and diagnostic information</small>
              </div>
              <div className="setting-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.enableVerboseLogging}
                    onChange={(e) => handleSettingChange('enableVerboseLogging', e.target.checked)}
                  />
                  Enable Verbose Logging
                </label>
                <small>Log all API requests and system events</small>
              </div>
              <div className="setting-group">
                <label>Log Level</label>
                <select
                  value={settings.logLevel}
                  onChange={(e) => handleSettingChange('logLevel', e.target.value)}
                  className="form-input"
                >
                  <option value="debug">Debug</option>
                  <option value="info">Info</option>
                  <option value="warning">Warning</option>
                  <option value="error">Error</option>
                </select>
              </div>
              <div className="setting-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.enableMetrics}
                    onChange={(e) => handleSettingChange('enableMetrics', e.target.checked)}
                  />
                  Enable Performance Metrics
                </label>
              </div>
              <div className="setting-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.enableHealthChecks}
                    onChange={(e) => handleSettingChange('enableHealthChecks', e.target.checked)}
                  />
                  Enable Health Checks
                </label>
              </div>
            </div>
          )}

          {activeSection === 'quotas' && (
            <div className="settings-section">
              <h3>API Quotas per Subscription Plan</h3>
              <p className="setting-info-text">Configure API request limits for each subscription tier.</p>
              
              <div className="setting-group">
                <label>Free Plan - API Quota (requests/month)</label>
                <input
                  type="number"
                  value={settings.freeQuota}
                  onChange={(e) => handleSettingChange('freeQuota', parseInt(e.target.value))}
                  className="form-input"
                  min="10"
                />
                <small>Basic file conversions and limited API access</small>
              </div>

              <div className="setting-group">
                <label>Starter Plan - API Quota (requests/month)</label>
                <input
                  type="number"
                  value={settings.starterQuota}
                  onChange={(e) => handleSettingChange('starterQuota', parseInt(e.target.value))}
                  className="form-input"
                  min="100"
                />
                <small>Enhanced conversions and basic analytics</small>
              </div>

              <div className="setting-group">
                <label>Professional Plan - API Quota (requests/month)</label>
                <input
                  type="number"
                  value={settings.proQuota}
                  onChange={(e) => handleSettingChange('proQuota', parseInt(e.target.value))}
                  className="form-input"
                  min="1000"
                />
                <small>Full API access, analytics, SEO, workers</small>
              </div>

              <div className="setting-group">
                <label>Enterprise Plan - API Quota</label>
                <select
                  value={settings.enterpriseQuota}
                  onChange={(e) => handleSettingChange('enterpriseQuota', e.target.value)}
                  className="form-input"
                >
                  <option value="unlimited">Unlimited</option>
                  <option value="50000">50,000 requests/month</option>
                  <option value="100000">100,000 requests/month</option>
                  <option value="500000">500,000 requests/month</option>
                </select>
                <small>Highest tier with all features and custom limits</small>
              </div>

              <button className="btn-secondary" style={{marginTop: '10px'}}><UniversalIcon icon="📊" size={16} /> View Quota Usage</button>
              <button className="btn-secondary"><UniversalIcon icon="🔄" size={16} /> Reset Quota Counters</button>
            </div>
          )}

          {activeSection === 'tiers' && (
            <div className="settings-section">
              <h3>User Tier Management</h3>
              <p className="setting-info-text">Manage user subscription tiers and upgrade policies.</p>
              
              <div className="setting-group">
                <label>Default User Tier</label>
                <select
                  value={settings.defaultUserTier}
                  onChange={(e) => handleSettingChange('defaultUserTier', e.target.value)}
                  className="form-input"
                >
                  <option value="free">Free</option>
                  <option value="starter">Starter</option>
                  <option value="pro">Professional</option>
                  <option value="enterprise">Enterprise</option>
                </select>
                <small>Tier assigned to new users on signup</small>
              </div>

              <div className="setting-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.allowTierUpgrade}
                    onChange={(e) => handleSettingChange('allowTierUpgrade', e.target.checked)}
                  />
                  Allow Users to Upgrade Tier
                </label>
                <small>Enable self-service tier upgrades</small>
              </div>

              <div className="setting-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.autoDowngradeOnQuotaExceed}
                    onChange={(e) => handleSettingChange('autoDowngradeOnQuotaExceed', e.target.checked)}
                  />
                  Auto-Downgrade on Quota Exceed
                </label>
                <small>Automatically downgrade users who exceed their quota</small>
              </div>

              <hr style={{margin: '20px 0'}} />
              
              <h4><UniversalIcon icon="📊" size={18} /> Tier Pricing Configuration</h4>
              <div className="tier-list" style={{marginTop: '15px'}}>
                <div className="tier-item" style={{padding: '12px', border: '1px solid #eee', marginBottom: '10px', borderRadius: '4px'}}>
                  <strong>Free</strong> - $0/month
                  <small style={{display: 'block', marginTop: '4px', color: '#666'}}>100 requests/month, Limited features</small>
                </div>
                <div className="tier-item" style={{padding: '12px', border: '1px solid #eee', marginBottom: '10px', borderRadius: '4px'}}>
                  <strong>Starter</strong> - $9/month
                  <small style={{display: 'block', marginTop: '4px', color: '#666'}}>500 requests/month, Basic analytics</small>
                </div>
                <div className="tier-item" style={{padding: '12px', border: '1px solid #eee', marginBottom: '10px', borderRadius: '4px'}}>
                  <strong>Professional</strong> - $49/month
                  <small style={{display: 'block', marginTop: '4px', color: '#666'}}>5,000 requests/month, Full features</small>
                </div>
                <div className="tier-item" style={{padding: '12px', border: '1px solid #eee', marginBottom: '10px', borderRadius: '4px'}}>
                  <strong>Enterprise</strong> - Custom
                  <small style={{display: 'block', marginTop: '4px', color: '#666'}}>Unlimited requests, Priority support</small>
                </div>
              </div>

              <button className="btn-secondary" style={{marginTop: '10px'}}><UniversalIcon icon="👥" size={16} /> View All Users by Tier</button>
              <button className="btn-secondary"><UniversalIcon icon="📈" size={16} /> Manage Tier Pricing</button>
            </div>
          )}

          {activeSection === 'database' && (
            <div className="settings-section">
              <h3>Database Management</h3>
              <div className="setting-group">
                <label>Database Type</label>
                <select
                  value={settings.databaseType}
                  onChange={(e) => handleSettingChange('databaseType', e.target.value)}
                  className="form-input"
                  disabled
                >
                  <option value="postgresql">PostgreSQL</option>
                  <option value="mysql">MySQL</option>
                  <option value="mongodb">MongoDB</option>
                  <option value="sqlite">SQLite</option>
                </select>
              </div>
              <div className="setting-group">
                <label>Database Status</label>
                <input
                  type="text"
                  value={settings.databaseStatus}
                  className="form-input"
                  disabled
                  style={{
                    background: settings.databaseStatus === 'connected' ? '#d4edda' : '#f8d7da',
                    color: settings.databaseStatus === 'connected' ? '#155724' : '#721c24'
                  }}
                />
              </div>
              <div className="setting-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.enableAutoMigration}
                    onChange={(e) => handleSettingChange('enableAutoMigration', e.target.checked)}
                  />
                  Enable Auto Migration
                </label>
                <small>Automatically apply schema migrations</small>
              </div>
              <button className="btn-secondary" style={{marginTop: '10px'}}><UniversalIcon icon="🔗" size={16} /> Test Connection</button>
              <button className="btn-secondary"><UniversalIcon icon="📊" size={16} /> Optimize Database</button>
              <button className="btn-warning" style={{marginLeft: '10px'}}><UniversalIcon icon="⚠️" size={18} /> Backup Database</button>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default SystemSettings
