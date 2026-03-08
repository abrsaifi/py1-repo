import React, { useState, useEffect } from 'react'
import { UniversalIcon } from '../utils/UniversalIcon'
import { RBACManager, PERMISSIONS } from '../services/rbac.jsx'

const RoleManagement = () => {
  const [roles, setRoles] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [editingRole, setEditingRole] = useState(null)
  const [expandedRole, setExpandedRole] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    permissions: []
  })

  const rbacManager = new RBACManager()
  const permissionOptions = Object.entries(PERMISSIONS).map(([key, value]) => ({
    id: key,
    label: value
  }))

  useEffect(() => {
    loadRoles()
  }, [])

  const loadRoles = () => {
    const allRoles = rbacManager.getAllRoles()
    setRoles(allRoles)
  }

  const handleOpenModal = (role = null) => {
    if (role) {
      setEditingRole(role)
      setFormData({
        name: role.name,
        description: role.description,
        permissions: role.permissions || []
      })
    } else {
      setEditingRole(null)
      setFormData({
        name: '',
        description: '',
        permissions: []
      })
    }
    setShowModal(true)
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setEditingRole(null)
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handlePermissionToggle = (permissionId) => {
    setFormData(prev => {
      const permissions = prev.permissions.includes(permissionId)
        ? prev.permissions.filter(p => p !== permissionId)
        : [...prev.permissions, permissionId]
      return { ...prev, permissions }
    })
  }

  const handleSaveRole = () => {
    if (!formData.name) {
      alert('Please enter a role name')
      return
    }

    const roleId = editingRole?.id || `role-${Date.now()}`

    if (editingRole) {
      rbacManager.updateRole(roleId, formData)
    } else {
      rbacManager.createRole(roleId, formData.name, formData.description, formData.permissions)
    }

    loadRoles()
    handleCloseModal()
  }

  const handleDeleteRole = (roleId) => {
    if (['admin', 'manager', 'analyst', 'viewer'].includes(roleId)) {
      alert('Cannot delete default roles')
      return
    }
    if (window.confirm('Are you sure you want to delete this role?')) {
      rbacManager.deleteRole(roleId)
      loadRoles()
    }
  }

  const togglePermission = (roleId, permission) => {
    const role = roles.find(r => r.id === roleId)
    if (role.permissions.includes(permission)) {
      rbacManager.removePermissionFromRole(roleId, permission)
    } else {
      rbacManager.assignPermissionToRole(roleId, permission)
    }
    loadRoles()
  }

  return (
    <div className="role-management">
      <div className="management-header">
        <h2><UniversalIcon icon="🔐" size={24} /> Role & Permission Management</h2>
        <button className="btn-primary" onClick={() => handleOpenModal()}>
          + Create Role
        </button>
      </div>

      <div className="roles-grid">
        {roles.map(role => (
          <div key={role.id} className="role-card">
            <div className="role-card-header">
              <h3>{role.name}</h3>
              <div className="role-actions">
                <button
                  className="btn-small"
                  onClick={() => handleOpenModal(role)}
                  title="Edit"
                >
                  <UniversalIcon icon="✏️" size={16} />
                </button>
                {!['admin', 'manager', 'analyst', 'viewer'].includes(role.id) && (
                  <button
                    className="btn-small btn-danger"
                    onClick={() => handleDeleteRole(role.id)}
                    title="Delete"
                  >
                    <UniversalIcon icon="🗑️" size={16} />
                  </button>
                )}
              </div>
            </div>
            
            <p className="role-description">{role.description}</p>
            
            <button
              className="expand-btn"
              onClick={() => setExpandedRole(expandedRole === role.id ? null : role.id)}
            >
              {expandedRole === role.id ? <><UniversalIcon icon="▼" size={14} /> Hide</> : <><UniversalIcon icon="▶" size={14} /> Show</>} Permissions ({role.permissions.length})
            </button>

            {expandedRole === role.id && (
              <div className="permissions-list">
                <div className="permissions-grid">
                  {permissionOptions.map(perm => (
                    <label key={perm.id} className="permission-checkbox">
                      <input
                        type="checkbox"
                        checked={role.permissions.includes(perm.id)}
                        onChange={() => togglePermission(role.id, perm.id)}
                      />
                      <span>{perm.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content modal-large">
            <div className="modal-header">
              <h3>{editingRole ? 'Edit Role' : 'Create New Role'}</h3>
              <button className="close-btn" onClick={handleCloseModal}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Role Name</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="e.g., Content Manager"
                  className="form-input"
                />
              </div>
              
              <div className="form-group">
                <label>Description</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Describe the purpose of this role"
                  className="form-input"
                  rows="3"
                />
              </div>

              <div className="form-group">
                <label>Permissions</label>
                <div className="permissions-grid">
                  {permissionOptions.map(perm => (
                    <label key={perm.id} className="permission-checkbox">
                      <input
                        type="checkbox"
                        checked={formData.permissions.includes(perm.id)}
                        onChange={() => handlePermissionToggle(perm.id)}
                      />
                      <span>{perm.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={handleCloseModal}>Cancel</button>
              <button className="btn-primary" onClick={handleSaveRole}>Save Role</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default RoleManagement
