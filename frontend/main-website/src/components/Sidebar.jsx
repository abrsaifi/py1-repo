import { useState } from 'react'
import { Link } from 'react-router-dom'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import '../styles/sidebar.css'

export const Sidebar = ({ onLogout, userName, userRole }) => {
  const [collapsed, setCollapsed] = useState(false)
  const [expandedMenu, setExpandedMenu] = useState(null)
  const [userMenuOpen, setUserMenuOpen] = useState(false)

  // Admin menu items
  const adminMenuItems = [
    {
      label: 'Dashboard',
      icon: 'fas fa-chart-bar',
      submenu: [
        { path: '/admin?tab=overview', label: 'Overview', icon: 'fas fa-chart-bar' },
        { path: '/admin?tab=activity', label: 'Activity Feed', icon: 'fas fa-stream' },
      ]
    },
    {
      label: 'Conversions',
      icon: 'fas fa-cube',
      submenu: [
        { path: '/admin?tab=conversions', label: 'Conversion Jobs', icon: 'fas fa-cube' },
        { path: '/admin?tab=traffic', label: 'Traffic Analytics', icon: 'fas fa-chart-line' },
      ]
    },
    {
      label: 'Users',
      icon: 'fas fa-users',
      submenu: [
        { path: '/admin?tab=users', label: 'Subscribers', icon: 'fas fa-user-circle' },
      ]
    },
    {
      label: 'Admin & Staff',
      icon: 'fas fa-user-tie',
      submenu: [
        { path: '/admin?tab=employees', label: 'Team Members', icon: 'fas fa-users' },
        { path: '/admin?tab=roles', label: 'Roles & Permissions', icon: 'fas fa-lock' },
        { path: '/admin?tab=audit', label: 'Audit Logs', icon: 'fas fa-clipboard-list' },
      ]
    },
    {
      label: 'Usage & Billing',
      icon: 'fas fa-credit-card',
      submenu: [
        { path: '/admin?tab=billing', label: 'Billing Overview', icon: 'fas fa-credit-card' },
        { path: '/admin?tab=api', label: 'API Usage', icon: 'fas fa-plug' },
      ]
    },
    {
      label: 'SEO Engine',
      icon: 'fas fa-search',
      submenu: [
        { path: '/admin?tab=seo', label: 'SEO Dashboard', icon: 'fas fa-search' },
      ]
    },
    {
      label: 'System Health',
      icon: 'fas fa-heartbeat',
      submenu: [
        { path: '/admin?tab=monitoring', label: 'Monitoring', icon: 'fas fa-heartbeat' },
        { path: '/admin?tab=reports', label: 'Report Scheduling', icon: 'fas fa-calendar' },
      ]
    },
    {
      label: 'Analytics',
      icon: 'fas fa-chart-pie',
      submenu: [
        { path: '/admin?tab=analytics-dashboard', label: 'Dashboard', icon: 'fas fa-th' },
        { path: '/admin?tab=analytics-metrics', label: 'Metrics', icon: 'fas fa-tachometer-alt' },
        { path: '/admin?tab=analytics-reports', label: 'Reports', icon: 'fas fa-file-alt' },
        { path: '/admin?tab=analytics-alerts', label: 'Alerts', icon: 'fas fa-bell' },
        { path: '/admin?tab=analytics-queries', label: 'Queries', icon: 'fas fa-search-plus' },
        { path: '/admin?tab=analytics-custom', label: 'Custom Metrics', icon: 'fas fa-sliders-h' },
        { path: '/admin?tab=analytics-advanced', label: 'Advanced', icon: 'fas fa-brain' },
      ]
    },
    {
      label: 'Workers',
      icon: 'fas fa-microchip',
      submenu: [
        { path: '/admin?tab=workers', label: 'Worker Status', icon: 'fas fa-microchip' },
      ]
    },
    {
      label: 'Files & Storage',
      icon: 'fas fa-database',
      submenu: [
        { path: '/admin?tab=storage', label: 'Storage Management', icon: 'fas fa-database' },
      ]
    },
    {
      label: 'Security',
      icon: 'fas fa-shield-alt',
      submenu: [
        { path: '/admin?tab=security', label: 'Security Center', icon: 'fas fa-shield-alt' },
      ]
    },
    {
      label: 'Automation',
      icon: 'fas fa-cogs',
      submenu: [
        { path: '/admin?tab=automation', label: 'Workflows', icon: 'fas fa-cogs' },
      ]
    },
    {
      label: 'CMS',
      icon: 'fas fa-file-alt',
      submenu: [
        { path: '/admin?tab=cms', label: 'Content Management', icon: 'fas fa-file-alt' },
      ]
    },
    {
      label: 'Settings',
      icon: 'fas fa-sliders-h',
      submenu: [
        { path: '/admin?tab=settings', label: 'System Settings', icon: 'fas fa-sliders-h' },
      ]
    },
  ]

  // Regular user menu items
  const userMenuItems = [
    {
      label: 'Dashboard',
      icon: 'fas fa-home',
      path: '/dashboard'
    },
    {
      label: 'My Conversions',
      icon: 'fas fa-exchange-alt',
      path: '/dashboard/history'
    },
    {
      label: 'Profile',
      icon: 'fas fa-user',
      path: '/dashboard/profile'
    },
    {
      label: 'Settings',
      icon: 'fas fa-cog',
      path: '/settings'
    },
  ]

  // Choose menu based on role
  const menuItems = userRole === 'admin' ? adminMenuItems : userMenuItems

  const toggleSubmenu = (index) => {
    setExpandedMenu(expandedMenu === index ? null : index)
  }

  return (
    <div className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <h2 className="sidebar-title">
          <UniversalIcon icon="fas fa-chart-pie" size={20} color="var(--primary-color)" />
          {!collapsed && <span>{userRole === 'admin' ? 'Admin Panel' : 'FastConvert'}</span>}
        </h2>
        <button
          className="collapse-btn"
          onClick={() => setCollapsed(!collapsed)}
          title={collapsed ? 'Expand' : 'Collapse'}
        >
          <UniversalIcon 
            icon={collapsed ? 'fas fa-chevron-right' : 'fas fa-chevron-left'} 
            size={20}
            color="white"
          />
        </button>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item, index) => (
          <div key={`menu-${index}-${item.label}`}>
            {item.submenu ? (
              <>
                <button
                  className={`nav-item nav-parent ${expandedMenu === index ? 'active' : ''}`}
                  onClick={() => toggleSubmenu(index)}
                  title={collapsed ? item.label : ''}
                >
                  <UniversalIcon icon={item.icon} size={20} color="#000000" />
                  {!collapsed && <span>{item.label}</span>}
                  {!collapsed && <UniversalIcon icon="fas fa-chevron-down" size={16} color="#000000" className={`chevron ${expandedMenu === index ? 'open' : ''}`} />}
                </button>
                {expandedMenu === index && !collapsed && (
                  <div className="submenu">
                    {item.submenu.map((subitem) => (
                      <Link
                        key={subitem.path}
                        to={subitem.path}
                        className="submenu-item"
                      >
                        <UniversalIcon icon={subitem.icon} size={18} color="#000000" />
                        <span>{subitem.label}</span>
                      </Link>
                    ))}
                  </div>
                )}
              </>
            ) : (
              <Link
                to={item.path}
                className="nav-item"
                title={collapsed ? item.label : ''}
              >
                <UniversalIcon icon={item.icon} size={20} color="#000000" />
                {!collapsed && <span>{item.label}</span>}
              </Link>
            )}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <button
          className="user-info-btn"
          onClick={() => setUserMenuOpen(!userMenuOpen)}
          title={collapsed ? userName || 'User' : ''}
        >
          <div className="user-avatar">
            <UniversalIcon icon="fas fa-user" size={18} color="#3b82f6" />
          </div>
          {!collapsed && (
            <div className="user-details">
              <p className="user-name">{userName || 'User'}</p>
              <p className="user-role">{userRole === 'admin' ? 'Administrator' : 'Subscriber'}</p>
            </div>
          )}
          {!collapsed && (
            <UniversalIcon icon="fas fa-chevron-up" size={16} color="#3b82f6" className={`chevron ${userMenuOpen ? 'open' : ''}`} />
          )}
        </button>

        {userMenuOpen && !collapsed && (
          <div className="user-menu-dropdown">
            <Link
              to="/dashboard/profile"
              className="user-menu-item"
              onClick={() => setUserMenuOpen(false)}
            >
              <UniversalIcon icon="fas fa-user-circle" size={18} color="#3b82f6" />
              <span>Profile Settings</span>
            </Link>
            <Link
              to="/dashboard/account"
              className="user-menu-item"
              onClick={() => setUserMenuOpen(false)}
            >
              <UniversalIcon icon="fas fa-cog" size={18} color="#3b82f6" />
              <span>Account Settings</span>
            </Link>
            <Link
              to="/dashboard/billing"
              className="user-menu-item"
              onClick={() => setUserMenuOpen(false)}
            >
              <UniversalIcon icon="fas fa-credit-card" size={18} color="#3b82f6" />
              <span>Billing & Plans</span>
            </Link>
            <div className="user-menu-divider"></div>
            <button
              className="user-menu-item logout"
              onClick={() => {
                setUserMenuOpen(false)
                onLogout()
              }}
            >
              <UniversalIcon icon="fas fa-sign-out-alt" size={18} color="#ef4444" />
              <span>Logout</span>
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default Sidebar
