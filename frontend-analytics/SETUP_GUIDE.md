# Frontend Analytics Dashboard - Setup Guide

## Quick Start (5 minutes)

```bash
# Navigate to frontend directory
cd frontend-analytics

# Install dependencies
npm install

# Start development server
npm run dev
```

Open http://localhost:3000 in your browser.

## Login

You have two options:

**Option 1: Demo Login (Recommended)**
- Click "Try Demo Login" button
- Instantly logs in with test credentials

**Option 2: Manual Login**
- Email: admin@example.com
- Password: any password
- Tenant ID: tenant-1

## Features Available

### 1. Dashboard
- Real-time metrics overview
- System performance charts
- Activity feed
- Recent alerts

### 2. Metrics
- Metric listing with filtering
- Type-based filtering (System, Service, Business)
- Trend analysis
- Detailed metric views

### 3. Reports
- Create scheduled reports
- Multiple report types
- Format selection (PDF, Excel, JSON)
- Report history

### 4. Dashboards
- Create custom dashboards
- Add/remove widgets
- Share dashboards
- Widget configuration

### 5. Alerts
- Configure metric alerts
- Set threshold conditions
- Adjust severity levels
- View alert history

### 6. Queries
- Create custom queries
- Save query templates
- Execute and view results
- Query history

### 7. Custom Metrics
- Create calculated metrics
- Define formulas using metrics
- Track calculation history
- Enable/disable metrics

### 8. Settings
- API configuration
- Theme selection
- Date format preferences
- Timezone settings
- Auto-refresh options

## API Connection

The frontend automatically connects to:
```
http://localhost:5009
```

If your backend is on a different URL, update in Settings:
1. Go to Settings page
2. Update "API Base URL"
3. Save settings

## Environment Variables

Create `.env` file in project root:

```bash
REACT_APP_API_URL=http://localhost:5009
```

## Production Build

```bash
# Build optimized version
npm run build

# Preview production build
npm run preview

# Deploy to web server
# Copy dist/ folder contents to your web server
```

## Troubleshooting

### 401 Unauthorized Error
- Make sure backend is running on port 5009
- Try "Try Demo Login" to get valid token
- Check if JWT token in localStorage is valid

### CORS Error
- Backend must have CORS enabled (it does by default in Phase 10)
- Check API URL in settings

### Charts Not Displaying
- Install chart.js: `npm install chart.js`
- Restart dev server

### Can't Connect to Backend
- Verify backend is running: `cd services/analytics-service && python main.py`
- Check backend port: should be 5009
- Verify API URL in Settings page

## Development Tips

### React Developer Tools
Install React DevTools extension for browser debugging

### Vite Dev Server
- Hot Module Replacement (HMR) enabled
- Fast rebuild on save
- Network proxy to backend

### File Structure
```
frontend-analytics/
├── src/
│   ├── pages/        → Page components
│   ├── components/   → Reusable components
│   ├── services/     → API clients
│   ├── hooks/        → Custom hooks
│   └── styles/       → CSS files
├── public/           → Static assets
└── vite.config.js    → Build configuration
```

### Adding New Pages

1. Create file: `src/pages/NewPage.jsx`
2. Update `src/App.jsx` to add route
3. Update `src/components/Sidebar.jsx` for navigation

### Adding New Components

1. Create file: `src/components/NewComponent.jsx`
2. Import in pages where needed
3. Add styles to `src/styles/`

## Common Tasks

### Change API Endpoint
- Settings page → API Base URL field

### Create Real API Connection
1. Update methods in `src/services/api.js`
2. Backend must return correct data format
3. Handle loading/error states in components

### Customize Colors
Edit `src/styles/index.css`:
```css
:root {
  --primary-color: #3b82f6;
  --success-color: #10b981;
  /* etc */
}
```

### Add New Metric Type
1. Update filter in MetricsPage.jsx
2. Add to backend custom metrics

### Change Dashboard Layout
Edit `src/styles/pages.css` for grid layouts

## Performance Optimization

### Already Implemented
- ✅ Component memoization
- ✅ Efficient re-renders
- ✅ CSS-in-JS avoided
- ✅ Lazy route loading ready
- ✅ Vite bundle optimization

### Future Improvements
- Add React.memo() for pure components
- Implement route code-splitting
- Add service worker for offline support
- Implement virtual scrolling for large tables

## Browser Debugging

### Check Console
Open DevTools (F12 or Cmd+Option+I)
- Check for errors
- Review API calls
- Check localStorage for token

### Network Tab
- Verify API calls to backend
- Check response status
- View request/response data

### Application Tab
- View localStorage (token, tenantId, user)
- Check session storage
- View cookies

## Deployment Checklist

- [ ] Backend running on production URL
- [ ] Update REACT_APP_API_URL for production
- [ ] Run `npm run build`
- [ ] Test production build: `npm run preview`
- [ ] Deploy dist/ folder to web server
- [ ] Configure web server for SPA routing

## Getting Help

1. **Check Backend Status**: Visit http://localhost:5009/health
2. **Review Browser Console**: Check for JavaScript errors
3. **Check Network Tab**: Verify API requests succeed
4. **Review Documentation**: See backend API_REFERENCE.md
5. **Check Phase 10 Summary**: See PHASE_10_COMPLETE_SUMMARY.md

## Next Steps

1. ✅ Frontend running and connected
2. 📊 Explore all dashboard features
3. 📝 Create custom dashboards
4. ⚙️ Configure alerts
5. 📊 Generate reports
6. 🚀 Deploy to production
