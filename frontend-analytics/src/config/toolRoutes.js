import React from 'react'
import toolCatalogData from './toolCatalog.json'

const CATEGORY_LABELS = {
  all: 'All Tools',
  pdf: 'PDF Tools',
  image: 'Images',
  document: 'Documents',
  data: 'Data & Sheets',
  premium: 'Premium',
  archive: 'Archives',
  media: 'Media',
  text: 'Text & Data',
}

const CATEGORY_ORDER = ['all', 'pdf', 'image', 'document', 'data', 'premium', 'archive', 'media', 'text']

export const TOOL_CATALOG = toolCatalogData.map((tool) => ({
  ...tool,
  name: tool.title,
  from: tool.from_format,
  to: tool.to_format,
  keyFeatures: tool.key_features || [],
  relatedTools: tool.related_tools || [],
  qualityIndicators: tool.quality_indicators || [],
  isPremium: Boolean(tool.is_premium),
}))

export const TOOL_ROUTES = TOOL_CATALOG.map(({ slug, title, path, category, icon }) => ({
  slug,
  title,
  path,
  category,
  icon,
}))

export { CATEGORY_LABELS, CATEGORY_ORDER }

export const getAllCatalogTools = () => TOOL_CATALOG

export const getAllToolRoutes = () => TOOL_ROUTES

export const getCatalogTool = (slug) => TOOL_CATALOG.find((tool) => tool.slug === slug)

export const getToolRoute = (slug) => TOOL_ROUTES.find((route) => route.slug === slug)

export const getToolsByCategory = (category) => {
  if (!category || category === 'all') {
    return TOOL_CATALOG
  }
  return TOOL_CATALOG.filter((tool) => tool.category === category)
}

export const getToolCategories = () => {
  const categories = new Set(TOOL_CATALOG.map((tool) => tool.category))
  return CATEGORY_ORDER.filter((category) => category === 'all' || categories.has(category))
}

export const generateToolSitemapEntries = (baseUrl = 'http://localhost:3000') => {
  return TOOL_ROUTES.map((route) => ({
    url: `${baseUrl}${route.path}`,
    lastmod: new Date().toISOString(),
    changefreq: 'monthly',
    priority: 0.8,
  }))
}

export const generateToolBreadcrumb = (toolSlug, baseUrl = 'http://localhost:3000') => {
  const tool = getToolRoute(toolSlug)
  if (!tool) return null

  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      {
        '@type': 'ListItem',
        position: 1,
        name: 'Home',
        item: baseUrl,
      },
      {
        '@type': 'ListItem',
        position: 2,
        name: tool.title,
        item: `${baseUrl}${tool.path}`,
      },
    ],
  }
}

export const createToolRoutes = (ToolComponent) => {
  return TOOL_ROUTES.map((route) => ({
    path: route.path,
    element: React.createElement(ToolComponent, { key: route.slug }),
  }))
}

export default TOOL_ROUTES
