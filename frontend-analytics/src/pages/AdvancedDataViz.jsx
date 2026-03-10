import React, { useState } from 'react'
import { UniversalIcon } from '../utils/UniversalIcon'

const AdvancedDataViz = () => {
  const [selectedViz, setSelectedViz] = useState('heatmap')

  const visualizations = [
    {
      id: 'heatmap',
      name: 'Heatmap',
      description: 'Time-series intensity visualization',
      icon: '🔥'
    },
    {
      id: 'scatter',
      name: 'Scatter Plot',
      description: 'Correlation and distribution analysis',
      icon: '📍'
    },
    {
      id: 'treemap',
      name: 'Treemap',
      description: 'Hierarchical data visualization',
      icon: '🌳'
    },
    {
      id: 'sankey',
      name: 'Sankey Diagram',
      description: 'Flow and relationship visualization',
      icon: '🔀'
    },
    {
      id: 'funnel',
      name: 'Funnel Chart',
      description: 'Conversion and drop-off analysis',
      icon: '📉'
    },
    {
      id: 'radar',
      name: 'Radar Chart',
      description: 'Multi-dimensional comparison',
      icon: '📡'
    }
  ]

  const renderVisualization = () => {
    switch (selectedViz) {
      case 'heatmap':
        return <HeatmapViz />
      case 'scatter':
        return <ScatterViz />
      case 'treemap':
        return <TreemapViz />
      case 'sankey':
        return <SankeyViz />
      case 'funnel':
        return <FunnelViz />
      case 'radar':
        return <RadarViz />
      default:
        return <HeatmapViz />
    }
  }

  return (
    <div className="advanced-data-viz">
      <div className="viz-selector">
        <h2><UniversalIcon icon="🎨" size={24} /> Advanced Visualizations</h2>
        <div className="viz-grid">
          {visualizations.map(viz => (
            <button
              key={viz.id}
              className={`viz-card ${selectedViz === viz.id ? 'selected' : ''}`}
              onClick={() => setSelectedViz(viz.id)}
            >
              <span className="viz-icon">{viz.icon}</span>
              <h3>{viz.name}</h3>
              <p>{viz.description}</p>
            </button>
          ))}
        </div>
      </div>

      <div className="viz-container">
        {renderVisualization()}
      </div>
    </div>
  )
}

const HeatmapViz = () => {
  const data = Array.from({ length: 7 }, (_, i) => ({
    day: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i],
    hours: Array.from({ length: 24 }, () => Math.floor(Math.random() * 100))
  }))

  return (
    <div className="viz-section">
      <h3>Daily Activity Heatmap (24-Hour View)</h3>
      <div className="heatmap">
        <div className="heatmap-labels">
          <div className="heatmap-label">Days</div>
          {Array.from({ length: 24 }, (_, i) => (
            <div key={`hour-${i}`} className="hour-label">{i}</div>
          ))}
        </div>
        {data.map((day, dayIdx) => (
          <div key={`day-${dayIdx}-${day.day}`} className="heatmap-row">
            <div className="day-label">{day.day}</div>
            {day.hours.map((value, hourIdx) => (
              <div
                key={`cell-${dayIdx}-${hourIdx}`}
                className="heatmap-cell"
                style={{
                  backgroundColor: `hsl(0, 100%, ${100 - value}%)`
                }}
                title={`${value} events`}
              />
            ))}
          </div>
        ))}
      </div>
      <div className="heatmap-legend">
        <span>Low</span>
        <div className="legend-gradient" />
        <span>High</span>
      </div>
    </div>
  )
}

const ScatterViz = () => {
  return (
    <div className="viz-section">
      <h3>Correlation Scatter Plot</h3>
      <svg width="100%" height="400" style={{ border: '1px solid #ddd', borderRadius: '8px' }}>
        <rect width="100%" height="400" fill="#f9f9f9" />
        {/* Y axis */}
        <line x1="60" y1="30" x2="60" y2="370" stroke="#333" strokeWidth="2" />
        {/* X axis */}
        <line x1="60" y1="370" x2="600" y2="370" stroke="#333" strokeWidth="2" />
        
        {/* Grid lines */}
        {Array.from({ length: 4 }, (_, i) => (
          <line key={`v${i}`} x1={60 + (i + 1) * 135} y1="30" x2={60 + (i + 1) * 135} y2="370" stroke="#e0e0e0" strokeDasharray="5,5" />
        ))}
        {Array.from({ length: 4 }, (_, i) => (
          <line key={`h${i}`} x1="60" y1={30 + (i + 1) * 85} x2="600" y2={30 + (i + 1) * 85} stroke="#e0e0e0" strokeDasharray="5,5" />
        ))}
        
        {/* Data points */}
        {Array.from({ length: 30 }, (_, i) => {
          const x = 60 + Math.random() * 540
          const y = 30 + Math.random() * 340
          return (
            <circle
              key={`point-${i}`}
              cx={x}
              cy={y}
              r="5"
              fill="#667eea"
              opacity="0.6"
              stroke="#764ba2"
              strokeWidth="2"
            />
          )
        })}
        
        {/* Labels */}
        <text x="30" y="350" fontSize="12" fill="#666">Y Axis</text>
        <text x="550" y="385" fontSize="12" fill="#666">X Axis</text>
      </svg>
      <div className="viz-stats">
        <p>Correlation: r = 0.87 (Strong Positive)</p>
        <p>R² = 0.76 (76% variance explained)</p>
      </div>
    </div>
  )
}

const TreemapViz = () => {
  const categories = [
    { name: 'Product A', value: 4200, color: '#667eea' },
    { name: 'Product B', value: 3100, color: '#764ba2' },
    { name: 'Product C', value: 2800, color: '#f093fb' },
    { name: 'Product D', value: 2100, color: '#4facfe' },
    { name: 'Product E', value: 1500, color: '#43e97b' },
    { name: 'Product F', value: 900, color: '#fa709a' }
  ]

  const total = categories.reduce((sum, cat) => sum + cat.value, 0)

  return (
    <div className="viz-section">
      <h3>Product Revenue Distribution</h3>
      <div className="treemap-grid">
        {categories.map((cat, idx) => {
          const percentage = (cat.value / total) * 100
          const size = Math.sqrt(percentage) * 30
          return (
            <div
              key={`cat-${idx}-${cat.name}`}
              className="treemap-box"
              style={{
                backgroundColor: cat.color,
                flex: percentage,
                minHeight: '100px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexDirection: 'column',
                color: 'white',
                padding: '10px',
                borderRadius: '8px',
                margin: '5px',
                textAlign: 'center'
              }}
            >
              <strong>{cat.name}</strong>
              <p>${cat.value.toLocaleString()}</p>
              <small>{percentage.toFixed(1)}%</small>
            </div>
          )
        })}
      </div>
    </div>
  )
}

const SankeyViz = () => {
  return (
    <div className="viz-section">
      <h3>Customer Journey Flow</h3>
      <svg width="100%" height="300" style={{ border: '1px solid #ddd', borderRadius: '8px' }}>
        <rect width="100%" height="300" fill="#f9f9f9" />
        
        {/* Landing */}
        <rect x="50" y="50" width="80" height="200" fill="#667eea" />
        <text x="90" y="160" fontSize="12" fill="white" textAnchor="middle" fontWeight="bold">Landing</text>
        <text x="90" y="175" fontSize="11" fill="white" textAnchor="middle">10,000</text>
        
        {/* Product Page */}
        <rect x="200" y="50" width="80" height="160" fill="#764ba2" />
        <text x="240" y="150" fontSize="12" fill="white" textAnchor="middle" fontWeight="bold">Product</text>
        <text x="240" y="165" fontSize="11" fill="white" textAnchor="middle">8,000</text>
        
        {/* Cart */}
        <rect x="350" y="50" width="80" height="100" fill="#f093fb" />
        <text x="390" y="110" fontSize="12" fill="white" textAnchor="middle" fontWeight="bold">Cart</text>
        <text x="390" y="125" fontSize="11" fill="white" textAnchor="middle">5,000</text>
        
        {/* Checkout */}
        <rect x="500" y="50" width="80" height="80" fill="#43e97b" />
        <text x="540" y="105" fontSize="12" fill="white" textAnchor="middle" fontWeight="bold">Checkout</text>
        <text x="540" y="120" fontSize="11" fill="white" textAnchor="middle">4,000</text>
        
        {/* Purchase */}
        <rect x="650" y="50" width="80" height="70" fill="#fa709a" />
        <text x="690" y="100" fontSize="12" fill="white" textAnchor="middle" fontWeight="bold">Purchase</text>
        <text x="690" y="115" fontSize="11" fill="white" textAnchor="middle">3,500</text>
        
        {/* Flow lines */}
        <path d="M 130 150 Q 165 145 200 130" stroke="#667eea" strokeWidth="8" fill="none" opacity="0.5" />
        <path d="M 280 130 Q 315 110 350 100" stroke="#764ba2" strokeWidth="5" fill="none" opacity="0.5" />
        <path d="M 430 90 Q 465 80 500 85" stroke="#f093fb" strokeWidth="4" fill="none" opacity="0.5" />
        <path d="M 580 85 Q 615 80 650 87" stroke="#43e97b" strokeWidth="3" fill="none" opacity="0.5" />
      </svg>
    </div>
  )
}

const FunnelViz = () => {
  const stages = [
    { label: 'Impressions', value: 100000, percentage: 100 },
    { label: 'Clicks', value: 65000, percentage: 65 },
    { label: 'Landing Page', value: 42000, percentage: 42 },
    { label: 'Product View', value: 28000, percentage: 28 },
    { label: 'Cart Add', value: 15000, percentage: 15 },
    { label: 'Checkout', value: 8500, percentage: 8.5 },
    { label: 'Purchase', value: 5100, percentage: 5.1 }
  ]

  return (
    <div className="viz-section">
      <h3>Conversion Funnel</h3>
      <div className="funnel-chart">
        {stages.map((stage, idx) => (
          <div key={`stage-${idx}-${stage.label}`} className="funnel-stage">
            <div
              className="funnel-bar"
              style={{
                width: `${stage.percentage * 3}px`,
                background: `linear-gradient(90deg, #667eea 0%, #764ba2 100%)`
              }}
            >
              <span className="stage-label">
                {stage.label}: {stage.value.toLocaleString()} ({stage.percentage.toFixed(1)}%)
              </span>
            </div>
            {idx < stages.length - 1 && (
              <div className="drop-off">
                Drop-off: {((stages[idx].value - stages[idx + 1].value) / stages[idx].value * 100).toFixed(1)}%
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

const RadarViz = () => {
  return (
    <div className="viz-section">
      <h3>Product Performance Radar</h3>
      <svg width="100%" height="400" viewBox="0 0 400 400" style={{ maxWidth: '500px', margin: '0 auto' }}>
        <circle cx="200" cy="200" r="100" fill="none" stroke="#ddd" />
        <circle cx="200" cy="200" r="80" fill="none" stroke="#ddd" />
        <circle cx="200" cy="200" r="60" fill="none" stroke="#ddd" />
        <circle cx="200" cy="200" r="40" fill="none" stroke="#ddd" />
        <circle cx="200" cy="200" r="20" fill="none" stroke="#ddd" />
        
        {/* Axes */}
        <line x1="200" y1="100" x2="200" y2="300" stroke="#ddd" />
        <line x1="100" y1="200" x2="300" y2="200" stroke="#ddd" />
        <line x1="129" y1="129" x2="271" y2="271" stroke="#ddd" />
        <line x1="271" y1="129" x2="129" y2="271" stroke="#ddd" />
        
        {/* Labels */}
        <text x="200" y="90" textAnchor="middle" fontSize="12" fontWeight="bold">Quality</text>
        <text x="310" y="205" textAnchor="start" fontSize="12" fontWeight="bold">Price</text>
        <text x="200" y="320" textAnchor="middle" fontSize="12" fontWeight="bold">Performance</text>
        <text x="80" y="205" textAnchor="end" fontSize="12" fontWeight="bold">Support</text>
        
        {/* Data polygon */}
        <polygon
          points="200,130 250,150 270,200 250,250 200,270 150,250 130,200 150,150"
          fill="#667eea"
          opacity="0.4"
          stroke="#667eea"
          strokeWidth="2"
        />
      </svg>
      <div className="radar-legend">
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#667eea' }} />
          <span>Current Product</span>
        </div>
      </div>
    </div>
  )
}

export default AdvancedDataViz
