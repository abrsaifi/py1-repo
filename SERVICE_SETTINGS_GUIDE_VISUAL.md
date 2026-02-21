# Service Settings - Quick Reference & Visual Guide

## 🎨 What You'll See in the Conversion Studio

### Right Panel Layout

```
╔════════════════════════════════════════╗
║  settings for PDF to B&W              ║
╠════════════════════════════════════════╣
│                                       │
│  Output Format                        │
│  [Auto-detect  ▼]                     │
│                                       │
│  Quality                              │
│  [Medium (balanced) ▼]                │
│                                       │
├─── PDF to B&W Options ────────────────┤
│                                       │
│  DPI (Resolution)                     │
│  Higher DPI = better quality          │
│                                       │
│  ●─────────────────────────────○ 300 │
│  [150] [200] [300] [400]             │
│                                       │
│  Threshold                            │
│  Contrast threshold (100-255)         │
│                                       │
│  ●────────────────────────────○ 250  │
│  [100]         [250]         [255]  │
│                                       │
│  Contrast                             │
│  Contrast enhancement (1-5)           │
│                                       │
│  ○────────────────────────────●  3.0 │
│                                       │
│  ⚙️ Quick Presets:                    │
│  [Document] [Photo] [Technical]      │
│                                       │
│                    [START CONVERSION] │
│                                       │
╚════════════════════════════════════════╝
```

---

## 🔘 Interactive Elements

### Range Sliders
- **Appearance**: Gradient bar from left (min) to right (max)
- **Interaction**: Click or drag the circular thumb
- **Value Display**: Real-time number shown on the right
- **Color**: Changes from accent color to gray based on value

Example interaction:
```
Before click:     ●─────────────────────────────○
After adjustment:      ●─────────────────────  75 │
                       │
                    Value updates
                    in real-time
```

### Dropdown Menus
- **Click to Open**: Shows all available options
- **Select One**: Highlights and closes
- **Selected Value**: Displayed in the field

Example:
```
[150 ▼]  →  150 selected
            200 selected  ✓
            300 selected
            400 selected
```

### Checkboxes
- **Click to Toggle**: ON/OFF state
- **Visual Feedback**: Checkmark appears/disappears
- **Color**: Uses accent color when checked

Example:
```
☐ Remove Metadata  →  ☑ Remove Metadata
(unchecked)           (checked)
```

### Preset Buttons
- **Quick Apply**: Click to instantly apply settings
- **Visual Feedback**: Button highlights on hover
- **Confirmation**: Toast message shows preset name applied

Example:
```
[Document] [Photo] [Technical]
  ↑ Click "Technical"
  
Toast: "Applied preset: Technical"
Settings auto-fill:
  DPI: 400
  Threshold: 200
  Contrast: 4.0
```

---

## 📝 Input Types Explained

### Text Input (for custom text)
```
Watermark Text
[_________________________________]
   Type watermark text here
```

### Number Input (for dimensions)
```
Width (px)
[800________________] px
```

### Range Slider (for continuous values)
```
Quality
[●─────────────────────────○] 85
```

### Select Dropdown (for predefined options)
```
Position
[diagonal ▼]
```

### Checkbox (for yes/no options)
```
☑ Keep Aspect Ratio
```

### Password Field (for security)
```
Password
[●●●●●●●●] (masked for security)
```

---

## 🎯 Popular Service Settings

### PDF to B&W (Black & White Conversion)

**When to use each preset:**

1. **Document Preset** (Default)
   - Best for: Text documents, forms, letters
   - DPI: 300 (standard quality)
   - Threshold: 250 (keep text clear)
   - Contrast: 3.0 (normal)
   - Result: Professional clean B&W

2. **Photo Preset**
   - Best for: Photographs, images with gradients
   - DPI: 200 (smaller file size)
   - Threshold: 200 (softer tones)
   - Contrast: 2.5 (reduced)
   - Result: Smoother grayscale

3. **Technical Preset**
   - Best for: Drawings, schematics, blueprints
   - DPI: 400 (maximum detail)
   - Threshold: 200 (includes fine lines)
   - Contrast: 4.0 (enhanced)
   - Result: Crisp technical drawing

**Customizing:**
- Lower Threshold = lighter output (less text visible)
- Higher Threshold = darker output (all text visible)
- Increase Contrast = more separation between light/dark

---

### Image Resize

**Social Media Dimensions:**
- Instagram: 1080×1080 (square)
- Twitter: 1200×675 (16:9)
- Facebook: 1200×630
- LinkedIn: 1200×627

**Web Sizes:**
- Thumbnail: 200×200
- Small: 400×300
- Medium: 800×600
- Large: 1024×768
- Full HD: 1920×1080

**Pro Tip:** Keep "Aspect Ratio" enabled unless you specifically want to stretch/compress

---

### Add Watermark

**Position Options:**
```
┌─────────────┐
│TL  TOP  TR  │  TL=Top-Left
│             │  TR=Top-Right
│LT CENTER RT │  BL=Bottom-Left
│             │  BR=Bottom-Right
│BL BOTTOM BR │  CENTER=Dead center
└─────────────┘  DIAGONAL=Angled
```

**Opacity Guide:**
- **0.1-0.3**: Very subtle (background watermark)
- **0.4-0.6**: Visible but not intrusive (typical)
- **0.7-1.0**: Very obvious (protection/notice)

**Examples:**
```
Opacity 0.2: WATERMARK (barely visible)
Opacity 0.5: WATERMARK (clearly visible)
Opacity 0.8: WATERMARK (very prominent)
```

---

### Image Compression

**Quality Settings Explained:**
```
Quality 10-30:   Tiny file, very low quality (web thumbnails only)
Quality 40-60:   Small file, acceptable quality (web images)
Quality 70-85:   Medium file, good quality (standard web use) ✓
Quality 90-95:   Large file, excellent quality (photography)
Quality 100:     Huge file, lossless (archive/print)
```

**Format Choice:**
- **JPG**: Best for photos, lossy compression, smallest files
- **PNG**: Best for graphics, lossless, supports transparency
- **WEBP**: Modern format, smaller than JPG/PNG, not all browsers

---

### Compress PDF

**Image Quality Scale (1-10):**
```
1-2: Maximum compression (small file, visible quality loss)
3-4: Aggressive (noticeably compressed)
5-7: Balanced (good size/quality trade-off) ✓
8-9: Minimal (large file, barely noticeable loss)
10:  None (original quality, largest file)
```

**Metadata Options:**
- **Remove**: Smaller file, privacy protection ✓
- **Keep**: Retains document info (author, date, etc.)

---

## 💡 User Tips

### Tip 1: Use Presets First
```
Don't manually adjust sliders immediately.
Step 1: Click the matching preset
Step 2: Fine-tune if needed
This is faster and uses proven settings!
```

### Tip 2: Preview Before Batch
```
Don't convert 100 files with new settings.
Step 1: Test with 1 file
Step 2: Check the result
Step 3: Adjust settings if needed
Step 4: Process all files at once
```

### Tip 3: Read the Tooltips
```
❓ What does "Threshold" mean?
Hover over the help icon → Full explanation
Learn what each setting does!
```

### Tip 4: Document Your Settings
```
Found perfect settings?
✍️ Note them down:
   "Best for PDFs: DPI=400, Threshold=200"
Reuse them next time!
```

### Tip 5: Test Edge Cases
```
Different input always behaves differently.
Document: PDF→B&W works great with 300 DPI
Sketch: Same conversion needs 400 DPI
Adjust per file type!
```

---

## 🎛️ Advanced: Customizing Settings

### How to Save Your Own Presets

**Current Method** (Manual):
1. Adjust all sliders to your preferred values
2. Take a screenshot or note the values
3. Next time, manually set the same values
4. Or use the closest preset and fine-tune

**Future Enhancement** (Coming Soon):
1. Set preferred values
2. Click "Save as Preset"
3. Name it (e.g., "My Document Preset")
4. Use it instantly next time

---

## 🔍 Troubleshooting Settings

### Problem: "Settings aren't saving"
**Solution:**
- Check that you're entering values in the right fields
- Click "Start Conversion" to apply settings
- Values should be sent to the backend

### Problem: "Preset button not working"
**Solution:**
- Reload the page (Ctrl+R)
- Try another preset
- Check browser console for errors

### Problem: "Settings appear grayed out"
**Solution:**
- This might indicate your browser doesn't fully support the feature
- Use Firefox, Chrome, or Edge for best compatibility
- Clear cache if experiencing display issues

### Problem: "I can't find settings for my service"
**Solution:**
- Not all services have custom settings yet
- Some use only the basic Quality/Format settings
- Check SERVICE_SETTINGS_GUIDE.md for which services have settings

---

## 📊 Settings by Service Category

### PDF Services (8 with settings)
- ✅ PDF to B&W (3 sliders)
- ✅ Add Watermark (3 controls)
- ✅ Encrypt PDF (2 controls)
- ✅ Compress PDF (2 controls)
- ✅ Extract Pages (1 input)
- ✅ Remove Pages (1 input)
- ✅ OCR Text (2 controls)
- ✅ Clean PDF (3 checkboxes)

### Image Services (2 with settings)
- ✅ Image Resize (3 controls)
- ✅ Image Compress (2 controls)

### Conversion Services (1 with settings)
- ✅ Excel to CSV (1 dropdown)

### More Coming Soon
- Additional services will gain settings in future updates

---

## 🎓 Learning Path

### Beginner
1. Select a service
2. Use the default preset
3. Click "Start Conversion"
4. View results

### Intermediate
1. Select a service
2. Try different presets
3. See how results change
4. Pick your favorite preset

### Advanced
1. Select a service
2. Choose a preset as starting point
3. Fine-tune individual sliders
4. Save your custom values for future use

### Expert
1. Understand each parameter's impact
2. Test multiple combinations
3. Document settings by file type
4. Optimize for your specific workflow

---

## ✨ Summary

**Key Benefits of Service Settings:**
- ✅ One-click presets for common tasks
- ✅ Fine control for advanced users
- ✅ Visual feedback (sliders, displays, buttons)
- ✅ No technical knowledge required
- ✅ All parameters have defaults (always works)
- ✅ Real-time adjustments visible

**Remember:**
1. **Start with presets** for speed
2. **Fine-tune with sliders** for quality
3. **Check results** before batch processing
4. **Document your settings** for next time

Happy Converting! 🚀
