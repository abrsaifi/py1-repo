import React, { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import { useNavigate } from 'react-router-dom'
import '../styles/dashboard.css'

const SubscriberDashboard = () => {
  const navigate = useNavigate()
  const auth = useAuth()
  const [activeTab, setActiveTab] = useState('subscription')
  const [showProfile, setShowProfile] = useState(false)
  const [showBillingModal, setShowBillingModal] = useState(false)

  // Redirect if not authenticated
  useEffect(() => {
    if (!auth.isAuthenticated || !auth.user) {
      navigate('/login', { replace: true })
    }
  }, [auth.isAuthenticated, auth.user, navigate])

  const [subscription, setSubscription] = useState({
    plan: 'Pro',
    status: 'active',
    nextBillingDate: '2024-04-15',
    amount: 9.99,
    billingCycle: 'monthly',
    autoRenewal: true,
    startDate: '2024-01-15',
    features: [
      'Unlimited conversions',
      '100GB storage',
      'Priority email support',
      'Advanced analytics',
      'API access',
      'Custom branding'
    ],
    nextTierFeatures: [
      'Everything in Pro +',
      '1TB storage',
      'Phone support',
      'Branded portal',
      'Webhook integrations',
      'Custom integrations'
    ]
  })

  const [billingHistory, setBillingHistory] = useState([
    { id: 1, date: '2024-03-15', description: 'Pro Plan Subscription', amount: '$9.99', status: 'paid', invoice: '#INV-2024-003' },
    { id: 2, date: '2024-02-15', description: 'Pro Plan Subscription', amount: '$9.99', status: 'paid', invoice: '#INV-2024-002' },
    { id: 3, date: '2024-01-15', description: 'Pro Plan Subscription', amount: '$9.99', status: 'paid', invoice: '#INV-2024-001' },
  ])

  const [plans, setPlans] = useState([
    {
      id: 'free',
      name: 'Free',
      price: 0,
      period: 'forever',
      description: 'Perfect for getting started',
      features: [
        'Up to 10 conversions/day',
        '2GB storage',
        'Email support',
        'Basic analytics'
      ],
      cta: 'Current Plan',
      highlighted: false
    },
    {
      id: 'pro',
      name: 'Pro',
      price: 9.99,
      period: 'month',
      description: 'Best for regular users',
      features: [
        'Unlimited conversions',
        '100GB storage',
        'Priority email support',
        'Advanced analytics',
        'API access',
        'Custom branding'
      ],
      cta: 'Current Plan',
      highlighted: true
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: 'Custom',
      period: 'month',
      description: 'For teams and enterprises',
      features: [
        'Everything in Pro +',
        '1TB+ storage',
        'Phone & email support',
        'Dedicated account manager',
        'Custom integrations',
        'SLA guarantee'
      ],
      cta: 'Contact Sales',
      highlighted: false
    }
  ])

  const handleDownloadInvoice = (invoiceId) => {
    console.log('Downloading invoice:', invoiceId)
    // Implement invoice download
  }

  const handleUpgrade = () => {
    setShowBillingModal(true)
  }

  const handleCancelSubscription = () => {
    if (window.confirm('Are you sure you want to cancel your subscription? Your access will end on ' + subscription.nextBillingDate)) {
      console.log('Subscription cancelled')
      // Implement cancel logic
    }
  }

  return (
    <div className="subscriber-dashboard">
      {/* Top Navigation */}
      <nav className="dashboard-topnav v2">
        <div className="topnav-left">
          <h1>💳 Subscriptions & Billing</h1>
        </div>
        <div className="topnav-right">
          <div className="profile-menu-wrapper">
            <button 
              className="profile-button"
              onClick={() => setShowProfile(!showProfile)}
            >
              <span className="profile-avatar">{auth.user?.username?.[0]?.toUpperCase() || '👤'}</span>
              <span className="profile-name">{auth.user?.username}</span>
            </button>
            
            {showProfile && (
              <div className="profile-dropdown">
                <div className="profile-header">
                  <div className="profile-avatar-large">{auth.user?.username?.[0]?.toUpperCase() || '👤'}</div>
                  <div>
                    <p className="profile-name-large"><strong>{auth.user?.username}</strong></p>
                    <p className="text-muted">{auth.user?.email}</p>
                  </div>
                </div>
                <hr />
                <button className="dropdown-item" onClick={() => navigate('/dashboard')}>
                  📊 Back to Dashboard
                </button>
                <button className="dropdown-item" onClick={() => navigate('/settings')}>
                  ⚙️ Account Settings
                </button>
                <hr />
                <button className="dropdown-item logout" onClick={auth.logout}>
                  🚪 Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </nav>

      {/* Tabs */}
      <div className="dashboard-nav sticky v2">
        <div className="nav-container">
          <button 
            className={`nav-tab ${activeTab === 'subscription' ? 'active' : ''}`}
            onClick={() => setActiveTab('subscription')}
          >
            📋 My Subscription
          </button>
          <button 
            className={`nav-tab ${activeTab === 'billing' ? 'active' : ''}`}
            onClick={() => setActiveTab('billing')}
          >
            💳 Billing History
          </button>
          <button 
            className={`nav-tab ${activeTab === 'plans' ? 'active' : ''}`}
            onClick={() => setActiveTab('plans')}
          >
            📦 All Plans
          </button>
          <button 
            className={`nav-tab ${activeTab === 'payment' ? 'active' : ''}`}
            onClick={() => setActiveTab('payment')}
          >
            💰 Payment Method
          </button>
        </div>
      </div>

      <div className="dashboard-container v2">
        {/* Sidebar */}
        <aside className="dashboard-sidebar v2">
          {/* Current Plan Card */}
          <div className="sidebar-card">
            <div className="card-header">🎯 Current Plan</div>
            <div className="plan-display">
              <div className="plan-name">{subscription.plan}</div>
              <div className="plan-price">${subscription.amount}<span className="period">/{subscription.billingCycle}</span></div>
              <div className={`plan-status ${subscription.status}`}>{subscription.status.charAt(0).toUpperCase() + subscription.status.slice(1)}</div>
            </div>
            <div className="plan-dates">
              <div className="date-item">
                <span className="label">Started</span>
                <span className="value">{subscription.startDate}</span>
              </div>
              <div className="date-item">
                <span className="label">Next Billing</span>
                <span className="value">{subscription.nextBillingDate}</span>
              </div>
            </div>
            <button className="btn-primary btn-block" onClick={handleUpgrade}>
              ⭐ Upgrade Plan
            </button>
            <button className="btn-secondary btn-block" onClick={handleCancelSubscription}>
              Cancel Subscription
            </button>
          </div>

          {/* Usage Card */}
          <div className="sidebar-card">
            <div className="card-header">📊 Usage This Month</div>
            <div className="usage-stats">
              <div className="usage-item">
                <div className="usage-label">Conversions</div>
                <div className="usage-bar">
                  <div className="usage-fill" style={{ width: '65%' }}></div>
                </div>
                <div className="usage-text">250 / 500 (unlimited)</div>
              </div>
              <div className="usage-item">
                <div className="usage-label">Storage</div>
                <div className="usage-bar">
                  <div className="usage-fill" style={{ width: '23%' }}></div>
                </div>
                <div className="usage-text">2.3 GB / 100 GB</div>
              </div>
              <div className="usage-item">
                <div className="usage-label">API Calls</div>
                <div className="usage-bar">
                  <div className="usage-fill" style={{ width: '45%' }}></div>
                </div>
                <div className="usage-text">4,500 / 100,000</div>
              </div>
            </div>
          </div>

          {/* Help Card */}
          <div className="sidebar-card">
            <div className="card-header">❓ Need Help?</div>
            <a href="#support" className="help-link">
              <span>📖</span> Billing FAQ
            </a>
            <a href="#support" className="help-link">
              <span>💬</span> Contact Support
            </a>
            <a href="#docs" className="help-link">
              <span>📚</span> Documentation
            </a>
          </div>
        </aside>

        {/* Main Content */}
        <main className="dashboard-main v2">
          {activeTab === 'subscription' && (
            <>
              <section className="subscription-section">
                <h2>Your Subscription Details</h2>
                
                <div className="section-card">
                  <h3>Plan Information</h3>
                  <div className="info-grid">
                    <div className="info-item">
                      <span className="info-label">Plan Name</span>
                      <span className="info-value">{subscription.plan}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Status</span>
                      <span className={`info-value status ${subscription.status}`}>{subscription.status}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Billing Cycle</span>
                      <span className="info-value">{subscription.billingCycle.charAt(0).toUpperCase() + subscription.billingCycle.slice(1)}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Monthly Amount</span>
                      <span className="info-value">${subscription.amount}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Auto-Renewal</span>
                      <span className="info-value">{subscription.autoRenewal ? 'Enabled' : 'Disabled'}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Next Billing Date</span>
                      <span className="info-value">{subscription.nextBillingDate}</span>
                    </div>
                  </div>
                </div>

                <div className="section-card">
                  <h3>Included Features</h3>
                  <div className="features-list">
                    {subscription.features.map((feature, idx) => (
                      <div key={idx} className="feature-item">
                        <span className="feature-icon">✅</span>
                        <span className="feature-name">{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="section-card upgrade-card">
                  <h3>Upgrade to Enterprise</h3>
                  <p>Get advanced features and dedicated support</p>
                  <div className="upgrade-features">
                    {subscription.nextTierFeatures.map((feature, idx) => (
                      <div key={idx} className="upgrade-feature">
                        <span className="feature-icon">🌟</span>
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>
                  <button className="btn-primary btn-lg" onClick={handleUpgrade}>
                    Upgrade to Enterprise
                  </button>
                </div>
              </section>
            </>
          )}

          {activeTab === 'billing' && (
            <section className="billing-section">
              <h2>Billing History</h2>
              
              <div className="billing-table">
                <div className="table-header">
                  <div className="col-date">Date</div>
                  <div className="col-description">Description</div>
                  <div className="col-amount">Amount</div>
                  <div className="col-status">Status</div>
                  <div className="col-actions">Invoice</div>
                </div>
                {billingHistory.map((bill) => (
                  <div key={bill.id} className="table-row">
                    <div className="col-date">{bill.date}</div>
                    <div className="col-description">
                      <strong>{bill.description}</strong>
                      <br />
                      <small className="text-muted">{bill.invoice}</small>
                    </div>
                    <div className="col-amount">{bill.amount}</div>
                    <div className="col-status">
                      <span className={`status-badge ${bill.status}`}>{bill.status}</span>
                    </div>
                    <div className="col-actions">
                      <button 
                        className="btn-icon"
                        onClick={() => handleDownloadInvoice(bill.invoice)}
                        title="Download invoice"
                      >
                        📥
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              <div className="billing-note">
                <p><strong>Note:</strong> All invoices include detailed information about your subscription and charges. Keep them for your records.</p>
              </div>
            </section>
          )}

          {activeTab === 'plans' && (
            <section className="plans-section">
              <h2>All Plans</h2>
              <p className="section-intro">Choose the perfect plan for your needs</p>
              
              <div className="plans-grid">
                {plans.map((plan) => (
                  <div key={plan.id} className={`plan-card ${plan.highlighted ? 'highlighted' : ''}`}>
                    {plan.highlighted && <div className="plan-badge">Most Popular</div>}
                    <div className="plan-header">
                      <h3>{plan.name}</h3>
                      <div className="plan-price">
                        {typeof plan.price === 'number' ? (
                          <>
                            <span className="currency">$</span>
                            <span className="amount">{plan.price}</span>
                            <span className="period">/{plan.period}</span>
                          </>
                        ) : (
                          <span className="amount">{plan.price}</span>
                        )}
                      </div>
                      <p className="plan-description">{plan.description}</p>
                    </div>
                    <ul className="plan-features">
                      {plan.features.map((feature, idx) => (
                        <li key={idx}>
                          <span className="feature-bullet">✓</span>
                          {feature}
                        </li>
                      ))}
                    </ul>
                    <button 
                      className={`btn-${plan.id === 'pro' ? 'secondary' : plan.highlighted ? 'primary' : 'tertiary'} btn-block btn-lg`}
                      onClick={() => plan.id !== 'pro' && handleUpgrade()}
                      disabled={plan.id === 'pro'}
                    >
                      {plan.cta}
                    </button>
                  </div>
                ))}
              </div>
            </section>
          )}

          {activeTab === 'payment' && (
            <section className="payment-section">
              <h2>Payment Method</h2>

              <div className="section-card">
                <h3>Current Payment Method</h3>
                <div className="payment-method-display">
                  <div className="card-visual">
                    <div className="card-type">💳 Visa</div>
                    <div className="card-number">•••• •••• •••• 4242</div>
                    <div className="card-details">
                      <span>Expires: 12/25</span>
                      <span>Cardholder: John Doe</span>
                    </div>
                  </div>
                </div>
                <button className="btn-secondary">Edit Payment Method</button>
                <button className="btn-secondary">Add Another Card</button>
              </div>

              <div className="section-card">
                <h3>Billing Address</h3>
                <div className="address-display">
                  <p>John Doe</p>
                  <p>123 Main Street</p>
                  <p>New York, NY 10001</p>
                  <p>United States</p>
                </div>
                <button className="btn-secondary">Edit Address</button>
              </div>

              <div className="section-card">
                <h3>Tax Information</h3>
                <div className="tax-settings">
                  <div className="setting-item">
                    <span className="label">Tax ID</span>
                    <span className="value">Not provided</span>
                  </div>
                  <div className="setting-item">
                    <span className="label">Tax Exemption</span>
                    <span className="value">Not applicable</span>
                  </div>
                </div>
                <button className="btn-secondary">Edit Tax Information</button>
              </div>
            </section>
          )}
        </main>
      </div>

      {/* Billing Modal */}
      {showBillingModal && (
        <div className="modal-overlay" onClick={() => setShowBillingModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setShowBillingModal(false)}>✕</button>
            <h2>Upgrade Your Subscription</h2>
            <p>Select a plan to upgrade to:</p>
            <div className="upgrade-plans">
              <button className="upgrade-plan" onClick={() => setShowBillingModal(false)}>
                <h3>Enterprise</h3>
                <p className="price">Custom Pricing</p>
                <p className="desc">Contact sales for custom pricing</p>
              </button>
            </div>
            <button className="btn-primary btn-block" onClick={() => setShowBillingModal(false)}>
              Contact Sales
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default SubscriberDashboard
