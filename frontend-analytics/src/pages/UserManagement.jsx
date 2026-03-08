import React, { useState, useEffect } from 'react'
import '../styles/admin.css'
import { UniversalIcon } from '../utils/UniversalIcon'
import { PlanBadge, StatusBadge } from '../utils/badgeIcons'

const UserManagement = () => {
  const [filterStatus, setFilterStatus] = useState('all') // all, active, suspended
  const [expandedUser, setExpandedUser] = useState(null)
  
  // Feature Access Map by Plan - SUBSCRIBER ONLY (NO BACKEND/ADMIN SERVICES)
  const planFeatures = {
    'Basic': ['Dashboard', 'Basic File Conversions', 'Activity Feed'],
    'Professional': ['Dashboard', 'Full File Conversions', 'Analytics Dashboard', 'Usage & Billing'],
    'Enterprise': ['Dashboard', 'Full File Conversions', 'Advanced Analytics', 'Usage & Billing', 'Priority Support', 'Custom Reports']
  }

  const [users, setUsers] = useState([
    { id: 'USR-001234', email: 'alice@company.com', signupDate: '2025-01-15', totalConversions: 1243, plan: 'Professional', status: 'active', lastActivity: '2026-03-06 14:32' },
    { id: 'USR-001235', email: 'bob@startup.io', signupDate: '2025-03-22', totalConversions: 567, plan: 'Basic', status: 'active', lastActivity: '2026-03-06 13:15' },
    { id: 'USR-001236', email: 'charlie@enterprise.com', signupDate: '2024-11-08', totalConversions: 5421, plan: 'Enterprise', status: 'active', lastActivity: '2026-03-06 14:50' },
    { id: 'USR-001237', email: 'diana@freelance.net', signupDate: '2025-06-10', totalConversions: 234, plan: 'Basic', status: 'suspended', lastActivity: '2026-02-28 09:20' },
    { id: 'USR-001238', email: 'evan@agency.co', signupDate: '2025-02-14', totalConversions: 3456, plan: 'Professional', status: 'active', lastActivity: '2026-03-06 11:45' },
    { id: 'USR-001239', email: 'fiona@corp.com', signupDate: '2024-12-01', totalConversions: 8920, plan: 'Enterprise', status: 'active', lastActivity: '2026-03-06 14:20' },
  ])

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

  const handleSuspendUser = (userId, currentStatus) => {
    const newStatus = currentStatus === 'suspended' ? 'active' : 'suspended'
    alert(`${newStatus === 'suspended' ? 'Suspending' : 'Reactivating'} user: ${userId}`)
    const updated = users.map(u => u.id === userId ? { ...u, status: newStatus } : u)
    setUsers(updated)
  }

  const handleResetUsage = (userId) => {
    alert(`Resetting usage for user: ${userId}`)
  }

  const handleUpgradePlan = (userId) => {
    alert(`Opening upgrade plan dialog for user: ${userId}`)
  }

  const handleViewHistory = (userId) => {
    alert(`Viewing conversion history for user: ${userId}`)
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
      <p className="section-subtitle">Basic user management and subscription overview</p>

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
            {filteredUsers.map(user => {
              const statusInfo = getStatusBadge(user.status)
              const planColor = getPlanColor(user.plan)
              const isExpanded = expandedUser === user.id
              const features = planFeatures[user.plan] || []
              
              return (
                <React.Fragment key={user.id}>
                  <tr className={`job-row ${user.status}`}>
                    <td className="job-id"><code>{user.id}</code></td>
                    <td>{user.email}</td>
                    <td>{user.signupDate}</td>
                    <td><strong>{user.totalConversions.toLocaleString()}</strong></td>
                    <td>
                      <PlanBadge plan={user.plan} style={{ background: `linear-gradient(135deg, ${planColor} 0%, ${adjustBrightness(planColor, -20)} 100%)` }} />
                    </td>
                    <td>
                      <StatusBadge status={user.status} text={statusInfo.text} style={{ backgroundColor: statusInfo.color }} />
                    </td>
                    <td className="timestamp">{user.lastActivity}</td>
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
                        onClick={() => handleSuspendUser(user.id, user.status)} 
                        title={user.status === 'suspended' ? 'Reactivate' : 'Suspend'}
                      >
                        <UniversalIcon icon="🔒" size={16} />
                      </button>
                      <button 
                        className="action-btn logs" 
                        onClick={() => handleResetUsage(user.id)} 
                        title="Reset Usage"
                      >
                        <UniversalIcon icon="↻" size={16} />
                      </button>
                      <button 
                        className="action-btn" 
                        style={{ background: 'linear-gradient(135deg, #11998e 0%, #087c67 100%)', color: 'white' }}
                        onClick={() => handleUpgradePlan(user.id)} 
                        title="Upgrade Plan"
                      >
                        <UniversalIcon icon="⬆" size={16} />
                      </button>
                      <button 
                        className="action-btn cancel" 
                        onClick={() => handleViewHistory(user.id)} 
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
                              <div key={idx} style={{ display: 'flex', alignItems: 'center', padding: '6px 8px', background: '#f5f5f5', borderRadius: '3px' }}>
                                <span style={{ color: '#11998e', marginRight: '6px' }}><UniversalIcon icon="✓" size={14} /></span>
                                <span style={{ fontSize: '13px' }}>{feature}</span>
                              </div>
                            ))}
                          </div>
                          <div style={{ marginTop: '12px', fontSize: '12px', color: '#666' }}>
                            <strong>Plan:</strong> {user.plan} | <strong>Conversions Used:</strong> {user.totalConversions.toLocaleString()} | <strong>Member Since:</strong> {user.signupDate}
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
