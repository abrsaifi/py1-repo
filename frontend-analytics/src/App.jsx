import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import MainLayout from './components/MainLayout'
import ToastProvider from './components/Toast'
import { NotificationProvider } from './components/Notification'
import DarkModeProvider from './hooks/useDarkMode.jsx'
import useAuth from './hooks/useAuth'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import DashboardPage from './pages/DashboardPage'
import MetricsPage from './pages/MetricsPage'
import ReportsPage from './pages/ReportsPage'
import ToolsPage from './pages/ToolsPage'
import ToolPage from './pages/ToolPage'
import AlertsPage from './pages/AlertsPage'
import QueryPage from './pages/QueryPage'
import CustomMetricsPage from './pages/CustomMetricsPage'
import SettingsPage from './pages/SettingsPage'
import AdminDashboard from './pages/AdminDashboard'
import AdvancedAnalyticsPage from './pages/AdvancedAnalyticsPage'
import UserDashboard from './pages/UserDashboard'
import UserProfile from './pages/UserProfile'
import AccountSettings from './pages/AccountSettings'
import './styles/app.css'

function AppContent() {
  const auth = useAuth()
  const [pageTitle, setPageTitle] = useState('Dashboard')

  const handleLogout = () => {
    auth.logout()
  }

  // If admin is authenticated, show admin dashboard without MainLayout
  if (auth.isAuthenticated && auth.user?.role === 'admin') {
    return (
      <Router>
        <Routes>
          <Route path="/admin" element={<AdminDashboard onTitleChange={setPageTitle} />} />
          <Route path="*" element={<Navigate to="/admin" />} />
        </Routes>
      </Router>
    )
  }

  // For all other users (not authenticated or subscriber), use MainLayout
  return (
    <Router>
      <MainLayout
        isAuthenticated={auth.isAuthenticated}
        onLogout={handleLogout}
        userName={auth.user?.name}
        userRole={auth.user?.role}
        pageTitle={pageTitle}
        onTitleChange={setPageTitle}
      >
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={auth.isAuthenticated ? <Navigate to={auth.user?.role === 'admin' ? '/admin' : '/dashboard'} /> : <LandingPage />} />
          <Route path="/login" element={auth.isAuthenticated ? <Navigate to="/dashboard" /> : <LoginPage />} />
          <Route path="/register" element={auth.isAuthenticated ? <Navigate to="/dashboard" /> : <RegisterPage />} />
          <Route path="/forgot-password" element={auth.isAuthenticated ? <Navigate to="/dashboard" /> : <ForgotPasswordPage />} />
          <Route path="/convert" element={auth.isAuthenticated ? <Navigate to="/dashboard" /> : <LandingPage />} />
          <Route path="/tools" element={<ToolsPage />} />
          <Route path="/tools/:toolSlug" element={<ToolPage />} />
          
          {/* Protected Routes */}
          <Route path="/dashboard" element={auth.isAuthenticated ? <UserDashboard onTitleChange={setPageTitle} /> : <Navigate to="/login" />} />
          <Route path="/dashboard/profile" element={auth.isAuthenticated ? <UserProfile onTitleChange={setPageTitle} /> : <Navigate to="/login" />} />
          <Route path="/dashboard/account" element={auth.isAuthenticated ? <AccountSettings onTitleChange={setPageTitle} /> : <Navigate to="/login" />} />
          <Route path="/metrics" element={auth.isAuthenticated ? <MetricsPage onTitleChange={setPageTitle} /> : <Navigate to="/login" />} />
          <Route path="/reports" element={auth.isAuthenticated ? <ReportsPage onTitleChange={setPageTitle} /> : <Navigate to="/login" />} />
          <Route path="/dashboards" element={auth.isAuthenticated ? <DashboardPage onTitleChange={setPageTitle} /> : <Navigate to="/login" />} />
          <Route path="/alerts" element={auth.isAuthenticated ? <AlertsPage onTitleChange={setPageTitle} /> : <Navigate to="/login" />} />
          <Route path="/queries" element={auth.isAuthenticated ? <QueryPage onTitleChange={setPageTitle} /> : <Navigate to="/login" />} />
          <Route path="/custom-metrics" element={auth.isAuthenticated ? <CustomMetricsPage onTitleChange={setPageTitle} /> : <Navigate to="/login" />} />
          <Route path="/settings" element={auth.isAuthenticated ? <SettingsPage onTitleChange={setPageTitle} /> : <Navigate to="/login" />} />
          <Route path="/advanced-analytics" element={auth.isAuthenticated ? <AdvancedAnalyticsPage onTitleChange={setPageTitle} /> : <Navigate to="/login" />} />
          
          {/* Catch all - redirect to appropriate page */}
          <Route path="*" element={<Navigate to={auth.isAuthenticated ? '/dashboard' : '/'} />} />
        </Routes>
      </MainLayout>
    </Router>
  )
}

function App() {
  return (
    <DarkModeProvider>
      <ToastProvider>
        <NotificationProvider>
          <AppContent />
        </NotificationProvider>
      </ToastProvider>
    </DarkModeProvider>
  )
}

export default App

