import React, { useEffect, useState } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import { adminAPI } from '@shared/api/api'
import { RoleBadge } from '@shared/utils/badgeIcons'

const RoleManagement = () => {
  const [roles, setRoles] = useState([])
  const [expandedRole, setExpandedRole] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadRoles()
  }, [])

  const loadRoles = async () => {
    try {
      setError('')
      const response = await adminAPI.getRoles()
      setRoles(response.data.roles || [])
    } catch (loadError) {
      setError(loadError.response?.data?.error || 'Failed to load role catalog')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="role-management">
      <div className="management-header">
        <h2><UniversalIcon icon="🔐" size={24} /> Role & Permission Management</h2>
        <div className="refresh-indicator">
          <span className="pulse"><UniversalIcon icon="🜢" size={14} /></span> Live backend roles
        </div>
      </div>

      <p className="section-subtitle">System roles are now sourced from the backend. Role assignment happens in Admin & Staff.</p>

      {error && (
        <div className="no-data">
          <p>{error}</p>
        </div>
      )}

      <div className="roles-grid">
        {loading ? (
          <div className="no-data">
            <p>Loading roles...</p>
          </div>
        ) : roles.map(role => (
          <div key={role.id} className="role-card">
            <div className="role-card-header">
              <div>
                <h3>{role.name}</h3>
                <RoleBadge role={role.name} />
              </div>
              <div className="role-actions">
                <span className="format-badge">{role.userCount} users</span>
              </div>
            </div>
            
            <p className="role-description">{role.description}</p>
            
            <button
              className="expand-btn"
              onClick={() => setExpandedRole(expandedRole === role.key ? null : role.key)}
            >
              {expandedRole === role.key ? <><UniversalIcon icon="▼" size={14} /> Hide</> : <><UniversalIcon icon="▶" size={14} /> Show</>} Permissions ({role.permissions.length})
            </button>

            {expandedRole === role.key && (
              <div className="permissions-list">
                <div className="permissions-grid">
                  {role.permissions.map((permission) => (
                    <div key={permission} className="permission-checkbox">
                      <span>{permission}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default RoleManagement
