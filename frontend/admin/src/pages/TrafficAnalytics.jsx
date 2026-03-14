import React, { useState, useEffect } from 'react'
import { adminAPI } from '@shared/api/api'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import '../styles/admin.css'

const TrafficAnalytics = () => {
  const [stats, setStats] = useState({
    realTimeVisitors: 0,
    conversionRate: 0,
    countries: 0,
    topPages: [],
    topPageVisits: 0,
    topPageName: 'N/A',
    trafficSource: [],
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [lastUpdated, setLastUpdated] = useState('')

  useEffect(() => {
    loadTrafficAnalytics()
    const intervalId = window.setInterval(() => {
      loadTrafficAnalytics(false)
    }, 15000)

    return () => window.clearInterval(intervalId)
  }, [])

  const loadTrafficAnalytics = async (showLoader = true) => {
    try {
      if (showLoader) {
        setLoading(true)
      }
      setError('')
      const response = await adminAPI.getAnalyticsOverview({ days: 7 })
      setStats(response.data?.traffic || {
        realTimeVisitors: 0,
        conversionRate: 0,
        countries: 0,
        topPages: [],
        topPageVisits: 0,
        topPageName: 'N/A',
        trafficSource: [],
      })
      setLastUpdated(response.data?.generatedAt || '')
    } catch (err) {
      console.error('Failed to fetch traffic analytics:', err)
      setError(err.message || 'Failed to fetch traffic analytics')
    } finally {
      if (showLoader) {
        setLoading(false)
      }
    }
  }

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="📊" size={24} /> Traffic Analytics</h2>
      <p className="section-subtitle">
        Live usage and conversion telemetry
        {lastUpdated ? ` • Last updated ${lastUpdated.replace('T', ' ').slice(0, 19)}` : ''}
      </p>

      {error && <div className="alert-banner error">{error}</div>}

      <div className="admin-stats-grid">
        <div className="admin-stat-card">
          <UniversalIcon icon="👥" size={32} />
          <div className="stat-content">
            <h3>Live Visitors</h3>
            <p className="stat-value">{stats.realTimeVisitors}</p>
            <p className="stat-detail">Active sessions</p>
          </div>
        </div>

        <div className="admin-stat-card">
          <UniversalIcon icon="📈" size={32} />
          <div className="stat-content">
            <h3>Conversion Rate</h3>
            <p className="stat-value">{stats.conversionRate}%</p>
            <p className="stat-detail">24h success rate</p>
          </div>
        </div>

        <div className="admin-stat-card">
          <UniversalIcon icon="🌍" size={32} />
          <div className="stat-content">
            <h3>Coverage Segments</h3>
            <p className="stat-value">{stats.countries}</p>
            <p className="stat-detail">Plans and roles tracked</p>
          </div>
        </div>

        <div className="admin-stat-card">
          <UniversalIcon icon="🔝" size={32} />
          <div className="stat-content">
            <h3>Top Output</h3>
            <p className="stat-value">{stats.topPageVisits}</p>
            <p className="stat-detail">{stats.topPageName}</p>
          </div>
        </div>
      </div>

      <div className="admin-section-content">
        <div className="filter-controls" style={{ justifyContent: 'flex-end', marginBottom: '16px' }}>
          <button className="action-button primary" onClick={() => loadTrafficAnalytics()} disabled={loading}>
            <UniversalIcon icon="📈" size={16} /> {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>

        <div className="two-column">
          <div className="column">
            <h3>Top Output Formats</h3>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Format</th>
                  <th>Completed Jobs</th>
                  <th>Share</th>
                </tr>
              </thead>
              <tbody>
                {stats.topPages.map((page, idx) => (
                  <tr key={`page-${idx}-${page.name}`}>
                    <td>{page.name}</td>
                    <td>{page.visits}</td>
                    <td>{page.rate}%</td>
                  </tr>
                ))}
                {!loading && stats.topPages.length === 0 && (
                  <tr>
                    <td colSpan="3">No completed format data available</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="column">
            <h3>Traffic Segments</h3>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Segment</th>
                  <th>Value</th>
                  <th>Percentage</th>
                </tr>
              </thead>
              <tbody>
                {stats.trafficSource.map((source, idx) => (
                  <tr key={`source-${idx}-${source.source}`}>
                    <td>{source.source}</td>
                    <td>{source.visitors}</td>
                    <td>
                      <div className="mini-progress-bar">
                        <div className="progress-fill" style={{ width: `${Math.min(source.percentage || 0, 100)}%` }}></div>
                      </div>
                      <span className="percentage">{source.percentage}%</span>
                    </td>
                  </tr>
                ))}
                {!loading && stats.trafficSource.length === 0 && (
                  <tr>
                    <td colSpan="3">No segment data available</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TrafficAnalytics