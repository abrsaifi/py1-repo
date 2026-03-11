import { useState, useCallback } from 'react'
import '../styles/filters.css'

export const AdvancedFilters = ({ 
  fields = [], 
  onApply, 
  onReset,
  activeFilters = {}
}) => {
  const [filters, setFilters] = useState(activeFilters)
  const [isExpanded, setIsExpanded] = useState(false)

  const handleFilterChange = useCallback((fieldName, value, operation = 'equals') => {
    setFilters(prev => ({
      ...prev,
      [fieldName]: { value, operation }
    }))
  }, [])

  const handleApply = useCallback(() => {
    onApply(filters)
    setIsExpanded(false)
  }, [filters, onApply])

  const handleReset = useCallback(() => {
    setFilters({})
    onReset()
  }, [onReset])

  return (
    <div className="advanced-filters">
      <button 
        className="filter-toggle"
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
      >
        <i className="fas fa-sliders-h"></i>
        Advanced Filters
        {Object.keys(filters).length > 0 && (
          <span className="filter-count">{Object.keys(filters).length}</span>
        )}
      </button>

      {isExpanded && (
        <div className="filter-panel">
          <div className="filter-controls">
            {fields.map(field => (
              <div key={field.name} className="filter-item">
                <label>{field.label}</label>
                
                <select 
                  className="filter-operation"
                  onChange={(e) => {
                    const current = filters[field.name]
                    handleFilterChange(field.name, current?.value, e.target.value)
                  }}
                  defaultValue={filters[field.name]?.operation || 'equals'}
                >
                  <option value="equals">Equals</option>
                  <option value="contains">Contains</option>
                  <option value="gt">Greater than</option>
                  <option value="lt">Less than</option>
                  <option value="range">Range</option>
                  <option value="between">Between</option>
                </select>

                {field.type === 'select' ? (
                  <select
                    className="filter-value"
                    onChange={(e) => handleFilterChange(field.name, e.target.value)}
                    defaultValue={filters[field.name]?.value || ''}
                  >
                    <option value="">Select {field.label}</option>
                    {field.options?.map(opt => (
                      <option key={opt} value={opt}>{opt}</option>
                    ))}
                  </select>
                ) : field.type === 'date' ? (
                  <input
                    type="date"
                    className="filter-value"
                    onChange={(e) => handleFilterChange(field.name, e.target.value)}
                    defaultValue={filters[field.name]?.value || ''}
                  />
                ) : field.type === 'number' ? (
                  <input
                    type="number"
                    className="filter-value"
                    placeholder={`Enter ${field.label}`}
                    onChange={(e) => handleFilterChange(field.name, e.target.value)}
                    defaultValue={filters[field.name]?.value || ''}
                  />
                ) : (
                  <input
                    type="text"
                    className="filter-value"
                    placeholder={`Search ${field.label}`}
                    onChange={(e) => handleFilterChange(field.name, e.target.value)}
                    defaultValue={filters[field.name]?.value || ''}
                  />
                )}
              </div>
            ))}
          </div>

          <div className="filter-actions">
            <button className="btn-apply" onClick={handleApply}>
              <i className="fas fa-check"></i> Apply Filters
            </button>
            <button className="btn-reset" onClick={handleReset}>
              <i className="fas fa-times"></i> Reset
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default AdvancedFilters
