import React, { useState, useEffect } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import '../styles/admin.css'

const TrafficAnalytics = () => {
  const [stats, setStats] = useState({
    realTimeVisitors: 412,
    conversionRate: 8.4,
    topPages: [
      { name: 'Convert PDF to DOCX', visits: 1245, rate: 9.2 },
      { name: 'Convert JPG to PNG', visits: 892, rate: 7.8 },
      { name: 'Convert XLSX to CSV', visits: 756, rate: 8.1 },
      { name: 'Batch Converter', visits: 634, rate: 6.5 }
    ],
    trafficSource: [
      { source: 'Organic Search', percentage: 45, visitors: 185 },
      { source: 'Direct', percentage: 30, visitors: 124 },
      { source: 'Social Media', percentage: 15, visitors: 62 },
      { source: 'Referral', percentage: 10, visitors: 41 }
    ]
  })

  useEffect(() => {
    const interval = setInterval(() => {
      setStats(prev => ({
        ...prev,
        realTimeVisitors: Math.max(0, prev.realTimeVisitors + Math.floor(Math.random() * 20) - 10)
      }))
    }, 2000)
    
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="📊" size={24} /> Traffic Analytics</h2>
      <p className="section-subtitle">Real-time visitor tracking and conversion metrics</p>

      <div className="admin-stats-grid">
        <div className="admin-stat-card">
          <UniversalIcon icon="👥" size={32} />
          <div className="stat-content">
            <h3>Live Visitors</h3>
            <p className="stat-value">{stats.realTimeVisitors}</p>
            <p className="stat-detail">Right now</p>
          </div>
        </div>

        <div className="admin-stat-card">
          <UniversalIcon icon="📈" size={32} />
          <div className="stat-content">
            <h3>Conversion Rate</h3>
            <p className="stat-value">{stats.conversionRate}%</p>
            <p className="stat-detail">Today average</p>
          </div>
        </div>

        <div className="admin-stat-card">
          <UniversalIcon icon="🌍" size={32} />
          <div className="stat-content">
            <h3>Geographic</h3>
            <p className="stat-value">47</p>
            <p className="stat-detail">Countries</p>
          </div>
        </div>

        <div className="admin-stat-card">
          <UniversalIcon icon="🔝" size={32} />
          <div className="stat-content">
            <h3>Top Page</h3>
            <p className="stat-value">1,245</p>
            <p className="stat-detail">Visits today</p>
          </div>
        </div>
      </div>

      <div className="admin-section-content">
        <div className="two-column">
          <div className="column">
            <h3>Top Converting Pages</h3>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Page Name</th>
                  <th>Visits</th>
                  <th>Conversion Rate</th>
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
              </tbody>
            </table>
          </div>

          <div className="column">
            <h3>Traffic Sources</h3>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Source</th>
                  <th>Visitors</th>
                  <th>Percentage</th>
                </tr>
              </thead>
              <tbody>
                {stats.trafficSource.map((source, idx) => (
                  <tr key={`source-${idx}-${source.name}`}>
                    <td>{source.source}</td>
                    <td>{source.visitors}</td>
                    <td>
                      <div className="mini-progress-bar">
                        <div 
                          className="progress-fill" 
                          style={{ width: `${source.percentage}%` }}
                        ></div>
                      </div>
                      <span className="percentage">{source.percentage}%</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TrafficAnalytics
