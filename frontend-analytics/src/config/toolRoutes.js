/**
 * Tool Routes Configuration
 * Auto-generated routes for all converter tools
 * Access tool pages at: /tools/[tool-slug]
 */

export const TOOL_ROUTES = [
  // Image Conversion Tools
  {
    slug: 'jpg-to-png',
    title: 'JPG to PNG',
    path: '/tools/jpg-to-png',
    category: 'image',
    icon: '🖼️'
  },
  {
    slug: 'png-to-jpg',
    title: 'PNG to JPG',
    path: '/tools/png-to-jpg',
    category: 'image',
    icon: '🖼️'
  },
  {
    slug: 'webp-to-png',
    title: 'WebP to PNG',
    path: '/tools/webp-to-png',
    category: 'image',
    icon: '🖼️'
  },
  {
    slug: 'image-to-pdf',
    title: 'Image to PDF',
    path: '/tools/image-to-pdf',
    category: 'image',
    icon: '📸'
  },
  // Document Conversion Tools
  {
    slug: 'pdf-to-docx',
    title: 'PDF to DOCX',
    path: '/tools/pdf-to-docx',
    category: 'document',
    icon: '📄'
  },
  {
    slug: 'docx-to-pdf',
    title: 'DOCX to PDF',
    path: '/tools/docx-to-pdf',
    category: 'document',
    icon: '📄'
  },
  {
    slug: 'pdf-to-excel',
    title: 'PDF to Excel',
    path: '/tools/pdf-to-excel',
    category: 'document',
    icon: '📊'
  },
  {
    slug: 'excel-to-pdf',
    title: 'Excel to PDF',
    path: '/tools/excel-to-pdf',
    category: 'document',
    icon: '📊'
  },
  {
    slug: 'pdf-to-pptx',
    title: 'PDF to PowerPoint',
    path: '/tools/pdf-to-pptx',
    category: 'document',
    icon: '🎯'
  },
  {
    slug: 'pptx-to-pdf',
    title: 'PowerPoint to PDF',
    path: '/tools/pptx-to-pdf',
    category: 'document',
    icon: '🎯'
  },
  {
    slug: 'csv-to-excel',
    title: 'CSV to Excel',
    path: '/tools/csv-to-excel',
    category: 'document',
    icon: '📋'
  },
  // PDF Tools
  {
    slug: 'pdf-to-image',
    title: 'PDF to Image',
    path: '/tools/pdf-to-image',
    category: 'pdf',
    icon: '📸'
  },
  {
    slug: 'compress-pdf',
    title: 'Compress PDF',
    path: '/tools/compress-pdf',
    category: 'pdf',
    icon: '📦'
  },
  {
    slug: 'merge-pdf',
    title: 'Merge PDF',
    path: '/tools/merge-pdf',
    category: 'pdf',
    icon: '🔗'
  },
  {
    slug: 'split-pdf',
    title: 'Split PDF',
    path: '/tools/split-pdf',
    category: 'pdf',
    icon: '✂️'
  },
  // Audio Tools (if needed)
  {
    slug: 'mp3-to-wav',
    title: 'MP3 to WAV',
    path: '/tools/mp3-to-wav',
    category: 'audio',
    icon: '🔊'
  },
  // Video Tools (if needed)
  {
    slug: 'mp4-to-webm',
    title: 'MP4 to WebM',
    path: '/tools/mp4-to-webm',
    category: 'video',
    icon: '🎬'
  }
]

/**
 * Get all available tool routes
 */
export const getAllToolRoutes = () => {
  return TOOL_ROUTES
}

/**
 * Get tool route by slug
 */
export const getToolRoute = (slug) => {
  return TOOL_ROUTES.find(route => route.slug === slug)
}

/**
 * Get routes by category
 */
export const getToolsByCategory = (category) => {
  return TOOL_ROUTES.filter(route => route.category === category)
}

/**
 * Get all unique categories
 */
export const getToolCategories = () => {
  const categories = new Set(TOOL_ROUTES.map(route => route.category))
  return Array.from(categories)
}

/**
 * Generate sitemap entries for all tools
 */
export const generateToolSitemapEntries = (baseUrl = 'http://localhost:3000') => {
  return TOOL_ROUTES.map(route => ({
    url: `${baseUrl}${route.path}`,
    lastmod: new Date().toISOString(),
    changefreq: 'monthly',
    priority: 0.8
  }))
}

/**
 * Generate structured breadcrumb schema for tools
 */
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
        item: baseUrl
      },
      {
        '@type': 'ListItem',
        position: 2,
        name: 'Tools',
        item: `${baseUrl}/tools`
      },
      {
        '@type': 'ListItem',
        position: 3,
        name: tool.title,
        item: `${baseUrl}${tool.path}`
      }
    ]
  }
}

/**
 * Export routes as React Router elements
 * Use in App.jsx like: TOOL_ROUTES.map(route => <Route key={route.slug} path={route.path} element={<ToolPage />} />)
 */
export const createToolRoutes = (ToolComponent) => {
  return TOOL_ROUTES.map(route => ({
    path: route.path,
    element: <ToolComponent key={route.slug} />
  }))
}

export default TOOL_ROUTES
