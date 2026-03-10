# Adding Service Settings - Developer Guide

## Quick Start: Add Settings to Any Service

### Step 1: Add to SERVICE_PARAMETERS (Frontend)

Open `templates/Index.html` and find the `SERVICE_PARAMETERS` object (around line 1240).

Add your service:

```javascript
'Your Service Name': {
  label: 'Display Label',
  params: [
    {
      name: 'param_id',
      label: 'Parameter Label',
      type: 'range',
      min: 0,
      max: 100,
      default: 50,
      step: 1,
      help: 'Help text explain what this does'
    }
  ],
  presets: {
    'Preset Name': {
      param_id: 75
    }
  }
}
```

### Step 2: Handle in Backend (Python)

In `execute_service_conversion()` function in `server.py`:

```python
elif tool_name == 'Your Service Name':
    # Get parameters from kwargs
    param_value = kwargs.get('param_id', 50)
    
    # Pass to your conversion function
    return your_conversion_func(input_path, output_path, param_value)
```

### Step 3: Create/Update Conversion Function

```python
def your_conversion_func(input_file, output_file, param_value):
    """Process file with custom parameter"""
    try:
        # Use param_value in your logic
        # ... do your conversion ...
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
```

---

## Parameter Type Reference

### 1. Range Slider

**When to use**: For continuous values (DPI, quality, opacity, etc.)

```javascript
{
  name: 'quality',
  label: 'Quality',
  type: 'range',
  min: 1,
  max: 100,
  default: 85,
  step: 5,
  help: 'Higher = better quality but larger files'
}
```

**Output Format**: String (e.g., "85")

**Backend Handling**:
```python
quality = int(kwargs.get('quality', 85))
```

---

### 2. Select Dropdown

**When to use**: For choosing from predefined options

```javascript
{
  name: 'format',
  label: 'Output Format',
  type: 'select',
  values: ['jpg', 'png', 'webp'],
  default: 'jpg',
  help: 'Choose output file format'
}
```

**Output Format**: String (selected value)

**Backend Handling**:
```python
format_choice = kwargs.get('format', 'jpg')
```

---

### 3. Number Input

**When to use**: For specific numeric values (width, height, etc.)

```javascript
{
  name: 'width',
  label: 'Width (pixels)',
  type: 'number',
  min: 50,
  max: 4000,
  default: 800,
  help: 'Target width in pixels'
}
```

**Output Format**: String (convertible to int)

**Backend Handling**:
```python
width = int(kwargs.get('width', 800))
```

---

### 4. Text Input

**When to use**: For custom text (watermarks, names, etc.)

```javascript
{
  name: 'watermarkText',
  label: 'Watermark Text',
  type: 'text',
  default: 'WATERMARK',
  help: 'Text to display as watermark'
}
```

**Output Format**: String

**Backend Handling**:
```python
text = kwargs.get('watermarkText', 'WATERMARK')
```

---

### 5. Checkbox

**When to use**: For yes/no toggles

```javascript
{
  name: 'removeMetadata',
  label: 'Remove Metadata',
  type: 'checkbox',
  default: true,
  help: 'Strip document information'
}
```

**Output Format**: String ("true" or "false") or Boolean

**Backend Handling**:
```python
remove = kwargs.get('removeMetadata', 'true').lower() in ('true', '1', 'on')
```

---

### 6. Password Field

**When to use**: For sensitive input (passwords, API keys)

```javascript
{
  name: 'password',
  label: 'Password',
  type: 'password',
  default: 'password123',
  help: 'Set password protection'
}
```

**Output Format**: String (masked in UI)

**Backend Handling**:
```python
password = kwargs.get('password', 'password123')
```

---

## Presets: Quick Settings Collections

Presets are one-click configurations. Define them in the `presets` object:

```javascript
'Your Service': {
  label: 'Service Label',
  params: [ /* ... */ ],
  presets: {
    'Preset 1': {
      param1: value1,
      param2: value2,
      param3: value3
    },
    'Preset 2': {
      param1: value1,
      param2: value2,
      param3: value3
    }
  }
}
```

**Frontend generates buttons automatically:**
```
[Preset 1] [Preset 2]
```

**On click:** All parameters auto-fill with preset values

---

## Complete Example: Adding PDF Page Extraction Settings

### Frontend (SERVICE_PARAMETERS)

```javascript
'ExtractPages': {
  label: 'Extract Pages',
  params: [
    {
      name: 'pages',
      label: 'Pages (e.g., 1, 3, 5-8)',
      type: 'text',
      default: '1',
      help: 'Enter page numbers/ranges to extract'
    }
  ],
  presets: {
    'First Page': { pages: '1' },
    'First 5': { pages: '1-5' },
    'Every Other': { pages: '1, 3, 5, 7, 9' }
  }
}
```

### Backend (execute_service_conversion)

```python
elif tool_name == 'ExtractPages':
    pages_input = kwargs.get('pages', '1')
    page_list = parse_page_numbers(pages_input)
    if page_list:
        return extract_pdf_pages(input_path, output_path, page_list)
    return False
```

### Backend (Conversion Function)

```python
def extract_pdf_pages(input_pdf, output_pdf, pages):
    """Extract specific pages from PDF"""
    try:
        src = fitz.open(input_pdf)
        out = fitz.open()
        for p in pages:
            idx = int(p)
            if 0 <= idx < len(src):
                page = src[idx]
                # Copy page to new PDF
                out.insert_pdf(src, from_page=idx, to_page=idx)
        out.save(output_pdf)
        out.close()
        src.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
```

---

## Testing Your Settings

### Frontend Testing

1. **Check JavaScript Console**
```javascript
// In browser console
console.log(SERVICE_PARAMETERS['Your Service'])
// Should show your config
```

2. **Test Parameter Collection**
```javascript
// Open conversion, set values, click convert
// Check Network tab → api/convert POST body
// Should contain your parameters
```

### Backend Testing

1. **Print Received Values**
```python
def execute_service_conversion(tool_name, input_path, output_path, **kwargs):
    print(f"Tool: {tool_name}")
    print(f"Parameters: {kwargs}")
    # ... rest of function
```

2. **Test Conversion Function**
```python
# Create test file and call directly
result = your_conversion_func('test.pdf', 'output.pdf', param_value=50)
print(f"Result: {result}")
```

---

## Checklist: Adding Service Settings

- [ ] Service visible in SERVICE_PARAMETERS
- [ ] All param types are supported (text, range, select, etc.)
- [ ] Help text is clear and helpful
- [ ] Default values are sensible
- [ ] Presets cover common use cases
- [ ] Backend receives parameters in `**kwargs`
- [ ] Backend passes to conversion function
- [ ] Conversion function uses parameters correctly
- [ ] Test with different parameter values
- [ ] Test with preset buttons
- [ ] Verify output quality changes as expected
- [ ] Document the settings in SERVICE_SETTINGS_GUIDE.md

---

## Best Practices

### 1. **Sensible Defaults**
Every parameter should have a default that works for most users.
```javascript
// Good
default: 300  // Common DPI value

// Bad
default: ''   // User confused, might fail
```

### 2. **Range Limits**
Set realistic min/max values for ranges.
```javascript
// Good
min: 1, max: 100

// Bad
min: -999, max: 999999  // Confusing
```

### 3. **Step Increments**
Use step values that make sense.
```javascript
// Good
step: 5  // For DPI (150, 155, 160...)

// Bad
step: 0.1  // Creates 1000 values in range
```

### 4. **Help Text**
Always explain what the parameter does.
```javascript
// Good
help: 'Higher DPI = better quality but slower processing'

// Bad
help: 'DPI'  // Doesn't help
```

### 5. **Preset Names**
Use clear, descriptive preset names.
```javascript
// Good
'High Quality': { ... }
'Web Standard': { ... }
'Mobile Optimized': { ... }

// Bad
'Preset1': { ... }
'Preset2': { ... }
```

### 6. **Parameter Naming**
Use camelCase that's consistent with backend.
```javascript
// Good - matches backend exactly
formData.append('watermarkText', value)
# Backend
watermark_text = request.form.get('watermarkText')

// Bad - inconsistent naming
formData.append('watermark-text', value)
# Won't match on backend
```

---

## Service Settings Template

Copy this template to add a new service:

```javascript
'New Service Name': {
  label: 'Display Name',
  params: [
    {
      name: 'param1',
      label: 'Parameter 1',
      type: 'range',  // or select, text, number, checkbox, password
      min: 0,
      max: 100,
      default: 50,
      step: 1,
      help: 'What does this parameter do?'
    },
    // Add more params as needed
  ],
  presets: {
    'Preset Name 1': {
      param1: 30
    },
    'Preset Name 2': {
      param1: 70
    }
  }
}
```

---

## Common Service Settings Patterns

### Image Processing Service
```javascript
{
  params: [
    { name: 'quality', type: 'range', min: 1, max: 100, default: 85 },
    { name: 'format', type: 'select', values: ['jpg', 'png', 'webp'] }
  ]
}
```

### PDF Manipulation Service
```javascript
{
  params: [
    { name: 'pages', type: 'text', default: '1-10' },
    { name: 'optimization', type: 'checkbox', default: true }
  ]
}
```

### Batch Processing Service
```javascript
{
  params: [
    { name: 'parallel', type: 'checkbox', default: true },
    { name: 'timeout', type: 'number', min: 30, max: 300, default: 60 }
  ]
}
```

---

## Troubleshooting

### Settings Don't Appear
```
1. Check SERVICE_PARAMETERS spelling matches service name exactly
2. Verify browser console for JavaScript errors
3. Reload page with Ctrl+Shift+R (hard refresh)
4. Check in DevTools → Application → localStorage (settings saved?)
```

### Parameters Not Sent to Backend
```
1. Verify parameter 'name' values
2. Check that inputs actually have those IDs
3. Inspect Network tab → POST body
4. Print kwargs in backend to verify received
```

### Presets Not Working
```
1. Check preset parameter names match param.name
2. Verify preset values are valid for that param type
3. Check console for JavaScript errors on preset click
4. Test with single preset first before multiple
```

### Backend Not Using Parameters
```
1. Verify kwargs contains expected parameters
2. Print kwargs at start of execute_service_conversion()
3. Check parameter names match between frontend and backend
4. Verify conversion function signature includes parameters
```

---

## Getting Help

**For Frontend Issues:**
- Check browser console (F12 → Console tab)
- Inspect HTML elements (F12 → Elements tab)
- Look at Network tab (F12 → Network tab)

**For Backend Issues:**
- Check Flask console output
- Add print() statements to debug
- Check test_service_integration.py

**For Service-Specific Issues:**
- Review SERVICE_SETTINGS_GUIDE.md
- Check corresponding conversion function
- Test function separately from Flask

---

## Summary

**Adding service settings is easy:**
1. ✅ Add to SERVICE_PARAMETERS dict
2. ✅ Handle in execute_service_conversion()
3. ✅ Use in conversion function
4. ✅ Test frontend and backend
5. ✅ Document in guides

That's it! The UI and parameter collection is handled automatically.
