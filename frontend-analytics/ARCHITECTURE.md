# Frontend Architecture & Component Guide

## Overview

This is a production-ready React 18 dashboard frontend for the Phase 10 Advanced Analytics & Dashboard Service. Built with Vite for optimal performance and developer experience.

## Technology Stack

- **Framework**: React 18.2.0
- **Build Tool**: Vite 5.0.0
- **HTTP Client**: Axios 1.6.0
- **Routing**: React Router v6
- **Charts**: Chart.js 4.4.0 + react-chartjs-2
- **Styling**: CSS3 with CSS Variables
- **Date Handling**: date-fns 2.30.0
- **Tables**: rc-pagination 3.5.0

## Project Structure

```
frontend-analytics/
├── public/                    # Static assets
│   └── index.html            # Main HTML entry point
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── Sidebar.jsx       # Navigation sidebar (collapsible)
│   │   ├── Header.jsx        # Top header with search & status
│   │   ├── MetricCard.jsx    # Metric display card with trend
│   │   ├── LineChart.jsx     # Time-series chart component
│   │   ├── BarChart.jsx      # Bar chart component
│   │   └── DataTable.jsx     # Sortable data table component
│   │
│   ├── pages/                # Page components (route views)
│   │   ├── LoginPage.jsx     # Authentication login
│   │   ├── DashboardPage.jsx # Main dashboard overview
│   │   ├── MetricsPage.jsx   # Metrics listing & filtering
│   │   ├── ReportsPage.jsx   # Report creation & management
│   │   ├── AlertsPage.jsx    # Alert configuration
│   │   ├── QueryPage.jsx     # Custom query builder
│   │   ├── CustomMetricsPage.jsx # Formula-based metrics
│   │   └── SettingsPage.jsx  # Application settings
│   │
│   ├── services/             # API and external services
│   │   └── api.js            # Axios instance + all API methods
│   │
│   ├── hooks/                # Custom React hooks
│   │   └── useAuth.js        # Authentication state management
│   │
│   ├── styles/               # CSS stylesheets
│   │   ├── index.css         # Global styles & design system
│   │   ├── sidebar.css       # Sidebar component styles
│   │   ├── header.css        # Header component styles
│   │   ├── cards.css         # Metric card styles
│   │   ├── table.css         # Data table styles
│   │   ├── pages.css         # Page layouts
│   │   └── app.css           # Main app styles
│   │
│   ├── App.jsx               # Root component with routing
│   ├── main.jsx              # React entry point
│   └── index.html            # HTML template
│
├── vite.config.js            # Vite build configuration
├── package.json              # Dependencies & scripts
├── .gitignore               # Git ignore patterns
├── README.md                # Main documentation
├── SETUP_GUIDE.md          # Quick start guide
└── ARCHITECTURE.md         # This file

```

## Component Hierarchy

```
App (Router setup)
├── LoginPage
│   └── Login form + demo button
└── MainLayout
    ├── Sidebar
    │   ├── Navigation links
    │   └── User section
    ├── Header
    │   ├── Page title
    │   ├── Search box
    │   └── Status indicators
    └── PageContent (Routes)
        ├── DashboardPage
        │   ├── MetricCards (grid)
        │   ├── LineChart
        │   ├── BarChart
        │   └── AlertsList
        ├── MetricsPage
        │   ├── Filter controls
        │   └── DataTable
        ├── ReportsPage
        │   ├── Form
        │   └── DataTable
        ├── AlertsPage
        │   ├── Form
        │   └── DataTable
        ├── QueryPage
        │   ├── Form
        │   └── DataTable
        ├── CustomMetricsPage
        │   ├── Form
        │   └── DataTable
        └── SettingsPage
            └── Settings sections
```

## Key Features

### 1. Authentication (useAuth hook)
```javascript
const auth = useAuth()
// auth.token, auth.tenantId, auth.user
// auth.login(), auth.logout(), auth.generateTestToken()
```

### 2. API Integration (api.js service)
```javascript
import { metricsAPI, dashboardsAPI, reportsAPI } from '../services/api'

// All methods include JWT token & tenant ID
// Organized by resource type
// Error handling with axios interceptors
```

### 3. Responsive Design
- Sidebar collapses on mobile
- Grid layouts adapt to screen size
- Touch-friendly buttons and inputs
- Mobile-optimized forms

### 4. Real-time Features
- Auto-refresh settings available
- Live health checks
- Status indicators
- Notification system

### 5. Data Visualization
- Interactive line charts
- Comparative bar charts
- Metric cards with trends
- Sortable data tables

## Design System

### Colors
```css
--primary-color: #3b82f6       /* Main brand color */
--secondary-color: #6366f1     /* Secondary accent */
--success-color: #10b981       /* Success states */
--warning-color: #f59e0b       /* Warning states */
--danger-color: #ef4444        /* Error states */
--dark-color: #1f2937          /* Dark backgrounds */
--light-color: #f3f4f6         /* Light backgrounds */
--border-color: #e5e7eb        /* Borders */
--text-dark: #111827           /* Dark text */
--text-light: #6b7280          /* Light text */
```

### Spacing Scale
```
4px   → Small padding/gaps
8px   → Component margins
12px  → Form spacing
16px  → Section padding
20px  → Card padding
24px  → Page margins
```

### Typography
- **Font Family**: System fonts (-apple-system, BlinkMacSystemFont, etc.)
- **Headings**: 700 weight, 24px-36px
- **Body**: 400 weight, 14px
- **Labels**: 500 weight, 14px
- **Small text**: 12px, lighter color

### Responsive Breakpoints
```javascript
desktop:  1024px+
tablet:   768px - 1023px
mobile:   < 768px
```

## API Service Structure

### Metrics API
```javascript
metricsAPI.getSystemMetrics(params)
metricsAPI.getServiceMetrics(params)
metricsAPI.getActivityMetrics(params)
metricsAPI.getBusinessMetrics(params)
metricsAPI.getMetricsOverTime(metricId, params)
metricsAPI.getMetricComparison(params)
metricsAPI.getMetricsBreakdown(metricId, params)
```

### Dashboards API
```javascript
dashboardsAPI.list(params)
dashboardsAPI.create(data)
dashboardsAPI.get(id)
dashboardsAPI.update(id, data)
dashboardsAPI.delete(id)
dashboardsAPI.addWidget(dashboardId, data)
dashboardsAPI.updateWidget(dashboardId, widgetId, data)
dashboardsAPI.removeWidget(dashboardId, widgetId)
dashboardsAPI.share(dashboardId, data)
dashboardsAPI.getShared()
```

### Reports API
```javascript
reportsAPI.list(params)
reportsAPI.create(data)
reportsAPI.generate(reportId)
reportsAPI.getHistory(reportId, params)
reportsAPI.schedule(reportId, data)
```

### Alerts API
```javascript
alertsAPI.list(params)
alertsAPI.create(data)
alertsAPI.getEvents(alertId, params)
alertsAPI.clearEvents(alertId)
alertsAPI.detectAnomalies(data)
```

### Queries API
```javascript
queriesAPI.list(params)
queriesAPI.create(data)
queriesAPI.execute(queryId)
queriesAPI.getResults(queryId, params)
queriesAPI.getTemplates()
```

### Custom Metrics API
```javascript
customMetricsAPI.list(params)
customMetricsAPI.create(data)
customMetricsAPI.calculate(metricId)
customMetricsAPI.getCalculationHistory(metricId, params)
```

### Export API
```javascript
exportsAPI.exportMetrics(data)
exportsAPI.exportDashboards(data)
exportsAPI.exportReports(data)
```

## Component Details

### Sidebar Component
- **Features**: Collapsible, navigation links, user info
- **State**: `collapsed` (local)
- **Props**: `onLogout`, `userName`
- **Mobile**: Collapses to icon-only on small screens

### Header Component
- **Features**: Title, search, status, time, notifications
- **State**: `health`, `time` (auto-updating)
- **Props**: `title`
- **Responsive**: Stacks on mobile

### MetricCard Component
- **Features**: Displays metric value with trend and color coding
- **Props**: `title`, `value`, `unit`, `trend`, `icon`, `color`
- **Styling**: Color-coded top border, hover effects

### LineChart Component
- **Features**: Time-series data visualization
- **Props**: `title`, `labels`, `datasets`, `options`
- **Library**: Chart.js via react-chartjs-2
- **Responsive**: Auto-scales to container

### BarChart Component
- **Features**: Comparative data visualization
- **Props**: `title`, `labels`, `datasets`, `options`
- **Library**: Chart.js via react-chartjs-2
- **Responsive**: Auto-scales to container

### DataTable Component
- **Features**: Sortable, filterable, paginated
- **Props**: `columns`, `data`, `title`, `onRowClick`, `loading`
- **Sorting**: Click column header to sort
- **State**: `sortConfig` for sort direction

## State Management

### Global State
- **Authentication**: Managed via `useAuth` hook
- **User Info**: Stored in localStorage and React state
- **Token**: Stored in localStorage, added to all API requests
- **Tenant ID**: Stored in localStorage, added to all API requests

### Component State
- **Page-level**: Loading, forms, modal state
- **Local**: Sidebar collapse, chart selection, filter state

## API Communication

### Authentication Flow
1. User logs in via LoginPage
2. Token & tenantId stored in localStorage
3. `useAuth` hook reads from localStorage
4. All API requests include Authorization header
5. API requests include X-Tenant-ID header

### Request Interceptors
```javascript
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  const tenantId = localStorage.getItem('tenantId')
  
  if (token) config.headers.Authorization = `Bearer ${token}`
  if (tenantId) config.headers['X-Tenant-ID'] = tenantId
  
  return config
})
```

### Error Handling
- 401: Unauthorized (invalid token)
- 403: Forbidden (insufficient permissions)
- 404: Not found
- 429: Too many requests
- 500: Server error

## Performance Optimizations

### Current Implementations
- ✅ Code splitting ready (React Router)
- ✅ Lazy component loading available
- ✅ CSS minimized in production builds
- ✅ Vite tree-shaking enabled
- ✅ Zero runtime overhead CSS-in-JS

### Development Features
- ✅ Fast HMR (Hot Module Replacement)
- ✅ Source maps enabled
- ✅ Network request proxying
- ✅ Dev server refresh rate optimization

## Best Practices

### Component Writing
```javascript
// Use functional components
export const MyComponent = ({ prop1, prop2 }) => {
  // Use hooks
  const { data, setData } = useState(null)
  const { token } = useAuth()
  
  // Effects
  useEffect(() => { /* ... */ }, [])
  
  // Render
  return <div>Content</div>
}
```

### API Usage
```javascript
// Import specific API methods
import { metricsAPI } from '../services/api'

// Use in components
const [data, setData] = useState([])
useEffect(() => {
  metricsAPI.getSystemMetrics()
    .then(res => setData(res.data))
    .catch(err => console.error(err))
}, [])
```

### Form Handling
```javascript
// Local state for form
const [form, setForm] = useState({ field: '' })

// Update handler
const handleChange = (field, value) => {
  setForm(prev => ({ ...prev, [field]: value }))
}

// Submit
const handleSubmit = async (e) => {
  e.preventDefault()
  await apiMethod(form)
}
```

## Extending the Dashboard

### Adding a New Page
1. Create `src/pages/NewPage.jsx`
2. Import in `App.jsx`
3. Add route in `<Routes>`
4. Add navigation link in `Sidebar.jsx`
5. Create styles as needed

### Adding a New Component
1. Create `src/components/NewComponent.jsx`
2. Export component
3. Import where needed
4. Add to `src/styles/` if complex styling

### Adding New API Methods
1. Add methods to `src/services/api.js`
2. Follow existing pattern
3. Use in components

## Deployment

### Build
```bash
npm install
npm run build
```

### Output
- Optimized bundle in `dist/`
- Source maps for debugging
- Minified CSS and JS

### Hosting
- Static file server (nginx, Apache, S3)
- SPA routing rules required
- CDN support for assets

### Environment
```
REACT_APP_API_URL=https://api.example.com
```

## Testing

### Unit Tests (Ready to add)
- Jest + React Testing Library
- Component props testing
- Hook testing with `@testing-library/react-hooks`

### E2E Tests (Ready to add)
- Cypress or Playwright
- User flow testing
- API interaction testing

## Security

### Implemented
- ✅ JWT token-based auth
- ✅ HttpOnly cookie ready
- ✅ CORS enabled on backend
- ✅ Tenant isolation
- ✅ Input validation in forms

### Recommended
- HTTPS in production
- Content Security Policy headers
- Regular dependency updates
- Rate limiting on API

## Troubleshooting

### Common Issues

**401 Unauthorized**
- Check token in localStorage
- Verify backend is running
- Try demo login

**CORS Error**
- Verify API URL in settings
- Check backend allows CORS
- Review console for detailed error

**Charts Not Rendering**
- Ensure chart.js installed
- Check data format
- Verify labels/datasets provided

**API Timeout**
- Check backend connection
- Review network tab
- Increase timeout if needed

## Future Enhancements

- [ ] Dark mode toggle
- [ ] Advanced filtering
- [ ] Report scheduling UI
- [ ] Real-time WebSocket updates
- [ ] Export to multiple formats
- [ ] Dashboard templates
- [ ] Advanced charting options
- [ ] User management GUI
- [ ] Audit logging
- [ ] Performance metrics
