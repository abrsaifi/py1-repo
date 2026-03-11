import React, { useState, useEffect } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import '../styles/admin.css'

const UsageBilling = () => {
  const [billingData, setBillingData] = useState({
    currentPlan: 'Professional',
    monthlyLimit: 50000,
    conversionsUsed: 34567,
    storageUsed: 245,
    storageLimit: 1000,
    nextBillingDate: '2026-04-06',
    monthlyRate: 299,
    totalInvoices: 12,
    lastInvoice: '2026-03-06'
  })

  const usagePercent = Math.round((billingData.conversionsUsed / billingData.monthlyLimit) * 100)
  const storagePercent = Math.round((billingData.storageUsed / billingData.storageLimit) * 100)

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="💳" size={24} /> Usage & Billing</h2>
      <p className="section-subtitle">Subscription, usage metrics, and billing information</p>

      <div className="admin-stats-grid">
        <div className="admin-stat-card metric-info">
          <UniversalIcon icon="📊" size={32} />
          <div className="stat-content">
            <h3>Current Plan</h3>
            <p className="stat-value">{billingData.currentPlan}</p>
            <p className="stat-detail">${billingData.monthlyRate}/month</p>
          </div>
        </div>

        <div className="admin-stat-card metric-primary">
          <UniversalIcon icon="📋" size={32} />
          <div className="stat-content">
            <h3>Conversions Used</h3>
            <p className="stat-value">{(billingData.conversionsUsed / 1000).toFixed(1)}K</p>
            <p className="stat-detail">{usagePercent}% of {(billingData.monthlyLimit / 1000).toFixed(0)}K</p>
          </div>
        </div>

        <div className="admin-stat-card metric-success">
          <UniversalIcon icon="💾" size={32} />
          <div className="stat-content">
            <h3>Storage Used</h3>
            <p className="stat-value">{billingData.storageUsed} GB</p>
            <p className="stat-detail">{storagePercent}% of {billingData.storageLimit} GB</p>
          </div>
        </div>

        <div className="admin-stat-card metric-revenue">
          <UniversalIcon icon="📅" size={32} />
          <div className="stat-content">
            <h3>Next Billing</h3>
            <p className="stat-value">{billingData.nextBillingDate}</p>
            <p className="stat-detail">{billingData.totalInvoices} invoices</p>
          </div>
        </div>
      </div>

      <div className="admin-section-content">
        <h3>Billing Overview</h3>
        <div className="billing-info">
          <div className="billing-card">
            <h4>Conversion Usage</h4>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${usagePercent}%` }}></div>
            </div>
            <p>{billingData.conversionsUsed.toLocaleString()} / {billingData.monthlyLimit.toLocaleString()} conversions</p>
          </div>
          <div className="billing-card">
            <h4>Storage Usage</h4>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${storagePercent}%` }}></div>
            </div>
            <p>{billingData.storageUsed} / {billingData.storageLimit} GB</p>
          </div>
        </div>

        <div className="action-buttons">
          <button className="action-button primary">Upgrade Plan</button>
          <button className="action-button secondary">Download Invoice</button>
          <button className="action-button secondary">Billing Settings</button>
        </div>
      </div>
    </div>
  )
}

export default UsageBilling
