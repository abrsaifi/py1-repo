import React, { useState } from 'react'
import { UniversalIcon } from '../utils/UniversalIcon'
import '../styles/admin.css'

const EmployeeManagement = () => {
  const [filterRole, setFilterRole] = useState('all') // all, admin, manager, analyst, viewer
  const [employees, setEmployees] = useState([
    { id: 'EMP-001', name: 'Admin User', email: 'admin@company.com', role: 'admin', department: 'Management', status: 'active', joinDate: '2024-01-15', lastLogin: '2026-03-06 14:50' },
    { id: 'EMP-002', name: 'John Manager', email: 'john@company.com', role: 'manager', department: 'Operations', status: 'active', joinDate: '2024-01-20', lastLogin: '2026-03-06 14:32' },
    { id: 'EMP-003', name: 'Sarah Analyst', email: 'sarah@company.com', role: 'analyst', department: 'Analytics', status: 'active', joinDate: '2024-02-01', lastLogin: '2026-03-06 13:15' },
    { id: 'EMP-004', name: 'Mike Viewer', email: 'mike@company.com', role: 'viewer', department: 'Support', status: 'inactive', joinDate: '2024-02-10', lastLogin: '2026-02-28 09:20' },
    { id: 'EMP-005', name: 'Lisa Developer', email: 'lisa@company.com', role: 'admin', department: 'Engineering', status: 'active', joinDate: '2024-03-05', lastLogin: '2026-03-06 14:45' },
  ])

  const getFilteredEmployees = () => {
    switch(filterRole) {
      case 'admin':
        return employees.filter(emp => emp.role === 'admin')
      case 'manager':
        return employees.filter(emp => emp.role === 'manager')
      case 'analyst':
        return employees.filter(emp => emp.role === 'analyst')
      case 'viewer':
        return employees.filter(emp => emp.role === 'viewer')
      default:
        return employees
    }
  }

  const handleChangeRole = (empId, newRole) => {
    alert(`Changing role for ${empId} to ${newRole}`)
    const updated = employees.map(e => e.id === empId ? { ...e, role: newRole } : e)
    setEmployees(updated)
  }

  const handleToggleStatus = (empId, currentStatus) => {
    const newStatus = currentStatus === 'active' ? 'inactive' : 'active'
    alert(`${newStatus === 'active' ? 'Activating' : 'Deactivating'} employee: ${empId}`)
    const updated = employees.map(e => e.id === empId ? { ...e, status: newStatus } : e)
    setEmployees(updated)
  }

  const handleResetPassword = (empId) => {
    alert(`Password reset email sent to: ${empId}`)
  }

  const handleViewAudit = (empId) => {
    alert(`Viewing audit log for employee: ${empId}`)
  }

  const getRoleBadge = (role) => {
    const roles = {
      admin: { color: '#eb3349', text: '👑 Admin' },
      manager: { color: '#667eea', text: '📋 Manager' },
      analyst: { color: '#11998e', text: '📊 Analyst' },
      viewer: { color: '#718096', text: '👁️ Viewer' }
    }
    return roles[role] || roles.viewer
  }

  const getStatusBadge = (status) => {
    const badges = {
      active: { color: '#11998e', text: '✅ Active' },
      inactive: { color: '#eb3349', text: '🔴 Inactive' }
    }
    return badges[status] || badges.inactive
  }

  const getDepartmentColor = (dept) => {
    const colors = {
      'Management': '#667eea',
      'Operations': '#11998e',
      'Analytics': '#764ba2',
      'Support': '#f6ad55',
      'Engineering': '#38b2ac'
    }
    return colors[dept] || '#718096'
  }

  const filteredEmployees = getFilteredEmployees()

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="👨‍💼" size={24} /> Admin & Staff</h2>
      <p className="section-subtitle">Internal team member management and role assignment</p>

      <div className="filter-controls">
        <label>Filter by Role:</label>
        <select value={filterRole} onChange={(e) => setFilterRole(e.target.value)}>
          <option value="all">All Employees ({employees.length})</option>
          <option value="admin">Admin ({employees.filter(e => e.role === 'admin').length})</option>
          <option value="manager">Manager ({employees.filter(e => e.role === 'manager').length})</option>
          <option value="analyst">Analyst ({employees.filter(e => e.role === 'analyst').length})</option>
          <option value="viewer">Viewer ({employees.filter(e => e.role === 'viewer').length})</option>
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
            {filteredEmployees.map(emp => {
              const roleBadge = getRoleBadge(emp.role)
              const statusBadge = getStatusBadge(emp.status)
              const deptColor = getDepartmentColor(emp.department)
              return (
                <tr key={emp.id} className={`job-row ${emp.status}`}>
                  <td className="job-id"><code>{emp.id}</code></td>
                  <td><strong>{emp.name}</strong></td>
                  <td>{emp.email}</td>
                  <td>
                    <span className="format-badge" style={{ background: `linear-gradient(135deg, ${roleBadge.color} 0%, ${adjustBrightness(roleBadge.color, -20)} 100%)` }}>
                      {roleBadge.text}
                    </span>
                  </td>
                  <td>
                    <span className="format-badge" style={{ background: `linear-gradient(135deg, ${deptColor} 0%, ${adjustBrightness(deptColor, -20)} 100%)` }}>
                      {emp.department}
                    </span>
                  </td>
                  <td>
                    <span className="status-badge" style={{ backgroundColor: statusBadge.color }}>
                      {statusBadge.text}
                    </span>
                  </td>
                  <td className="timestamp">{emp.joinDate}</td>
                  <td className="timestamp">{emp.lastLogin}</td>
                  <td className="actions">
                    <button 
                      className="action-btn retry" 
                      onClick={() => handleChangeRole(emp.id, emp.role === 'admin' ? 'manager' : 'admin')} 
                      title="Change Role"
                    >
                      <UniversalIcon icon="🔄" size={14} />
                    </button>
                    <button 
                      className="action-btn logs" 
                      onClick={() => handleToggleStatus(emp.id, emp.status)} 
                      title={emp.status === 'active' ? 'Deactivate' : 'Activate'}
                    >
                      {emp.status === 'active' ? <UniversalIcon icon="🔓" size={14} /> : <UniversalIcon icon="🔒" size={14} />}
                    </button>
                    <button 
                      className="action-btn" 
                      style={{ background: 'linear-gradient(135deg, #f6ad55 0%, #ed8936 100%)', color: 'white' }}
                      onClick={() => handleResetPassword(emp.id)} 
                      title="Reset Password"
                    >
                      <UniversalIcon icon="🔑" size={14} />
                    </button>
                    <button 
                      className="action-btn cancel" 
                      onClick={() => handleViewAudit(emp.id)} 
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

export default EmployeeManagement
