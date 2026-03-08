// Empty and error state components
import React from 'react'
import { UniversalIcon } from '../utils/UniversalIcon'
import '../styles/empty.css'

export const EmptyState = ({ 
  icon = 'fas fa-inbox',
  title = 'No data',
  message = 'No data available at this time',
  action,
  actionLabel = 'Create'
}) => {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">
        <UniversalIcon icon={icon} size={48} />
      </div>
      <h3 className="empty-state-title">{title}</h3>
      <p className="empty-state-message">{message}</p>
      {action && (
        <button className="btn btn-primary" onClick={action}>
          <UniversalIcon icon="fas fa-plus" size={16} /> {actionLabel}
        </button>
      )}
    </div>
  )
}

export const ErrorState = ({ 
  icon = 'fas fa-exclamation-triangle',
  title = 'Something went wrong',
  message = 'An error occurred while loading data',
  action,
  actionLabel = 'Try Again'
}) => {
  return (
    <div className="error-state">
      <div className="error-state-icon">
        <UniversalIcon icon={icon} size={48} />
      </div>
      <h3 className="error-state-title">{title}</h3>
      <p className="error-state-message">{message}</p>
      {action && (
        <button className="btn btn-primary" onClick={action}>
          <UniversalIcon icon="fas fa-redo" size={16} /> {actionLabel}
        </button>
      )}
    </div>
  )
}

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <ErrorState 
          title="Component Error"
          message={this.state.error?.message || 'An unexpected error occurred'}
          action={() => this.setState({ hasError: false, error: null })}
          actionLabel="Try Again"
        />
      )
    }

    return this.props.children
  }
}

export default EmptyState
