import api from './api'

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