import { useState, useMemo } from 'react'
import { UniversalIcon } from '../utils/UniversalIcon'
import '../styles/table.css'

export const DataTable = ({ columns, data, title, onRowClick, loading = false }) => {
  const [sortConfig, setSortConfig] = useState(null)

  const sortedData = useMemo(() => {
    if (!sortConfig) return data

    const sorted = [...data].sort((a, b) => {
      const aValue = a[sortConfig.key]
      const bValue = b[sortConfig.key]

      if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1
      if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1
      return 0
    })

    return sorted
  }, [data, sortConfig])

  const handleSort = (key) => {
    setSortConfig(current => ({
      key,
      direction: current?.key === key && current.direction === 'asc' ? 'desc' : 'asc',
    }))
  }

  return (
    <div className="data-table-container">
      {title && <h3 className="table-title">{title}</h3>}

      <table className="data-table">
        <thead>
          <tr>
            {columns.map(col => (
              <th
                key={col.key}
                onClick={() => col.sortable !== false && handleSort(col.key)}
                className={col.sortable !== false ? 'sortable' : ''}
              >
                {col.label}
                {sortConfig?.key === col.key && (
                  <UniversalIcon icon={`fas fa-arrow-${sortConfig.direction === 'asc' ? 'up' : 'down'}`} size={16} />
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {loading ? (
            <tr>
              <td colSpan={columns.length} className="loading">
                <UniversalIcon icon="fas fa-spinner" size={20} className="fa-spin" /> Loading...
              </td>
            </tr>
          ) : sortedData.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="empty">
                No data available
              </td>
            </tr>
          ) : (
            sortedData.map((row, idx) => (
              <tr
                key={`row-${idx}-${Object.values(row).join('-')}`}
                onClick={() => onRowClick && onRowClick(row)}
                className={onRowClick ? 'clickable' : ''}
              >
                {columns.map(col => (
                  <td key={col.key}>{row[col.key]}</td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}

export default DataTable
