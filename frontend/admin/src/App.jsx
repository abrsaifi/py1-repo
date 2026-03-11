import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '@shared/hooks/useAuth'
import ToastProvider from '@shared/components/Toast'
import { NotificationProvider } from '@shared/components/Notification'
import AdminDashboard from './pages/AdminDashboard'
import AdminLoginPage from './pages/AdminLoginPage'
import '@shared/styles/refinements.css'

function AppContent() {
  const auth = useAuth()

  if (!auth.isAuthenticated) {
    return (
      <Router>
        <Routes>
          <Route path="/" element={<AdminLoginPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    )
  }

  if (auth.user?.role !== 'admin') {
    auth.logout()
    return (
      <Router>
        <Routes>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    )
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<AdminDashboard />} />
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="*" element={<Navigate to="/admin" replace />} />
      </Routes>
    </Router>
  )
}

export default function App() {
  return (
    <ToastProvider>
      <NotificationProvider>
        <AppContent />
      </NotificationProvider>
    </ToastProvider>
  )
}
