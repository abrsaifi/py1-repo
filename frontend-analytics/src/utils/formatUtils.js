/**
 * Data formatting and validation utilities
 */

export const formatNumber = (number, decimals = 2) => {
  if (number === null || number === undefined) return '-'
  return Number(number).toFixed(decimals)
}

export const formatCurrency = (number, currency = 'USD') => {
  const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
  })
  return formatter.format(number)
}

export const formatPercentage = (number, decimals = 1) => {
  return `${formatNumber(number * 100, decimals)}%`
}

export const formatBytes = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

export const formatDate = (date, format = 'MMM dd, yyyy') => {
  if (!date) return '-'
  const dateObj = new Date(date)
  
  // Simple format implementation
  const options = {
    'MMM dd, yyyy': { month: 'short', day: '2-digit', year: 'numeric' },
    'yy-MM-dd': { year: '2-digit', month: '2-digit', day: '2-digit' },
    'yyyy-MM-dd': { year: 'numeric', month: '2-digit', day: '2-digit' },
  }
  
  const formatter = new Intl.DateTimeFormat('en-US', options[format] || options['MMM dd, yyyy'])
  return formatter.format(dateObj)
}

export const formatTime = (date) => {
  if (!date) return '-'
  const dateObj = new Date(date)
  return dateObj.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    second: '2-digit',
  })
}

export const formatDuration = (ms) => {
  if (ms < 1000) return `${Math.round(ms)}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  return `${(ms / 60000).toFixed(1)}m`
}

export const truncateText = (text, length = 50) => {
  if (!text || text.length <= length) return text
  return text.substring(0, length) + '...'
}

export const getStatusColor = (status) => {
  const statusColors = {
    success: '#10b981',
    error: '#ef4444',
    warning: '#f59e0b',
    info: '#3b82f6',
    pending: '#8b5cf6',
  }
  return statusColors[status] || '#6b7280'
}

export const getStatusIcon = (status) => {
  const statusIcons = {
    success: 'fas fa-check-circle',
    error: 'fas fa-times-circle',
    warning: 'fas fa-exclamation-circle',
    info: 'fas fa-info-circle',
    pending: 'fas fa-hourglass-half',
  }
  return statusIcons[status] || 'fas fa-question-circle'
}

export const calculateTrend = (current, previous) => {
  if (previous === 0) return 0
  return ((current - previous) / previous) * 100
}

export default {
  formatNumber,
  formatCurrency,
  formatPercentage,
  formatBytes,
  formatDate,
  formatTime,
  formatDuration,
  truncateText,
  getStatusColor,
  getStatusIcon,
  calculateTrend,
}
