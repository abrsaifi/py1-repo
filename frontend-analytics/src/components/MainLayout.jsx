import { useState } from 'react'
import Sidebar from './Sidebar'
import Header from './Header'
import '../styles/main-layout.css'

export const MainLayout = ({ children, isAuthenticated, onLogout, userName, userRole, pageTitle, onTitleChange }) => {
  const [pageTitle_, setPageTitle] = useState(pageTitle || 'Dashboard')

  // Update page title when prop changes
  if (pageTitle && pageTitle !== pageTitle_) {
    setPageTitle(pageTitle)
  }

  return (
    <div className={`main-layout ${isAuthenticated ? 'authenticated' : 'public'}`}>
      {isAuthenticated && (
        <Sidebar onLogout={onLogout} userName={userName} userRole={userRole} />
      )}
      
      <div className="layout-wrapper">
        {isAuthenticated && (
          <Header title={pageTitle_} />
        )}
        
        <div className={`layout-content ${isAuthenticated ? 'with-header' : 'full-screen'}`}>
          {children}
        </div>
      </div>
    </div>
  )
}

export default MainLayout
