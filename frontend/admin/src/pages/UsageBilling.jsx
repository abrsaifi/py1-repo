import React, { useState, useEffect } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import '../styles/admin.css'

const emptyBillingData = {
  summary: {
    periodDays: 30,
    periodStart: null,
    periodEnd: null,
    isCustomRange: false,
    monthlyRecurringRevenue: 0,
    activePaidSubscriptions: 0,
    totalInvoices: 0,
    paidInvoices: 0,
    pendingInvoices: 0,
    failedInvoices: 0,
    refundedInvoices: 0,
    invoicesDuringPeriod: 0,
    billedDuringPeriod: 0,
    planChangesDuringPeriod: 0,
    nextRenewalDate: null,
  },
  usage: {
    conversionsUsedThisMonth: 0,
    conversionsCapacity: 0,
    storageUsedGb: 0,
    storageCapacityGb: 0,
  },
  planDistribution: [],
  recentInvoices: [],
  recentPlanChanges: [],
  recentStatusChanges: [],
  auditFilters: {
    status: 'all',
    actor: 'all',
    invoice: '',
    matchingCount: 0,
    availableActors: [],
  },
  invoicePagination: {
    total: 0,
    pages: 0,
    currentPage: 1,
    perPage: 10,
    hasNext: false,
    hasPrev: false,
    nextPage: null,
    prevPage: null,
  },
  auditPagination: {
    total: 0,
    pages: 0,
    currentPage: 1,
    perPage: 25,
    hasNext: false,
    hasPrev: false,
    nextPage: null,
    prevPage: null,
  },
  providerSync: {
    endpoint: '',
    secretConfigured: false,
    signatureHeader: 'X-DocPro-Billing-Signature',
    supportedProviders: [],
    stripeMetadataKeys: [],
    supportedEventTypes: [],
  },
}

const UsageBilling = () => {
  const emptyStatusEditor = {
    isOpen: false,
    invoice: null,
    status: '',
    form: {
      status: '',
      status_note: '',
      failure_code: '',
      failure_reason: '',
      refund_amount: '',
      gateway_reference_id: '',
      processor_event_at: '',
    },
  }

  const [billingData, setBillingData] = useState(emptyBillingData)
  const [filterMode, setFilterMode] = useState('preset')
  const [selectedDays, setSelectedDays] = useState(30)
  const [customStartDate, setCustomStartDate] = useState('')
  const [customEndDate, setCustomEndDate] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [downloadingInvoiceId, setDownloadingInvoiceId] = useState(null)
  const [updatingInvoiceId, setUpdatingInvoiceId] = useState(null)
  const [exportingAudit, setExportingAudit] = useState(false)
  const [auditStatusFilter, setAuditStatusFilter] = useState('all')
  const [auditActorFilter, setAuditActorFilter] = useState('all')
  const [auditInvoiceFilter, setAuditInvoiceFilter] = useState('')
  const [statusEditor, setStatusEditor] = useState(emptyStatusEditor)
  const [invoicePage, setInvoicePage] = useState(1)
  const [invoicePerPage, setInvoicePerPage] = useState(10)
  const [auditPage, setAuditPage] = useState(1)
  const [auditPerPage, setAuditPerPage] = useState(25)

  const buildBillingParams = (overrides = {}) => {
    const nextFilterMode = overrides.filterMode ?? filterMode
    const nextSelectedDays = overrides.selectedDays ?? selectedDays
    const nextCustomStartDate = overrides.customStartDate ?? customStartDate
    const nextCustomEndDate = overrides.customEndDate ?? customEndDate
    const nextAuditStatusFilter = overrides.auditStatusFilter ?? auditStatusFilter
    const nextAuditActorFilter = overrides.auditActorFilter ?? auditActorFilter
    const nextAuditInvoiceFilter = overrides.auditInvoiceFilter ?? auditInvoiceFilter

    const params = new URLSearchParams()
    if (nextFilterMode === 'custom') {
      if (!nextCustomStartDate || !nextCustomEndDate) {
        throw new Error('Select both start and end dates for a custom range')
      }
      if (nextCustomStartDate > nextCustomEndDate) {
        throw new Error('Start date must be on or before end date')
      }
      params.set('start_date', nextCustomStartDate)
      params.set('end_date', nextCustomEndDate)
    } else {
      params.set('days', String(nextSelectedDays))
    }

    if (nextAuditStatusFilter !== 'all') {
      params.set('audit_status', nextAuditStatusFilter)
    }
    if (nextAuditActorFilter !== 'all') {
      params.set('audit_actor', nextAuditActorFilter)
    }
    if (nextAuditInvoiceFilter.trim()) {
      params.set('audit_invoice', nextAuditInvoiceFilter.trim())
    }

    params.set('invoice_page', String(overrides.invoicePage ?? invoicePage))
    params.set('invoice_per_page', String(overrides.invoicePerPage ?? invoicePerPage))
    params.set('audit_page', String(overrides.auditPage ?? auditPage))
    params.set('audit_per_page', String(overrides.auditPerPage ?? auditPerPage))

    return params
  }

  const loadBilling = async (overrides = {}) => {
    try {
      setLoading(true)
      setError('')

      const params = buildBillingParams(overrides)

      const response = await fetch(`/api/admin/billing/overview?${params.toString()}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` },
      })

      if (!response.ok) {
        throw new Error('Failed to load billing overview')
      }

      const payload = await response.json()
      setBillingData({
        ...emptyBillingData,
        ...payload,
        summary: { ...emptyBillingData.summary, ...(payload.summary || {}) },
        usage: { ...emptyBillingData.usage, ...(payload.usage || {}) },
        planDistribution: payload.planDistribution || [],
        recentInvoices: payload.recentInvoices || [],
        recentPlanChanges: payload.recentPlanChanges || [],
        recentStatusChanges: payload.recentStatusChanges || [],
        auditFilters: { ...emptyBillingData.auditFilters, ...(payload.auditFilters || {}) },
        invoicePagination: { ...emptyBillingData.invoicePagination, ...(payload.invoicePagination || {}) },
        auditPagination: { ...emptyBillingData.auditPagination, ...(payload.auditPagination || {}) },
        providerSync: { ...emptyBillingData.providerSync, ...(payload.providerSync || {}) },
      })
    } catch (loadError) {
      console.error('Failed to load admin billing overview:', loadError)
      setError(loadError.message || 'Failed to load billing overview')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (filterMode === 'preset') {
      loadBilling()
    }
  }, [filterMode, selectedDays])

  const usagePercent = billingData.usage.conversionsCapacity > 0
    ? Math.min(100, Math.round((billingData.usage.conversionsUsedThisMonth / billingData.usage.conversionsCapacity) * 100))
    : 0
  const storagePercent = billingData.usage.storageCapacityGb > 0
    ? Math.min(100, Math.round((billingData.usage.storageUsedGb / billingData.usage.storageCapacityGb) * 100))
    : 0
  const auditActors = billingData.auditFilters.availableActors || []

  const formatCurrency = (amount, currency = 'USD') => {
    try {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency,
        maximumFractionDigits: 2,
      }).format(amount || 0)
    } catch {
      return `$${(amount || 0).toFixed(2)}`
    }
  }

  const getStatusStyle = (status) => {
    const normalized = (status || '').toLowerCase()
    if (normalized === 'paid') {
      return { backgroundColor: '#11998e', color: 'white' }
    }
    if (normalized === 'pending') {
      return { backgroundColor: '#dd6b20', color: 'white' }
    }
    if (normalized === 'failed') {
      return { backgroundColor: '#c53030', color: 'white' }
    }
    if (normalized === 'refunded') {
      return { backgroundColor: '#4c51bf', color: 'white' }
    }
    return { backgroundColor: '#718096', color: 'white' }
  }

  const getInvoiceStatusDetails = (invoice) => {
    const details = []
    if (invoice.statusNote) {
      details.push(invoice.statusNote)
    }
    if (invoice.failureCode || invoice.failureReason) {
      details.push(`Failure: ${[invoice.failureCode, invoice.failureReason].filter(Boolean).join(' - ')}`)
    }
    if (invoice.refundAmount != null) {
      details.push(`Refund amount: ${formatCurrency(invoice.refundAmount, invoice.currency)}`)
    }
    if (invoice.gatewayReferenceId) {
      details.push(`Gateway ref: ${invoice.gatewayReferenceId}`)
    }
    if (invoice.processorEventAt) {
      details.push(`Processor event: ${invoice.processorEventAt.replace('T', ' ')}`)
    }
    return details
  }

  const buildStatusUpdatePayload = (invoice, status) => {
    const today = new Date().toISOString().slice(0, 10)

    return {
      status,
      status_note: `Set from admin billing console on ${today}`,
    }
  }

  const openStatusEditor = (invoice, status) => {
    const today = new Date().toISOString().slice(0, 10)
    setStatusEditor({
      isOpen: true,
      invoice,
      status,
      form: {
        status,
        status_note: invoice.statusNote || (status === 'failed'
          ? `Marked failed from admin billing console on ${today}`
          : `Refunded from admin billing console on ${today}`),
        failure_code: invoice.failureCode || 'gateway_retry_exhausted',
        failure_reason: invoice.failureReason || invoice.statusNote || 'Gateway retry exhausted',
        refund_amount: String(invoice.refundAmount ?? invoice.amount ?? 0),
        gateway_reference_id: invoice.gatewayReferenceId || '',
        processor_event_at: invoice.processorEventAt || '',
      },
    })
  }

  const closeStatusEditor = () => {
    setStatusEditor(emptyStatusEditor)
  }

  const updateStatusEditorField = (field, value) => {
    setStatusEditor((current) => ({
      ...current,
      form: {
        ...current.form,
        [field]: value,
      },
    }))
  }

  const updateInvoiceStatus = async (invoice, statusPayload) => {
    try {
      setUpdatingInvoiceId(invoice.id)
      setError('')

      const response = await fetch(`/api/admin/billing/invoices/${invoice.id}/status`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(statusPayload),
      })

      const payload = await response.json()
      if (!response.ok) {
        throw new Error(payload.error || 'Failed to update invoice status')
      }

      setBillingData((current) => ({
        ...current,
        recentInvoices: current.recentInvoices.map((invoice) => (
          invoice.id === payload.invoice.id ? payload.invoice : invoice
        )),
      }))
      await loadBilling()
    } catch (updateError) {
      console.error('Failed to update invoice status:', updateError)
      setError(updateError.message || 'Failed to update invoice status')
    } finally {
      setUpdatingInvoiceId(null)
    }
  }

  const submitStatusEditor = async () => {
    if (!statusEditor.invoice) {
      return
    }

    await updateInvoiceStatus(statusEditor.invoice, statusEditor.form)
    closeStatusEditor()
  }

  const downloadInvoice = async (invoiceId, invoiceNumber) => {
    try {
      setDownloadingInvoiceId(invoiceId)

      const response = await fetch(`/api/admin/billing/invoices/${invoiceId}/download`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` },
      })

      if (!response.ok) {
        throw new Error('Failed to download invoice')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${invoiceNumber || 'invoice'}.txt`
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (downloadError) {
      console.error('Failed to download admin invoice:', downloadError)
      setError(downloadError.message || 'Failed to download invoice')
    } finally {
      setDownloadingInvoiceId(null)
    }
  }

  const exportCsv = (filename, headers, rows) => {
    const escapeCsv = (value) => {
      const normalized = value == null ? '' : String(value)
      return `"${normalized.replace(/"/g, '""')}"`
    }

    const csvContent = [
      headers.map(escapeCsv).join(','),
      ...rows.map((row) => row.map(escapeCsv).join(',')),
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  }

  const exportInvoicesCsv = () => {
    const fileSuffix = billingData.summary.isCustomRange && billingData.summary.periodStart && billingData.summary.periodEnd
      ? `${billingData.summary.periodStart}_to_${billingData.summary.periodEnd}`
      : `${billingData.summary.periodDays}d`

    exportCsv(
      `billing-invoices-${fileSuffix}.csv`,
      ['Invoice Number', 'Username', 'Email', 'Plan', 'Amount', 'Currency', 'Status', 'Status Note', 'Failure Code', 'Failure Reason', 'Refund Amount', 'Gateway Reference', 'Processor Event At', 'Issued At', 'Period Start', 'Period End', 'Description'],
      billingData.recentInvoices.map((invoice) => ([
        invoice.invoiceNumber,
        invoice.user.username,
        invoice.user.email,
        invoice.plan,
        invoice.amount,
        invoice.currency,
        invoice.status,
        invoice.statusNote || '',
        invoice.failureCode || '',
        invoice.failureReason || '',
        invoice.refundAmount ?? '',
        invoice.gatewayReferenceId || '',
        invoice.processorEventAt ? invoice.processorEventAt.replace('T', ' ') : '',
        invoice.issuedAt || '',
        invoice.periodStart || '',
        invoice.periodEnd || '',
        invoice.description,
      ])),
    )
  }

  const exportPlanChangesCsv = () => {
    const fileSuffix = billingData.summary.isCustomRange && billingData.summary.periodStart && billingData.summary.periodEnd
      ? `${billingData.summary.periodStart}_to_${billingData.summary.periodEnd}`
      : `${billingData.summary.periodDays}d`

    exportCsv(
      `billing-plan-changes-${fileSuffix}.csv`,
      ['Changed At', 'Username', 'Email', 'From Plan', 'To Plan', 'Invoice Number', 'Amount', 'Currency'],
      billingData.recentPlanChanges.map((change) => ([
        change.changedAt || '',
        change.user.username,
        change.user.email,
        change.fromPlan,
        change.toPlan,
        change.invoiceNumber,
        change.amount,
        change.currency,
      ])),
    )
  }

  const applyAuditFilters = async () => {
    setAuditPage(1)
    await loadBilling({ auditPage: 1 })
  }

  const clearAuditFilters = async () => {
    setAuditStatusFilter('all')
    setAuditActorFilter('all')
    setAuditInvoiceFilter('')
    setAuditPage(1)
    await loadBilling({
      auditStatusFilter: 'all',
      auditActorFilter: 'all',
      auditInvoiceFilter: '',
      auditPage: 1,
    })
  }

  const changeInvoicePage = async (nextPage) => {
    setInvoicePage(nextPage)
    await loadBilling({ invoicePage: nextPage })
  }

  const changeAuditPage = async (nextPage) => {
    setAuditPage(nextPage)
    await loadBilling({ auditPage: nextPage })
  }

  const changeInvoicePerPage = async (nextPerPage) => {
    setInvoicePerPage(nextPerPage)
    setInvoicePage(1)
    await loadBilling({ invoicePerPage: nextPerPage, invoicePage: 1 })
  }

  const changeAuditPerPage = async (nextPerPage) => {
    setAuditPerPage(nextPerPage)
    setAuditPage(1)
    await loadBilling({ auditPerPage: nextPerPage, auditPage: 1 })
  }

  const exportAuditCsv = async () => {
    try {
      setExportingAudit(true)
      setError('')

      const response = await fetch(`/api/admin/billing/audit/export?${buildBillingParams().toString()}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` },
      })

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}))
        throw new Error(payload.error || 'Failed to export billing audit history')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const downloadName = response.headers.get('Content-Disposition')?.match(/filename=\"?([^\";]+)\"?/)?.[1] || 'billing-audit.csv'
      const link = document.createElement('a')
      link.href = url
      link.download = downloadName
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (exportError) {
      console.error('Failed to export billing audit history:', exportError)
      setError(exportError.message || 'Failed to export billing audit history')
    } finally {
      setExportingAudit(false)
    }
  }

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="💳" size={24} /> Usage & Billing</h2>
      <p className="section-subtitle">Persisted invoice activity, plan-change history, and platform billing usage</p>

      {!loading && billingData.summary.periodStart && billingData.summary.periodEnd && (
        <p className="section-subtitle" style={{ marginTop: '-8px' }}>
          Active range: {billingData.summary.periodStart} to {billingData.summary.periodEnd}
        </p>
      )}

      {error && (
        <div className="no-data" style={{ marginBottom: '20px', border: '1px solid #fed7d7', background: '#fff5f5', color: '#c53030' }}>
          <p>{error}</p>
        </div>
      )}

      <div className="admin-stats-grid">
        <div className="admin-stat-card metric-info">
          <UniversalIcon icon="📊" size={32} />
          <div className="stat-content">
            <h3>MRR</h3>
            <p className="stat-value">{loading ? '...' : formatCurrency(billingData.summary.monthlyRecurringRevenue)}</p>
            <p className="stat-detail">{loading ? 'Loading' : `${billingData.summary.activePaidSubscriptions} active paid subscriptions`}</p>
          </div>
        </div>

        <div className="admin-stat-card metric-primary">
          <UniversalIcon icon="📋" size={32} />
          <div className="stat-content">
            <h3>Invoices ({billingData.summary.periodDays}d)</h3>
            <p className="stat-value">{loading ? '...' : billingData.summary.invoicesDuringPeriod}</p>
            <p className="stat-detail">{loading ? 'Loading' : `${billingData.summary.totalInvoices} total persisted invoices`}</p>
          </div>
        </div>

        <div className="admin-stat-card metric-success">
          <UniversalIcon icon="💾" size={32} />
          <div className="stat-content">
            <h3>Collected ({billingData.summary.periodDays}d)</h3>
            <p className="stat-value">{loading ? '...' : formatCurrency(billingData.summary.billedDuringPeriod)}</p>
            <p className="stat-detail">{loading ? 'Loading' : `${billingData.summary.paidInvoices} paid / ${billingData.summary.pendingInvoices} pending`}</p>
          </div>
        </div>

        <div className="admin-stat-card metric-revenue">
          <UniversalIcon icon="📅" size={32} />
          <div className="stat-content">
            <h3>Plan Changes</h3>
            <p className="stat-value">{loading ? '...' : billingData.summary.planChangesDuringPeriod}</p>
            <p className="stat-detail">{loading ? 'Loading' : (billingData.summary.nextRenewalDate || 'No renewal scheduled')}</p>
          </div>
        </div>
        <div className="admin-stat-card metric-revenue">
          <UniversalIcon icon="⚠️" size={32} />
          <div className="stat-content">
            <h3>Invoice Exceptions</h3>
            <p className="stat-value">{loading ? '...' : (billingData.summary.failedInvoices + billingData.summary.refundedInvoices)}</p>
            <p className="stat-detail">{loading ? 'Loading' : `${billingData.summary.failedInvoices} failed / ${billingData.summary.refundedInvoices} refunded`}</p>
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
            <p>
              {loading ? 'Loading...' : `${billingData.usage.conversionsUsedThisMonth.toLocaleString()} / ${billingData.usage.conversionsCapacity.toLocaleString()} conversions`}
            </p>
          </div>
          <div className="billing-card">
            <h4>Storage Usage</h4>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${storagePercent}%` }}></div>
            </div>
            <p>
              {loading ? 'Loading...' : `${billingData.usage.storageUsedGb} / ${billingData.usage.storageCapacityGb} GB`}
            </p>
          </div>
          <div className="billing-card">
            <h4>Plan Mix</h4>
            {loading ? (
              <p>Loading...</p>
            ) : billingData.planDistribution.length > 0 ? (
              billingData.planDistribution.map((item) => (
                <p key={item.plan}>{item.plan}: {item.count}</p>
              ))
            ) : (
              <p>No active subscriptions yet</p>
            )}
          </div>
        </div>

        <div className="action-buttons">
          <label style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', color: '#4a5568' }}>
            <span>Mode</span>
            <select
              value={filterMode}
              onChange={(event) => setFilterMode(event.target.value)}
              disabled={loading}
              style={{ padding: '10px 12px', borderRadius: '8px', border: '1px solid #d2d6dc', background: 'white' }}
            >
              <option value="preset">Preset range</option>
              <option value="custom">Custom dates</option>
            </select>
          </label>
          {filterMode === 'preset' ? (
            <label style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', color: '#4a5568' }}>
              <span>Range</span>
              <select
                value={selectedDays}
                onChange={(event) => setSelectedDays(Number(event.target.value))}
                disabled={loading}
                style={{ padding: '10px 12px', borderRadius: '8px', border: '1px solid #d2d6dc', background: 'white' }}
              >
                <option value={7}>Last 7 days</option>
                <option value={30}>Last 30 days</option>
                <option value={90}>Last 90 days</option>
                <option value={365}>Last 12 months</option>
              </select>
            </label>
          ) : (
            <>
              <label style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', color: '#4a5568' }}>
                <span>Start</span>
                <input
                  type="date"
                  value={customStartDate}
                  onChange={(event) => setCustomStartDate(event.target.value)}
                  disabled={loading}
                  style={{ padding: '10px 12px', borderRadius: '8px', border: '1px solid #d2d6dc', background: 'white' }}
                />
              </label>
              <label style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', color: '#4a5568' }}>
                <span>End</span>
                <input
                  type="date"
                  value={customEndDate}
                  onChange={(event) => setCustomEndDate(event.target.value)}
                  disabled={loading}
                  style={{ padding: '10px 12px', borderRadius: '8px', border: '1px solid #d2d6dc', background: 'white' }}
                />
              </label>
            </>
          )}
          <button className="action-button secondary" onClick={loadBilling} disabled={loading}>
            {loading ? 'Refreshing...' : filterMode === 'custom' ? 'Apply Custom Range' : 'Refresh Billing Data'}
          </button>
          <button className="action-button secondary" onClick={exportInvoicesCsv} disabled={loading || billingData.recentInvoices.length === 0}>
            Export Invoices CSV
          </button>
          <button className="action-button secondary" onClick={exportPlanChangesCsv} disabled={loading || billingData.recentPlanChanges.length === 0}>
            Export Plan Changes CSV
          </button>
        </div>

        <div className="billing-info" style={{ marginTop: '20px' }}>
          <div className="billing-card" style={{ minWidth: '280px' }}>
            <h4>Provider Sync Endpoint</h4>
            <p style={{ wordBreak: 'break-all', marginBottom: '8px' }}>{billingData.providerSync.endpoint || 'Unavailable'}</p>
            <p style={{ color: billingData.providerSync.secretConfigured ? '#166534' : '#b45309', marginBottom: '6px' }}>
              {billingData.providerSync.secretConfigured ? 'Webhook secret configured' : 'Set BILLING_PROVIDER_WEBHOOK_SECRET to enable signed provider ingestion'}
            </p>
            <p style={{ marginBottom: 0 }}>Signature header: {billingData.providerSync.signatureHeader}</p>
          </div>
          <div className="billing-card" style={{ minWidth: '280px' }}>
            <h4>Supported Provider Events</h4>
            {billingData.providerSync.supportedProviders.length > 0 ? (
              <p style={{ color: '#4a5568' }}>Providers: {billingData.providerSync.supportedProviders.join(', ')}</p>
            ) : null}
            {billingData.providerSync.supportedEventTypes.length > 0 ? (
              billingData.providerSync.supportedEventTypes.slice(0, 6).map((eventType) => (
                <p key={eventType}>{eventType}</p>
              ))
            ) : (
              <p>No provider events configured yet</p>
            )}
            {billingData.providerSync.stripeMetadataKeys.length > 0 ? (
              <p style={{ color: '#4a5568', marginBottom: 0 }}>
                Stripe metadata keys: {billingData.providerSync.stripeMetadataKeys.join(', ')}
              </p>
            ) : null}
          </div>
        </div>

        <h3 style={{ marginTop: '28px' }}>Recent Invoices</h3>
        <div className="action-buttons" style={{ marginBottom: '12px' }}>
          <label style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', color: '#4a5568' }}>
            <span>Rows</span>
            <select
              value={invoicePerPage}
              onChange={(event) => changeInvoicePerPage(Number(event.target.value))}
              disabled={loading}
              style={{ padding: '10px 12px', borderRadius: '8px', border: '1px solid #d2d6dc', background: 'white' }}
            >
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
            </select>
          </label>
          <span style={{ color: '#4a5568' }}>
            {loading ? 'Loading invoice page...' : `Page ${billingData.invoicePagination.currentPage} of ${Math.max(billingData.invoicePagination.pages, 1)} · ${billingData.invoicePagination.total} invoices`}
          </span>
          <button className="action-button secondary" onClick={() => changeInvoicePage(Math.max(1, invoicePage - 1))} disabled={loading || !billingData.invoicePagination.hasPrev}>
            Previous
          </button>
          <button className="action-button secondary" onClick={() => changeInvoicePage(invoicePage + 1)} disabled={loading || !billingData.invoicePagination.hasNext}>
            Next
          </button>
        </div>
        <div className="jobs-table-wrapper">
          <table className="jobs-table">
            <thead>
              <tr>
                <th>Invoice</th>
                <th>User</th>
                <th>Plan</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Issued</th>
                <th>Description</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="8">Loading invoices...</td>
                </tr>
              ) : billingData.recentInvoices.length > 0 ? (
                billingData.recentInvoices.map((invoice) => (
                  <tr key={invoice.id}>
                    <td className="job-id"><code>{invoice.invoiceNumber}</code></td>
                    <td>
                      <strong>{invoice.user.username}</strong>
                      <div style={{ color: '#718096', fontSize: '12px' }}>{invoice.user.email}</div>
                    </td>
                    <td>{invoice.plan}</td>
                    <td>{formatCurrency(invoice.amount, invoice.currency)}</td>
                    <td>
                      <span className="status-badge" style={getStatusStyle(invoice.status)}>{invoice.status}</span>
                    </td>
                    <td>{invoice.issuedAt || 'N/A'}</td>
                    <td>
                      {invoice.description}
                      {getInvoiceStatusDetails(invoice).map((detail) => (
                        <div key={detail} style={{ color: '#718096', fontSize: '12px', marginTop: '4px' }}>{detail}</div>
                      ))}
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                        <button
                          className="action-btn logs"
                          onClick={() => downloadInvoice(invoice.id, invoice.invoiceNumber)}
                          disabled={downloadingInvoiceId === invoice.id || updatingInvoiceId === invoice.id}
                          title="Download invoice"
                        >
                          <UniversalIcon icon="⬇" size={16} />
                        </button>
                        <button
                          className="action-btn"
                          style={{ background: '#11998e', color: 'white' }}
                          onClick={() => updateInvoiceStatus(invoice, buildStatusUpdatePayload(invoice, 'paid'))}
                          disabled={invoice.status === 'paid' || updatingInvoiceId === invoice.id}
                          title="Mark paid"
                        >
                          <UniversalIcon icon="✓" size={16} />
                        </button>
                        <button
                          className="action-btn"
                          style={{ background: '#dd6b20', color: 'white' }}
                          onClick={() => updateInvoiceStatus(invoice, buildStatusUpdatePayload(invoice, 'pending'))}
                          disabled={invoice.status === 'pending' || updatingInvoiceId === invoice.id}
                          title="Mark pending"
                        >
                          <UniversalIcon icon="…" size={16} />
                        </button>
                        <button
                          className="action-btn cancel"
                          onClick={() => openStatusEditor(invoice, 'failed')}
                          disabled={invoice.status === 'failed' || updatingInvoiceId === invoice.id}
                          title="Mark failed"
                        >
                          <UniversalIcon icon="✕" size={16} />
                        </button>
                        <button
                          className="action-btn"
                          style={{ background: '#4c51bf', color: 'white' }}
                          onClick={() => openStatusEditor(invoice, 'refunded')}
                          disabled={invoice.status === 'refunded' || updatingInvoiceId === invoice.id}
                          title="Mark refunded"
                        >
                          <UniversalIcon icon="↺" size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="8">No invoices have been recorded yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <h3 style={{ marginTop: '28px' }}>Recent Plan Changes</h3>
        <div className="jobs-table-wrapper">
          <table className="jobs-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Changed</th>
                <th>From</th>
                <th>To</th>
                <th>Invoice</th>
                <th>Amount</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="6">Loading plan changes...</td>
                </tr>
              ) : billingData.recentPlanChanges.length > 0 ? (
                billingData.recentPlanChanges.map((change) => (
                  <tr key={change.id}>
                    <td>
                      <strong>{change.user.username}</strong>
                      <div style={{ color: '#718096', fontSize: '12px' }}>{change.user.email}</div>
                    </td>
                    <td>{change.changedAt || 'N/A'}</td>
                    <td>{change.fromPlan}</td>
                    <td>{change.toPlan}</td>
                    <td className="job-id"><code>{change.invoiceNumber}</code></td>
                    <td>{formatCurrency(change.amount, change.currency)}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6">No plan changes recorded in this period.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <h3 style={{ marginTop: '28px' }}>Recent Status Changes</h3>
        <p className="section-subtitle" style={{ marginTop: '-4px', marginBottom: '12px' }}>
          {loading ? 'Loading audit history...' : `${billingData.auditFilters.matchingCount} matching status changes in the selected period`}
        </p>
        <div className="action-buttons" style={{ marginBottom: '12px' }}>
          <label style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', color: '#4a5568' }}>
            <span>Status</span>
            <select
              value={auditStatusFilter}
              onChange={(event) => setAuditStatusFilter(event.target.value)}
              style={{ padding: '10px 12px', borderRadius: '8px', border: '1px solid #d2d6dc', background: 'white' }}
            >
              <option value="all">All statuses</option>
              <option value="paid">Paid</option>
              <option value="pending">Pending</option>
              <option value="failed">Failed</option>
              <option value="refunded">Refunded</option>
            </select>
          </label>
          <label style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', color: '#4a5568' }}>
            <span>Admin</span>
            <select
              value={auditActorFilter}
              onChange={(event) => setAuditActorFilter(event.target.value)}
              style={{ padding: '10px 12px', borderRadius: '8px', border: '1px solid #d2d6dc', background: 'white' }}
            >
              <option value="all">All admins</option>
              {auditActors.map((actor) => (
                <option key={actor} value={actor}>{actor}</option>
              ))}
            </select>
          </label>
          <label style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', color: '#4a5568' }}>
            <span>Invoice</span>
            <input
              type="text"
              value={auditInvoiceFilter}
              onChange={(event) => setAuditInvoiceFilter(event.target.value)}
              placeholder="INV-202603..."
              style={{ padding: '10px 12px', borderRadius: '8px', border: '1px solid #d2d6dc', background: 'white' }}
            />
          </label>
          <button className="action-button secondary" onClick={applyAuditFilters} disabled={loading}>
            Apply Audit Filters
          </button>
          <button className="action-button secondary" onClick={clearAuditFilters} disabled={loading && !exportingAudit}>
            Clear Filters
          </button>
          <button className="action-button secondary" onClick={exportAuditCsv} disabled={loading || exportingAudit}>
            {exportingAudit ? 'Exporting Audit CSV...' : 'Export Audit CSV'}
          </button>
          <label style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', color: '#4a5568' }}>
            <span>Rows</span>
            <select
              value={auditPerPage}
              onChange={(event) => changeAuditPerPage(Number(event.target.value))}
              disabled={loading}
              style={{ padding: '10px 12px', borderRadius: '8px', border: '1px solid #d2d6dc', background: 'white' }}
            >
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </label>
        </div>
        <div className="jobs-table-wrapper">
          <table className="jobs-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Invoice</th>
                <th>Admin</th>
                <th>From</th>
                <th>To</th>
                <th>Note</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="6">Loading status changes...</td>
                </tr>
              ) : billingData.recentStatusChanges.length > 0 ? (
                billingData.recentStatusChanges.map((entry) => (
                  <tr key={entry.id}>
                    <td>{entry.createdAt || 'N/A'}</td>
                    <td className="job-id"><code>{entry.invoiceNumber || `#${entry.invoiceId}`}</code></td>
                    <td>
                      <strong>{entry.actor.username}</strong>
                      <div style={{ color: '#718096', fontSize: '12px' }}>{entry.actor.email}</div>
                    </td>
                    <td>{entry.fromStatus || 'N/A'}</td>
                    <td>
                      <span className="status-badge" style={getStatusStyle(entry.toStatus)}>{entry.toStatus}</span>
                    </td>
                    <td>{entry.statusNote || 'No note provided'}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6">No invoice status changes match the current server-side filters.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="action-buttons" style={{ marginTop: '12px' }}>
          <span style={{ color: '#4a5568' }}>
            {loading ? 'Loading audit page...' : `Page ${billingData.auditPagination.currentPage} of ${Math.max(billingData.auditPagination.pages, 1)} · ${billingData.auditPagination.total} matching entries`}
          </span>
          <button className="action-button secondary" onClick={() => changeAuditPage(Math.max(1, auditPage - 1))} disabled={loading || !billingData.auditPagination.hasPrev}>
            Previous
          </button>
          <button className="action-button secondary" onClick={() => changeAuditPage(auditPage + 1)} disabled={loading || !billingData.auditPagination.hasNext}>
            Next
          </button>
        </div>
      </div>

      {statusEditor.isOpen && statusEditor.invoice ? (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(15, 23, 42, 0.55)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '24px', zIndex: 1200 }}>
          <div style={{ width: '100%', maxWidth: '720px', background: 'white', borderRadius: '16px', padding: '24px', boxShadow: '0 24px 80px rgba(15, 23, 42, 0.28)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: '16px', alignItems: 'flex-start', marginBottom: '18px' }}>
              <div>
                <h3 style={{ margin: 0 }}>Update {statusEditor.status} status</h3>
                <p className="section-subtitle" style={{ marginTop: '6px', marginBottom: 0 }}>
                  {statusEditor.invoice.invoiceNumber} for {statusEditor.invoice.user.username}
                </p>
              </div>
              <button className="action-button secondary" onClick={closeStatusEditor}>Close</button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: '16px' }}>
              <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', color: '#334155' }}>
                <span>Admin note</span>
                <textarea
                  value={statusEditor.form.status_note}
                  onChange={(event) => updateStatusEditorField('status_note', event.target.value)}
                  rows={3}
                  style={{ padding: '12px', borderRadius: '10px', border: '1px solid #d2d6dc', resize: 'vertical' }}
                />
              </label>

              {statusEditor.status === 'failed' ? (
                <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', color: '#334155' }}>
                  <span>Failure reason</span>
                  <textarea
                    value={statusEditor.form.failure_reason}
                    onChange={(event) => updateStatusEditorField('failure_reason', event.target.value)}
                    rows={3}
                    style={{ padding: '12px', borderRadius: '10px', border: '1px solid #d2d6dc', resize: 'vertical' }}
                  />
                </label>
              ) : (
                <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', color: '#334155' }}>
                  <span>Refund amount</span>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={statusEditor.form.refund_amount}
                    onChange={(event) => updateStatusEditorField('refund_amount', event.target.value)}
                    style={{ padding: '12px', borderRadius: '10px', border: '1px solid #d2d6dc' }}
                  />
                </label>
              )}

              {statusEditor.status === 'failed' ? (
                <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', color: '#334155' }}>
                  <span>Failure code</span>
                  <input
                    type="text"
                    value={statusEditor.form.failure_code}
                    onChange={(event) => updateStatusEditorField('failure_code', event.target.value)}
                    style={{ padding: '12px', borderRadius: '10px', border: '1px solid #d2d6dc' }}
                  />
                </label>
              ) : (
                <div />
              )}

              <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', color: '#334155' }}>
                <span>Gateway reference</span>
                <input
                  type="text"
                  value={statusEditor.form.gateway_reference_id}
                  onChange={(event) => updateStatusEditorField('gateway_reference_id', event.target.value)}
                  placeholder="ch_123... or evt_456..."
                  style={{ padding: '12px', borderRadius: '10px', border: '1px solid #d2d6dc' }}
                />
              </label>

              <label style={{ display: 'flex', flexDirection: 'column', gap: '6px', color: '#334155' }}>
                <span>Processor event time</span>
                <input
                  type="datetime-local"
                  value={statusEditor.form.processor_event_at}
                  onChange={(event) => updateStatusEditorField('processor_event_at', event.target.value)}
                  style={{ padding: '12px', borderRadius: '10px', border: '1px solid #d2d6dc' }}
                />
              </label>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '20px' }}>
              <button className="action-button secondary" onClick={closeStatusEditor}>Cancel</button>
              <button className="action-button primary" onClick={submitStatusEditor} disabled={updatingInvoiceId === statusEditor.invoice.id}>
                {updatingInvoiceId === statusEditor.invoice.id ? 'Saving...' : 'Save Status Update'}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  )
}

export default UsageBilling
