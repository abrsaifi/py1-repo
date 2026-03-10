// Role-Based Access Control (RBAC) System
import { useState, useCallback, createContext, useContext } from 'react'

// Permission definitions
export const PERMISSIONS = {
  // Dashboard permissions
  'dashboard.view': 'View dashboard',
  'dashboard.create': 'Create dashboard',
  'dashboard.edit': 'Edit dashboard',
  'dashboard.delete': 'Delete dashboard',

  // Report permissions
  'reports.view': 'View reports',
  'reports.create': 'Create reports',
  'reports.edit': 'Edit reports',
  'reports.delete': 'Delete reports',
  'reports.schedule': 'Schedule reports',
  'reports.export': 'Export reports',

  // Metrics permissions
  'metrics.view': 'View metrics',
  'metrics.create': 'Create metrics',
  'metrics.edit': 'Edit metrics',
  'metrics.delete': 'Delete metrics',

  // User permissions
  'users.view': 'View users',
  'users.create': 'Create users',
  'users.edit': 'Edit users',
  'users.delete': 'Delete users',

  // Settings permissions
  'settings.view': 'View settings',
  'settings.edit': 'Edit settings',

  // Audit permissions
  'audit.view': 'View audit logs',

  // Admin permissions
  'admin.manage': 'Manage system',
  'admin.users': 'Manage users',
  'admin.roles': 'Manage roles'
}

// Default roles
const DEFAULT_ROLES = {
  admin: {
    name: 'Administrator',
    description: 'Full system access',
    permissions: Object.keys(PERMISSIONS)
  },
  manager: {
    name: 'Manager',
    description: 'Can manage reports and users',
    permissions: [
      'dashboard.view', 'dashboard.create', 'dashboard.edit',
      'reports.view', 'reports.create', 'reports.edit', 'reports.schedule', 'reports.export',
      'metrics.view',
      'users.view', 'users.create', 'users.edit',
      'settings.view',
      'audit.view'
    ]
  },
  analyst: {
    name: 'Analyst',
    description: 'Can view and create reports',
    permissions: [
      'dashboard.view', 'dashboard.create',
      'reports.view', 'reports.create', 'reports.export',
      'metrics.view', 'metrics.create',
      'settings.view',
      'audit.view'
    ]
  },
  viewer: {
    name: 'Viewer',
    description: 'Read-only access',
    permissions: [
      'dashboard.view',
      'reports.view',
      'metrics.view',
      'settings.view'
    ]
  }
}

// RBAC Manager Class
export class RBACManager {
  constructor() {
    this.roles = this.loadRoles()
    this.userRoles = this.loadUserRoles()
  }

  loadRoles() {
    try {
      const saved = localStorage.getItem('rbac-roles')
      return saved ? JSON.parse(saved) : { ...DEFAULT_ROLES }
    } catch (error) {
      return { ...DEFAULT_ROLES }
    }
  }

  loadUserRoles() {
    try {
      const saved = localStorage.getItem('user-roles')
      return saved ? JSON.parse(saved) : {}
    } catch (error) {
      return {}
    }
  }

  saveRoles() {
    localStorage.setItem('rbac-roles', JSON.stringify(this.roles))
  }

  saveUserRoles() {
    localStorage.setItem('user-roles', JSON.stringify(this.userRoles))
  }

  createRole(roleId, name, description, permissions = []) {
    this.roles[roleId] = {
      name,
      description,
      permissions,
      createdAt: new Date().toISOString()
    }
    this.saveRoles()
    return this.roles[roleId]
  }

  updateRole(roleId, updates) {
    const role = this.roles[roleId]
    if (!role) return null

    Object.assign(role, updates, {
      updatedAt: new Date().toISOString()
    })
    this.saveRoles()
    return role
  }

  deleteRole(roleId) {
    delete this.roles[roleId]
    this.saveRoles()
  }

  assignPermissionToRole(roleId, permission) {
    const role = this.roles[roleId]
    if (!role) return null

    if (!role.permissions.includes(permission)) {
      role.permissions.push(permission)
      this.saveRoles()
    }
    return role
  }

  removePermissionFromRole(roleId, permission) {
    const role = this.roles[roleId]
    if (!role) return null

    role.permissions = role.permissions.filter(p => p !== permission)
    this.saveRoles()
    return role
  }

  assignRoleToUser(userId, roleId) {
    if (!this.roles[roleId]) return null

    if (!this.userRoles[userId]) {
      this.userRoles[userId] = []
    }

    if (!this.userRoles[userId].includes(roleId)) {
      this.userRoles[userId].push(roleId)
      this.saveUserRoles()
    }

    return this.userRoles[userId]
  }

  removeRoleFromUser(userId, roleId) {
    if (!this.userRoles[userId]) return null

    this.userRoles[userId] = this.userRoles[userId].filter(r => r !== roleId)
    this.saveUserRoles()
    return this.userRoles[userId]
  }

  hasPermission(userId, permission) {
    const userRoleIds = this.userRoles[userId] || []

    return userRoleIds.some(roleId => {
      const role = this.roles[roleId]
      return role && role.permissions.includes(permission)
    })
  }

  hasAnyPermission(userId, permissions) {
    return permissions.some(permission => this.hasPermission(userId, permission))
  }

  hasAllPermissions(userId, permissions) {
    return permissions.every(permission => this.hasPermission(userId, permission))
  }

  getUserRoles(userId) {
    const roleIds = this.userRoles[userId] || []
    return roleIds.map(id => ({ id, ...this.roles[id] }))
  }

  getUserPermissions(userId) {
    const userRoleIds = this.userRoles[userId] || []
    const permissions = new Set()

    userRoleIds.forEach(roleId => {
      const role = this.roles[roleId]
      if (role) {
        role.permissions.forEach(p => permissions.add(p))
      }
    })

    return Array.from(permissions)
  }

  canAccess(userId, resource) {
    const permission = `${resource}.view`
    return this.hasPermission(userId, permission)
  }

  getRole(roleId) {
    return this.roles[roleId]
  }

  getAllRoles() {
    return Object.entries(this.roles).map(([id, role]) => ({ id, ...role }))
  }
}

// React Context for RBAC
const RBACContext = createContext(null)

export const RBACProvider = ({ children, currentUserId }) => {
  const [rbacManager] = useState(() => new RBACManager())

  const value = {
    hasPermission: (permission) => rbacManager.hasPermission(currentUserId, permission),
    hasAnyPermission: (permissions) => rbacManager.hasAnyPermission(currentUserId, permissions),
    hasAllPermissions: (permissions) => rbacManager.hasAllPermissions(currentUserId, permissions),
    canAccess: (resource) => rbacManager.canAccess(currentUserId, resource),
    getPermissions: () => rbacManager.getUserPermissions(currentUserId),
    getRoles: () => rbacManager.getUserRoles(currentUserId)
  }

  return <RBACContext.Provider value={value}>{children}</RBACContext.Provider>
}

export const useRBAC = () => {
  const context = useContext(RBACContext)
  if (!context) {
    throw new Error('useRBAC must be used within RBACProvider')
  }
  return context
}

// Protected Component Wrapper
export const Protected = ({ permission, fallback = null, children }) => {
  const { hasPermission } = useRBAC()

  if (!hasPermission(permission)) {
    return fallback
  }

  return children
}

// Hook for checking permissions
export const usePermission = (permission) => {
  const { hasPermission } = useRBAC()
  return hasPermission(permission)
}

export const useCanAccess = (resource) => {
  const { canAccess } = useRBAC()
  return canAccess(resource)
}

export default RBACManager
