import React, { useEffect, useState } from 'react'
import { adminAPI } from '@shared/api/api'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import '../styles/admin.css'

const ReportSchedulingAdmin = () => {
  const [payload, setPayload] = useState({
    stats: {
      totalSchedules: 0,
      activeSchedules: 0,
      disabledSchedules: 0,
      totalRecipients: 0,
    },
    schedules: [],
  })
  const [showModal, setShowModal] = useState(false)
  const [editingSchedule, setEditingSchedule] = useState(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [formData, setFormData] = useState({
    reportName: '',
    frequency: 'daily',
    time: '09:00',
    recipients: [],
    format: 'pdf',
    enabled: true,
    includeCharts: true
  })
  const [newRecipient, setNewRecipient] = useState('')

  useEffect(() => {
    loadSchedules()
  }, [])

  const loadSchedules = async (showLoader = true) => {
    try {
      if (showLoader) {
        setLoading(true)
      }
      setError('')
      const response = await adminAPI.getReportSchedules()
      setPayload(response.data || { stats: {}, schedules: [] })
    } catch (err) {
      console.error('Failed to load report schedules:', err)
      setError(err.response?.data?.error || err.message || 'Failed to load report schedules')
    } finally {
      if (showLoader) {
        setLoading(false)
      }
    }
  }

  const handleOpenModal = (schedule = null) => {
    if (schedule) {
      setEditingSchedule(schedule)
      setFormData(schedule)
    } else {
      setEditingSchedule(null)
      setFormData({
        reportName: '',
        frequency: 'daily',
        time: '09:00',
        recipients: [],
        format: 'pdf',
        enabled: true,
        includeCharts: true
      })
    }
    setShowModal(true)
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setEditingSchedule(null)
    setNewRecipient('')
  }

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleAddRecipient = () => {
    if (newRecipient && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newRecipient)) {
      setFormData(prev => ({
        ...prev,
        recipients: [...prev.recipients, newRecipient]
      }))
      setNewRecipient('')
    }
  }

  const handleRemoveRecipient = (email) => {
    setFormData(prev => ({
      ...prev,
      recipients: prev.recipients.filter(r => r !== email)
    }))
  }

  const handleSaveSchedule = async () => {
    if (!formData.reportName) {
      setError('Please enter a report name')
      return
    }

    if (formData.recipients.length === 0) {
      setError('Please add at least one recipient')
      return
    }

    try {
      setActionLoading(editingSchedule?.id || 'create')
      setError('')
      setMessage('')

      const response = editingSchedule
        ? await adminAPI.updateReportSchedule(editingSchedule.id, formData)
        : await adminAPI.createReportSchedule(formData)

      setMessage(response.data?.message || 'Schedule saved.')
      handleCloseModal()
      await loadSchedules(false)
    } catch (err) {
      console.error('Failed to save schedule:', err)
      setError(err.response?.data?.error || err.message || 'Failed to save schedule')
    } finally {
      setActionLoading('')
    }
  }

  const handleToggleSchedule = async (schedule) => {
    try {
      setActionLoading(schedule.id)
      setError('')
      setMessage('')
      const response = await adminAPI.updateReportSchedule(schedule.id, {
        ...schedule,
        enabled: !schedule.enabled,
      })
      setMessage(response.data?.message || 'Schedule updated.')
      await loadSchedules(false)
    } catch (err) {
      console.error('Failed to toggle schedule:', err)
      setError(err.response?.data?.error || err.message || 'Failed to update schedule')
    } finally {
      setActionLoading('')
    }
  }

  const handleDeleteSchedule = async (scheduleId) => {
    try {
      setActionLoading(scheduleId)
      setError('')
      setMessage('')
      const response = await adminAPI.deleteReportSchedule(scheduleId)
      setMessage(response.data?.message || 'Schedule deleted.')
      await loadSchedules(false)
    } catch (err) {
      console.error('Failed to delete schedule:', err)
      setError(err.response?.data?.error || err.message || 'Failed to delete schedule')
    } finally {
      setActionLoading('')
    }
  }

  const handleTestSchedule = async (schedule) => {
    try {
      setActionLoading(`test-${schedule.id}`)
      setError('')
      setMessage('')
      const response = await adminAPI.testReportSchedule(schedule.id)
      setMessage(response.data?.message || 'Test dispatch recorded.')
      await loadSchedules(false)
    } catch (err) {
      console.error('Failed to send test schedule:', err)
      setError(err.response?.data?.error || err.message || 'Failed to record test dispatch')
    } finally {
      setActionLoading('')
    }
  }

  const schedules = payload.schedules || []
  const stats = payload.stats || {}

  return (
    <div className="report-scheduling-admin">
      <div className="management-header">
        <h2><UniversalIcon icon="📅" size={24} /> Report Scheduling</h2>
        <button className="btn-primary" onClick={() => handleOpenModal()}>
          + Create Schedule
        </button>
      </div>

      {error && <div className="alert-banner error">{error}</div>}
      {message && <div className="alert-banner success">{message}</div>}

      <div className="admin-stats-grid" style={{ marginBottom: '24px' }}>
        <div className="admin-stat-card metric-primary">
          <UniversalIcon icon="📅" size={32} />
          <div className="stat-content">
            <h3>Total Schedules</h3>
            <p className="stat-value">{stats.totalSchedules || 0}</p>
            <p className="stat-detail">Persisted admin schedules</p>
          </div>
        </div>

        <div className="admin-stat-card metric-success">
          <UniversalIcon icon="✅" size={32} />
          <div className="stat-content">
            <h3>Active</h3>
            <p className="stat-value">{stats.activeSchedules || 0}</p>
            <p className="stat-detail">Enabled delivery plans</p>
          </div>
        </div>

        <div className="admin-stat-card metric-warning">
          <UniversalIcon icon="⏸️" size={32} />
          <div className="stat-content">
            <h3>Disabled</h3>
            <p className="stat-value">{stats.disabledSchedules || 0}</p>
            <p className="stat-detail">Held back from dispatch</p>
          </div>
        </div>

        <div className="admin-stat-card metric-info">
          <UniversalIcon icon="👥" size={32} />
          <div className="stat-content">
            <h3>Total Recipients</h3>
            <p className="stat-value">{stats.totalRecipients || 0}</p>
            <p className="stat-detail">Across all saved schedules</p>
          </div>
        </div>
      </div>

      <div className="quick-actions" style={{ marginBottom: '24px' }}>
        <button className="action-button primary" onClick={() => loadSchedules()} disabled={loading}>
          <UniversalIcon icon="🔄" size={14} /> {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      <div className="schedules-grid">
        {schedules.length > 0 ? (
          schedules.map(schedule => (
            <div key={schedule.id} className={`schedule-card ${schedule.enabled ? 'enabled' : 'disabled'}`}>
              <div className="schedule-header">
                <h3>{schedule.reportName}</h3>
                <div className="schedule-actions">
                  <button
                    className={`status-toggle ${schedule.enabled ? 'enabled' : 'disabled'}`}
                    onClick={() => handleToggleSchedule(schedule)}
                    title={schedule.enabled ? 'Disable' : 'Enable'}
                    disabled={actionLoading === schedule.id}
                  >
                    {schedule.enabled ? <UniversalIcon icon="✓" size={14} /> : <UniversalIcon icon="✗" size={14} />}
                  </button>
                </div>
              </div>

              <div className="schedule-details">
                <div className="detail-row">
                  <span className="label">Frequency:</span>
                  <span className="value">
                    {schedule.frequency.charAt(0).toUpperCase() + schedule.frequency.slice(1)}
                  </span>
                </div>
                <div className="detail-row">
                  <span className="label">Time:</span>
                  <span className="value">{schedule.time}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Format:</span>
                  <span className="value">{schedule.format.toUpperCase()}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Next Run:</span>
                  <span className="value">{schedule.nextRun}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Recipients:</span>
                  <span className="value">{schedule.recipients.length}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Last Test:</span>
                  <span className="value">{schedule.testSentAt || 'Not sent'}</span>
                </div>
              </div>

              <div className="recipients-preview">
                {schedule.recipients.slice(0, 2).map(email => (
                  <span key={email} className="recipient-badge">{email}</span>
                ))}
                {schedule.recipients.length > 2 && (
                  <span className="recipient-badge">+{schedule.recipients.length - 2} more</span>
                )}
              </div>

              <div className="schedule-button-group">
                <button
                  className="btn-small"
                  onClick={() => handleOpenModal(schedule)}
                  title="Edit"
                  disabled={actionLoading === schedule.id}
                >
                  <UniversalIcon icon="✍️" size={14} /> Edit
                </button>
                <button
                  className="btn-small btn-info"
                  onClick={() => handleTestSchedule(schedule)}
                  title="Send Test Email"
                  disabled={actionLoading === `test-${schedule.id}`}
                >
                  <UniversalIcon icon="📧" size={14} /> {actionLoading === `test-${schedule.id}` ? 'Testing...' : 'Test'}
                </button>
                <button
                  className="btn-small btn-danger"
                  onClick={() => handleDeleteSchedule(schedule.id)}
                  title="Delete"
                  disabled={actionLoading === schedule.id}
                >
                  <UniversalIcon icon="🗑️" size={14} /> Delete
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="no-schedules">
            <p><UniversalIcon icon="📭" size={18} /> No report schedules created yet</p>
            <p>Create a new schedule to automatically send reports to your team</p>
          </div>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content modal-large">
            <div className="modal-header">
              <h3>{editingSchedule ? 'Edit Schedule' : 'Create Report Schedule'}</h3>
              <button className="close-btn" onClick={handleCloseModal}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-row">
                <div className="form-group">
                  <label>Report Name</label>
                  <input
                    type="text"
                    name="reportName"
                    value={formData.reportName}
                    onChange={handleInputChange}
                    placeholder="e.g., Weekly Sales Report"
                    className="form-input"
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Frequency</label>
                  <select
                    name="frequency"
                    value={formData.frequency}
                    onChange={handleInputChange}
                    className="form-input"
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Send Time</label>
                  <input
                    type="time"
                    name="time"
                    value={formData.time}
                    onChange={handleInputChange}
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label>Format</label>
                  <select
                    name="format"
                    value={formData.format}
                    onChange={handleInputChange}
                    className="form-input"
                  >
                    <option value="pdf">PDF</option>
                    <option value="excel">Excel</option>
                    <option value="csv">CSV</option>
                  </select>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Recipients</label>
                  <div className="recipient-input-group">
                    <input
                      type="email"
                      value={newRecipient}
                      onChange={(e) => setNewRecipient(e.target.value)}
                      placeholder="Enter email address"
                      className="form-input"
                      onKeyPress={(e) => e.key === 'Enter' && handleAddRecipient()}
                    />
                    <button
                      type="button"
                      className="btn-secondary"
                      onClick={handleAddRecipient}
                    >
                      Add
                    </button>
                  </div>
                  <div className="recipients-list">
                    {formData.recipients.map(email => (
                      <div key={email} className="recipient-item">
                        <span>{email}</span>
                        <button
                          type="button"
                          className="remove-btn"
                          onClick={() => handleRemoveRecipient(email)}
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group checkbox">
                  <label>
                    <input
                      type="checkbox"
                      name="includeCharts"
                      checked={formData.includeCharts}
                      onChange={handleInputChange}
                    />
                    Include Charts & Visualizations
                  </label>
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={handleCloseModal}>Cancel</button>
              <button className="btn-primary" onClick={handleSaveSchedule} disabled={actionLoading === (editingSchedule?.id || 'create')}>
                {actionLoading === (editingSchedule?.id || 'create') ? 'Saving...' : 'Save Schedule'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ReportSchedulingAdmin
