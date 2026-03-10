// Audit Logging System
// Tracks user actions, changes, and access events in the application

export class AuditLogger {
  constructor() {
    this.logs = this.loadLogs()
    this.maxLogs = 10000 // Maximum logs to keep in memory
  }

  loadLogs() {
    try {
      const saved = localStorage.getItem('audit-logs')
      return saved ? JSON.parse(saved) : []
    } catch (error) {
      console.error('Failed to load audit logs:', error)
      return []
    }
  }

  saveLogs() {
    // Only keep recent logs to prevent storage overflow
    const logsToSave = this.logs.slice(-this.maxLogs)
    try {
      localStorage.setItem('audit-logs', JSON.stringify(logsToSave))
    } catch (error) {
      console.error('Failed to save audit logs:', error)
      // If storage fails, keep only recent 100 logs
      this.logs = this.logs.slice(-100)
      localStorage.setItem('audit-logs', JSON.stringify(this.logs))
    }
  }

  log(action, metadata = {}) {
    const logEntry = {
      id: `audit-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
      action,
      userId: metadata.userId || 'anonymous',
      userName: metadata.userName || 'Unknown',
      resourceType: metadata.resourceType,
      resourceId: metadata.resourceId,
      resourceName: metadata.resourceName,
      changes: metadata.changes || {},
      status: metadata.status || 'success',
      ipAddress: metadata.ipAddress,
      userAgent: metadata.userAgent,
      details: metadata.details,
      severity: this.getSeverity(action)
    }

    this.logs.push(logEntry)
    this.saveLogs()
    return logEntry
  }

  getSeverity(action) {
    const severityMap = {
      'user-login': 'info',
      'user-logout': 'info',
      'user-created': 'warning',
      'user-updated': 'info',
      'user-deleted': 'critical',
      'role-updated': 'warning',
      'permission-granted': 'warning',
      'permission-revoked': 'warning',
      'report-created': 'info',
      'report-updated': 'info',
      'report-deleted': 'warning',
      'settings-changed': 'warning',
      'data-exported': 'info',
      'access-denied': 'warning',
      'error': 'critical'
    }

    return severityMap[action] || 'info'
  }

  logUserLogin(userId, userName, ipAddress, userAgent) {
    return this.log('user-login', {
      userId,
      userName,
      ipAddress,
      userAgent
    })
  }

  logUserLogout(userId, userName) {
    return this.log('user-logout', {
      userId,
      userName
    })
  }

  logResourceCreate(userId, userName, resourceType, resourceId, resourceName, details) {
    return this.log(`${resourceType}-created`, {
      userId,
      userName,
      resourceType,
      resourceId,
      resourceName,
      details
    })
  }

  logResourceUpdate(userId, userName, resourceType, resourceId, resourceName, changes) {
    return this.log(`${resourceType}-updated`, {
      userId,
      userName,
      resourceType,
      resourceId,
      resourceName,
      changes,
      status: 'success'
    })
  }

  logResourceDelete(userId, userName, resourceType, resourceId, resourceName) {
    return this.log(`${resourceType}-deleted`, {
      userId,
      userName,
      resourceType,
      resourceId,
      resourceName,
      status: 'success'
    })
  }

  logPermissionChange(userId, userName, changeType, targetUser, permission, newValue) {
    return this.log('permission-changed', {
      userId,
      userName,
      resourceType: 'permission',
      resourceName: permission,
      changes: {
        targetUser,
        permission,
        newValue,
        changeType
      }
    })
  }

  logAccessDenied(userId, action, resource) {
    return this.log('access-denied', {
      userId,
      resourceType: resource,
      details: {
        attemptedAction: action,
        deniedReason: 'Insufficient permissions'
      },
      status: 'denied',
      severity: 'warning'
    })
  }

  logError(userId, errorType, errorMessage) {
    return this.log('error', {
      userId,
      details: {
        errorType,
        errorMessage
      },
      status: 'error'
    })
  }

  logDataExport(userId, userName, format, filters = {}, rowCount = 0) {
    return this.log('data-exported', {
      userId,
      userName,
      details: {
        format,
        filters,
        rowCount
      }
    })
  }

  // Query methods
  getLogs(options = {}) {
    let results = [...this.logs]

    if (options.userId) {
      results = results.filter(log => log.userId === options.userId)
    }

    if (options.action) {
      results = results.filter(log => log.action === options.action)
    }

    if (options.resourceType) {
      results = results.filter(log => log.resourceType === options.resourceType)
    }

    if (options.resourceId) {
      results = results.filter(log => log.resourceId === options.resourceId)
    }

    if (options.severity) {
      results = results.filter(log => log.severity === options.severity)
    }

    if (options.startDate) {
      const start = new Date(options.startDate)
      results = results.filter(log => new Date(log.timestamp) >= start)
    }

    if (options.endDate) {
      const end = new Date(options.endDate)
      results = results.filter(log => new Date(log.timestamp) <= end)
    }

    if (options.status) {
      results = results.filter(log => log.status === options.status)
    }

    // Sorting
    if (options.sortBy) {
      const sortKey = options.sortBy
      const order = options.sortOrder === 'asc' ? 1 : -1
      results.sort((a, b) => {
        const aVal = a[sortKey]
        const bVal = b[sortKey]
        if (aVal < bVal) return -1 * order
        if (aVal > bVal) return 1 * order
        return 0
      })
    } else {
      // Default: newest first
      results.reverse()
    }

    // Pagination
    if (options.limit) {
      const offset = options.offset || 0
      results = results.slice(offset, offset + options.limit)
    }

    return results
  }

  getUserActivity(userId, days = 30) {
    const startDate = new Date()
    startDate.setDate(startDate.getDate() - days)

    return this.getLogs({
      userId,
      startDate,
      sortBy: 'timestamp',
      sortOrder: 'desc'
    })
  }

  getResourceAuditTrail(resourceType, resourceId) {
    return this.getLogs({
      resourceType,
      resourceId,
      sortBy: 'timestamp',
      sortOrder: 'desc'
    })
  }

  getChanges(resourceType, resourceId) {
    const trail = this.getResourceAuditTrail(resourceType, resourceId)
    return trail
      .filter(log => log.action.endsWith('-updated'))
      .map(log => ({
        timestamp: log.timestamp,
        userId: log.userId,
        userName: log.userName,
        changes: log.changes
      }))
  }

  getStatistics(startDate, endDate) {
    const logs = this.getLogs({
      startDate,
      endDate
    })

    const stats = {
      totalEvents: logs.length,
      byAction: {},
      bySeverity: {},
      byUser: {},
      byResource: {}
    }

    logs.forEach(log => {
      stats.byAction[log.action] = (stats.byAction[log.action] || 0) + 1
      stats.bySeverity[log.severity] = (stats.bySeverity[log.severity] || 0) + 1
      stats.byUser[log.userId] = (stats.byUser[log.userId] || 0) + 1
      stats.byResource[log.resourceType] = (stats.byResource[log.resourceType] || 0) + 1
    })

    return stats
  }

  export(options = {}) {
    const logs = this.getLogs(options)
    return logs.map(log => ({
      ...log,
      timestamp: new Date(log.timestamp).toLocaleString(),
      changes: typeof log.changes === 'object' ? JSON.stringify(log.changes) : log.changes
    }))
  }

  clear(olderThan = null) {
    if (!olderThan) {
      this.logs = []
    } else {
      const cutoffDate = new Date(olderThan)
      this.logs = this.logs.filter(log => new Date(log.timestamp) > cutoffDate)
    }
    this.saveLogs()
  }
}

// React Hook
import { useState, useCallback } from 'react'

const auditLoggerInstance = new AuditLogger()

export const useAuditLogger = () => {
  const log = useCallback((action, metadata = {}) => {
    return auditLoggerInstance.log(action, metadata)
  }, [])

  const getLogs = useCallback((options = {}) => {
    return auditLoggerInstance.getLogs(options)
  }, [])

  const getResourceTrail = useCallback((resourceType, resourceId) => {
    return auditLoggerInstance.getResourceAuditTrail(resourceType, resourceId)
  }, [])

  const getStatistics = useCallback((startDate, endDate) => {
    return auditLoggerInstance.getStatistics(startDate, endDate)
  }, [])

  const exportLogs = useCallback((options = {}) => {
    return auditLoggerInstance.export(options)
  }, [])

  const logUserLogin = useCallback((userId, userName, ipAddress = '', userAgent = '') => {
    return auditLoggerInstance.logUserLogin(userId, userName, ipAddress, userAgent)
  }, [])

  const logResourceCreate = useCallback((userId, userName, resourceType, resourceId, resourceName, details) => {
    return auditLoggerInstance.logResourceCreate(userId, userName, resourceType, resourceId, resourceName, details)
  }, [])

  const logResourceUpdate = useCallback((userId, userName, resourceType, resourceId, resourceName, changes) => {
    return auditLoggerInstance.logResourceUpdate(userId, userName, resourceType, resourceId, resourceName, changes)
  }, [])

  const logDataExport = useCallback((userId, userName, format, filters, rowCount) => {
    return auditLoggerInstance.logDataExport(userId, userName, format, filters, rowCount)
  }, [])

  const logAccessDenied = useCallback((userId, action, resource) => {
    return auditLoggerInstance.logAccessDenied(userId, action, resource)
  }, [])

  return {
    log,
    getLogs,
    getResourceTrail,
    getStatistics,
    exportLogs,
    logUserLogin,
    logResourceCreate,
    logResourceUpdate,
    logDataExport,
    logAccessDenied
  }
}

export default AuditLogger
