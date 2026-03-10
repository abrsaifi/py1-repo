// Advanced Search with debounce and type-ahead
import { useState, useCallback, useEffect } from 'react'

class SearchEngine {
  constructor(data = []) {
    this.data = data
    this.searchIndex = this.buildIndex(data)
  }

  buildIndex(data) {
    const index = new Map()
    data.forEach((item, idx) => {
      Object.values(item).forEach(value => {
        const text = String(value).toLowerCase()
        if (!index.has(text)) {
          index.set(text, [])
        }
        index.get(text).push(idx)
      })
    })
    return index
  }

  search(query, fields = [], options = {}) {
    const {
      limit = 10,
      fuzzy = false,
      caseSensitive = false
    } = options

    const q = caseSensitive ? query : query.toLowerCase()
    const results = new Set()

    // Exact matches
    if (this.searchIndex.has(q)) {
      this.searchIndex.get(q).forEach(idx => results.add(idx))
    }

    // Partial matches
    this.searchIndex.forEach((indices, key) => {
      if (key.includes(q)) {
        indices.forEach(idx => results.add(idx))
      }
    })

    return Array.from(results)
      .slice(0, limit)
      .map(idx => this.data[idx])
  }

  updateData(data) {
    this.data = data
    this.searchIndex = this.buildIndex(data)
  }
}

export default SearchEngine

// Debounce util for search
export function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

// Advanced Search Hook
export function useAdvancedSearch(initialData = []) {
  const [data, setData] = useState(initialData)
  const [searchResults, setSearchResults] = useState([])
  const [searchQuery, setSearchQuery] = useState('')

  const searchEngine = new SearchEngine(data)

  const handleSearch = useCallback(debounce((query) => {
    if (!query.trim()) {
      setSearchResults([])
      setSearchQuery('')
      return
    }

    const results = searchEngine.search(query, [], {
      limit: 20,
      fuzzy: false
    })
    
    setSearchResults(results)
    setSearchQuery(query)
  }, 300), [data])

  useEffect(() => {
    searchEngine.updateData(data)
  }, [data])

  return {
    searchResults,
    searchQuery,
    handleSearch,
    setData,
    resultCount: searchResults.length
  }
}
