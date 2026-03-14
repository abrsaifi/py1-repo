import { Suspense, lazy, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import MainLayout from './components/MainLayout'
import ToastProvider from './components/Toast'
import { NotificationProvider } from './components/Notification'
import DarkModeProvider from './hooks/useDarkMode.jsx'
import useAuth from './hooks/useAuth'
import './styles/app.css'

const LandingPage = lazy(() => import('./pages/LandingPage'))
const LoginPage = lazy(() => import('./pages/LoginPage'))
const AdminLoginPage = lazy(() => import('./pages/AdminLoginPage'))
const RegisterPage = lazy(() => import('./pages/RegisterPage'))
const ForgotPasswordPage = lazy(() => import('./pages/ForgotPasswordPage'))
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const MetricsPage = lazy(() => import('./pages/MetricsPage'))
const ReportsPage = lazy(() => import('./pages/ReportsPage'))
const ToolsPage = lazy(() => import('./pages/ToolsPage'))
const ToolPage = lazy(() => import('./pages/ToolPage'))
const EditorPage = lazy(() => import('./pages/EditorPage'))
const AlertsPage = lazy(() => import('./pages/AlertsPage'))
const QueryPage = lazy(() => import('./pages/QueryPage'))
const CustomMetricsPage = lazy(() => import('./pages/CustomMetricsPage'))
const SettingsPage = lazy(() => import('./pages/SettingsPage'))
const AdminDashboard = lazy(() => import('./pages/AdminDashboard'))
const AdvancedAnalyticsPage = lazy(() => import('./pages/AdvancedAnalyticsPage'))
const UserDashboard = lazy(() => import('./pages/UserDashboard'))
const SubscriberDashboard = lazy(() => import('./pages/SubscriberDashboard'))
const UserProfile = lazy(() => import('./pages/UserProfile'))
const AccountSettings = lazy(() => import('./pages/AccountSettings'))

function RouteFallback() {
  return (
    <div style={{ minHeight: '40vh', display: 'grid', placeItems: 'center' }}>
      <p>Loading...</p>
    </div>
  )
}

function AppContent() {
  const auth = useAuth()
  const [pageTitle, setPageTitle] = useState('Dashboard')

  const handleLogout = () => {
    auth.logout()
  }

  // DEV MODE: On dev server (localhost:5173), show admin dashboard only if authenticated as admin
  const isDevServer = ['localhost', '127.0.0.1'].includes(window.location.hostname) && window.location.port === '5173'
  
  if (isDevServer && auth.isAuthenticated && auth.user?.role === 'admin') {
    return (
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Suspense fallback={<RouteFallback />}>
          <Routes>
            <Route path="/" element={<AdminDashboard onTitleChange={setPageTitle} />} />
            <Route path="/admin" element={<AdminDashboard onTitleChange={setPageTitle} />} />
            <Route path="*" element={<Navigate to="/admin" />} />
          </Routes>
        </Suspense>
      </Router>
    )
  }

  // If admin is authenticated, show admin dashboard without MainLayout
  if (auth.isAuthenticated && auth.user?.role === 'admin') {
    return (
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Suspense fallback={<RouteFallback />}>
          <Routes>
            <Route path="/admin" element={<AdminDashboard onTitleChange={setPageTitle} />} />
            <Route path="*" element={<Navigate to="/admin" />} />
          </Routes>
        </Suspense>
      </Router>
    )
  }

  // For all other users (not authenticated or subscriber), use MainLayout
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <MainLayout
        isAuthenticated={auth.isAuthenticated}
        onLogout={handleLogout}
        userName={auth.user?.name}
        userRole={auth.user?.role}
        pageTitle={pageTitle}
        onTitleChange={setPageTitle}
      >
        <Suspense fallback={<RouteFallback />}>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={auth.isAuthenticated ? <Navigate to="/dashboard" /> : <LoginPage />} />
            <Route path="/admin-login" element={auth.isAuthenticated && auth.user?.role === 'admin' ? <Navigate to="/admin" /> : <AdminLoginPage />} />
            <Route path="/register" element={auth.isAuthenticated ? <Navigate to="/dashboard" /> : <RegisterPage />} />
            <Route path="/forgot-password" element={auth.isAuthenticated ? <Navigate to="/dashboard" /> : <ForgotPasswordPage />} />
            <Route path="/convert" element={auth.isAuthenticated ? <Navigate to="/dashboard" /> : <LandingPage />} />
            <Route path="/tools" element={<ToolsPage />} />
            <Route path="/editor" element={<EditorPage />} />
            <Route path="/:toolSlug" element={<ToolPage />} />

            {/* Protected Routes */}
            <Route path="/dashboard" element={auth.isAuthenticated ? <UserDashboard onTitleChange={setPageTitle} /> : <Navigate to="/login" />} />
            <Route path="/billing" element={auth.isAuthenticated ? <SubscriberDashboard onTitleChange={setPageTitle} /> : <Navigate to="/login" />} />
            <Route path="/subscription" element={auth.isAuthenticated ? <SubscriberDashboard onTitleChange={setPageTitle} /> : <Navigate to="/login" />} />
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
        </Suspense>
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

