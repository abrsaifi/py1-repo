import React, { useState, useEffect } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import { useExportManager } from '../services/advancedExport'
import { analyticsAPI } from '@shared/api/api'

const CustomReportBuilder = () => {
  const { exportData } = useExportManager()
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showBuilder, setShowBuilder] = useState(false)
  const [editingReport, setEditingReport] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    metrics: [],
    dimensions: [],
    dateRange: '30d',
    format: 'pdf'
  })

  useEffect(() => {
    loadReports()
  }, [])

  const loadReports = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await analyticsAPI.listReports()
      
      if (response.data && response.data.data) {
        setReports(response.data.data)
      }
    } catch (err) {
      console.error('Failed to load reports:', err)
      setError('Failed to load reports')
      // Fallback mock data
      setReports([
        {
          id: 'report-1',
          name: 'Monthly Sales Summary',
          description: 'Key sales metrics and trends',
          metrics: ['revenue', 'units_sold', 'avg_price'],
          dimensions: ['product_category', 'region'],
          dateRange: '30d'
        },
        {
          id: 'report-2',
          name: 'Customer Behavior Analysis',
          description: 'User engagement and retention metrics',
          metrics: ['active_users', 'engagement_rate', 'churn_rate'],
          dimensions: ['user_segment', 'channel'],
          dateRange: '90d'
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const availableMetrics = [
    { id: 'revenue', label: 'Revenue', icon: '💰' },
    { id: 'units_sold', label: 'Units Sold', icon: '📦' },
    { id: 'avg_price', label: 'Average Price', icon: '💵' },
    { id: 'active_users', label: 'Active Users', icon: '👥' },
    { id: 'engagement_rate', label: 'Engagement Rate', icon: '📊' },
    { id: 'churn_rate', label: 'Churn Rate', icon: '📉' },
    { id: 'conversion_rate', label: 'Conversion Rate', icon: '✅' },
    { id: 'nps_score', label: 'NPS Score', icon: '⭐' }
  ]

  const availableDimensions = [
    { id: 'product_category', label: 'Product Category' },
    { id: 'region', label: 'Region' },
    { id: 'user_segment', label: 'User Segment' },
    { id: 'channel', label: 'Channel' },
    { id: 'device_type', label: 'Device Type' },
    { id: 'time_period', label: 'Time Period' }
  ]

  const handleOpenBuilder = (report = null) => {
    if (report) {
      setEditingReport(report)
      setFormData(report)
    } else {
      setEditingReport(null)
      setFormData({
        name: '',
        description: '',
        metrics: [],
        dimensions: [],
        dateRange: '30d',
        format: 'pdf'
      })
    }
    setShowBuilder(true)
  }

  const handleCloseBuilder = () => {
    setShowBuilder(false)
    setEditingReport(null)
  }

  const handleMetricToggle = (metricId) => {
    setFormData(prev => ({
      ...prev,
      metrics: prev.metrics.includes(metricId)
        ? prev.metrics.filter(m => m !== metricId)
        : [...prev.metrics, metricId]
    }))
  }

  const handleDimensionToggle = (dimensionId) => {
    setFormData(prev => ({
      ...prev,
      dimensions: prev.dimensions.includes(dimensionId)
        ? prev.dimensions.filter(d => d !== dimensionId)
        : [...prev.dimensions, dimensionId]
    }))
  }

  const handleSaveReport = async () => {
    if (!formData.name || formData.metrics.length === 0) {
      alert('Please provide a report name and select at least one metric')
      return
    }

    try {
      if (editingReport) {
        await analyticsAPI.updateReport(editingReport.id, formData)
        setReports(reports.map(r => r.id === editingReport.id ? { ...formData, id: editingReport.id } : r))
      } else {
        const response = await analyticsAPI.createReport(formData)
        if (response.data && response.data.data) {
          setReports([...reports, response.data.data])
        } else {
          setReports([...reports, { ...formData, id: `report-${Date.now()}` }])
        }
      }
      handleCloseBuilder()
    } catch (err) {
      console.error('Failed to save report:', err)
      alert('Failed to save report. Please try again.')
    }
  }

  const handleDeleteReport = async (reportId) => {
    if (window.confirm('Delete this report?')) {
      try {
        await analyticsAPI.deleteReport(reportId)
        setReports(reports.filter(r => r.id !== reportId))
      } catch (err) {
        console.error('Failed to delete report:', err)
        alert('Failed to delete report. Please try again.')
      }
    }
  }

  const handleGenerateReport = async (report) => {
    try {
      const response = await analyticsAPI.exportReport(report.id, report.format)
      
      if (response.data) {
        // Handle the exported file
        const blob = new Blob([response.data], { type: getContentType(report.format) })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${report.name}.${report.format}`
        a.click()
        window.URL.revokeObjectURL(url)
      }
    } catch (err) {
      console.error('Failed to generate report:', err)
      alert('Failed to generate report. Please try again.')
    }
  }

  const getContentType = (format) => {
    const types = {
      pdf: 'application/pdf',
      excel: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      csv: 'text/csv'
    }
    return types[format] || 'application/octet-stream'
  }

  return (
    <div className="custom-report-builder">
      <div className="builder-header">
        <h2><UniversalIcon icon="📝" size={24} /> Custom Report Builder</h2>
        <button className="btn-primary" onClick={() => handleOpenBuilder()}>
          + New Report
        </button>
      </div>

      {loading && (
        <div className="loading-container">
          <UniversalIcon icon="⏳" size={32} />
          <p>Loading reports...</p>
        </div>
      )}

      {error && (
        <div className="error-container">
          <p className="error-message"><UniversalIcon icon="⚠️" size={18} /> {error}</p>
          <button onClick={loadReports}>Retry</button>
        </div>
      )}

      {!loading && !error && reports.length === 0 && (
        <div className="empty-state">
          <p><UniversalIcon icon="📋" size={24} /> No reports yet. Create your first report!</p>
        </div>
      )}

      <div className="reports-grid">
        {reports.map(report => (
          <div key={report.id} className="report-card">
            <div className="report-header">
              <h3>{report.name}</h3>
              <div className="report-actions">
                <button
                  className="btn-small"
                  onClick={() => handleOpenBuilder(report)}
                  title="Edit"
                >
                  ✏️
                </button>
                <button
                  className="btn-small btn-danger"
                  onClick={() => handleDeleteReport(report.id)}
                  title="Delete"
                >
                  🗑️
                </button>
              </div>
            </div>

            <p className="report-description">{report.description}</p>

            <div className="report-details">
              <div className="detail">
                <span className="label">Metrics:</span>
                <span className="value">{report.metrics.length}</span>
              </div>
              <div className="detail">
                <span className="label">Dimensions:</span>
                <span className="value">{report.dimensions.length}</span>
              </div>
              <div className="detail">
                <span className="label">Period:</span>
                <span className="value">{report.dateRange}</span>
              </div>
            </div>

            <button
              className="btn-primary"
              onClick={() => handleGenerateReport(report)}
            >
              <UniversalIcon icon="📥" size={14} /> Generate & Export
            </button>
          </div>
        ))}
      </div>

      {showBuilder && (
        <div className="modal-overlay">
          <div className="modal-content modal-large">
            <div className="modal-header">
              <h3>{editingReport ? 'Edit Report' : 'Create New Report'}</h3>
              <button className="close-btn" onClick={handleCloseBuilder}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Report Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., Monthly Sales Report"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Describe what this report shows"
                  className="form-input"
                  rows="2"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Date Range</label>
                  <select
                    value={formData.dateRange}
                    onChange={(e) => setFormData(prev => ({ ...prev, dateRange: e.target.value }))}
                    className="form-input"
                  >
                    <option value="7d">Last 7 days</option>
                    <option value="30d">Last 30 days</option>
                    <option value="90d">Last 90 days</option>
                    <option value="1y">Last year</option>
                    <option value="custom">Custom range</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Export Format</label>
                  <select
                    value={formData.format}
                    onChange={(e) => setFormData(prev => ({ ...prev, format: e.target.value }))}
                    className="form-input"
                  >
                    <option value="pdf">PDF</option>
                    <option value="excel">Excel</option>
                    <option value="csv">CSV</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Select Metrics</label>
                <div className="metric-grid">
                  {availableMetrics.map(metric => (
                    <label key={metric.id} className="metric-checkbox">
                      <input
                        type="checkbox"
                        checked={formData.metrics.includes(metric.id)}
                        onChange={() => handleMetricToggle(metric.id)}
                      />
                      <span>{metric.icon} {metric.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label>Select Dimensions (Breakdowns)</label>
                <div className="dimension-grid">
                  {availableDimensions.map(dim => (
                    <label key={dim.id} className="dimension-checkbox">
                      <input
                        type="checkbox"
                        checked={formData.dimensions.includes(dim.id)}
                        onChange={() => handleDimensionToggle(dim.id)}
                      />
                      <span>{dim.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={handleCloseBuilder}>Cancel</button>
              <button className="btn-primary" onClick={handleSaveReport}>Save Report</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default CustomReportBuilder
