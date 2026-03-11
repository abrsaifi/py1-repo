// Advanced Export Features
// Supports scheduled exports, batch operations, templates, and delivery options

export class ExportManager {
  constructor() {
    this.exports = this.loadExports()
    this.templates = this.loadTemplates()
  }

  loadExports() {
    try {
      const saved = localStorage.getItem('exports-history')
      return saved ? JSON.parse(saved) : []
    } catch (error) {
      console.error('Failed to load exports:', error)
      return []
    }
  }

  loadTemplates() {
    try {
      const saved = localStorage.getItem('export-templates')
      return saved ? JSON.parse(saved) : this.getDefaultTemplates()
    } catch (error) {
      return this.getDefaultTemplates()
    }
  }

  saveExports() {
    try {
      localStorage.setItem('exports-history', JSON.stringify(this.exports.slice(-1000)))
    } catch (error) {
      console.error('Failed to save exports:', error)
    }
  }

  saveTemplates() {
    try {
      localStorage.setItem('export-templates', JSON.stringify(this.templates))
    } catch (error) {
      console.error('Failed to save templates:', error)
    }
  }

  getDefaultTemplates() {
    return {
      'daily-summary': {
        id: 'daily-summary',
        name: 'Daily Summary',
        description: 'Export daily metrics and KPIs',
        format: 'pdf',
        frequency: 'daily',
        time: '09:00',
        filters: {},
        columns: ['date', 'metric', 'value', 'change']
      },
      'weekly-report': {
        id: 'weekly-report',
        name: 'Weekly Report',
        description: 'Comprehensive weekly analysis',
        format: 'excel',
        frequency: 'weekly',
        dayOfWeek: 'monday',
        time: '08:00',
        filters: {},
        columns: ['date', 'metric', 'value', 'trend', 'forecast']
      },
      'monthly-snapshot': {
        id: 'monthly-snapshot',
        name: 'Monthly Snapshot',
        description: 'Monthly overview and analysis',
        format: 'pdf',
        frequency: 'monthly',
        dayOfMonth: 1,
        time: '08:00',
        filters: {},
        columns: ['month', 'metric', 'value', 'variance', 'forecast']
      }
    }
  }

  // Create custom export template
  createTemplate(templateId, name, config) {
    this.templates[templateId] = {
      id: templateId,
      name,
      ...config,
      createdAt: new Date().toISOString()
    }
    this.saveTemplates()
    return this.templates[templateId]
  }

  updateTemplate(templateId, updates) {
    const template = this.templates[templateId]
    if (!template) return null

    Object.assign(template, updates, {
      updatedAt: new Date().toISOString()
    })
    this.saveTemplates()
    return template
  }

  deleteTemplate(templateId) {
    delete this.templates[templateId]
    this.saveTemplates()
  }

  getTemplate(templateId) {
    return this.templates[templateId]
  }

  getAllTemplates() {
    return Object.values(this.templates)
  }

  // Single export
  async exportData(data, options = {}) {
    const {
      format = 'csv',
      filename = 'export',
      filters = {},
      columns = null,
      userId = null,
      userName = null
    } = options

    const filteredData = this.applyFilters(data, filters)
    const selectedData = columns ? this.selectColumns(filteredData, columns) : filteredData

    const exportEntry = {
      id: `export-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
      format,
      filename,
      rowCount: selectedData.length,
      fileSize: this.estimateSize(selectedData),
      userId,
      userName,
      status: 'completed'
    }

    this.exports.push(exportEntry)
    this.saveExports()

    const blob = this.formatData(selectedData, format, filename)
    return { blob, entry: exportEntry }
  }

  // Batch export multiple datasets
  async batchExport(datasets, options = {}) {
    const {
      format = 'zip',
      folder = 'batch-export',
      userId = null,
      userName = null
    } = options

    const batchEntry = {
      id: `batch-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
      format,
      datasetsCount: datasets.length,
      userId,
      userName,
      status: 'completed'
    }

    this.exports.push(batchEntry)
    this.saveExports()

    // Return batch export with all datasets
    const files = datasets.map(ds => ({
      name: ds.name,
      blob: this.formatData(ds.data, ds.format || 'csv', ds.name)
    }))

    return { files, entry: batchEntry }
  }

  // Scheduled export from template
  scheduleExport(templateId, options = {}) {
    const template = this.templates[templateId]
    if (!template) return null

    const scheduled = {
      id: `scheduled-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      templateId,
      ...template,
      ...options,
      enabled: true,
      lastRun: null,
      nextRun: this.calculateNextRun(template.frequency, template),
      createdAt: new Date().toISOString()
    }

    return scheduled
  }

  calculateNextRun(frequency, template) {
    const now = new Date()
    const time = template.time || '08:00'
    const [hours, minutes] = time.split(':').map(Number)

    switch (frequency) {
      case 'daily':
        const tomorrow = new Date(now)
        tomorrow.setDate(tomorrow.getDate() + 1)
        tomorrow.setHours(hours, minutes, 0, 0)
        return tomorrow.toISOString()

      case 'weekly':
        const dayOfWeek = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'].indexOf(
          template.dayOfWeek || 'monday'
        )
        const next = new Date(now)
        next.setDate(next.getDate() + ((dayOfWeek + 7 - next.getDay()) % 7))
        next.setHours(hours, minutes, 0, 0)
        return next.toISOString()

      case 'monthly':
        const nextMonth = new Date(now.getFullYear(), now.getMonth() + 1, template.dayOfMonth || 1)
        nextMonth.setHours(hours, minutes, 0, 0)
        return nextMonth.toISOString()

      default:
        return now.toISOString()
    }
  }

  // Format data for different export types
  formatData(data, format, filename) {
    let content
    let mimeType

    switch (format.toLowerCase()) {
      case 'csv':
        content = this.toCSV(data)
        mimeType = 'text/csv;charset=utf-8;'
        break

      case 'json':
        content = JSON.stringify(data, null, 2)
        mimeType = 'application/json;charset=utf-8;'
        break

      case 'tsv':
        content = this.toTSV(data)
        mimeType = 'text/tab-separated-values;charset=utf-8;'
        break

      case 'xlsx':
        content = this.toExcel(data)
        mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        break

      case 'pdf':
        // PDF would need additional library like pdfkit or jsPDF
        content = this.toPDF(data)
        mimeType = 'application/pdf'
        break

      default:
        content = JSON.stringify(data)
        mimeType = 'text/plain;charset=utf-8;'
    }

    return new Blob([content], { type: mimeType })
  }

  toCSV(data) {
    if (!data || data.length === 0) return ''

    const headers = Object.keys(data[0])
    const rows = data.map(obj =>
      headers.map(header => {
        const value = obj[header]
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`
        }
        return value
      }).join(',')
    )

    return [headers.join(','), ...rows].join('\n')
  }

  toTSV(data) {
    if (!data || data.length === 0) return ''

    const headers = Object.keys(data[0])
    const rows = data.map(obj =>
      headers.map(header => obj[header]).join('\t')
    )

    return [headers.join('\t'), ...rows].join('\n')
  }

  toExcel(data) {
    // Basic Excel format (would use xlsx library for production)
    return this.toCSV(data)
  }

  toPDF(data) {
    // Basic PDF text (would use jsPDF library for production)
    return JSON.stringify(data, null, 2)
  }

  // Helper methods
  applyFilters(data, filters) {
    if (!filters || Object.keys(filters).length === 0) return data

    return data.filter(item => {
      return Object.entries(filters).every(([key, value]) => {
        if (!value) return true
        if (Array.isArray(value)) {
          return value.includes(item[key])
        }
        if (value.min !== undefined && item[key] < value.min) return false
        if (value.max !== undefined && item[key] > value.max) return false
        return String(item[key]).toLowerCase().includes(String(value).toLowerCase())
      })
    })
  }

  selectColumns(data, columns) {
    return data.map(item => {
      const obj = {}
      columns.forEach(col => {
        obj[col] = item[col]
      })
      return obj
    })
  }

  estimateSize(data) {
    const json = JSON.stringify(data)
    return `${(json.length / 1024).toFixed(2)} KB`
  }

  // Query methods
  getExportHistory(options = {}) {
    let results = [...this.exports]

    if (options.userId) {
      results = results.filter(e => e.userId === options.userId)
    }

    if (options.format) {
      results = results.filter(e => e.format === options.format)
    }

    if (options.startDate) {
      const start = new Date(options.startDate)
      results = results.filter(e => new Date(e.timestamp) >= start)
    }

    if (options.endDate) {
      const end = new Date(options.endDate)
      results = results.filter(e => new Date(e.timestamp) <= end)
    }

    // Default: newest first
    results.reverse()

    // Pagination
    if (options.limit) {
      const offset = options.offset || 0
      results = results.slice(offset, offset + options.limit)
    }

    return results
  }

  getExportStats() {
    const stats = {
      totalExports: this.exports.length,
      byFormat: {},
      byUser: {}
    }

    this.exports.forEach(exp => {
      stats.byFormat[exp.format] = (stats.byFormat[exp.format] || 0) + 1
      if (exp.userId) {
        stats.byUser[exp.userId] = (stats.byUser[exp.userId] || 0) + 1
      }
    })

    return stats
  }
}

// React Hook
import { useState, useCallback } from 'react'

const exportManagerInstance = new ExportManager()

export const useExportManager = () => {
  const [history, setHistory] = useState(exportManagerInstance.getExportHistory())

  const exportData = useCallback(async (data, options = {}) => {
    const result = await exportManagerInstance.exportData(data, options)
    setHistory(exportManagerInstance.getExportHistory())
    return result
  }, [])

  const batchExport = useCallback(async (datasets, options = {}) => {
    const result = await exportManagerInstance.batchExport(datasets, options)
    setHistory(exportManagerInstance.getExportHistory())
    return result
  }, [])

  const scheduleExport = useCallback((templateId, options = {}) => {
    return exportManagerInstance.scheduleExport(templateId, options)
  }, [])

  const createTemplate = useCallback((templateId, name, config) => {
    return exportManagerInstance.createTemplate(templateId, name, config)
  }, [])

  const getTemplates = useCallback(() => {
    return exportManagerInstance.getAllTemplates()
  }, [])

  const getHistory = useCallback((options = {}) => {
    return exportManagerInstance.getExportHistory(options)
  }, [])

  const getStats = useCallback(() => {
    return exportManagerInstance.getExportStats()
  }, [])

  return {
    exportData,
    batchExport,
    scheduleExport,
    createTemplate,
    getTemplates,
    getHistory,
    getStats,
    history
  }
}

export default ExportManager
