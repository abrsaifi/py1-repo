import React, { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@shared/hooks/useAuth'
import { useToast } from '@shared/components/Toast'
import '../../styles/subscriber-dashboard.css'

const DEFAULT_SUBSCRIPTION = {
  plan: 'Free',
  status: 'active',
  amount: 0,
  cycle: 'forever',
  startDate: 'N/A',
  nextBilling: 'N/A',
  autoRenew: false,
  features: ['2 GB storage', 'Basic analytics'],
}

const DEFAULT_PAYMENT = {
  method: {
    brand: 'No card on file',
    last4: '----',
    expiry: 'N/A',
    holder: 'N/A',
    status: 'No payment data available.',
  },
  billingAddress: {
    name: 'N/A',
    line1: 'N/A',
    line2: '',
    country: 'N/A',
  },
  taxInfo: {
    taxId: 'Not provided',
    taxExemption: 'Not applicable',
  },
}

export default function SubscriberDashboard() {
  const navigate = useNavigate()
  const auth = useAuth()
  const { addToast } = useToast()
  const profileRef = useRef(null)

  const [tab, setTab] = useState('subscription')
  const [profileOpen, setProfile] = useState(false)
  const [upgradeModal, setUpgrade] = useState(false)
  const [loading, setLoading] = useState(true)
  const [planChangeLoading, setPlanChangeLoading] = useState('')
  const [subscription, setSubscription] = useState(DEFAULT_SUBSCRIPTION)
  const [usage, setUsage] = useState([])
  const [billingHistory, setBillingHistory] = useState([])
  const [plans, setPlans] = useState([])
  const [payment, setPayment] = useState(DEFAULT_PAYMENT)

  useEffect(() => {
    if (!auth.isAuthenticated) {
      navigate('/login', { replace: true })
    }
  }, [auth.isAuthenticated, navigate])

  useEffect(() => {
    const handleMouseDown = (event) => {
      if (profileRef.current && !profileRef.current.contains(event.target)) {
        setProfile(false)
      }
    }

    document.addEventListener('mousedown', handleMouseDown)
    return () => document.removeEventListener('mousedown', handleMouseDown)
  }, [])

  const getAuthHeaders = () => ({
    Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
  })

  const loadSubscriptionDashboard = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/account/subscription', {
        headers: getAuthHeaders(),
      })
      const payload = await response.json()

      if (!response.ok) {
        throw new Error(payload.error || 'Failed to load subscription dashboard')
      }

      setSubscription(payload.subscription || DEFAULT_SUBSCRIPTION)
      setUsage(payload.usage || [])
      setBillingHistory(payload.billingHistory || [])
      setPlans(payload.plans || [])
      setPayment(payload.payment || DEFAULT_PAYMENT)
    } catch (error) {
      addToast({ type: 'error', title: 'Billing unavailable', message: error.message })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!auth.isAuthenticated) {
      return
    }

    loadSubscriptionDashboard()
  }, [auth.isAuthenticated])

  const initials = auth.user?.username?.[0]?.toUpperCase() || 'U'

  const downloadInvoice = (invoice) => {
    fetch(`/api/account/invoices/${invoice.id}/download`, {
      headers: getAuthHeaders(),
    })
      .then(async (response) => {
        if (!response.ok) {
          const payload = await response.json().catch(() => ({}))
          throw new Error(payload.error || 'Failed to download invoice')
        }

        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${invoice.invoice}.txt`
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        addToast({ type: 'success', title: 'Invoice downloaded', message: invoice.invoice })
      })
      .catch((error) => {
        addToast({ type: 'error', title: 'Invoice download failed', message: error.message })
      })
  }

  const openSupport = () => {
    addToast({ type: 'info', title: 'Opening support', message: 'Launching your mail client for support@docpro.app' })
    window.location.href = 'mailto:support@docpro.app'
  }

  const requestEnterprise = () => {
    addToast({ type: 'info', title: 'Opening sales contact', message: 'Launching your mail client for enterprise inquiries' })
    window.location.href = 'mailto:sales@docpro.app?subject=Enterprise%20Plan%20Inquiry'
  }

  const cancelSubscription = async () => {
    try {
      const response = await fetch('/api/account/subscription/cancel', {
        method: 'POST',
        headers: getAuthHeaders(),
      })
      const payload = await response.json()

      if (!response.ok) {
        throw new Error(payload.error || 'Failed to cancel subscription')
      }

      setSubscription(payload.subscription || subscription)
      addToast({ type: 'warning', title: 'Cancellation scheduled', message: payload.message || 'Auto-renew has been disabled.' })
    } catch (error) {
      addToast({ type: 'error', title: 'Cancellation failed', message: error.message })
    }
  }

  const changePlan = async (targetPlan) => {
    try {
      setPlanChangeLoading(targetPlan)
      const response = await fetch('/api/account/subscription/change-plan', {
        method: 'POST',
        headers: {
          ...getAuthHeaders(),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ target_plan: targetPlan }),
      })
      const payload = await response.json()

      if (!response.ok) {
        throw new Error(payload.error || 'Failed to change plan')
      }

      setSubscription(payload.dashboard?.subscription || DEFAULT_SUBSCRIPTION)
      setUsage(payload.dashboard?.usage || [])
      setBillingHistory(payload.dashboard?.billingHistory || [])
      setPlans(payload.dashboard?.plans || [])
      setPayment(payload.dashboard?.payment || DEFAULT_PAYMENT)
      setUpgrade(false)
      addToast({ type: 'success', title: 'Plan updated', message: payload.message || 'Your subscription plan has been updated.' })
    } catch (error) {
      addToast({ type: 'error', title: 'Plan update failed', message: error.message })
    } finally {
      setPlanChangeLoading('')
    }
  }

  return (
    <div className="sb-root">
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

      <nav className="sb-tabs">
        {[
          { id: 'subscription', label: 'My Subscription', icon: '📋' },
          { id: 'billing', label: 'Billing History', icon: '💳' },
          { id: 'plans', label: 'All Plans', icon: '📦' },
          { id: 'payment', label: 'Payment Method', icon: '💰' },
        ].map((item) => (
          <button key={item.id} className={`sb-tab${tab === item.id ? ' active' : ''}`} onClick={() => setTab(item.id)}>
            {item.icon} {item.label}
          </button>
        ))}
      </nav>

      <div className="sb-body">
        <aside className="sb-sidebar">
          <div className="sb-card">
            <div className="sb-card-title">Current Plan</div>
            <div className="sb-plan-name">{subscription.plan}</div>
            <div className="sb-plan-price">{subscription.amount === 0 ? '$0' : `$${subscription.amount}`}<span>/{subscription.cycle}</span></div>
            <div className="sb-status active">{subscription.status}</div>
            <div className="sb-dates">
              <div className="sb-date-row"><span>Started</span><span>{subscription.startDate}</span></div>
              <div className="sb-date-row"><span>Next Billing</span><span>{subscription.nextBilling}</span></div>
              <div className="sb-date-row"><span>Auto-Renew</span><span>{subscription.autoRenew ? 'On' : 'Off'}</span></div>
            </div>
            <button className="sb-btn-primary" onClick={() => setTab('plans')}>⭐ Upgrade Plan</button>
            <button className="sb-btn-ghost" onClick={cancelSubscription} disabled={!subscription.autoRenew || subscription.plan === 'Free'}>Cancel Subscription</button>
          </div>

          <div className="sb-card">
            <div className="sb-card-title">Usage This Month</div>
            {usage.map((item) => (
              <div className="sb-usage-item" key={item.label}>
                <div className="sb-usage-top">
                  <span>{item.label}</span>
                  <span className="sb-usage-vals">{item.used} / {item.total}</span>
                </div>
                <div className="sb-usage-bar">
                  <div className="sb-usage-fill" style={{ width: `${item.pct}%` }}></div>
                </div>
              </div>
            ))}
            {!usage.length && <p className="sb-note">Usage data will appear after your subscription is loaded.</p>}
          </div>

          <div className="sb-card">
            <div className="sb-card-title">Help & Support</div>
            <button className="sb-help-link" onClick={() => navigate('/')}>📖 Billing FAQ</button>
            <button className="sb-help-link" onClick={openSupport}>💬 Contact Support</button>
            <button className="sb-help-link" onClick={() => navigate('/tools')}>📚 Documentation</button>
          </div>
        </aside>

        <main className="sb-main">
          {tab === 'subscription' && (
            <div className="sb-section">
              <h2>Subscription Details</h2>
              {loading && <p className="sb-note">Loading subscription data...</p>}
              <div className="sb-info-card">
                <h3>Plan Information</h3>
                <div className="sb-info-grid">
                  <div className="sb-info-row"><span>Plan</span><strong>{subscription.plan}</strong></div>
                  <div className="sb-info-row"><span>Status</span><span className="sb-status active">{subscription.status}</span></div>
                  <div className="sb-info-row"><span>Billing Cycle</span><strong>{subscription.cycle}</strong></div>
                  <div className="sb-info-row"><span>Amount</span><strong>{subscription.amount === 0 ? '$0' : `$${subscription.amount}`}/{subscription.cycle}</strong></div>
                  <div className="sb-info-row"><span>Auto-Renewal</span><strong>{subscription.autoRenew ? 'Enabled' : 'Disabled'}</strong></div>
                  <div className="sb-info-row"><span>Next Billing</span><strong>{subscription.nextBilling}</strong></div>
                </div>
              </div>
              <div className="sb-info-card">
                <h3>Included Features</h3>
                <div className="sb-features">
                  {subscription.features.map((feature) => (
                    <div key={feature} className="sb-feature-item">✅ {feature}</div>
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

          {tab === 'billing' && (
            <div className="sb-section">
              <h2>Billing History</h2>
              <div className="sb-table-wrap">
                <div className="sb-table-head">
                  <span>Date</span><span>Description</span><span>Amount</span><span>Status</span><span>Invoice</span>
                </div>
                {billingHistory.map((item) => (
                  <div className="sb-table-row" key={item.id}>
                    <span>{item.date}</span>
                    <span>{item.description}<br /><small>{item.invoice}</small></span>
                    <span>{item.amount}</span>
                    <span><span className={`sb-badge ${item.status}`}>{item.status}</span></span>
                    <span><button className="sb-icon-btn" title="Download" onClick={() => downloadInvoice(item)}>📥</button></span>
                  </div>
                ))}
              </div>
              {!billingHistory.length && <p className="sb-note">No billing events recorded yet for this account.</p>}
              <p className="sb-note">All invoices include full charge details. Keep them for your records.</p>
            </div>
          )}

          {tab === 'plans' && (
            <div className="sb-section">
              <h2>All Plans</h2>
              <p className="sb-sub">Choose the plan that works for you.</p>
              <div className="sb-plans-grid">
                {plans.map((item) => (
                  <div key={item.id} className={`sb-plan-card${item.popular ? ' popular' : ''}`}>
                    {item.popular && <div className="sb-popular-badge">Most Popular</div>}
                    <div className="sb-plan-card-name">{item.name}</div>
                    <div className="sb-plan-card-price">
                      {item.price !== null ? <><span className="sb-currency">$</span>{item.price}<span className="sb-period">/{item.period}</span></> : <span>Custom</span>}
                    </div>
                    <p className="sb-plan-desc">{item.description}</p>
                    <ul className="sb-plan-features">
                      {item.features.map((feature) => <li key={feature}>✓ {feature}</li>)}
                    </ul>
                    <button
                      className={item.isCurrent ? 'sb-btn-current' : 'sb-btn-primary'}
                      onClick={() => item.id === 'enterprise' ? requestEnterprise() : changePlan(item.id)}
                      disabled={item.isCurrent || planChangeLoading === item.id}
                    >
                      {planChangeLoading === item.id ? 'Updating...' : item.cta}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {tab === 'payment' && (
            <div className="sb-section">
              <h2>Payment Method</h2>
              <div className="sb-info-card">
                <h3>Current Card</h3>
                <div className="sb-credit-card">
                  <div className="sb-card-type">💳 {payment.method.brand}</div>
                  <div className="sb-card-num">•••• •••• •••• {payment.method.last4}</div>
                  <div className="sb-card-meta"><span>Expires {payment.method.expiry}</span><span>{payment.method.holder}</span></div>
                </div>
                <p className="sb-note">{payment.method.status}</p>
                <div className="sb-btn-row">
                  <button className="sb-btn-ghost" onClick={() => navigate('/dashboard/account')}>Edit Card</button>
                  <button className="sb-btn-ghost" onClick={() => navigate('/dashboard/account')}>Add Card</button>
                </div>
              </div>
              <div className="sb-info-card">
                <h3>Billing Address</h3>
                <div className="sb-address">
                  <p>{payment.billingAddress.name}</p>
                  <p>{payment.billingAddress.line1}</p>
                  <p>{payment.billingAddress.line2}</p>
                  <p>{payment.billingAddress.country}</p>
                </div>
                <button className="sb-btn-ghost" onClick={() => navigate('/dashboard/account')}>Edit Address</button>
              </div>
              <div className="sb-info-card">
                <h3>Tax Information</h3>
                <div className="sb-info-grid">
                  <div className="sb-info-row"><span>Tax ID</span><strong>{payment.taxInfo.taxId}</strong></div>
                  <div className="sb-info-row"><span>Tax Exemption</span><strong>{payment.taxInfo.taxExemption}</strong></div>
                </div>
                <button className="sb-btn-ghost" onClick={() => navigate('/dashboard/account')}>Edit Tax Info</button>
              </div>
            </div>
          )}
        </main>
      </div>

      {upgradeModal && (
        <div className="sb-modal-overlay" onClick={() => setUpgrade(false)}>
          <div className="sb-modal" onClick={(event) => event.stopPropagation()}>
            <button className="sb-modal-close" onClick={() => setUpgrade(false)}>✕</button>
            <h2>Upgrade to Enterprise</h2>
            <p>Contact our sales team for custom pricing tailored to your team's needs.</p>
            <div className="sb-modal-features">
              {['1TB+ storage', 'Dedicated account manager', 'Phone & email support', 'Custom integrations', 'SLA guarantee', 'Branded portal'].map((feature) => (
                <div key={feature} className="sb-modal-feature">🌟 {feature}</div>
              ))}
            </div>
            <button className="sb-btn-primary" onClick={requestEnterprise}>Contact Sales</button>
          </div>
        </div>
      )}
    </div>
  )
}
