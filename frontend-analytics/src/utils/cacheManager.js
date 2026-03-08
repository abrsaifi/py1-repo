// API Cache Management Service
class CacheManager {
  constructor(maxAge = 5 * 60 * 1000) { // 5 minutes default
    this.cache = new Map()
    this.maxAge = maxAge
  }

  set(key, value, customMaxAge = null) {
    this.cache.set(key, {
      value,
      timestamp: Date.now(),
      maxAge: customMaxAge || this.maxAge
    })
  }

  get(key) {
    const item = this.cache.get(key)
    
    if (!item) return null

    // Check if cache is expired
    if (Date.now() - item.timestamp > item.maxAge) {
      this.cache.delete(key)
      return null
    }

    return item.value
  }

  has(key) {
    return this.get(key) !== null
  }

  delete(key) {
    this.cache.delete(key)
  }

  clear() {
    this.cache.clear()
  }

  invalidatePattern(pattern) {
    const regex = new RegExp(pattern)
    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.cache.delete(key)
      }
    }
  }

  getStats() {
    return {
      size: this.cache.size,
      items: Array.from(this.cache.entries()).map(([key, value]) => ({
        key,
        age: Date.now() - value.timestamp,
        expired: Date.now() - value.timestamp > value.maxAge
      }))
    }
  }
}

// Export singleton instance
export const cacheManager = new CacheManager()

// Hook for cache usage
export function useCachedAPI(endpoint, fetchFn, options = {}) {
  const [data, setData] = React.useState(null)
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState(null)
  const [isCached, setIsCached] = React.useState(false)

  const { maxAge = 5 * 60 * 1000 } = options

  React.useEffect(() => {
    const loadData = async () => {
      // Check cache first
      const cached = cacheManager.get(endpoint)
      if (cached) {
        setData(cached)
        setIsCached(true)
        return
      }

      setLoading(true)
      setIsCached(false)
      
      try {
        const result = await fetchFn()
        cacheManager.set(endpoint, result, maxAge)
        setData(result)
        setError(null)
      } catch (err) {
        setError(err.message)
        setData(null)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [endpoint, fetchFn, maxAge])

  const refetch = React.useCallback(async () => {
    cacheManager.delete(endpoint)
    setLoading(true)
    
    try {
      const result = await fetchFn()
      cacheManager.set(endpoint, result, maxAge)
      setData(result)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [endpoint, fetchFn, maxAge])

  return { data, loading, error, isCached, refetch }
}

export default CacheManager
