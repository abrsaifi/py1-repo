import { useState, useEffect } from 'react'
import { queriesAPI } from '../services/api'
import DataTable from '../components/DataTable'
import { UniversalIcon } from '../utils/UniversalIcon'
import '../styles/pages.css'

export const QueryPage = ({ onTitleChange }) => {
  const [queries, setQueries] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [selectedQuery, setSelectedQuery] = useState(null)
  const [newQuery, setNewQuery] = useState({
    name: '',
    query: '',
    description: '',
  })

  useEffect(() => {
    onTitleChange('Queries')
    fetchQueries()
  }, [onTitleChange])

  const fetchQueries = async () => {
    try {
      setLoading(true)
      // Mock data
      setQueries([
        {
          id: '1',
          name: 'Daily Active Users',
          queryType: 'aggregation',
          created: '2026-02-01',
          lastExecuted: '2026-03-04 08:00',
          status: 'success',
        },
        {
          id: '2',
          name: 'Revenue by Region',
          queryType: 'custom',
          created: '2026-02-15',
          lastExecuted: '2026-03-04 12:30',
          status: 'success',
        },
        {
          id: '3',
          name: 'Error Log Analysis',
          queryType: 'analysis',
          created: '2026-02-28',
          lastExecuted: '2026-03-04 15:45',
          status: 'failed',
        },
      ])
    } catch (error) {
      console.error('Failed to fetch queries:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateQuery = async (e) => {
    e.preventDefault()
    try {
      await queriesAPI.create(newQuery)
      setNewQuery({ name: '', query: '', description: '' })
      setShowForm(false)
      fetchQueries()
    } catch (error) {
      console.error('Failed to create query:', error)
    }
  }

  const columns = [
    { key: 'name', label: 'Query Name', sortable: true },
    { key: 'queryType', label: 'Type', sortable: true },
    { key: 'created', label: 'Created', sortable: true },
    { key: 'lastExecuted', label: 'Last Executed', sortable: true },
    { key: 'status', label: 'Status', sortable: true },
  ]

  return (
    <div className="query-page">
      <div className="page-header">
        <div>
          <h2>Queries</h2>
          <p>Execute and manage custom queries</p>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => setShowForm(!showForm)}
        >
          <UniversalIcon icon="fas fa-plus" size={20} /> New Query
        </button>
      </div>

      {showForm && (
        <div className="form-card">
          <h3>Create Custom Query</h3>
          <form onSubmit={handleCreateQuery}>
            <div className="form-group">
              <label>Query Name*</label>
              <input
                type="text"
                value={newQuery.name}
                onChange={(e) => setNewQuery({ ...newQuery, name: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label>Description</label>
              <textarea
                value={newQuery.description}
                onChange={(e) => setNewQuery({ ...newQuery, description: e.target.value })}
                rows="3"
              />
            </div>

            <div className="form-group">
              <label>Query*</label>
              <textarea
                value={newQuery.query}
                onChange={(e) => setNewQuery({ ...newQuery, query: e.target.value })}
                placeholder="Enter your query..."
                rows="6"
                required
              />
            </div>

            <div className="form-actions">
              <button type="submit" className="btn btn-success">
                Create Query
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
        title="Saved Queries"
        columns={columns}
        data={queries}
        loading={loading}
        onRowClick={setSelectedQuery}
      />
    </div>
  )
}

export default QueryPage
