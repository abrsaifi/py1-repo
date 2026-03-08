import { useEffect } from 'react'

/**
 * Custom hook for managing SEO meta tags and structured data
 * @param {Object} config - SEO configuration
 * @param {string} config.title - Page title
 * @param {string} config.description - Meta description
 * @param {string} config.image - OG image URL
 * @param {string} config.url - Page URL
 * @param {string} config.type - Schema type (e.g., 'Product', 'Software', 'Article')
 * @param {Object} config.structuredData - Additional structured data
 */
export const useSEO = (config = {}) => {
  useEffect(() => {
    const { title, description, image, url, type = 'WebPage', structuredData = {} } = config

    // Set page title
    if (title) {
      document.title = title
    }

    // Remove existing meta tags
    const existingMeta = document.querySelectorAll('meta[data-seo="true"]')
    existingMeta.forEach(el => el.remove())

    const existingStructured = document.getElementById('schema-structured-data')
    if (existingStructured) existingStructured.remove()

    // Add meta description
    if (description) {
      const metaDescription = document.createElement('meta')
      metaDescription.name = 'description'
      metaDescription.content = description
      metaDescription.setAttribute('data-seo', 'true')
      document.head.appendChild(metaDescription)
    }

    // Add OpenGraph tags
    if (title) {
      const ogTitle = document.createElement('meta')
      ogTitle.property = 'og:title'
      ogTitle.content = title
      ogTitle.setAttribute('data-seo', 'true')
      document.head.appendChild(ogTitle)
    }

    if (description) {
      const ogDescription = document.createElement('meta')
      ogDescription.property = 'og:description'
      ogDescription.content = description
      ogDescription.setAttribute('data-seo', 'true')
      document.head.appendChild(ogDescription)
    }

    if (image) {
      const ogImage = document.createElement('meta')
      ogImage.property = 'og:image'
      ogImage.content = image
      ogImage.setAttribute('data-seo', 'true')
      document.head.appendChild(ogImage)
    }

    if (url) {
      const ogUrl = document.createElement('meta')
      ogUrl.property = 'og:url'
      ogUrl.content = url
      ogUrl.setAttribute('data-seo', 'true')
      document.head.appendChild(ogUrl)
    }

    // Add Twitter Card tags
    if (title) {
      const twitterTitle = document.createElement('meta')
      twitterTitle.name = 'twitter:title'
      twitterTitle.content = title
      twitterTitle.setAttribute('data-seo', 'true')
      document.head.appendChild(twitterTitle)
    }

    if (description) {
      const twitterDescription = document.createElement('meta')
      twitterDescription.name = 'twitter:description'
      twitterDescription.content = description
      twitterDescription.setAttribute('data-seo', 'true')
      document.head.appendChild(twitterDescription)
    }

    if (image) {
      const twitterImage = document.createElement('meta')
      twitterImage.name = 'twitter:image'
      twitterImage.content = image
      twitterImage.setAttribute('data-seo', 'true')
      document.head.appendChild(twitterImage)
    }

    // Add canonical URL
    let canonical = document.querySelector('link[rel="canonical"]')
    if (!canonical) {
      canonical = document.createElement('link')
      canonical.rel = 'canonical'
      document.head.appendChild(canonical)
    }
    if (url) canonical.href = url

    // Add structured data (JSON-LD)
    if (Object.keys(structuredData).length > 0 || type) {
      const schema = {
        '@context': 'https://schema.org',
        '@type': type,
        ...(title && { name: title }),
        ...(description && { description }),
        ...(image && { image }),
        ...(url && { url }),
        ...structuredData
      }

      const script = document.createElement('script')
      script.type = 'application/ld+json'
      script.id = 'schema-structured-data'
      script.textContent = JSON.stringify(schema)
      script.setAttribute('data-seo', 'true')
      document.head.appendChild(script)
    }

    return () => {
      // Cleanup is optional - these tags can persist
    }
  }, [config])
}

/**
 * Generate SEO config for converter tool pages
 */
export const generateToolSEOConfig = (tool, baseUrl = 'http://localhost:3000') => {
  const toolUrl = `${baseUrl}/tools/${tool.slug}`
  
  return {
    title: `${tool.title} Online Converter - Free ${tool.from_format} to ${tool.to_format} Conversion`,
    description: `Convert ${tool.from_format} to ${tool.to_format} files online for free. ${tool.description?.substring(0, 100) || ''}. No registration required.`,
    image: `${baseUrl}/tool-icons/${tool.slug}.png`,
    url: toolUrl,
    type: 'SoftwareApplication',
    structuredData: {
      name: tool.title,
      applicationCategory: 'UtilityApplication',
      featureList: tool.key_features || [],
      aggregateRating: {
        '@type': 'AggregateRating',
        ratingValue: '4.8',
        ratingCount: '2500'
      },
      offers: {
        '@type': 'Offer',
        price: '0',
        priceCurrency: 'USD'
      }
    }
  }
}

/**
 * Create breadcrumb schema
 */
export const createBreadcrumbSchema = (breadcrumbs) => {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: breadcrumbs.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.label,
      item: item.url
    }))
  }
}
