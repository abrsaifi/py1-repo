import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import '../styles/subscriber-dashboard.css'

const PLANS = [
  {
    id: 'free', name: 'Free', price: 0, period: 'forever',
    description: 'Perfect for getting started',
    features: ['10 conversions/day', '2 GB storage', 'Basic analytics', 'Email support'],
    cta: 'Downgrade'
  },
  {
    id: 'pro', name: 'Pro', price: 9.99, period: 'month',
    description: 'For regular users', popular: true,
    features: ['Unlimited conversions', '100 GB storage', 'Advanced analytics', 'Priority support', 'API access', 'Custom branding'],
    cta: 'Current Plan'
  },
  {
    id: 'enterprise', name: 'Enterprise', price: null, period: 'month',
    description: 'For teams & enterprises',
    features: ['Everything in Pro', '1 TB+ storage', 'Dedicated account manager', 'Phone support', 'Custom integrations', 'SLA guarantee'],
    cta: 'Contact Sales'
  }
]

const BILLING_HISTORY = [
  { id: 1, date: '2026-03-15', description: 'Pro Plan Subscription', amount: '$9.99', status: 'paid',    invoice: 'INV-2026-003' },
  { id: 2, date: '2026-02-15', description: 'Pro Plan Subscription', amount: '$9.99', status: 'paid',    invoice: 'INV-2026-002' },
  { id: 3, date: '2026-01-15', description: 'Pro Plan Subscription', amount: '$9.99', status: 'paid',    invoice: 'INV-2026-001' },
  { id: 4, date: '2025-12-15', description: 'Pro Plan Subscription', amount: '$9.99', status: 'paid',    invoice: 'INV-2025-012' },
  { id: 5, date: '2025-11-15', description: 'Pro Plan Subscription', amount: '$9.99', status: 'refunded',invoice: 'INV-2025-011' },
]

export default function SubscriberDashboard() {
  const navigate = useNavigate()
  const auth = useAuth()
  const profileRef = useRef(null)

  const [tab, setTab]             = useState('subscription')
  const [profileOpen, setProfile] = useState(false)
  const [upgradeModal, setUpgrade]= useState(false)

  useEffect(() => {
    if (!auth.isAuthenticated) navigate('/login', { replace: true })
  }, [auth.isAuthenticated, navigate])

  useEffect(() => {
    const h = (e) => { if (profileRef.current && !profileRef.current.contains(e.target)) setProfile(false) }
    document.addEventListener('mousedown', h)
    return () => document.removeEventListener('mousedown', h)
  }, [])

  const sub = {
    plan: 'Pro', status: 'active', amount: 9.99, cycle: 'monthly',
    startDate: '2026-01-15', nextBilling: '2026-04-15', autoRenew: true,
    features: ['Unlimited conversions', '100 GB storage', 'Priority support', 'Advanced analytics', 'API access', 'Custom branding']
  }

  const usage = [
    { label: 'Conversions', used: 250, total: 'unlimited', pct: 50 },
    { label: 'Storage',     used: '2.3 GB', total: '100 GB', pct: 23 },
    { label: 'API Calls',   used: '4,500', total: '100,000', pct: 5 },
  ]

  const initials = auth.user?.username?.[0]?.toUpperCase() || 'U'

  return (
    <div className="sb-root">
      {/* ── Header ── */}
      <header className="sb-header">
        <div className="sb-header-left">
          <div className="sb-logo">⚡ <span>FastConvert</span></div>
          <h1 className="sb-title">Subscription & Billing</h1>
        </div>
        <div className="sb-header-right" ref={profileRef}>
          <button className="sb-avatar" onClick={() => setProfile(!profileOpen)}>{initials}</button>
          {profileOpen && (
            <div className="sb-profile-drop">
              <div className="sb-drop-user">
                <div className="sb-drop-avatar">{initials}</div>
                <div>
                  <strong>{auth.user?.username}</strong>
                  <small>{auth.user?.email}</small>
                </div>
              </div>
              <hr />
              <button className="sb-drop-item" onClick={() => { navigate('/dashboard'); setProfile(false) }}>📊 Dashboard</button>
              <button className="sb-drop-item" onClick={() => { navigate('/settings'); setProfile(false) }}>⚙️ Settings</button>
              <hr />
              <button className="sb-drop-item danger" onClick={auth.logout}>🚪 Logout</button>
            </div>
          )}
        </div>
      </header>

      {/* ── Tabs ── */}
      <nav className="sb-tabs">
        {[
          { id: 'subscription', label: 'My Subscription', icon: '📋' },
          { id: 'billing',      label: 'Billing History',  icon: '💳' },
          { id: 'plans',        label: 'All Plans',         icon: '📦' },
          { id: 'payment',      label: 'Payment Method',    icon: '💰' },
        ].map((t) => (
          <button key={t.id} className={`sb-tab${tab === t.id ? ' active' : ''}`} onClick={() => setTab(t.id)}>
            {t.icon} {t.label}
          </button>
        ))}
      </nav>

      {/* ── Body ── */}
      <div className="sb-body">
        {/* Sidebar */}
        <aside className="sb-sidebar">
          <div className="sb-card">
            <div className="sb-card-title">Current Plan</div>
            <div className="sb-plan-name">{sub.plan}</div>
            <div className="sb-plan-price">${sub.amount}<span>/{sub.cycle}</span></div>
            <div className="sb-status active">{sub.status}</div>
            <div className="sb-dates">
              <div className="sb-date-row"><span>Started</span><span>{sub.startDate}</span></div>
              <div className="sb-date-row"><span>Next Billing</span><span>{sub.nextBilling}</span></div>
              <div className="sb-date-row"><span>Auto-Renew</span><span>{sub.autoRenew ? 'On' : 'Off'}</span></div>
            </div>
            <button className="sb-btn-primary" onClick={() => setUpgrade(true)}>⭐ Upgrade Plan</button>
            <button className="sb-btn-ghost" onClick={() => { if (window.confirm('Cancel subscription?')) alert('Contact support to cancel.') }}>Cancel Subscription</button>
          </div>

          <div className="sb-card">
            <div className="sb-card-title">Usage This Month</div>
            {usage.map((u) => (
              <div className="sb-usage-item" key={u.label}>
                <div className="sb-usage-top">
                  <span>{u.label}</span>
                  <span className="sb-usage-vals">{u.used} / {u.total}</span>
                </div>
                <div className="sb-usage-bar">
                  <div className="sb-usage-fill" style={{ width: u.pct + '%' }}></div>
                </div>
              </div>
            ))}
          </div>

          <div className="sb-card">
            <div className="sb-card-title">Help & Support</div>
            <a className="sb-help-link" href="#faq">📖 Billing FAQ</a>
            <a className="sb-help-link" href="#support">💬 Contact Support</a>
            <a className="sb-help-link" href="#docs">📚 Documentation</a>
          </div>
        </aside>

        {/* Main content */}
        <main className="sb-main">
          {/* ── Subscription tab ── */}
          {tab === 'subscription' && (
            <div className="sb-section">
              <h2>Subscription Details</h2>
              <div className="sb-info-card">
                <h3>Plan Information</h3>
                <div className="sb-info-grid">
                  <div className="sb-info-row"><span>Plan</span><strong>{sub.plan}</strong></div>
                  <div className="sb-info-row"><span>Status</span><span className="sb-status active">{sub.status}</span></div>
                  <div className="sb-info-row"><span>Billing Cycle</span><strong>{sub.cycle}</strong></div>
                  <div className="sb-info-row"><span>Amount</span><strong>${sub.amount}/mo</strong></div>
                  <div className="sb-info-row"><span>Auto-Renewal</span><strong>{sub.autoRenew ? 'Enabled' : 'Disabled'}</strong></div>
                  <div className="sb-info-row"><span>Next Billing</span><strong>{sub.nextBilling}</strong></div>
                </div>
              </div>
              <div className="sb-info-card">
                <h3>Included Features</h3>
                <div className="sb-features">
                  {sub.features.map((f) => (
                    <div key={f} className="sb-feature-item">✅ {f}</div>
                  ))}
                </div>
              </div>
              <div className="sb-cta-card">
                <h3>Upgrade to Enterprise</h3>
                <p>Get dedicated support, 1TB+ storage, custom integrations and an SLA guarantee.</p>
                <button className="sb-btn-primary" onClick={() => setUpgrade(true)}>View Enterprise Plans</button>
              </div>
            </div>
          )}

          {/* ── Billing History tab ── */}
          {tab === 'billing' && (
            <div className="sb-section">
              <h2>Billing History</h2>
              <div className="sb-table-wrap">
                <div className="sb-table-head">
                  <span>Date</span><span>Description</span><span>Amount</span><span>Status</span><span>Invoice</span>
                </div>
                {BILLING_HISTORY.map((b) => (
                  <div className="sb-table-row" key={b.id}>
                    <span>{b.date}</span>
                    <span>{b.description}<br /><small>{b.invoice}</small></span>
                    <span>{b.amount}</span>
                    <span><span className={`sb-badge ${b.status}`}>{b.status}</span></span>
                    <span><button className="sb-icon-btn" title="Download">📥</button></span>
                  </div>
                ))}
              </div>
              <p className="sb-note">All invoices include full charge details. Keep them for your records.</p>
            </div>
          )}

          {/* ── Plans tab ── */}
          {tab === 'plans' && (
            <div className="sb-section">
              <h2>All Plans</h2>
              <p className="sb-sub">Choose the plan that works for you.</p>
              <div className="sb-plans-grid">
                {PLANS.map((p) => (
                  <div key={p.id} className={`sb-plan-card${p.popular ? ' popular' : ''}`}>
                    {p.popular && <div className="sb-popular-badge">Most Popular</div>}
                    <div className="sb-plan-card-name">{p.name}</div>
                    <div className="sb-plan-card-price">
                      {p.price !== null ? <><span className="sb-currency">$</span>{p.price}<span className="sb-period">/{p.period}</span></> : <span>Custom</span>}
                    </div>
                    <p className="sb-plan-desc">{p.description}</p>
                    <ul className="sb-plan-features">
                      {p.features.map((f) => <li key={f}>✓ {f}</li>)}
                    </ul>
                    <button
                      className={p.id === 'pro' ? 'sb-btn-current' : 'sb-btn-primary'}
                      disabled={p.id === 'pro'}
                      onClick={() => p.id !== 'pro' && setUpgrade(true)}
                    >
                      {p.cta}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ── Payment tab ── */}
          {tab === 'payment' && (
            <div className="sb-section">
              <h2>Payment Method</h2>
              <div className="sb-info-card">
                <h3>Current Card</h3>
                <div className="sb-credit-card">
                  <div className="sb-card-type">💳 Visa</div>
                  <div className="sb-card-num">•••• •••• •••• 4242</div>
                  <div className="sb-card-meta"><span>Expires 12/25</span><span>John Doe</span></div>
                </div>
                <div className="sb-btn-row">
                  <button className="sb-btn-ghost">Edit Card</button>
                  <button className="sb-btn-ghost">Add Card</button>
                </div>
              </div>
              <div className="sb-info-card">
                <h3>Billing Address</h3>
                <div className="sb-address">
                  <p>John Doe</p><p>123 Main Street</p><p>New York, NY 10001</p><p>United States</p>
                </div>
                <button className="sb-btn-ghost">Edit Address</button>
              </div>
              <div className="sb-info-card">
                <h3>Tax Information</h3>
                <div className="sb-info-grid">
                  <div className="sb-info-row"><span>Tax ID</span><strong>Not provided</strong></div>
                  <div className="sb-info-row"><span>Tax Exemption</span><strong>Not applicable</strong></div>
                </div>
                <button className="sb-btn-ghost">Edit Tax Info</button>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* ── Upgrade Modal ── */}
      {upgradeModal && (
        <div className="sb-modal-overlay" onClick={() => setUpgrade(false)}>
          <div className="sb-modal" onClick={(e) => e.stopPropagation()}>
            <button className="sb-modal-close" onClick={() => setUpgrade(false)}>✕</button>
            <h2>Upgrade to Enterprise</h2>
            <p>Contact our sales team for custom pricing tailored to your team's needs.</p>
            <div className="sb-modal-features">
              {['1TB+ storage','Dedicated account manager','Phone & email support','Custom integrations','SLA guarantee','Branded portal'].map((f) => (
                <div key={f} className="sb-modal-feature">🌟 {f}</div>
              ))}
            </div>
            <button className="sb-btn-primary" onClick={() => setUpgrade(false)}>Contact Sales</button>
          </div>
        </div>
      )}
    </div>
  )
}
