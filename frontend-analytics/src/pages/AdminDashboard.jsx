import React, { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { UniversalIcon } from '../utils/UniversalIcon'
import { Line, Pie, Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import UserManagement from './UserManagement'
import EmployeeManagement from './EmployeeManagement'
import RoleManagement from './RoleManagement'
import AuditLogsViewer from './AuditLogsViewer'
import SystemSettings from './SystemSettings'
import SystemMonitoring from './SystemMonitoring'
import ReportSchedulingAdmin from './ReportSchedulingAdmin'
import ActivityFeed from './ActivityFeed'
import ConversionMonitoring from './ConversionMonitoring'
import WorkerMonitoring from './WorkerMonitoring'
import TrafficAnalytics from './TrafficAnalytics'
import SEOEngine from './SEOEngine'
import StorageManagement from './StorageManagement'
import APIMonitoring from './APIMonitoring'
import UsageBilling from './UsageBilling'
import SecurityManagement from './SecurityManagement'
import AutomationCenter from './AutomationCenter'
import ContentManager from './CMSIntegration'
import DashboardPage from './DashboardPage'
import MetricsPage from './MetricsPage'
import ReportsPage from './ReportsPage'
import AlertsPage from './AlertsPage'
import QueryPage from './QueryPage'
import CustomMetricsPage from './CustomMetricsPage'
import AdvancedAnalyticsPage from './AdvancedAnalyticsPage'
import '../styles/admin.css'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const AdminDashboard = () => {
  const [searchParams] = useSearchParams()
  const auth = useAuth()
  const tabFromUrl = searchParams.get('tab')
  const [activeTab, setActiveTab] = useState(tabFromUrl || 'overview')
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [avatarDropdownOpen, setAvatarDropdownOpen] = useState(false)
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('adminTheme')
    return saved ? JSON.parse(saved) : false
  })
  const [stats, setStats] = useState({
    totalUsers: 0,
    activeUsers: 0,
    totalRoles: 0,
    auditLogsCount: 0,
    systemHealth: 'healthy'
  })

  useEffect(() => {
    // Update activeTab if URL changes
    if (tabFromUrl) {
      setActiveTab(tabFromUrl)
    }
  }, [tabFromUrl])

  useEffect(() => {
    // Load admin stats
    loadAdminStats()
  }, [])

  useEffect(() => {
    // Apply theme to document
    if (isDarkMode) {
      document.documentElement.setAttribute('data-theme', 'dark')
    } else {
      document.documentElement.setAttribute('data-theme', 'light')
    }
    localStorage.setItem('adminTheme', JSON.stringify(isDarkMode))
  }, [isDarkMode])

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode)
  }

  const loadAdminStats = () => {
    // This would be loaded from API in production
    setStats({
      totalUsers: 42,
      activeUsers: 28,
      totalRoles: 4,
      auditLogsCount: 1250,
      systemHealth: 'healthy'
    })
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return <AdminOverview stats={stats} />
      case 'conversions':
        return <ConversionMonitoring />
      case 'workers':
        return <WorkerMonitoring />
      case 'traffic':
        return <TrafficAnalytics />
      case 'seo':
        return <SEOEngine />
      case 'storage':
        return <StorageManagement />
      case 'api':
        return <APIMonitoring />
      case 'analytics-dashboard':
        return <DashboardPage onTitleChange={() => {}} />
      case 'analytics-metrics':
        return <MetricsPage onTitleChange={() => {}} />
      case 'analytics-reports':
        return <ReportsPage onTitleChange={() => {}} />
      case 'analytics-alerts':
        return <AlertsPage onTitleChange={() => {}} />
      case 'analytics-queries':
        return <QueryPage onTitleChange={() => {}} />
      case 'analytics-custom':
        return <CustomMetricsPage onTitleChange={() => {}} />
      case 'analytics-advanced':
        return <AdvancedAnalyticsPage onTitleChange={() => {}} />
      case 'users':
        return <UserManagement />
      case 'employees':
        return <EmployeeManagement />
      case 'roles':
        return <RoleManagement />
      case 'audit':
        return <AuditLogsViewer />
      case 'settings':
        return <SystemSettings />
      case 'monitoring':
        return <SystemMonitoring />
      case 'reports':
        return <ReportSchedulingAdmin />
      case 'activity':
        return <ActivityFeed />
      case 'billing':
        return <UsageBilling />
      case 'security':
        return <SecurityManagement />
      case 'automation':
        return <AutomationCenter />
      case 'cms':
        return <ContentManager />
      default:
        return <AdminOverview stats={stats} />
    }
  }

  // Icon components for menu items - using iconName property for UniversalIcon
  const adminMenuItems = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'conversions', label: 'Conversions', icon: '📦' },
    { id: 'workers', label: 'Workers', icon: '⚙️' },
    { id: 'traffic', label: 'Traffic', icon: '📈' },
    { id: 'seo', label: 'SEO', icon: '🔍' },
    { id: 'storage', label: 'Storage', icon: '💾' },
    { id: 'api', label: 'API', icon: '🔌' },
    { id: 'users', label: 'Users', icon: '👥' },
    { id: 'employees', label: 'Employees', icon: '👔' },
    { id: 'roles', label: 'Roles', icon: '🎭' },
    { id: 'audit', label: 'Audit Logs', icon: '📋' },
    { id: 'settings', label: 'Settings', icon: '⚙️' },
    { id: 'monitoring', label: 'Monitoring', icon: '📡' },
    { id: 'reports', label: 'Reports', icon: '📑' },
    { id: 'activity', label: 'Activity', icon: '📝' },
    { id: 'billing', label: 'Billing', icon: '💳' },
    { id: 'security', label: 'Security', icon: '🔒' },
    { id: 'automation', label: 'Automation', icon: '🤖' },
    { id: 'cms', label: 'CMS', icon: '📄' }
  ]

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <div className="header-left">
          <div className="header-logo">
            <UniversalIcon icon="⚡" size={24} />
            <span className="logo-text">FastConvert</span>
          </div>
        </div>

        <div className="header-right">
          <div className="avatar-container">
            <button 
              className="avatar-button"
              onClick={() => setAvatarDropdownOpen(!avatarDropdownOpen)}
              title="Admin Settings"
            >
              <UniversalIcon icon="👤" size={24} />
            </button>

            {avatarDropdownOpen && (
              <div className="avatar-dropdown">
                <div className="dropdown-header">Admin User</div>
                <div className="dropdown-divider"></div>
                <button className="dropdown-item"><UniversalIcon icon="⚙️" size={16} /> Admin Settings</button>
                <button className="dropdown-item"><UniversalIcon icon="👤" size={16} /> Profile</button>
                <button className="dropdown-item"><UniversalIcon icon="🔔" size={16} /> Notifications</button>
                <button className="dropdown-item"><UniversalIcon icon="🔐" size={16} /> Security</button>
                <button className="dropdown-item" onClick={toggleTheme}><UniversalIcon icon="🌓" size={16} /> Toggle Dark/Light</button>
                <div className="dropdown-divider"></div>
                <button className="dropdown-item logout" onClick={auth.logout}><UniversalIcon icon="🔒" size={16} /> Logout</button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Left Sidebar Navigation - Outside container for fixed positioning */}
      <aside className={`admin-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <button 
          className="sidebar-toggle"
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          title={sidebarCollapsed ? 'Expand' : 'Collapse'}
        >
          {sidebarCollapsed ? <UniversalIcon icon="→" size={18} /> : <UniversalIcon icon="←" size={18} />}
        </button>
        
        <nav className="admin-nav">
          <div className="admin-nav-section">
            <h3 className="admin-nav-title">Operations</h3>
            <ul className="admin-nav-items">
              {adminMenuItems.slice(0, 7).map(item => (
                <li key={item.id}>
                  <button
                    className={`admin-nav-link ${activeTab === item.id ? 'active' : ''}`}
                    onClick={() => setActiveTab(item.id)}
                    title={item.label}
                  >
                    <UniversalIcon icon={item.icon} size={18} />
                    {!sidebarCollapsed && <span className="nav-label">{item.label}</span>}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <div className="admin-nav-section">
            <h3 className="admin-nav-title">Management</h3>
            <ul className="admin-nav-items">
              {adminMenuItems.slice(7, 11).map(item => (
                <li key={item.id}>
                  <button
                    className={`admin-nav-link ${activeTab === item.id ? 'active' : ''}`}
                    onClick={() => setActiveTab(item.id)}
                    title={item.label}
                  >
                    <UniversalIcon icon={item.icon} size={18} />
                    {!sidebarCollapsed && <span className="nav-label">{item.label}</span>}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <div className="admin-nav-section">
            <h3 className="admin-nav-title">System</h3>
            <ul className="admin-nav-items">
              {adminMenuItems.slice(11).map(item => (
                <li key={item.id}>
                  <button
                    className={`admin-nav-link ${activeTab === item.id ? 'active' : ''}`}
                    onClick={() => setActiveTab(item.id)}
                    title={item.label}
                  >
                    <UniversalIcon icon={item.icon} size={18} />
                    {!sidebarCollapsed && <span className="nav-label">{item.label}</span>}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </nav>
      </aside>

      <div className="admin-container">
        <main className="admin-content">
          {renderContent()}
        </main>
      </div>
    </div>
  )
}

const AdminOverview = ({ stats }) => {
  const [dashboardData, setDashboardData] = useState({
    conversionsToday: 3204,
    successRate: 98.2,
    failedConversions: 58,
    activeUsers: 234,
    serverLoad: 42,
    workerQueue: 27,
    revenue: 5240,
    hourlyConversions: [120, 145, 167, 142, 189, 203, 195, 187, 172, 156, 198, 211],
    topFormats: [
      { name: 'PDF', value: 45 },
      { name: 'DOCX', value: 28 },
      { name: 'PNG', value: 15 },
      { name: 'XLSX', value: 12 }
    ],
    trafficSources: [285, 195, 142, 87, 56],
    errorTrends: [5, 8, 3, 6, 4, 7, 5, 8, 6, 4, 7, 6]
  })

  // Conversions per hour - Line Chart
  const conversionsChartData = {
    labels: ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'],
    datasets: [
      {
        label: 'Conversions per Hour',
        data: dashboardData.hourlyConversions,
        borderColor: '#667eea',
        backgroundColor: 'rgba(102, 126, 234, 0.1)',
        tension: 0.4,
        fill: true,
        pointRadius: 4,
        pointBackgroundColor: '#667eea'
      }
    ]
  }

  // Top Format Types - Pie Chart
  const formatsChartData = {
    labels: dashboardData.topFormats.map(f => f.name),
    datasets: [
      {
        data: dashboardData.topFormats.map(f => f.value),
        backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#4facfe'],
        borderColor: '#fff',
        borderWidth: 2
      }
    ]
  }

  // Traffic Sources - Bar Chart
  const trafficChartData = {
    labels: ['Direct', 'Search', 'Social', 'Referral', 'Email'],
    datasets: [
      {
        label: 'Traffic',
        data: dashboardData.trafficSources,
        backgroundColor: '#667eea',
        borderColor: '#764ba2',
        borderWidth: 1
      }
    ]
  }

  // Error Trends - Line Chart
  const errorChartData = {
    labels: ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'],
    datasets: [
      {
        label: 'Failed Conversions',
        data: dashboardData.errorTrends,
        borderColor: '#ff6b6b',
        backgroundColor: 'rgba(255, 107, 107, 0.1)',
        tension: 0.4,
        fill: true,
        pointRadius: 3,
        pointBackgroundColor: '#ff6b6b'
      }
    ]
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: true,
        position: 'top'
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }

  return (
    <div className="admin-overview">
      <h1 className="admin-overview-title">Admin Dashboard</h1>
      {/* Key Metrics Cards */}
      <div className="admin-stats-grid">
        <div className="admin-stat-card metric-primary">
          <UniversalIcon icon="📦" size={32} />
          <div className="stat-content">
            <h3>Conversions Today</h3>
            <p className="stat-value">{dashboardData.conversionsToday.toLocaleString()}</p>
            <p className="stat-detail">Total completed</p>
          </div>
        </div>

        <div className="admin-stat-card metric-success">
          <UniversalIcon icon="✅" size={32} />
          <div className="stat-content">
            <h3>Success Rate</h3>
            <p className="stat-value">{dashboardData.successRate}%</p>
            <p className="stat-detail">High quality</p>
          </div>
        </div>

        <div className="admin-stat-card metric-danger">
          <UniversalIcon icon="❌" size={32} />
          <div className="stat-content">
            <h3>Failed</h3>
            <p className="stat-value">{dashboardData.failedConversions}</p>
            <p className="stat-detail">Needs review</p>
          </div>
        </div>

        <div className="admin-stat-card metric-info">
          <UniversalIcon icon="👥" size={32} />
          <div className="stat-content">
            <h3>Active Users</h3>
            <p className="stat-value">{dashboardData.activeUsers}</p>
            <p className="stat-detail">Right now</p>
          </div>
        </div>

        <div className="admin-stat-card metric-warning">
          <UniversalIcon icon="⚙️" size={32} />
          <div className="stat-content">
            <h3>Server Load</h3>
            <p className="stat-value">{dashboardData.serverLoad}%</p>
            <p className="stat-detail">Normal</p>
          </div>
        </div>

        <div className="admin-stat-card metric-queue">
          <UniversalIcon icon="📋" size={32} />
          <div className="stat-content">
            <h3>Worker Queue</h3>
            <p className="stat-value">{dashboardData.workerQueue}</p>
            <p className="stat-detail">Jobs waiting</p>
          </div>
        </div>

        <div className="admin-stat-card metric-revenue">
          <UniversalIcon icon="💰" size={32} />
          <div className="stat-content">
            <h3>Revenue Today</h3>
            <p className="stat-value">${dashboardData.revenue.toLocaleString()}</p>
            <p className="stat-detail">Running total</p>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-section">
        <div className="chart-container">
          <h3>Conversions per Hour</h3>
          <div className="chart-wrapper">
            <Line data={conversionsChartData} options={chartOptions} />
          </div>
        </div>

        <div className="chart-container">
          <h3>Top Format Types</h3>
          <div className="chart-wrapper pie-chart">
            <Pie data={formatsChartData} />
          </div>
        </div>

        <div className="chart-container">
          <h3>Traffic Sources</h3>
          <div className="chart-wrapper">
            <Bar data={trafficChartData} options={chartOptions} />
          </div>
        </div>

        <div className="chart-container">
          <h3>Error Trends</h3>
          <div className="chart-wrapper">
            <Line data={errorChartData} options={chartOptions} />
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="admin-welcome">
        <h2>Founder Command Center</h2>
        <p>
          Monitor conversion metrics, system performance, and user activity in real-time.
          Access detailed analytics, manage operations, and optimize your conversion pipeline.
        </p>
        <div className="quick-actions">
          <button className="action-button primary"><UniversalIcon icon="📊" size={16} /> View Detailed Metrics</button>
          <button className="action-button secondary"><UniversalIcon icon="⚙️" size={16} /> Manage Workers</button>
          <button className="action-button secondary"><UniversalIcon icon="👥" size={16} /> User Management</button>
        </div>
      </div>
    </div>
  )
}

export default AdminDashboard
