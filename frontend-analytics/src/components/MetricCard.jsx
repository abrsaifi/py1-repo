// Metric card component
import { UniversalIcon } from '../utils/UniversalIcon'
import '../styles/cards.css'

export const MetricCard = ({ title, value, unit, trend, icon, color = 'blue' }) => {
  const isPositive = trend >= 0
  // Build Font Awesome class from icon name
  const faIcon = icon ? `fas fa-${icon}` : 'fas fa-chart-bar'

  return (
    <div className={`metric-card ${color}`}>
      <div className="metric-header">
        <h3 className="metric-title">{title}</h3>
        <div className="metric-icon">
          <UniversalIcon icon={faIcon} size={24} />
        </div>
      </div>

      <div className="metric-value">
        <span className="value">{typeof value === 'number' ? value.toLocaleString() : value}</span>
        {unit && <span className="unit">{unit}</span>}
      </div>

      {trend !== undefined && (
        <div className={`metric-trend ${isPositive ? 'positive' : 'negative'}`}>
          <UniversalIcon icon={isPositive ? 'fas fa-arrow-up' : 'fas fa-arrow-down'} size={16} />
          <span>{Math.abs(trend)}%</span>
        </div>
      )}
    </div>
  )
}

export default MetricCard
