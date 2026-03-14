import React, { useEffect, useState } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import '../styles/admin.css'
import { RoleBadge, StatusBadge } from '@shared/utils/badgeIcons'
import { adminAPI } from '@shared/api/api'

const EmployeeManagement = () => {
  const [filterRole, setFilterRole] = useState('all')
  const [employees, setEmployees] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionMessage, setActionMessage] = useState('')
  const [auditState, setAuditState] = useState({ employee: null, entries: [], loading: false })

  useEffect(() => {
    loadEmployees()
  }, [])

  const loadEmployees = async () => {
    try {
      setError('')
      const response = await adminAPI.getUsers({ per_page: 200 })
      setEmployees(response.data.users || [])
    } catch (loadError) {
      setError(loadError.response?.data?.error || 'Failed to load admin and staff users')
    } finally {
      setLoading(false)
    }
  }

  const getFilteredEmployees = () => {
    switch(filterRole) {
      case 'admin':
        return employees.filter(emp => emp.role === 'admin')
      case 'moderator':
        return employees.filter(emp => emp.role === 'moderator')
      case 'user':
        return employees.filter(emp => emp.role === 'user')
      default:
        return employees
    }
  }

  const setUpdatedEmployee = (updatedEmployee) => {
    setEmployees((currentEmployees) => currentEmployees.map((employee) => employee.id === updatedEmployee.id ? updatedEmployee : employee))
  }

  const handleChangeRole = async (employee, newRole) => {
    try {
      const response = await adminAPI.updateUser(employee.id, { role: newRole })
      setUpdatedEmployee(response.data.user)
      setActionMessage(`${response.data.user.name} is now assigned to ${newRole}.`)
    } catch (actionError) {
      setActionMessage(actionError.response?.data?.error || 'Failed to update role')
    }
  }

  const handleToggleStatus = async (employee) => {
    try {
      const response = await adminAPI.updateUser(employee.id, { is_active: employee.status !== 'active' })
      setUpdatedEmployee(response.data.user)
      setActionMessage(`${response.data.user.name} is now ${response.data.user.status}.`)
    } catch (actionError) {
      setActionMessage(actionError.response?.data?.error || 'Failed to update status')
    }
  }

  const handleResetPassword = async (employee) => {
    try {
      const response = await adminAPI.resetUserPassword(employee.id)
      setActionMessage(`Temporary password for ${employee.name}: ${response.data.temporaryPassword}`)
    } catch (actionError) {
      setActionMessage(actionError.response?.data?.error || 'Failed to reset password')
    }
  }

  const handleViewAudit = async (employee) => {
    setAuditState({ employee, entries: [], loading: true })
    try {
      const response = await adminAPI.getActivityFeed({ limit: 25, user_id: employee.id, period_days: 90 })
      setAuditState({ employee, entries: response.data.entries || [], loading: false })
    } catch (auditError) {
      setActionMessage(auditError.response?.data?.error || 'Failed to load audit history')
      setAuditState({ employee: null, entries: [], loading: false })
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      active: { color: '#11998e', text: '✅ Active' },
      suspended: { color: '#eb3349', text: '🔴 Suspended' }
    }
    return badges[status] || badges.suspended
  }

  const filteredEmployees = getFilteredEmployees()

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="👨‍💼" size={24} /> Admin & Staff</h2>
      <p className="section-subtitle">Live role assignment, account status changes, password resets, and recent staff activity</p>

      {error && <div className="no-data"><p>{error}</p></div>}
      {actionMessage && <div className="no-data"><p>{actionMessage}</p></div>}

      <div className="filter-controls">
        <label>Filter by Role:</label>
        <select value={filterRole} onChange={(e) => setFilterRole(e.target.value)}>
          <option value="all">All Employees ({employees.length})</option>
          <option value="admin">Admin ({employees.filter(e => e.role === 'admin').length})</option>
          <option value="moderator">Moderator ({employees.filter(e => e.role === 'moderator').length})</option>
          <option value="user">User ({employees.filter(e => e.role === 'user').length})</option>
        </select>
      </div>

      <div className="jobs-table-wrapper">
        <table className="jobs-table">
          <thead>
            <tr>
              <th>Employee ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Department</th>
              <th>Status</th>
              <th>Join Date</th>
              <th>Last Login</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="9" style={{ textAlign: 'center', padding: '20px' }}>Loading employees...</td>
              </tr>
            ) : filteredEmployees.map(emp => {
              const statusBadge = getStatusBadge(emp.status)
              return (
                <tr key={emp.id} className={`job-row ${emp.status}`}>
                  <td className="job-id"><code>{emp.displayId}</code></td>
                  <td><strong>{emp.name}</strong></td>
                  <td>{emp.email}</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <RoleBadge role={emp.role} />
                      <select value={emp.role} onChange={(e) => handleChangeRole(emp, e.target.value)}>
                        <option value="user">user</option>
                        <option value="moderator">moderator</option>
                        <option value="admin">admin</option>
                      </select>
                    </div>
                  </td>
                  <td>
                    <span className="format-badge">{emp.department}</span>
                  </td>
                  <td>
                    <StatusBadge status={emp.status} text={statusBadge.text} style={{ backgroundColor: statusBadge.color }} />
                  </td>
                  <td className="timestamp">{emp.signupDate}</td>
                  <td className="timestamp">{emp.lastActivity || 'No recent activity'}</td>
                  <td className="actions">
                    <button 
                      className="action-btn logs" 
                      onClick={() => handleToggleStatus(emp)} 
                      title={emp.status === 'active' ? 'Suspend' : 'Reactivate'}
                    >
                      {emp.status === 'active' ? <UniversalIcon icon="🔒" size={14} /> : <UniversalIcon icon="🔓" size={14} />}
                    </button>
                    <button 
                      className="action-btn" 
                      style={{ background: 'linear-gradient(135deg, #f6ad55 0%, #ed8936 100%)', color: 'white' }}
                      onClick={() => handleResetPassword(emp)} 
                      title="Reset Password"
                    >
                      <UniversalIcon icon="🔑" size={14} />
                    </button>
                    <button 
                      className="action-btn cancel" 
                      onClick={() => handleViewAudit(emp)} 
                      title="View Audit"
                    >
                      <UniversalIcon icon="📋" size={14} />
                    </button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {filteredEmployees.length === 0 && (
        <div className="no-data">
          <p>No employees match the selected role</p>
        </div>
      )}

      {auditState.employee && (
        <div className="modal-overlay">
          <div className="modal-content modal-large">
            <div className="modal-header">
              <h3>Recent activity for {auditState.employee.name}</h3>
              <button className="close-btn" onClick={() => setAuditState({ employee: null, entries: [], loading: false })}>×</button>
            </div>
            <div className="modal-body">
              {auditState.loading ? (
                <p>Loading audit entries...</p>
              ) : auditState.entries.length ? (
                <table className="jobs-table">
                  <thead>
                    <tr>
                      <th>Timestamp</th>
                      <th>Action</th>
                      <th>Resource</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {auditState.entries.map((entry) => (
                      <tr key={entry.id}>
                        <td>{new Date(entry.timestamp).toLocaleString()}</td>
                        <td>{entry.action.replace(/-/g, ' ')}</td>
                        <td>{entry.resourceName || entry.resourceType || '-'}</td>
                        <td>{entry.status}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p>No audit activity found for this user.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default EmployeeManagement
