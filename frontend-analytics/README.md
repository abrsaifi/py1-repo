# Frontend Analytics Dashboard

Modern React-based dashboard for Phase 10 Advanced Analytics & Dashboard Service

## Project Structure

```
frontend-analytics/
├── public/
│   └── index.html           # Main HTML file
├── src/
│   ├── components/          # Reusable React components
│   │   ├── Sidebar.jsx
│   │   ├── Header.jsx
│   │   ├── MetricCard.jsx
│   │   ├── LineChart.jsx
│   │   ├── BarChart.jsx
│   │   └── DataTable.jsx
│   ├── pages/              # Page components
│   │   ├── LoginPage.jsx
│   │   ├── DashboardPage.jsx
│   │   ├── MetricsPage.jsx
│   │   ├── ReportsPage.jsx
│   │   ├── AlertsPage.jsx
│   │   ├── QueryPage.jsx
│   │   ├── CustomMetricsPage.jsx
│   │   └── SettingsPage.jsx
│   ├── services/           # API services
│   │   └── api.js          # Axios API client with all endpoints
│   ├── hooks/              # React hooks
│   │   └── useAuth.js      # Authentication hook
│   ├── styles/             # CSS files
│   │   ├── index.css       # Global styles
│   │   ├── sidebar.css     # Sidebar styles
│   │   ├── header.css      # Header styles
│   │   ├── cards.css       # Metric cards
│   │   ├── table.css       # Data tables
│   │   ├── pages.css       # Page styles
│   │   └── app.css         # App layout
│   ├── App.jsx             # Main app component
│   └── main.jsx            # React DOM entry point
├── vite.config.js          # Vite configuration
├── package.json            # Dependencies
└── README.md               # This file

## Features

✅ **Dashboard** - Real-time metrics and analytics overview
✅ **Metrics** - View and filter system, service, and business metrics
✅ **Reports** - Generate, schedule, and manage reports
✅ **Alerts** - Create and monitor system alerts
✅ **Queries** - Execute and save custom queries
✅ **Custom Metrics** - Create calculated metrics using formulas
✅ **Settings** - Configure app preferences and API endpoints
✅ **Authentication** - JWT-based auth with tenant isolation
✅ **Charts** - Interactive line and bar charts
✅ **Data Tables** - Sortable, paginated data display
✅ **Responsive Design** - Works on desktop, tablet, and mobile

## Installation

```bash
# Install dependencies
npm install

# Start development server (port 3000)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## API Integration

The dashboard connects to Phase 10 Analytics Service at `http://localhost:5009`

### API Endpoints

All endpoints are wrapped in the `api.js` service:

- **Metrics**: `/api/metrics/*` (system, service, activity, business)
- **Dashboards**: `/api/dashboards/*` (CRUD, widgets, sharing)
- **Reports**: `/api/reports/*` (generation, scheduling)
- **Alerts**: `/api/alerts/*` (management, events, anomaly detection)
- **Queries**: `/api/queries/*` (execution, templates)
- **Custom Metrics**: `/api/custom-metrics/*` (formulas, calculation)
- **Export**: `/api/export/*` (multi-format: CSV, JSON, XLSX, PDF)
- **Health**: `/health`, `/metrics`

## Authentication

### Demo Login

The authentication system supports:
- Email/password login
- Tenant ID configuration
- JWT token storage
- Demo login button for quick access

**Demo Credentials**:
- Email: admin@example.com
- Password: any password
- Tenant ID: tenant-1

### Implementation

Authentication is managed via the `useAuth` hook:

```javascript
const auth = useAuth()
auth.login(token, tenantId, userData)
auth.logout()
auth.generateTestToken()
```

## Configuration

### Environment Variables

Create `.env` file:

```
REACT_APP_API_URL=http://localhost:5009
```

### Vite Configuration

The vite.config.js includes:
- Port 3000 for dev server
- API proxy to backend (http://localhost:5009)
- Source maps for development

## Component Architecture

### Page Components
- **LoginPage**: Authentication interface
- **DashboardPage**: Main analytics dashboard
- **MetricsPage**: Metrics listing and filtering
- **ReportsPage**: Report management
- **AlertsPage**: Alert configuration
- **QueryPage**: Custom query builder
- **CustomMetricsPage**: Formula-based metrics
- **SettingsPage**: Application settings

### Reusable Components
- **Sidebar**: Navigation menu with collapsible state
- **Header**: Top bar with search, status, time
- **MetricCard**: Displays metric value with trend
- **LineChart**: Time-series visualization
- **BarChart**: Comparative data visualization
- **DataTable**: Sortable, filterable data grid

## Styling

### Design System
- **Colors**: Primary (#3b82f6), Secondary (#6366f1), Success (#10b981), etc.
- **Spacing**: 4px, 8px, 12px, 16px, 20px, 24px units
- **Typography**: System fonts, responsive sizes
- **Components**: Cards, buttons, forms, alerts, spinners
- **Animations**: Smooth transitions (0.3s ease-in)

### Responsive Breakpoints
- Desktop: 1024px+
- Tablet: 768px - 1023px
- Mobile: < 768px

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Development

### Adding a New Page

1. Create component in `src/pages/NewPage.jsx`
2. Add route in `App.jsx`
3. Add navigation in `Sidebar.jsx`
4. Create styles as needed

### Adding API Integration

1. Add methods to `src/services/api.js`
2. Use in components via direct import
3. Handle loading/error states

### Building Components

Use existing components as templates:
```jsx
import MetricCard from '../components/MetricCard'

<MetricCard
  title="Revenue"
  value={15420}
  unit="$"
  trend={12}
/>
```

## Performance

- Vite for fast builds and dev server
- React 18 for optimal rendering
- Lazy loading for routes
- Chart.js for efficient visualization
- Axios caching support

## Deployment

### Build
```bash
npm run build
```

### Deploy to production:
1. Copy `/dist` folder to web server
2. Configure API_URL to production backend
3. Serve via nginx/Apache with SPA rewrite rules

### Docker Example
```dockerfile
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## Documentation

- Full API Reference: See `/API_REFERENCE.md` in backend
- Phase 10 Implementation: See `/PHASE_10_COMPLETE_SUMMARY.md`
- Component Stories: Check component JSDoc comments

## Support

For issues or questions:
1. Check existing issues
2. Review component documentation
3. Check backend API reference
4. Review Phase 10 documentation

## License

MIT
