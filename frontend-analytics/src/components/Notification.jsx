import { useState, useCallback, useRef } from 'react'
import { UniversalIcon } from '../utils/UniversalIcon'
import '../styles/notifications.css'

// Notification System
export const useNotification = () => {
  const [notifications, setNotifications] = useState([])
  const countRef = useRef(0)

  const addNotification = useCallback((message, type = 'info', duration = 5000) => {
    const id = countRef.current++
    const notification = { id, message, type, timestamp: Date.now() }
    
    setNotifications(prev => [...prev, notification])

    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, duration)
    }

    return id
  }, [])

  const removeNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }, [])

  const success = useCallback((message, duration = 5000) => {
    return addNotification(message, 'success', duration)
  }, [addNotification])

  const error = useCallback((message, duration = 8000) => {
    return addNotification(message, 'error', duration)
  }, [addNotification])

  const warning = useCallback((message, duration = 6000) => {
    return addNotification(message, 'warning', duration)
  }, [addNotification])

  const info = useCallback((message, duration = 5000) => {
    return addNotification(message, 'info', duration)
  }, [addNotification])

  return {
    notifications,
    addNotification,
    removeNotification,
    success,
    error,
    warning,
    info
  }
}

// Notification Component
export const NotificationContainer = ({ notifications, onDismiss }) => {
  return (
    <div className="notification-container">
      {notifications.map(notification => (
        <Notification
          key={notification.id}
          notification={notification}
          onDismiss={() => onDismiss(notification.id)}
        />
      ))}
    </div>
  )
}

const Notification = ({ notification, onDismiss }) => {
  const getIcon = () => {
    switch (notification.type) {
      case 'success': return 'fas fa-check-circle'
      case 'error': return 'fas fa-exclamation-circle'
      case 'warning': return 'fas fa-exclamation-triangle'
      default: return 'fas fa-info-circle'
    }
  }

  return (
    <div className={`notification notification-${notification.type}`}>
      <div className="notification-content">
        <UniversalIcon icon={getIcon()} size={20} className="notification-icon" />
        <p className="notification-message">{notification.message}</p>
      </div>
      <button className="notification-close" onClick={onDismiss}>
        <UniversalIcon icon="fas fa-times" size={16} />
      </button>
    </div>
  )
}

// Context for global notification access
import { createContext, useContext } from 'react'

const NotificationContext = createContext(null)

export const NotificationProvider = ({ children }) => {
  const notification = useNotification()

  return (
    <NotificationContext.Provider value={notification}>
      <>
        <NotificationContainer
          notifications={notification.notifications}
          onDismiss={notification.removeNotification}
        />
        {children}
      </>
    </NotificationContext.Provider>
  )
}

export const useNotificationContext = () => {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error('useNotificationContext must be used within NotificationProvider')
  }
  return context
}
