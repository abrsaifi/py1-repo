# Phase 2 Developer's Technical Reference

## 🔧 Code Location Reference

### CSS Added (210 lines)
**File**: `templates/Index.html` - Lines ~1450-1665
**Before**: `  </style>` tag at line 1455
**After**: New CSS classes before original closing tag

#### CSS Classes Added:

**Search Box**
```css
.param-search-box { ... }        /* Search container */
.search-results { ... }           /* Results counter */
.search-results.found { ... }     /* Found state */
```

**Settings Toolbar**
```css
.settings-toolbar { ... }         /* Button container */
.settings-toolbar button { ... }  /* Button styling */
.btn-danger { ... }               /* Reset button */
.btn-success { ... }              /* Save button */
```

**Hidden/Visible States**
```css
.param-group.hidden { ... }       /* Hide groups */
.form-group.hidden { ... }        /* Hide params */
```

**Modals**
```css
.modal { ... }                    /* Modal overlay */
.modal.show { ... }               /* Show modal */
.modal-content { ... }            /* Content box */
.modal-header { ... }             /* Header */
.modal-body { ... }               /* Body */
.modal-footer { ... }             /* Footer */
.btn-primary { ... }              /* Primary button */
.btn-secondary { ... }            /* Secondary button */
```

**Custom Presets**
```css
.presets-divider { ... }          /* "Custom Presets" header */
.custom-preset-card { ... }       /* Custom preset styling */
.custom-preset-badge { ... }      /* "Custom" label */
.custom-preset-delete { ... }     /* Delete button */
```

---

### HTML Added (35 lines)
**File**: `templates/Index.html` 

#### Search Box (Advanced Tab)
**Location**: Inside `id="tab-advanced"` container (lines ~1795-1812)
```html
<div class="param-search-box">
  <i class="fa-regular fa-magnifying-glass"></i>
  <input type="text" id="paramSearch" placeholder="Search parameters..." onkeyup="searchParameters(this.value)">
  <span class="search-results" id="searchResults">All parameters</span>
</div>
```

#### Settings Toolbar (Bottom of Advanced Tab)
**Location**: Below `advancedParamsContainer` (lines ~1812-present)
```html
<div class="settings-toolbar">
  <button onclick="resetSettings()" class="btn-danger">...</button>
  <button onclick="saveAsPreset()" class="btn-success">...</button>
  <button onclick="exportSettings()">...</button>
  <button onclick="importSettings()">...</button>
</div>
```

#### Modals (After serviceSettingsContainer)
**Location**: Lines ~1820-present
- `savePresetModal` - For saving custom presets
- `importModal` - For importing settings

---

### JavaScript Functions (605 lines)
**File**: `templates/Index.html` - Lines ~3025-3200 (Phase 2 section)

#### Search Function
```javascript
function searchParameters(query) {
  // Filters parameters based on query
  // Shows/hides param-group and form-group elements
  // Updates results counter
  // ~60 lines
}
```

#### Reset Function
```javascript
function resetSettings() {
  // Confirms reset action
  // Resets all parameter values to defaults
  // Clears search box
  // ~40 lines
}
```

#### Save Preset Functions
```javascript
function saveAsPreset() {
  // Opens save dialog modal
  // ~5 lines

function confirmSavePreset() {
  // Validates preset name
  // Saves to localStorage
  // Refreshes presets display
  // ~35 lines

function deleteCustomPreset(toolName, presetName) {
  // Confirms deletion
  // Removes from localStorage
  // Refreshes display
  // ~15 lines
}
```

#### Export/Import Functions
```javascript
function exportSettings() {
  // Creates JSON from current parameters
  // Triggers download
  // ~20 lines

function importSettings() {
  // Opens import dialog
  // ~5 lines

function confirmImport() {
  // Reads selected file
  // Parses JSON
  // Applies settings
  // Validates tool name
  // Error handling
  // ~50 lines
}
```

#### Modal Management
```javascript
function closeSavePresetModal() { ... }     // 1 line
function closeImportModal() { ... }          // 1 line

// Event listeners for click-outside closing
document.getElementById('savePresetModal').addEventListener('click', ...)
document.getElementById('importModal').addEventListener('click', ...)
```

---

## 🔌 Integration Points

### Where Functions are Called

**Search Box** → `onkeyup="searchParameters(this.value)"`
- Real-time as user types

**Reset Button** → `onclick="resetSettings()"`
- Immediate when clicked

**Save Button** → `onclick="saveAsPreset()"`
- Opens modal dialog

**Export Button** → `onclick="exportSettings()"`
- Immediate download

**Import Button** → `onclick="importSettings()"`
- Opens modal dialog

**Modal Buttons** → `onclick="confirmSavePreset()"`
- When user confirms action

**Delete Button** → `onclick="deleteCustomPreset(toolName, preset)"`
- When user hovers and clicks X

---

## 💾 Data Structure

### localStorage Format

**Custom Presets Key**
```
custom_presets_{toolName}
Example: custom_presets_To PDF
```

**Value (JSON)**
```javascript
{
  "Preset Name": {
    "param1": "value1",
    "param2": "value2",
    ...
  }
}
```

**Example**
```javascript
// localStorage['custom_presets_To PDF']
{
  "My Reports": {
    "orientation": "portrait",
    "paper_size": "A4",
    "margin_top": "20",
    ...
  },
  "Client A": {
    "orientation": "landscape",
    ...
  }
}
```

### Export File Format

**Filename**: `{ToolName}_settings_{DATE}.json`
**Example**: `To PDF_settings_2025-02-22.json`

**Content**:
```json
{
  "tool": "To PDF",
  "params": {
    "orientation": "portrait",
    "paper_size": "A4",
    ...
  }
}
```

---

## 🎯 Function Signatures

### Phase 2 Functions

```javascript
// Search & Filter
searchParameters(query: string) → void
  // Filters params based on query string

// Reset
resetSettings() → void
  // Resets all params to defaults after confirmation

// Save Preset
saveAsPreset() → void
  // Opens modal for preset name
  
confirmSavePreset() → void
  // Saves current values to localStorage

deleteCustomPreset(toolName: string, presetName: string) → void
  // Removes preset from localStorage

// Export/Import
exportSettings() → void
  // Downloads current settings as JSON

importSettings() → void
  // Opens file dialog

confirmImport() → void
  // Loads settings from selected JSON file
```

---

## 🧪 Testing Checklist for Developers

### Unit Tests to Add
- [ ] searchParameters filters correctly
- [ ] resetSettings resets all param types
- [ ] saveAsPreset validates name
- [ ] Custom presets save to localStorage
- [ ] deleteCustomPreset removes from storage
- [ ] exportSettings creates valid JSON
- [ ] importSettings parses JSON correctly
- [ ] Import validates tool name

### Integration Tests to Add
- [ ] Search works with all parameter types
- [ ] Reset preserves other tabs
- [ ] Saved presets appear in Presets tab
- [ ] Export file can be imported
- [ ] Presets persist across refresh
- [ ] Multiple tools have separate presets

### Browser Compatibility
- [ ] Chrome/Edge - all features
- [ ] Firefox - all features
- [ ] Safari - all features
- [ ] Mobile Safari - all features
- [ ] Chrome Mobile - all features

---

## 🔍 Key Implementation Details

### Search Algorithm
1. Get all form-groups in advanced tab
2. For each group, check if label text contains query
3. Hide group if no match, show if match
4. For param-groups, hide if all children are hidden
5. Update results counter

### Reset Implementation
1. Confirm with dialog
2. For each param in SERVICE_PARAMETERS:
   - Get input element by param.name
   - Set value to param.default
   - For ranges: update display and gradient
   - For checkboxes: set checked property

### Save Preset Implementation
1. Validate preset name is not empty
2. Create object with all parameter values
3. Get or create custom_presets_{toolName} object
4. Add new preset to object
5. Save to localStorage
6. Refresh presets display

### Import Implementation  
1. Read file as text
2. Parse JSON
3. Validate tool name matches
4. For each param in file:
   - Get input element
   - Update value
   - Update displays
   - Update gradients

---

## 🚀 Performance Considerations

### Search Performance
- Current: O(n) where n = number of params
- Acceptable: <100ms even with regex
- Optimization: Could add debouncing if >100 params

### localStorage Performance
- Reads: <1ms typical
- Writes: <10ms typical
- Limit: ~5MB per origin (plenty for presets)

### DOM Operations
- Reset: Batch updates (no animation lag)
- Search: Direct classList toggle (fast)
- Modal: CSS animations only (smooth)

---

## 🐛 Debugging Tips

### Check localStorage
```javascript
// In browser console:
console.log(localStorage.getItem('custom_presets_To PDF'))
console.table(JSON.parse(localStorage.getItem('custom_presets_To PDF')))
```

### Check All Presets
```javascript
// List all custom presets across all tools
for (let i = 0; i < localStorage.length; i++) {
  let key = localStorage.key(i);
  if (key.startsWith('custom_presets_')) {
    console.log(key, JSON.parse(localStorage.getItem(key)));
  }
}
```

### Test Search
```javascript
// In console while Advanced tab open:
searchParameters('margin');  // Filter to margin params
searchParameters('');        // Show all
```

### Clear All Custom Presets
```javascript
// Remove all custom presets:
for (let i = 0; i < localStorage.length; i++) {
  let key = localStorage.key(i);
  if (key.startsWith('custom_presets_')) {
    localStorage.removeItem(key);
  }
}
location.reload();
```

---

## 📊 Code Metrics

| Metric | Value |
|--------|-------|
| Phase 2 CSS | 210 lines |
| Phase 2 HTML | 35 lines |
| Phase 2 JavaScript | 605 lines |
| Functions Added | 10 |
| CSS Classes Added | 18 |
| Event Listeners | 15+ |

---

## 🔄 Update Scenarios

### Adding New Tool
1. Tool inherits all Phase 2 features automatically
2. If SERVICE_PARAMETERS defined: full feature support
3. Custom presets stored separately per tool
4. Search works on tool's parameters

### Adding New Parameter Type
1. In `renderServiceSettings()`: `createParamElement()`
2. Add case for new type
3. Set/get value appropriately
4. Search algorithm already supports

### Changing Parameter Categories
1. Edit `getParameterCategory()` function
2. Add/remove parameters from category lists
3. Color coding updates automatically

---

## 📝 Code Style

### JavaScript Style Used
- Camel case for functions: `saveAsPreset()`
- Camel case for variables: `customPresets`
- Arrow functions: `() => { ... }`
- Template literals: `` `${value}` ``
- const/let (no var)

### CSS Style Used
- BEM-like naming: `.param-search-box`
- CSS variables: `var(--accent-primary)`
- Flexbox for layout
- CSS transitions for animations
- Mobile-first media queries

### HTML Style Used
- Semantic HTML5
- ARIA for accessibility
- Data attributes: `data-tab="basic"`
- Event listeners via onclick attributes

---

## 🎓 Learning Resources

### For Understanding the Code
1. Start with CSS (simplest)
2. Then HTML (structure)
3. Then JavaScript (most complex)

### Key Files to Study
- `templates/Index.html` lines 1450-1665 (CSS)
- `templates/Index.html` lines 1795-1850 (HTML)
- `templates/Index.html` lines 3025-3200 (JavaScript)

### Useful Resources
- MDN localStorage: https://mdn.io/window.localStorage
- JSON stringify/parse: https://mdn.io/JSON
- classList API: https://mdn.io/classList

---

## ✅ Checklist for Code Review

- [ ] All CSS classes properly scoped
- [ ] No naming conflicts with Phase 1
- [ ] JavaScript functions have proper error handling
- [ ] localStorage keys are unique
- [ ] Modal dialogs close on escape (click outside)
- [ ] All buttons have tooltips/clear labels
- [ ] Search is real-time and responsive
- [ ] Import validates JSON structure
- [ ] Export creates valid JSON
- [ ] No console errors
- [ ] Performance is acceptable
- [ ] Code is properly commented
- [ ] No unused variables/styles

---

**Phase 2 Technical Documentation Complete** ✅

*For user-facing documentation, see PHASE_2_VISUAL_TESTING_GUIDE.md*
