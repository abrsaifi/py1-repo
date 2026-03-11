// Report Scheduling & Email Service
import { useState, useCallback } from 'react'

// Report Scheduler Class
export class ReportScheduler {
  constructor() {
    this.schedules = new Map()
    this.jobs = new Map()
  }

  // Schedule a report with cron-like syntax
  scheduleReport(reportId, config) {
    const {
      frequency,      // 'daily', 'weekly', 'monthly'
      time,           // 'HH:MM' format
      recepients,     // email array
      format,         // 'pdf', 'csv', 'json'
      enabled = true
    } = config

    const schedule = {
      reportId,
      frequency,
      time,
      recipients: recepients,
      format,
      enabled,
      createdAt: new Date(),
      lastRun: null,
      nextRun: this.calculateNextRun(frequency, time)
    }

    this.schedules.set(reportId, schedule)
    
    if (enabled) {
      this.createJob(reportId, schedule)
    }

    return schedule
  }

  calculateNextRun(frequency, time) {
    const [hours, minutes] = time.split(':').map(Number)
    const next = new Date()
    next.setHours(hours, minutes, 0, 0)

    if (next < new Date()) {
      next.setDate(next.getDate() + 1)
      if (frequency === 'weekly') {
        next.setDate(next.getDate() + 7)
      } else if (frequency === 'monthly') {
        next.setMonth(next.getMonth() + 1)
      }
    }

    return next
  }

  createJob(reportId, schedule) {
    const job = setInterval(() => {
      this.executeReport(reportId, schedule)
    }, 60000) // Check every minute

    this.jobs.set(reportId, job)
  }

  executeReport(reportId, schedule) {
    const now = new Date()
    if (now >= schedule.nextRun) {
      // Trigger report generation
      console.log(`Executing scheduled report: ${reportId}`)
      schedule.lastRun = new Date()
      schedule.nextRun = this.calculateNextRun(schedule.frequency, schedule.time)
      
      // Send email
      this.sendReportEmail(reportId, schedule)
    }
  }

  sendReportEmail(reportId, schedule) {
    // Construct email payload
    const emailPayload = {
      reportId,
      recipients: schedule.recipients,
      subject: `Scheduled Report: ${reportId}`,
      format: schedule.format,
      timestamp: new Date().toISOString()
    }

    // Send via API
    fetch('/api/reports/send-email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(emailPayload)
    }).catch(err => console.error('Email send failed:', err))
  }

  updateSchedule(reportId, updates) {
    const schedule = this.schedules.get(reportId)
    if (!schedule) return null

    Object.assign(schedule, updates)
    
    // Restart job if frequency changed
    if (updates.frequency || updates.time) {
      clearInterval(this.jobs.get(reportId))
      this.createJob(reportId, schedule)
    }

    return schedule
  }

  deleteSchedule(reportId) {
    clearInterval(this.jobs.get(reportId))
    this.jobs.delete(reportId)
    this.schedules.delete(reportId)
  }

  getSchedule(reportId) {
    return this.schedules.get(reportId)
  }

  getAllSchedules() {
    return Array.from(this.schedules.values())
  }
}

// React Hook for Report Scheduling
export function useReportScheduler() {
  const [schedules, setSchedules] = useState([])
  const schedulerRef = React.useRef(new ReportScheduler())

  const createSchedule = useCallback((reportId, config) => {
    const schedule = schedulerRef.current.scheduleReport(reportId, config)
    setSchedules(prev => [...prev, schedule])
    return schedule
  }, [])

  const updateSchedule = useCallback((reportId, updates) => {
    const schedule = schedulerRef.current.updateSchedule(reportId, updates)
    setSchedules(prev => prev.map(s => s.reportId === reportId ? schedule : s))
    return schedule
  }, [])

  const deleteSchedule = useCallback((reportId) => {
    schedulerRef.current.deleteSchedule(reportId)
    setSchedules(prev => prev.filter(s => s.reportId !== reportId))
  }, [])

  return {
    schedules,
    createSchedule,
    updateSchedule,
    deleteSchedule
  }
}

// Email Service
export class EmailService {
  static async sendReport(reportId, recipients, format = 'pdf') {
    try {
      const response = await fetch('/api/reports/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          reportId,
          recipients,
          format,
          timestamp: new Date().toISOString()
        })
      })

      if (!response.ok) throw new Error('Failed to send email')
      return await response.json()
    } catch (error) {
      console.error('Email send error:', error)
      throw error
    }
  }

  static async sendNotification(userId, message, type = 'info') {
    try {
      const response = await fetch('/api/notifications/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId,
          message,
          type,
          timestamp: new Date().toISOString()
        })
      })

      return await response.json()
    } catch (error) {
      console.error('Notification send error:', error)
      throw error
    }
  }

  static async scheduleEmail(recipients, subject, body, sendAt) {
    try {
      const response = await fetch('/api/emails/schedule', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recipients,
          subject,
          body,
          sendAt,
          status: 'scheduled'
        })
      })

      return await response.json()
    } catch (error) {
      console.error('Email scheduling error:', error)
      throw error
    }
  }
}

export default ReportScheduler
