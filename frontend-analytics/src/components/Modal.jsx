// Minimal imports needed for this component
import { UniversalIcon } from '../utils/UniversalIcon'
import '../styles/modal.css'

export const Modal = ({ 
  isOpen = false, 
  title, 
  children, 
  onClose, 
  size = 'md',
  footer,
  closeButton = true
}) => {
  if (!isOpen) return null

  return (
    <>
      <div className="modal-overlay" onClick={onClose}></div>
      <div className={`modal modal-${size}`}>
        {title && (
          <div className="modal-header">
            <h2 className="modal-title">{title}</h2>
            {closeButton && (
              <button className="modal-close" onClick={onClose}>
                <UniversalIcon icon="fas fa-times" size={20} />
              </button>
            )}
          </div>
        )}
        <div className="modal-body">
          {children}
        </div>
        {footer && <div className="modal-footer">{footer}</div>}
      </div>
    </>
  )
}

export default Modal
