# Phase 10+ Enhancements - Quick Reference Guide

**Last Updated:** March 5, 2026

---

## 🚀 Quick Start

### 1. Using Notifications (Easiest)
```jsx
import { useNotificationContext } from './components/Notification'

function MyComponent() {
  const { success, error, warning, info } = useNotificationContext()
  
  success('Operation completed!')
  error('Something went wrong')
  warning('Please be careful')
  info('FYI, something happened')
}
```

### 2. Using Cached API Calls
```jsx
import { useCachedAPI } from './utils/cacheManager'

const { data, loading, error, refetch } = useCachedAPI(
  '/api/metrics', // cache key
  () => api.getMetrics(), // fetch function
  { maxAge: 5 * 60 * 1000 } // 5 minutes
)
```

### 3. Using Advanced Filters
```jsx
import AdvancedFilters from './components/AdvancedFilters'

<AdvancedFilters
  fields={[
    { name: 'status', label: 'Status', type: 'select', options: ['Active', 'Inactive'] },
    { name: 'date', label: 'Created', type: 'date' },
  ]}
  onApply={(filters) => console.log(filters)}
  onReset={() => console.log('Reset')}
/>
```

### 4. Using Advanced Search
```jsx
import { useAdvancedSearch } from './utils/searchEngine'

const { searchResults, handleSearch } = useAdvancedSearch(myData)

<input onChange={(e) => handleSearch(e.target.value)} placeholder="Search..." />
```

### 5. Using Analytics
```jsx
import AdvancedAnalytics from './components/AdvancedAnalytics'

<AdvancedAnalytics 
  data={timeSeriesData} 
  metric="value" // field to analyze
/>
```

### 6. Using WebSocket
```jsx
import { useWebSocket } from './services/websocket'

const { isConnected, subscribe, send } = useWebSocket('ws://localhost:5000')

useEffect(() => {
  const unsubscribe = subscribe('data-update', (data) => {
    console.log('New data:', data)
  })
  return unsubscribe
}, [])
```

### 7. Using Performance Utilities
```jsx
import { useLazyLoad, memoize, debounce } from './utils/performance'

// Lazy load on scroll
const { ref, isVisible } = useLazyLoad()
return <div ref={ref}>{isVisible && <HeavyComponent />}</div>

// Memoize expensive calculations
const cached = memoize(expensiveFunction, { maxSize: 100 })

// Debounce search
const debouncedSearch = debounce((query) => {
  search(query)
}, 300)
```

---

## 📋 Integration Checklist

- [x] Notification system - Already integrated in App.jsx
- [ ] Caching - Add to API pages (MetricsPage, ReportsPage, etc.)
- [ ] Filters - Add to table pages
- [ ] Search - Add search inputs
- [ ] Analytics - Add to dashboard/metrics pages
- [ ] WebSocket - Configure backend endpoint
- [ ] Performance - Add to heavy components

---

## 🎯 Common Use Cases

### Use Case 1: Add Notifications to a Form
```jsx
const { success, error } = useNotificationContext()

const handleSubmit = async (formData) => {
  try {
    await api.saveData(formData)
    success('Data saved successfully!')
  } catch (err) {
    error('Failed to save: ' + err.message)
  }
}
```

### Use Case 2: Cache API Data
```jsx
const { data: users, refetch } = useCachedAPI(
  'users-list',
  () => api.fetchUsers(),
  { maxAge: 10 * 60 * 1000 }
)

// Manually refresh
<button onClick={refetch}>Refresh Users</button>
```

### Use Case 3: Filter Table Data
```jsx
const [filters, setFilters] = useState({})
const [filteredData, setFilteredData] = useState(allData)

const applyFilters = (newFilters) => {
  const filtered = applyFilterLogic(allData, newFilters)
  setFilteredData(filtered)
  setFilters(newFilters)
}

return (
  <>
    <AdvancedFilters onApply={applyFilters} />
    <DataTable data={filteredData} />
  </>
)
```

### Use Case 4: Real-time Dashboard Updates
```jsx
const { subscribe } = useWebSocket('ws://localhost:5000')

useEffect(() => {
  const unsubscribe = subscribe('metrics-updated', (newMetrics) => {
    setMetrics(newMetrics)
    notif.info('Dashboard updated!')
  })
  return unsubscribe
}, [])
```

### Use Case 5: Show Analytics on Report
```jsx
const { data: reportData } = useCachedAPI(
  'report:' + reportId,
  () => api.getReport(reportId)
)

return (
  <>
    <h2>{report.name}</h2>
    <AdvancedAnalytics 
      data={reportData} 
      metric="revenue" 
    />
  </>
)
```

---

## 🔧 Configuration Reference

### Notification Settings
```javascript
// Auto-dismiss duration (ms)
success(message, 5000)    // 5 seconds
error(message, 8000)      // 8 seconds
warning(message, 6000)    // 6 seconds
info(message, 5000)       // 5 seconds

// No auto-dismiss
addNotification(message, 'info', 0)
```

### Cache Settings
```javascript
// Set custom TTL per item
cacheManager.set(key, value, 60000) // 1 minute

// Invalidate by pattern
cacheManager.invalidatePattern('user:.*')

// Clear entire cache
cacheManager.clear()

// Get cache stats
cacheManager.getStats()
```

### Search Settings
```javascript
searchEngine.search(query, [], {
  limit: 20,           // Max results
  fuzzy: false,        // Fuzzy matching
  caseSensitive: false // Case sensitivity
})
```

### Performance Settings
```javascript
// Lazy load threshold
useLazyLoad({ threshold: 0.1, rootMargin: '50px' })

// Memoization cache size
memoize(fn, { maxSize: 100, ttl: 60000 })

// Debounce delay
debounce(fn, 300)

// Throttle limit
throttle(fn, 1000)
```

---

## 🐛 Debugging Tips

### Debug Notifications
```javascript
// List all active notifications
console.log(notificationContext.notifications)

// Force show notification
notificationContext.addNotification('Test', 'info')
```

### Debug Cache
```javascript
import { cacheManager } from './utils/cacheManager'

// Check cache contents
console.log(cacheManager.getStats())

// Clear specific key
cacheManager.delete(key)

// Monitor cache hits
cacheManager.get(key) // null if miss
```

### Debug Search
```javascript
// Test search engine
const engine = new SearchEngine(data)
console.log(engine.search('query'))
```

### Debug Performance
```javascript
// Monitor component performance
const monitor = new PerformanceMonitor('Component')
monitor.mark('start')
// ... work ...
monitor.mark('end')
console.log(monitor.measure('time', 'start', 'end'))
```

---

## 📊 Performance Monitoring

```javascript
// Check actual performance gains
const stats = cacheManager.getStats()
console.log(`Cache hit rate: ${stats.size} items`)

// Monitor network requests
Performance API:
- performance.getEntriesByType('resource')
- performance.getEntriesByType('measure')
```

---

## 🔄 Updating Data

### Refresh Cached Data
```jsx
const { refetch } = useCachedAPI('/api/data', fetch)
<button onClick={refetch}>Refresh</button>
```

### Invalidate Cache Pattern
```javascript
import { cacheManager } from './utils/cacheManager'

// After creating new user
cacheManager.invalidatePattern('users:.*')

// After updating metric
cacheManager.delete('metrics:summary')
```

### WebSocket Auto-update
```jsx
subscribe('data-changed', (newData) => {
  cacheManager.invalidatePattern('.*')
  refetch()
})
```

---

## 🎨 Styling the New Components

All new components support dark mode automatically!

To customize colors, edit CSS variables in `src/styles/app.css`:

```css
:root {
  --primary-color: #3b82f6;
  --primary-dark: #1d4ed8;
  --danger-color: #ef4444;
  --danger-dark: #dc2626;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --border-color: #e5e7eb;
  --text-color: #111827;
  --text-secondary: #6b7280;
}
```

---

## 📚 File Locations Reference

```
src/
├── components/
│   ├── AdvancedFilters.jsx      (Advanced filtering UI)
│   ├── AdvancedAnalytics.jsx    (Analytics dashboard)
│   └── Notification.jsx          (NotificationProvider + hook)
├── hooks/
│   └── (existing hooks)
├── services/
│   └── websocket.js              (WebSocket service)
├── utils/
│   ├── searchEngine.js           (Search functionality)
│   ├── cacheManager.js           (API caching)
│   └── performance.js            (Performance utilities)
└── styles/
    ├── filters.css               (Filter styles)
    ├── notifications.css         (Notification styles)
    └── analytics.css             (Analytics styles)
```

---

## 🚀 Next Steps

1. **Test locally** - Verify all features work
2. **Add to pages** - Integrate into existing pages
3. **Connect backend** - Wire up WebSocket and API caching
4. **Monitor performance** - Check Network tab improvements
5. **Gather feedback** - Get user input on new features
6. **Deploy** - Push to production

---

**Questions?** Check [PHASE_10_ENHANCEMENTS_COMPLETE.md](./PHASE_10_ENHANCEMENTS_COMPLETE.md) for detailed documentation.

**Ready to deploy?** Run `npm run build` and push to production!
