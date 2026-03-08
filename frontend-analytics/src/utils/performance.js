// Performance Optimization Utilities
import { lazy, Suspense } from 'react'

// Dynamic Import with Error Handling
export function asyncComponent(importFunc, fallback) {
  const Component = lazy(importFunc)
  
  return (props) => (
    <Suspense fallback={fallback || <div>Loading...</div>}>
      <Component {...props} />
    </Suspense>
  )
}

// Intersection Observer Hook for Lazy Loading
export function useLazyLoad(options = {}) {
  const [isVisible, setIsVisible] = React.useState(false)
  const ref = React.useRef(null)

  React.useEffect(() => {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '50px',
      ...options
    }

    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setIsVisible(true)
        observer.unobserve(entry.target)
      }
    }, observerOptions)

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current)
      }
    }
  }, [options])

  return { ref, isVisible }
}

// Performance Monitoring
export class PerformanceMonitor {
  constructor(name) {
    this.name = name
    this.marks = new Map()
  }

  mark(label) {
    performance.mark(`${this.name}-${label}`)
    this.marks.set(label, Date.now())
  }

  measure(label, startMark, endMark) {
    try {
      performance.measure(
        `${this.name}-${label}`,
        `${this.name}-${startMark}`,
        `${this.name}-${endMark}`
      )
      
      const measure = performance.getEntriesByName(`${this.name}-${label}`)[0]
      return measure.duration
    } catch (err) {
      console.warn(`Measurement failed: ${err.message}`)
      return 0
    }
  }

  getMetrics() {
    const metrics = {}
    const entries = performance.getEntriesByType('measure')
    
    entries.forEach(entry => {
      if (entry.name.startsWith(this.name)) {
        metrics[entry.name] = entry.duration
      }
    })
    
    return metrics
  }
}

// Memoization Helper
export function memoize(fn, options = {}) {
  const cache = new Map()
  const { maxSize = 100, ttl = null } = options

  return (...args) => {
    const key = JSON.stringify(args)
    
    if (cache.has(key)) {
      const cached = cache.get(key)
      if (!ttl || Date.now() - cached.timestamp < ttl) {
        return cached.value
      }
      cache.delete(key)
    }

    const result = fn(...args)
    
    if (cache.size >= maxSize) {
      const firstKey = cache.keys().next().value
      cache.delete(firstKey)
    }

    cache.set(key, { value: result, timestamp: Date.now() })
    return result
  }
}

// Resource Hints
export class ResourceHints {
  static preload(href, as = 'script') {
    const link = document.createElement('link')
    link.rel = 'preload'
    link.href = href
    link.as = as
    document.head.appendChild(link)
  }

  static prefetch(href) {
    const link = document.createElement('link')
    link.rel = 'prefetch'
    link.href = href
    document.head.appendChild(link)
  }

  static preconnect(href) {
    const link = document.createElement('link')
    link.rel = 'preconnect'
    link.href = href
    document.head.appendChild(link)
  }

  static dnsPrefetch(href) {
    const link = document.createElement('link')
    link.rel = 'dns-prefetch'
    link.href = href
    document.head.appendChild(link)
  }
}

// Debounce & Throttle
export function debounce(func, delay) {
  let timeoutId
  return function debounced(...args) {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func(...args), delay)
  }
}

export function throttle(func, limit) {
  let isThrottled = false
  return function throttled(...args) {
    if (!isThrottled) {
      func(...args)
      isThrottled = true
      setTimeout(() => (isThrottled = false), limit)
    }
  }
}

// Virtual Scrolling for Large Lists
export function useVirtualScroll(items, itemHeight, containerHeight) {
  const [scrollTop, setScrollTop] = React.useState(0)

  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - 5)
  const endIndex = Math.min(
    items.length,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + 5
  )

  const visibleItems = items.slice(startIndex, endIndex)
  const offsetY = startIndex * itemHeight

  return { visibleItems, offsetY, startIndex, endIndex, setScrollTop }
}

export default {
  asyncComponent,
  useLazyLoad,
  PerformanceMonitor,
  memoize,
  ResourceHints,
  debounce,
  throttle,
  useVirtualScroll
}
