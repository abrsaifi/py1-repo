/**
 * Sitemap Generator for SEO
 * Generates XML sitemap entries for all converter tools
 */

import { generateToolSitemapEntries } from './toolRoutes'

/**
 * Generate XML sitemap content
 */
export const generateSitemapXML = (baseUrl = (import.meta && import.meta.env && import.meta.env.VITE_BASE_URL) || 'http://localhost:3000') => {
  const toolEntries = generateToolSitemapEntries(baseUrl)
  const staticPages = [
    { url: baseUrl, lastmod: new Date().toISOString(), changefreq: 'daily', priority: 1.0 },
    { url: `${baseUrl}/pricing`, lastmod: new Date().toISOString(), changefreq: 'monthly', priority: 0.8 },
    { url: `${baseUrl}/about`, lastmod: new Date().toISOString(), changefreq: 'monthly', priority: 0.7 }
  ]

  const allEntries = [...staticPages, ...toolEntries]

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${allEntries.map(entry => `  <url>
    <loc>${escapeXml(entry.url)}</loc>
    <lastmod>${entry.lastmod}</lastmod>
    <changefreq>${entry.changefreq}</changefreq>
    <priority>${entry.priority}</priority>
  </url>`).join('\n')}
</urlset>`

  return xml
}

/**
 * Escape XML special characters
 */
const escapeXml = (str) => {
  return str.replace(/[<>&'"]/g, (char) => {
    const chars = {
      '<': '&lt;',
      '>': '&gt;',
      '&': '&amp;',
      "'": '&apos;',
      '"': '&quot;'
    }
    return chars[char] || char
  })
}

/**
 * Generate robots.txt content
 */
export const generateRobotsTxt = (baseUrl = (import.meta && import.meta.env && import.meta.env.VITE_BASE_URL) || 'http://localhost:3000') => {
  return `# Robots.txt for file converter tools
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /auth/

# Sitemaps
Sitemap: ${baseUrl}/sitemap.xml

# Crawl delay and rate
Crawl-delay: 1
Request-rate: 30/1m
`
}

/**
 * Global robots meta tag configuration
 */
export const ROBOTS_META = {
  'index': 'yes',
  'follow': 'yes',
  'nocache': 'no',
  'googlebot': 'index, follow',
  'bingbot': 'index, follow'
}

/**
 * Global meta tags for all pages
 */
export const GLOBAL_META_TAGS = {
  'viewport': 'width=device-width, initial-scale=1.0',
  'charset': 'utf-8',
  'author': 'Fileconverter Team',
  'theme-color': '#667eea',
  'msapplication-TileColor': '#667eea',
  'og:type': 'website',
  'og:site_name': 'FastConvert',
  'twitter:card': 'summary_large_image',
  'twitter:site': '@fastconvert'
}

/**
 * Apply global SEO tags to document head
 */
export const applyGlobalSEOTags = () => {
  // Apply robots meta tag
  let robotsMeta = document.querySelector('meta[name="robots"]')
  if (!robotsMeta) {
    robotsMeta = document.createElement('meta')
    robotsMeta.name = 'robots'
    document.head.appendChild(robotsMeta)
  }
  robotsMeta.content = `${ROBOTS_META.index}, ${ROBOTS_META.follow}`

  // Apply theme color
  let themeColor = document.querySelector('meta[name="theme-color"]')
  if (!themeColor) {
    themeColor = document.createElement('meta')
    themeColor.name = 'theme-color'
    document.head.appendChild(themeColor)
  }
  themeColor.content = GLOBAL_META_TAGS['theme-color']

  // Apply viewport if not exists
  let viewport = document.querySelector('meta[name="viewport"]')
  if (!viewport) {
    viewport = document.createElement('meta')
    viewport.name = 'viewport'
    viewport.content = GLOBAL_META_TAGS.viewport
    document.head.appendChild(viewport)
  }
}

/**
 * Create JSON-LD Organization schema
 */
export const createOrganizationSchema = (baseUrl = (import.meta && import.meta.env && import.meta.env.VITE_BASE_URL) || 'http://localhost:3000') => {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'FastConvert',
    url: baseUrl,
    logo: `${baseUrl}/logo.png`,
    description: 'Fast, secure, and free online file converter. Convert documents, images, PDFs, and more.',
    sameAs: [
      'https://www.facebook.com/fastconvert',
      'https://www.twitter.com/fastconvert',
      'https://www.instagram.com/fastconvert'
    ],
    contactPoint: {
      '@type': 'ContactPoint',
      telephone: '+1-555-123-4567',
      contactType: 'Customer Support'
    }
  }
}

export default {
  generateSitemapXML,
  generateRobotsTxt,
  ROBOTS_META,
  GLOBAL_META_TAGS,
  applyGlobalSEOTags,
  createOrganizationSchema
}
