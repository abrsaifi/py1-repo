import React, { useState, useEffect, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '@shared/hooks/useAuth'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement,
  BarElement, ArcElement, Title, Tooltip, Legend, Filler
} from 'chart.js'
import { Line, Pie, Bar } from 'react-chartjs-2'
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
import '../styles/admin-dashboard.css'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler)

const NAV_SECTIONS = [
  {
    label: 'Operations',
    items: [
      { id: 'overview',     icon: '📊', label: 'Overview' },
      { id: 'conversions',  icon: '🔄', label: 'Conversions' },
      { id: 'workers',      icon: '⚙️',  label: 'Workers' },
      { id: 'traffic',      icon: '📈', label: 'Traffic' },
      { id: 'seo',          icon: '🔍', label: 'SEO' },
      { id: 'storage',      icon: '💾', label: 'Storage' },
      { id: 'api',          icon: '🔌', label: 'API' },
    ]
  },
  {
    label: 'Management',
    items: [
      { id: 'users',      icon: '👥', label: 'Users' },
      { id: 'employees',  icon: '👔', label: 'Employees' },
      { id: 'roles',      icon: '🎭', label: 'Roles' },
      { id: 'audit',      icon: '📋', label: 'Audit Logs' },
    ]
  },
  {
    label: 'System',
    items: [
      { id: 'settings',   icon: '⚙️',  label: 'Settings' },
      { id: 'monitoring', icon: '📡', label: 'Monitoring' },
      { id: 'reports',    icon: '📑', label: 'Reports' },
      { id: 'activity',   icon: '📝', label: 'Activity' },
      { id: 'billing',    icon: '💳', label: 'Billing' },
      { id: 'security',   icon: '🔒', label: 'Security' },
      { id: 'automation', icon: '🤖', label: 'Automation' },
      { id: 'cms',        icon: '📄', label: 'CMS' },
    ]
  }
]

const OVERVIEW_STATS = [
  { label: 'Conversions Today', value: '3,204', icon: '🔄', trend: '+12%', color: '#667eea' },
  { label: 'Active Users',      value: '234',   icon: '👥', trend: '+5%',  color: '#48bb78' },
  { label: 'Success Rate',      value: '98.2%', icon: '✅', trend: '+0.3%',color: '#38b2ac' },
  { label: 'Revenue Today',     value: '$5,240',icon: '💰', trend: '+8%',  color: '#ed8936' },
  { label: 'Server Load',       value: '42%',   icon: '📡', trend: '-3%',  color: '#9f7aea' },
  { label: 'Worker Queue',      value: '27',    icon: '⚙️',  trend: '-8',   color: '#f56565' },
]

const CHART_OPTS = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: { x: { grid: { display: false } }, y: { grid: { color: 'rgba(0,0,0,0.05)' } } }
}

const PIE_OPTS = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom', labels: { padding: 12, font: { size: 11 } } } }
}

function AdminOverview() {
  const convData = {
    labels: ['00:00','02:00','04:00','06:00','08:00','10:00','12:00','14:00','16:00','18:00','20:00','22:00'],
    datasets: [{ label: 'Conversions', data: [120,145,167,142,189,203,195,187,172,156,198,211], borderColor: '#667eea', backgroundColor: 'rgba(102,126,234,0.08)', tension: 0.4, fill: true }]
  }
  const fmtData = {
    labels: ['PDF','DOCX','PNG','XLSX'],
    datasets: [{ data: [45,28,15,12], backgroundColor: ['#667eea','#764ba2','#f093fb','#4facfe'], borderWidth: 2, borderColor: '#fff' }]
  }
  const trafData = {
    labels: ['Direct','Search','Social','Referral','Email'],
    datasets: [{ label: 'Visitors', data: [285,195,142,87,56], backgroundColor: 'rgba(102,126,234,0.7)', borderColor: '#667eea', borderWidth: 1, borderRadius: 4 }]
  }
  const SERVICES = [
    { name: 'API Server', latency: '12ms' }, { name: 'Worker Pool', latency: '8ms' },
    { name: 'Database', latency: '3ms' }, { name: 'Storage', latency: '45ms' },
    { name: 'Email Service', latency: '120ms' }, { name: 'CDN', latency: '18ms' },
  ]
  return (
    <div className="ad-overview">
      <div className="ad-stats-grid">
        {OVERVIEW_STATS.map((s) => (
          <div className="ad-stat-card" key={s.label}>
            <div className="ad-stat-icon" style={{ background: s.color + '20', color: s.color }}>{s.icon}</div>
            <div className="ad-stat-body">
              <div className="ad-stat-value">{s.value}</div>
              <div className="ad-stat-label">{s.label}</div>
              <div className={`ad-stat-trend ${s.trend.startsWith('+') ? 'up' : 'down'}`}>{s.trend} vs yesterday</div>
            </div>
          </div>
        ))}
      </div>
      <div className="ad-charts-row">
        <div className="ad-chart-card wide">
          <h3>Conversions per Hour</h3>
          <div className="ad-chart-wrap"><Line data={convData} options={CHART_OPTS} /></div>
        </div>
        <div className="ad-chart-card">
          <h3>Format Distribution</h3>
          <div className="ad-chart-wrap"><Pie data={fmtData} options={PIE_OPTS} /></div>
        </div>
      </div>
      <div className="ad-charts-row">
        <div className="ad-chart-card">
          <h3>Traffic Sources</h3>
          <div className="ad-chart-wrap"><Bar data={trafData} options={CHART_OPTS} /></div>
        </div>
        <div className="ad-chart-card wide">
          <h3>System Status</h3>
          <div className="ad-status-list">
            {SERVICES.map((s) => (
              <div className="ad-status-row" key={s.name}>
                <div className="ad-status-dot"></div>
                <span className="ad-status-name">{s.name}</span>
                <span className="ad-status-latency">{s.latency}</span>
                <span className="ad-status-badge">Online</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function AdminDashboard() {
  const [searchParams, setSearchParams] = useSearchParams()
  const auth = useAuth()
  const navigate = useNavigate()
  const dropdownRef = useRef(null)

  const [tab, setTab]               = useState(searchParams.get('tab') || 'overview')
  const [collapsed, setCollapsed]   = useState(false)
  const [dropOpen, setDropOpen]     = useState(false)
  const [dark, setDark]             = useState(() => JSON.parse(localStorage.getItem('adminTheme') || 'false'))

  useEffect(() => {
    if (!auth.isAuthenticated) navigate('/login', { replace: true })
  }, [auth.isAuthenticated, navigate])

  useEffect(() => {
    setSearchParams({ tab }, { replace: true })
  }, [tab])

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light')
    localStorage.setItem('adminTheme', JSON.stringify(dark))
  }, [dark])

  useEffect(() => {
    const handler = (e) => { if (dropdownRef.current && !dropdownRef.current.contains(e.target)) setDropOpen(false) }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const tabLabel = NAV_SECTIONS.flatMap(s => s.items).find(i => i.id === tab)?.label || 'Overview'

  const renderContent = () => {
    if (tab === 'overview') return <AdminOverview />
    const map = {
      conversions: <ConversionMonitoring />, workers: <WorkerMonitoring />,
      traffic: <TrafficAnalytics />, seo: <SEOEngine />, storage: <StorageManagement />,
      api: <APIMonitoring />, users: <UserManagement />, employees: <EmployeeManagement />,
      roles: <RoleManagement />, audit: <AuditLogsViewer />, settings: <SystemSettings />,
      monitoring: <SystemMonitoring />, reports: <ReportSchedulingAdmin />,
      activity: <ActivityFeed />, billing: <UsageBilling />, security: <SecurityManagement />,
      automation: <AutomationCenter />, cms: <ContentManager />,
    }
    return map[tab] ?? <AdminOverview />
  }

  return (
    <div className={`ad-root${dark ? ' dark' : ''}`}>
      <header className="ad-header">
        <div className="ad-header-left">
          <div className="ad-logo">
            <span>⚡</span>
            {!collapsed && <span className="ad-logo-text">FastConvert</span>}
          </div>
          <div className="ad-breadcrumb">
            <span>Admin</span>
            <span className="ad-sep">/</span>
            <span className="ad-active">{tabLabel}</span>
          </div>
        </div>
        <div className="ad-header-right">
          <button className="ad-icon-btn" onClick={() => setDark(!dark)} title="Toggle theme">
            {dark ? '☀️' : '🌙'}
          </button>
          <button className="ad-icon-btn" title="Notifications">
            🔔<span className="ad-badge">3</span>
          </button>
          <div className="ad-user-wrap" ref={dropdownRef}>
            <button className="ad-avatar" onClick={() => setDropOpen(!dropOpen)}>
              {auth.user?.username?.[0]?.toUpperCase() || 'A'}
            </button>
            {dropOpen && (
              <div className="ad-dropdown">
                <div className="ad-drop-user">
                  <strong>{auth.user?.username || 'Admin'}</strong>
                  <small>{auth.user?.email || 'admin@docpro.local'}</small>
                </div>
                <hr />
                <button className="ad-drop-item" onClick={() => { setTab('settings'); setDropOpen(false) }}>⚙️ Settings</button>
                <button className="ad-drop-item" onClick={() => { setTab('security'); setDropOpen(false) }}>🔒 Security</button>
                <hr />
                <button className="ad-drop-item danger" onClick={auth.logout}>🚪 Logout</button>
              </div>
            )}
          </div>
        </div>
      </header>

      <aside className={`ad-sidebar${collapsed ? ' collapsed' : ''}`}>
        <button className="ad-toggle" onClick={() => setCollapsed(!collapsed)}>
          {collapsed ? '→' : '←'}
        </button>
        <nav className="ad-nav">
          {NAV_SECTIONS.map((sec) => (
            <div key={sec.label} className="ad-nav-sec">
              {!collapsed && <div className="ad-nav-sec-title">{sec.label}</div>}
              {sec.items.map((item) => (
                <button
                  key={item.id}
                  className={`ad-nav-btn${tab === item.id ? ' active' : ''}`}
                  onClick={() => setTab(item.id)}
                  title={collapsed ? item.label : undefined}
                >
                  <span>{item.icon}</span>
                  {!collapsed && <span>{item.label}</span>}
                </button>
              ))}
            </div>
          ))}
        </nav>
      </aside>

      <main className="ad-main">{renderContent()}</main>
    </div>
  )
}
