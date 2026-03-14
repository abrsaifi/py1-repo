import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const cmsAPI = {
  listPages: () => api.get('/api/cms/pages'),
  getPage: (pageId) => api.get(`/api/cms/pages/${pageId}`),
  createPage: (data) => api.post('/api/cms/pages', data),
  updatePage: (pageId, data) => api.put(`/api/cms/pages/${pageId}`, data),
  deletePage: (pageId) => api.delete(`/api/cms/pages/${pageId}`),
  getPublicPage: (slug) => api.get(`/api/cms/pages/slug/${slug}`),
  listWidgetTypes: () => api.get('/api/cms/widgets/types'),
}

export default cmsAPI
