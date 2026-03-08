import { useState, useEffect } from 'react'
import { reportsAPI } from '../services/api'
import DataTable from '../components/DataTable'
import { UniversalIcon } from '../utils/UniversalIcon'
import '../styles/pages.css'

export const ReportsPage = ({ onTitleChange }) => {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [newReport, setNewReport] = useState({
    name: '',
    type: 'standard',
    format: 'pdf',
    frequency: 'weekly',
  })

  useEffect(() => {
    onTitleChange('Reports')
    fetchReports()
  }, [onTitleChange])

  const fetchReports = async () => {
    try {
      setLoading(true)
      // Mock data
      setReports([
        {
          id: '1',
          name: 'Weekly Performance Report',
          type: 'standard',
          frequency: 'weekly',
          lastGenerated: '2026-03-03',
          status: 'completed',
        },
        {
          id: '2',
          name: 'Monthly Revenue Report',
          type: 'financial',
          frequency: 'monthly',
          lastGenerated: '2026-02-28',
          status: 'completed',
        },
        {
          id: '3',
          name: 'Daily Metrics Summary',
          type: 'metrics',
          frequency: 'daily',
          lastGenerated: '2026-03-04',
          status: 'pending',
        },
      ])
    } catch (error) {
      console.error('Failed to fetch reports:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateReport = async (e) => {
    e.preventDefault()
    try {
      await reportsAPI.create(newReport)
      setNewReport({ name: '', type: 'standard', format: 'pdf', frequency: 'weekly' })
      setShowForm(false)
      fetchReports()
    } catch (error) {
      console.error('Failed to create report:', error)
    }
  }

  const columns = [
    { key: 'name', label: 'Report Name', sortable: true },
    { key: 'type', label: 'Type', sortable: true },
    { key: 'frequency', label: 'Frequency', sortable: true },
    { key: 'lastGenerated', label: 'Last Generated', sortable: true },
    { key: 'status', label: 'Status', sortable: true },
  ]

  return (
    <div className="reports-page">
      <div className="page-header">
        <div>
          <h2>Reports</h2>
          <p>Generate and manage analytics reports</p>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => setShowForm(!showForm)}
        >
          <UniversalIcon icon="fas fa-plus" size={20} /> Create Report
        </button>
      </div>

      {showForm && (
        <div className="form-card">
          <h3>Create New Report</h3>
          <form onSubmit={handleCreateReport}>
            <div className="form-group">
              <label>Report Name*</label>
              <input
                type="text"
                value={newReport.name}
                onChange={(e) => setNewReport({ ...newReport, name: e.target.value })}
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Report Type</label>
                <select
                  value={newReport.type}
                  onChange={(e) => setNewReport({ ...newReport, type: e.target.value })}
                >
                  <option value="standard">Standard</option>
                  <option value="financial">Financial</option>
                  <option value="metrics">Metrics</option>
                </select>
              </div>

              <div className="form-group">
                <label>Format</label>
                <select
                  value={newReport.format}
                  onChange={(e) => setNewReport({ ...newReport, format: e.target.value })}
                >
                  <option value="pdf">PDF</option>
                  <option value="excel">Excel</option>
                  <option value="json">JSON</option>
                </select>
              </div>

              <div className="form-group">
                <label>Frequency</label>
                <select
                  value={newReport.frequency}
                  onChange={(e) => setNewReport({ ...newReport, frequency: e.target.value })}
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn btn-success">
                Create Report
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setShowForm(false)}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <DataTable
        title="All Reports"
        columns={columns}
        data={reports}
        loading={loading}
      />
    </div>
  )
}

export default ReportsPage
