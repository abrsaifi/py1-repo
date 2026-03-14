import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add JWT token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  
  return config
})

// Handle errors silently for health checks
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Silently handle health check failures without throwing to prevent console errors
    if (error.config?.url === '/health' || error.config?.url?.includes('/health')) {
      // Return a rejected promise but the caller will handle it in their try/catch
      return Promise.reject(error)
    }
    // For other errors, pass them through
    return Promise.reject(error)
  }
)

// Also add request error handler to suppress health check warnings
api.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
)

// Metrics API
export const metricsAPI = {
  // System metrics
  getSystemMetrics: (params) => api.get('/api/metrics/system', { params }),
  getServiceMetrics: (params) => api.get('/api/metrics/service', { params }),
  getActivityMetrics: (params) => api.get('/api/metrics/activity', { params }),
  getBusinessMetrics: (params) => api.get('/api/metrics/business', { params }),
  
  // Metric details
  getMetricsOverTime: (metricId, params) => api.get(`/api/metrics/${metricId}/over-time`, { params }),
  getMetricComparison: (params) => api.get('/api/metrics/comparison', { params }),
  getMetricsBreakdown: (metricId, params) => api.get(`/api/metrics/${metricId}/breakdown`, { params }),
}

// Dashboards API
export const dashboardsAPI = {
  list: (params) => api.get('/api/dashboards', { params }),
  create: (data) => api.post('/api/dashboards', data),
  get: (id) => api.get(`/api/dashboards/${id}`),
  update: (id, data) => api.put(`/api/dashboards/${id}`, data),
  delete: (id) => api.delete(`/api/dashboards/${id}`),
  
  // Widget management
  addWidget: (dashboardId, data) => api.post(`/api/dashboards/${dashboardId}/widgets`, data),
  updateWidget: (dashboardId, widgetId, data) => api.put(`/api/dashboards/${dashboardId}/widgets/${widgetId}`, data),
  removeWidget: (dashboardId, widgetId) => api.delete(`/api/dashboards/${dashboardId}/widgets/${widgetId}`),
  
  // Sharing
  share: (dashboardId, data) => api.post(`/api/dashboards/${dashboardId}/share`, data),
  getShared: () => api.get('/api/dashboards/shared/list'),
}

// Reports API
export const reportsAPI = {
  list: (params) => api.get('/api/reports', { params }),
  create: (data) => api.post('/api/reports', data),
  get: (id) => api.get(`/api/reports/${id}`),
  update: (id, data) => api.put(`/api/reports/${id}`, data),
  delete: (id) => api.delete(`/api/reports/${id}`),
  
  // Report scheduling
  schedule: (reportId, data) => api.post(`/api/reports/${reportId}/schedule`, data),
  updateSchedule: (reportId, data) => api.put(`/api/reports/${reportId}/schedule`, data),
  
  // Report generation
  generate: (reportId) => api.post(`/api/reports/${reportId}/generate`),
  getHistory: (reportId, params) => api.get(`/api/reports/${reportId}/history`, { params }),
}

// Alerts API
export const alertsAPI = {
  list: (params) => api.get('/api/alerts', { params }),
  create: (data) => api.post('/api/alerts', data),
  get: (id) => api.get(`/api/alerts/${id}`),
  update: (id, data) => api.put(`/api/alerts/${id}`, data),
  delete: (id) => api.delete(`/api/alerts/${id}`),
  
  // Alert events
  getEvents: (alertId, params) => api.get(`/api/alerts/${alertId}/events`, { params }),
  clearEvents: (alertId) => api.delete(`/api/alerts/${alertId}/events`),
  
  // Anomaly detection
  detectAnomalies: (data) => api.post('/api/alerts/anomalies/detect', data),
}

// Queries API
export const queriesAPI = {
  list: (params) => api.get('/api/queries', { params }),
  create: (data) => api.post('/api/queries', data),
  get: (id) => api.get(`/api/queries/${id}`),
  update: (id, data) => api.put(`/api/queries/${id}`, data),
  delete: (id) => api.delete(`/api/queries/${id}`),
  
  // Query execution
  execute: (queryId) => api.post(`/api/queries/${queryId}/execute`),
  getResults: (queryId, params) => api.get(`/api/queries/${queryId}/results`, { params }),
  
  // Query templates
  getTemplates: () => api.get('/api/queries/templates/list'),
  createTemplate: (data) => api.post('/api/queries/templates', data),
}

// Custom Metrics API
export const customMetricsAPI = {
  list: (params) => api.get('/api/custom-metrics', { params }),
  create: (data) => api.post('/api/custom-metrics', data),
  get: (id) => api.get(`/api/custom-metrics/${id}`),
  update: (id, data) => api.put(`/api/custom-metrics/${id}`, data),
  delete: (id) => api.delete(`/api/custom-metrics/${id}`),
  
  // Formula calculation
  calculate: (metricId) => api.post(`/api/custom-metrics/${metricId}/calculate`),
  getCalculationHistory: (metricId, params) => api.get(`/api/custom-metrics/${metricId}/history`, { params }),
}

// Export API
export const exportsAPI = {
  exportMetrics: (data) => api.post('/api/export/metrics', data, { responseType: 'blob' }),
  exportDashboards: (data) => api.post('/api/export/dashboards', data, { responseType: 'blob' }),
  exportReports: (data) => api.post('/api/export/reports', data, { responseType: 'blob' }),
}

// Health API
export const healthAPI = {
  getHealth: () => {
    // Make the request but suppress error logging in console
    return api.get('/api/healthz').catch((error) => {
      // Silently reject - caller's try/catch will handle it
      return Promise.reject(error)
    })
  },
  getMetrics: () => api.get('/api/health/metrics'),
}

// ========== PHASE 14: ANALYTICS API (Phase 12) ==========
export const analyticsAPI = {
  // Dashboard
  getDashboard: () => api.get('/api/analytics/dashboard'),
  
  // Statistical analysis
  getStatistics: (dataset) => api.post('/api/analytics/statistics', { dataset }),
  
  // Forecasting
  getForecast: (metric, daysAhead) => api.post('/api/analytics/forecast', { 
    metric, 
    days_ahead: daysAhead 
  }),
  
  // Visualizations
  getHeatmapData: () => api.get('/api/analytics/heatmap'),
  getScatterData: () => api.get('/api/analytics/scatter'),
  getTreemapData: () => api.get('/api/analytics/treemap'),
  getSankeyData: () => api.get('/api/analytics/sankey'),
  getFunnelData: () => api.get('/api/analytics/funnel'),
  getRadarData: () => api.get('/api/analytics/radar'),
  
  // Reports
  listReports: () => api.get('/api/reports'),
  createReport: (data) => api.post('/api/reports', data),
  getReport: (reportId) => api.get(`/api/reports/${reportId}`),
  updateReport: (reportId, data) => api.put(`/api/reports/${reportId}`, data),
  deleteReport: (reportId) => api.delete(`/api/reports/${reportId}`),
  exportReport: (reportId, format) => api.post(`/api/reports/${reportId}/export`, { format }),
}

// ========== MONITORING API ==========
export const monitoringAPI = {
  getHealth: () => api.get('/api/health'),
  getMetrics: () => api.get('/api/monitoring/metrics'),
  getSystemHealth: () => api.get('/api/monitoring/health'),
}

export default api
