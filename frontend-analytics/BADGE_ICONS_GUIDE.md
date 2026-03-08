# Badge Icons Implementation Guide

## Overview
Enhanced badges with icon support across the dashboard for a more visual and refined experience.

## Available Badge Components

### 1. FormatBadge
Used for file formats and conversion types.
```jsx
import { FormatBadge } from '../utils/badgeIcons';

<FormatBadge format="PNG" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }} />
```

**Supported Formats:**
- Documents: PDF, DOC, DOCX, TXT, XLSX, XLS, CSV
- Images: JPG, JPEG, PNG, GIF, SVG, WebP, ICO
- Audio: MP3, WAV, FLAC, AAC
- Video: MP4, AVI, MOV, MKV, WebM

### 2. StatusBadge
Used for job/task status indicators.
```jsx
import { StatusBadge, getStatusIcon } from '../utils/badgeIcons';

<StatusBadge status="completed" text="Completed" style={{ backgroundColor: '#10b981' }} />
```

**Supported Statuses:**
- Success: completed, success, done
- Processing: processing, running, in-progress
- Pending: pending, queued, waiting
- Failed: failed, error, cancelled
- Active/Inactive: active, inactive
- Info: warning, info

### 3. RoleBadge
Used for user roles.
```jsx
import { RoleBadge, getRoleIcon } from '../utils/badgeIcons';

<RoleBadge role="Admin" style={...} />
```

**Supported Roles:**
- Admin, Administrator
- Manager, Lead
- Analyst, Data Analyst
- Viewer, Guest
- User, Member

### 4. PlanBadge
Used for subscription/plan badges.
```jsx
import { PlanBadge, getPlanIcon } from '../utils/badgeIcons';

<PlanBadge plan="Pro" style={...} />
```

**Supported Plans:**
- Free, Starter, Pro, Premium, Enterprise, Business

### 5. BadgeWithIcon
Generic badge component with custom icon.
```jsx
import { BadgeWithIcon } from '../utils/badgeIcons';
import { FiDownload } from 'react-icons/fi';

<BadgeWithIcon icon={<FiDownload />} text="Download" className="format-badge" />
```

## Icon Sets Used
- **Feather Icons (react-icons/fi)**: Lightweight, consistent 24px icons
- Includes: File, Image, Music, Video, Lock, User, Check, Alert, etc.

## CSS Classes

### Badge Display
- `.badge-with-icon`: Wrapper for icon + text
- `.badge-icon`: Icon container
- `.badge-text`: Text container

### Animations
- **Subtle Pulse**: Status badges pulse gently (2s cycle)
- **Spin**: Processing icons rotate continuously
- **Hover Lift**: All badges translate up on hover

## Usage Examples

### In Tables
```jsx
// Old way (text only)
<td className="format-badge">{job.inputFormat}</td>

// New way (with icon)
<td>
  <FormatBadge format={job.inputFormat} />
</td>
```

### With Custom Styles
```jsx
<StatusBadge 
  status="failed" 
  text="Failed"
  style={{ 
    backgroundColor: '#ef4444',
    boxShadow: '0 4px 12px rgba(239, 68, 68, 0.3)'
  }} 
/>
```

### Dynamic Colors
```jsx
<FormatBadge 
  format={user.plan} 
  style={{ 
    background: `linear-gradient(135deg, ${planColor} 0%, ${adjustBrightness(planColor, -20)} 100%)`
  }} 
/>
```

## Icon Sizing
All icons use consistent `size={14}` for badges, ensuring perfect alignment with text.

## Accessibility
- Icons have proper ARIA labels through semantic HTML
- Color is not the only means of conveyance
- High contrast ratios maintained
- Touch targets: minimum 36px buttons

## Performance
- Tree-shakeable icons from react-icons/fi
- Only imported icons are bundled
- SVG-based, scalable to any size
- No additional dependencies beyond react-icons

## Migration Notes
1. Install: `npm install react-icons`
2. Import badge components from `utils/badgeIcons.jsx`
3. Replace existing badge elements with component versions
4. Maintain style props for custom colors

## Benefits
✓ Visual clarity with meaningful icons
✓ Consistent design across dashboard
✓ Better user recognition and scanning
✓ Professional, modern appearance
✓ Lightweight and performant
✓ Easy to customize and extend
