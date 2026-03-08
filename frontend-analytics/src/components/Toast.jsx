import { useState, useCallback, createContext, useContext } from 'react'
import '../styles/toast.css'

const ToastContext = createContext()

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback(({ type = 'info', title, message, duration = 4000 }) => {
    const id = Date.now()
    const toast = { id, type, title, message, duration }
    
    setToasts(prev => [...prev, toast])
    
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }
    
    return id
  }, [])

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      <div className="toast-container">
        {toasts.map(toast => (
          <div key={toast.id} className={`toast toast-${toast.type}`}>
            <div className="toast-icon">
              {toast.type === 'success' && <i className="fas fa-check-circle"></i>}
              {toast.type === 'error' && <i className="fas fa-exclamation-circle"></i>}
              {toast.type === 'warning' && <i className="fas fa-warning"></i>}
              {toast.type === 'info' && <i className="fas fa-info-circle"></i>}
            </div>
            <div className="toast-content">
              {toast.title && <div className="toast-title">{toast.title}</div>}
              {toast.message && <div className="toast-message">{toast.message}</div>}
            </div>
            <button 
              className="toast-close"
              onClick={() => removeToast(toast.id)}
            >
              <i className="fas fa-times"></i>
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export const useToast = () => {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within ToastProvider')
  }
  return context
}

export default ToastProvider
