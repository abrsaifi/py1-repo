import React, { useState, useEffect } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import { useReportScheduler } from '../services/reportScheduler'

const ReportSchedulingAdmin = () => {
  const { scheduleReport, getSchedules, updateSchedule, deleteSchedule } = useReportScheduler()
  const [schedules, setSchedules] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [editingSchedule, setEditingSchedule] = useState(null)
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

  const loadSchedules = () => {
    const stored = localStorage.getItem('report-schedules')
    if (stored) {
      setSchedules(JSON.parse(stored))
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

  const handleSaveSchedule = () => {
    if (!formData.reportName) {
      alert('Please enter a report name')
      return
    }

    if (formData.recipients.length === 0) {
      alert('Please add at least one recipient')
      return
    }

    const schedule = {
      id: editingSchedule?.id || `schedule-${Date.now()}`,
      ...formData,
      createdAt: editingSchedule?.createdAt || new Date().toISOString().split('T')[0],
      updatedAt: new Date().toISOString().split('T')[0],
      nextRun: calculateNextRun(formData.frequency, formData.time)
    }

    let updatedSchedules
    if (editingSchedule) {
      updatedSchedules = schedules.map(s => s.id === editingSchedule.id ? schedule : s)
    } else {
      updatedSchedules = [...schedules, schedule]
    }

    setSchedules(updatedSchedules)
    localStorage.setItem('report-schedules', JSON.stringify(updatedSchedules))
    handleCloseModal()
  }

  const calculateNextRun = (frequency, time) => {
    const now = new Date()
    const [hours, minutes] = time.split(':').map(Number)

    const next = new Date(now)
    next.setHours(hours, minutes, 0, 0)

    if (next <= now) {
      next.setDate(next.getDate() + 1)
    }

    return next.toISOString().split('T')[0]
  }

  const handleToggleSchedule = (scheduleId) => {
    const updatedSchedules = schedules.map(s => {
      if (s.id === scheduleId) {
        return { ...s, enabled: !s.enabled }
      }
      return s
    })
    setSchedules(updatedSchedules)
    localStorage.setItem('report-schedules', JSON.stringify(updatedSchedules))
  }

  const handleDeleteSchedule = (scheduleId) => {
    if (window.confirm('Are you sure you want to delete this schedule?')) {
      const updatedSchedules = schedules.filter(s => s.id !== scheduleId)
      setSchedules(updatedSchedules)
      localStorage.setItem('report-schedules', JSON.stringify(updatedSchedules))
    }
  }

  const handleTestSchedule = (schedule) => {
    alert(`Test email would be sent to: ${schedule.recipients.join(', ')}`)
  }

  return (
    <div className="report-scheduling-admin">
      <div className="management-header">
        <h2><UniversalIcon icon="📅" size={24} /> Report Scheduling</h2>
        <button className="btn-primary" onClick={() => handleOpenModal()}>
          + Create Schedule
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
                    onClick={() => handleToggleSchedule(schedule.id)}
                    title={schedule.enabled ? 'Disable' : 'Enable'}
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
                >
                  <UniversalIcon icon="✍️" size={14} /> Edit
                </button>
                <button
                  className="btn-small btn-info"
                  onClick={() => handleTestSchedule(schedule)}
                  title="Send Test Email"
                >
                  <UniversalIcon icon="📧" size={14} /> Test
                </button>
                <button
                  className="btn-small btn-danger"
                  onClick={() => handleDeleteSchedule(schedule.id)}
                  title="Delete"
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
              <button className="btn-primary" onClick={handleSaveSchedule}>Save Schedule</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ReportSchedulingAdmin
