import { useState, useEffect } from 'react'
import { healthAPI } from '../services/api'
import { useDarkMode } from '../hooks/useDarkMode'
import { UniversalIcon } from '../utils/UniversalIcon'
import '../styles/header.css'

export const Header = ({ title }) => {
  const [health, setHealth] = useState(null)
  const [time, setTime] = useState(new Date())
  const [searchQuery, setSearchQuery] = useState('')
  const { isDark, toggleDarkMode } = useDarkMode()

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const response = await healthAPI.getHealth()
        setHealth(response.data?.status || 'healthy')
      } catch (error) {
        // Backend not available - set to unavailable without logging error
        setHealth('unavailable')
      }
    }

    // Only fetch health if backend is available
    // In development, backend may not be running
    const timer = setTimeout(fetchHealth, 500)
    const interval = setInterval(() => setTime(new Date()), 1000)

    return () => {
      clearTimeout(timer)
      clearInterval(interval)
    }
  }, [])

  return (
    <header className="header">
      <div className="header-left">
        <h1 className="page-title">{title}</h1>
      </div>

      <div className="header-center">
        <div className="search-box">
          <UniversalIcon icon="fas fa-search" size={18} />
          <input 
            type="text" 
            placeholder="Search metrics, dashboards..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <button 
              className="search-clear"
              onClick={() => setSearchQuery('')}
            >
              <UniversalIcon icon="fas fa-times" size={16} />
            </button>
          )}
        </div>
      </div>

      <div className="header-right">
        <div className="status-indicator">
          <span className={`status-dot ${health === 'healthy' ? 'healthy' : health === 'unavailable' ? 'danger' : 'warning'}`}></span>
          <span className="status-text">
            {health === 'healthy' ? 'System OK' : health === 'unavailable' ? 'Offline' : 'Checking...'}
          </span>
        </div>

        <div className="time-display">
          <UniversalIcon icon="fas fa-clock" size={16} />
          <span>{time.toLocaleTimeString()}</span>
        </div>

        <button className="mode-toggle-btn" onClick={toggleDarkMode} title={isDark ? 'Light Mode' : 'Dark Mode'}>
          <UniversalIcon icon={isDark ? 'fas fa-sun' : 'fas fa-moon'} size={18} />
        </button>

        <button className="notification-btn" title="Notifications">
          <UniversalIcon icon="fas fa-bell" size={18} />
          <span className="notification-badge">3</span>
        </button>

        <button className="help-btn" title="Help">
          <UniversalIcon icon="fas fa-question-circle" size={18} />
        </button>
      </div>
    </header>
  )
}

export default Header
