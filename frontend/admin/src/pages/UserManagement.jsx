import React, { useEffect, useState } from 'react'
import '../styles/admin.css'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import { PlanBadge, StatusBadge } from '@shared/utils/badgeIcons'
import { adminAPI } from '@shared/api/api'

const UserManagement = () => {
  const [filterStatus, setFilterStatus] = useState('all')
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionMessage, setActionMessage] = useState('')
  const [expandedUser, setExpandedUser] = useState(null)
  const [historyState, setHistoryState] = useState({ user: null, conversions: [], loading: false })

  const planFeatures = {
    'Basic': ['Dashboard', 'Basic File Conversions', 'Activity Feed'],
    'Professional': ['Dashboard', 'Full File Conversions', 'Analytics Dashboard', 'Usage & Billing'],
    'Enterprise': ['Dashboard', 'Full File Conversions', 'Advanced Analytics', 'Usage & Billing', 'Priority Support', 'Custom Reports']
  }

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    try {
      setError('')
      const response = await adminAPI.getUsers({ per_page: 200 })
      setUsers(response.data.users || [])
    } catch (loadError) {
      setError(loadError.response?.data?.error || 'Failed to load users')
    } finally {
      setLoading(false)
    }
  }

  const getFilteredUsers = () => {
    switch(filterStatus) {
      case 'suspended':
        return users.filter(user => user.status === 'suspended')
      case 'active':
        return users.filter(user => user.status === 'active')
      default:
        return users
    }
  }

  const setUpdatedUser = (updatedUser) => {
    setUsers((currentUsers) => currentUsers.map((user) => user.id === updatedUser.id ? updatedUser : user))
  }

  const handleSuspendUser = async (user) => {
    try {
      const response = await adminAPI.updateUser(user.id, { is_active: user.status !== 'active' })
      setUpdatedUser(response.data.user)
      setActionMessage(`${response.data.user.name} is now ${response.data.user.status}.`)
    } catch (actionError) {
      setActionMessage(actionError.response?.data?.error || 'Failed to update user status')
    }
  }

  const handleResetUsage = async (user) => {
    try {
      const response = await adminAPI.resetUserUsage(user.id)
      setUpdatedUser(response.data.user)
      setActionMessage(`Usage reset for ${response.data.user.name}.`)
    } catch (actionError) {
      setActionMessage(actionError.response?.data?.error || 'Failed to reset usage')
    }
  }

  const getNextPlan = (plan) => {
    const planOrder = ['free', 'pro', 'enterprise']
    const currentIndex = planOrder.indexOf((plan || 'free').toLowerCase())
    return planOrder[(currentIndex + 1) % planOrder.length]
  }

  const handleUpgradePlan = async (user) => {
    try {
      const nextPlan = getNextPlan(user.plan)
      const response = await adminAPI.updateUser(user.id, { plan: nextPlan })
      setUpdatedUser(response.data.user)
      setActionMessage(`${response.data.user.name} moved to ${response.data.user.planLabel}.`)
    } catch (actionError) {
      setActionMessage(actionError.response?.data?.error || 'Failed to change plan')
    }
  }

  const handleViewHistory = async (user) => {
    setHistoryState({ user, conversions: [], loading: true })
    try {
      const response = await adminAPI.getConversions({ user_id: user.id, per_page: 10 })
      setHistoryState({ user, conversions: response.data.conversions || [], loading: false })
    } catch (historyError) {
      setActionMessage(historyError.response?.data?.error || 'Failed to load conversion history')
      setHistoryState({ user: null, conversions: [], loading: false })
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      active: { color: '#11998e', text: '✅ Active' },
      suspended: { color: '#eb3349', text: '🚫 Suspended' }
    }
    return badges[status] || badges.active
  }

  const getPlanColor = (plan) => {
    const colors = {
      'Basic': '#718096',
      'Professional': '#667eea',
      'Enterprise': '#764ba2'
    }
    return colors[plan] || '#718096'
  }

  const filteredUsers = getFilteredUsers()

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="👥" size={24} /> Users</h2>
      <p className="section-subtitle">Live subscriber management, plan updates, and recent conversion history</p>

      {error && <div className="no-data"><p>{error}</p></div>}
      {actionMessage && <div className="no-data"><p>{actionMessage}</p></div>}

      <div className="filter-controls">
        <label>Filter:</label>
        <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
          <option value="all">All Users ({users.length})</option>
          <option value="active">Active ({users.filter(u => u.status === 'active').length})</option>
          <option value="suspended">Suspended ({users.filter(u => u.status === 'suspended').length})</option>
        </select>
      </div>

      <div className="jobs-table-wrapper">
        <table className="jobs-table">
          <thead>
            <tr>
              <th>User ID</th>
              <th>Email</th>
              <th>Signup Date</th>
              <th>Total Conversions</th>
              <th>Plan</th>
              <th>Status</th>
              <th>Last Activity</th>
              <th>Features</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="9" style={{ textAlign: 'center', padding: '20px' }}>Loading users...</td>
              </tr>
            ) : filteredUsers.map(user => {
              const statusInfo = getStatusBadge(user.status)
              const planColor = getPlanColor(user.planLabel)
              const isExpanded = expandedUser === user.id
              const features = planFeatures[user.planLabel] || []
              
              return (
                <React.Fragment key={user.id}>
                  <tr className={`job-row ${user.status}`}>
                    <td className="job-id"><code>{user.displayId}</code></td>
                    <td>{user.email}</td>
                    <td>{user.signupDate}</td>
                    <td><strong>{(user.conversionsCount || 0).toLocaleString()}</strong></td>
                    <td>
                      <PlanBadge plan={user.planLabel} style={{ background: `linear-gradient(135deg, ${planColor} 0%, ${adjustBrightness(planColor, -20)} 100%)` }} />
                    </td>
                    <td>
                      <StatusBadge status={user.status} text={statusInfo.text} style={{ backgroundColor: statusInfo.color }} />
                    </td>
                    <td className="timestamp">{user.lastActivity || 'No recent activity'}</td>
                    <td>
                      <button 
                        className="action-btn" 
                        style={{ background: '#667eea', color: 'white', padding: '4px 8px', fontSize: '12px' }}
                        onClick={() => setExpandedUser(isExpanded ? null : user.id)} 
                        title="View Features"
                      >
                        {isExpanded ? <UniversalIcon icon="▼" size={14} /> : <UniversalIcon icon="▶" size={14} />} {features.length}
                      </button>
                    </td>
                    <td className="actions">
                      <button 
                        className="action-btn retry" 
                        onClick={() => handleSuspendUser(user)} 
                        title={user.status === 'suspended' ? 'Reactivate' : 'Suspend'}
                      >
                        <UniversalIcon icon="🔒" size={16} />
                      </button>
                      <button 
                        className="action-btn logs" 
                        onClick={() => handleResetUsage(user)} 
                        title="Reset Usage"
                      >
                        <UniversalIcon icon="↻" size={16} />
                      </button>
                      <button 
                        className="action-btn" 
                        style={{ background: 'linear-gradient(135deg, #11998e 0%, #087c67 100%)', color: 'white' }}
                        onClick={() => handleUpgradePlan(user)} 
                        title="Upgrade Plan"
                      >
                        <UniversalIcon icon="⬆" size={16} />
                      </button>
                      <button 
                        className="action-btn cancel" 
                        onClick={() => handleViewHistory(user)} 
                        title="View History"
                      >
                        <UniversalIcon icon="📊" size={16} />
                      </button>
                    </td>
                  </tr>
                  
                  {isExpanded && (
                    <tr style={{ background: '#f9f9f9', borderBottom: '2px solid #eee' }}>
                      <td colSpan="9" style={{ padding: '15px 20px' }}>
                        <div style={{ background: 'white', padding: '12px', borderRadius: '4px', border: '1px solid #eee' }}>
                          <strong><UniversalIcon icon="📋" size={16} /> Accessible Features ({features.length}):</strong>
                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '8px', marginTop: '10px' }}>
                            {features.map((feature, idx) => (
                              <div key={`feature-${idx}-${feature}`} style={{ display: 'flex', alignItems: 'center', padding: '6px 8px', background: '#f5f5f5', borderRadius: '3px' }}>
                                <span style={{ color: '#11998e', marginRight: '6px' }}><UniversalIcon icon="✓" size={14} /></span>
                                <span style={{ fontSize: '13px' }}>{feature}</span>
                              </div>
                            ))}
                          </div>
                          <div style={{ marginTop: '12px', fontSize: '12px', color: '#666' }}>
                            <strong>Plan:</strong> {user.planLabel} | <strong>Conversions:</strong> {(user.conversionsCount || 0).toLocaleString()} | <strong>Role:</strong> {user.role} | <strong>Member Since:</strong> {user.signupDate}
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              )
            })}
          </tbody>
        </table>
      </div>

      {filteredUsers.length === 0 && (
        <div className="no-data">
          <p>No users match the selected filter</p>
        </div>
      )}

      {historyState.user && (
        <div className="modal-overlay">
          <div className="modal-content modal-large">
            <div className="modal-header">
              <h3>Recent conversions for {historyState.user.name}</h3>
              <button className="close-btn" onClick={() => setHistoryState({ user: null, conversions: [], loading: false })}>×</button>
            </div>
            <div className="modal-body">
              {historyState.loading ? (
                <p>Loading conversion history...</p>
              ) : historyState.conversions.length ? (
                <table className="jobs-table">
                  <thead>
                    <tr>
                      <th>File</th>
                      <th>Formats</th>
                      <th>Status</th>
                      <th>Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {historyState.conversions.map((conversion) => (
                      <tr key={conversion.id}>
                        <td>{conversion.input_filename || `Conversion ${conversion.id}`}</td>
                        <td>{conversion.input_format} → {conversion.output_format}</td>
                        <td>{conversion.status}</td>
                        <td>{conversion.created_at ? new Date(conversion.created_at).toLocaleString() : '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p>No recent conversions found for this user.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Helper function to adjust brightness of hex colors
const adjustBrightness = (color, percent) => {
  const num = parseInt(color.replace("#", ""), 16);
  const amt = Math.round(2.55 * percent);
  const R = Math.max(0, Math.min(255, (num >> 16) + amt));
  const G = Math.max(0, Math.min(255, (num >> 8 & 0x00FF) + amt));
  const B = Math.max(0, Math.min(255, (num & 0x0000FF) + amt));
  return "#" + (0x1000000 + R * 0x10000 + G * 0x100 + B).toString(16).slice(1);
}

export default UserManagement
