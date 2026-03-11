import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '@shared/hooks/useAuth'
import ToastProvider from '@shared/components/Toast'
import { NotificationProvider } from '@shared/components/Notification'
import MainLayout from './components/MainLayout'

import LandingPage from './pages/public/LandingPage'
import LoginPage from './pages/public/LoginPage'
import RegisterPage from './pages/public/RegisterPage'
import ForgotPasswordPage from './pages/public/ForgotPasswordPage'

import UserDashboard from './pages/dashboard/UserDashboard'
import SubscriberDashboard from './pages/dashboard/SubscriberDashboard'
import UserProfile from './pages/dashboard/UserProfile'
import AccountSettings from './pages/dashboard/AccountSettings'
import SettingsPage from './pages/dashboard/SettingsPage'

import ToolsPage from './pages/ToolsPage'
import ToolPage from './pages/ToolPage'

import './styles/app.css'

function AppContent() {
  const auth = useAuth()
  const [pageTitle, setPageTitle] = useState('Dashboard')

  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <MainLayout
        isAuthenticated={auth.isAuthenticated}
        onLogout={auth.logout}
        userName={auth.user?.name}
        userRole={auth.user?.role}
        pageTitle={pageTitle}
        onTitleChange={setPageTitle}
      >
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={auth.isAuthenticated ? <Navigate to="/dashboard" /> : <LoginPage />} />
          <Route path="/register" element={auth.isAuthenticated ? <Navigate to="/dashboard" /> : <RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/tools" element={<ToolsPage />} />
          <Route path="/:toolSlug" element={<ToolPage />} />

          {/* Protected user/subscriber routes */}
          <Route path="/dashboard" element={auth.isAuthenticated ? <UserDashboard onTitleChange={setPageTitle} /> : <Navigate to="/login" />} />
          <Route path="/billing" element={auth.isAuthenticated ? <SubscriberDashboard onTitleChange={setPageTitle} /> : <Navigate to="/login" />} />
          <Route path="/subscription" element={auth.isAuthenticated ? <SubscriberDashboard onTitleChange={setPageTitle} /> : <Navigate to="/login" />} />
          <Route path="/dashboard/profile" element={auth.isAuthenticated ? <UserProfile onTitleChange={setPageTitle} /> : <Navigate to="/login" />} />
          <Route path="/dashboard/account" element={auth.isAuthenticated ? <AccountSettings onTitleChange={setPageTitle} /> : <Navigate to="/login" />} />
          <Route path="/settings" element={auth.isAuthenticated ? <SettingsPage onTitleChange={setPageTitle} /> : <Navigate to="/login" />} />

          <Route path="*" element={<Navigate to={auth.isAuthenticated ? '/dashboard' : '/'} />} />
        </Routes>
      </MainLayout>
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
