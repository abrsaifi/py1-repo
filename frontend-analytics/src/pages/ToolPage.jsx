import React, { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { UniversalIcon } from '../utils/UniversalIcon'
import '../styles/tool-page.css'
import { useSEO, generateToolSEOConfig } from '../hooks/useSEO'
import { getCatalogTool } from '../config/toolRoutes'

const DEFAULT_QUALITY_INDICATORS = [
  { icon: '⚡', title: 'Lightning Fast', description: 'Convert files in seconds' },
  { icon: '🔒', title: '100% Secure', description: 'Files encrypted and deleted after conversion' },
  { icon: '💯', title: 'High Quality', description: 'Best quality conversion with no loss' },
  { icon: '📱', title: 'Works Everywhere', description: 'Desktop, tablet, mobile supported' },
]

const DEFAULT_FAQ = [
  { q: 'Is the conversion free?', a: 'Yes! Basic conversions are completely free. No registration or credit card required.' },
  { q: 'What happens to my file?', a: 'Your file is uploaded securely, converted, and then automatically deleted. We never store your files.' },
  { q: 'Is there a file size limit?', a: 'Free users can convert files up to 50MB. Premium users get up to 500MB.' },
]

const DEFAULT_STEPS = [
  { num: 1, title: 'Upload', description: 'Select your file' },
  { num: 2, title: 'Process', description: 'Configure settings' },
  { num: 3, title: 'Convert', description: 'Start conversion' },
  { num: 4, title: 'Download', description: 'Get your file' },
]

const mapRelatedTools = (relatedEntries = []) => {
  return relatedEntries
    .map((entry) => {
      if (typeof entry === 'string') {
        return getCatalogTool(entry)
      }

      if (!entry) {
        return null
      }

      if (entry.slug) {
        return {
          ...getCatalogTool(entry.slug),
          ...entry,
        }
      }

      return entry
    })
    .filter(Boolean)
}

const normalizeTool = (toolData, catalogTool, toolSlug) => {
  if (!toolData && !catalogTool) {
    return null
  }

  const merged = {
    ...catalogTool,
    ...toolData,
  }

  const title = merged.title || merged.name || catalogTool?.title || `${toolSlug} Converter`
  const description = merged.description || catalogTool?.description || 'Convert your files with ease'
  const fromFormat = merged.from_format || merged.fromFormat || merged.from || catalogTool?.from_format || 'Source Format'
  const toFormat = merged.to_format || merged.toFormat || merged.to || catalogTool?.to_format || 'Target Format'
  const keyFeatures = merged.key_features || merged.keyFeatures || catalogTool?.key_features || []
  const steps = merged.steps || catalogTool?.steps || DEFAULT_STEPS
  const faq = merged.faq || catalogTool?.faq || DEFAULT_FAQ
  const qualityIndicators = merged.quality_indicators || merged.qualityIndicators || DEFAULT_QUALITY_INDICATORS
  const related = mapRelatedTools(merged.related_tools || merged.relatedTools || catalogTool?.related_tools || [])

  return {
    ...merged,
    slug: merged.slug || toolSlug,
    title,
    name: title,
    description,
    icon: merged.icon || catalogTool?.icon || '🔄',
    from_format: fromFormat,
    fromFormat,
    to_format: toFormat,
    toFormat,
    key_features: keyFeatures,
    keyFeatures,
    steps,
    faq,
    quality_indicators: qualityIndicators,
    qualityIndicators,
    related_tools: related,
    relatedTools: related,
  }
}

const getDefaultParamValues = (toolConfig) => {
  return Object.fromEntries(
    (toolConfig?.params || []).map((param) => [
      param.name,
      param.default ?? (param.type === 'checkbox' ? false : ''),
    ]),
  )
}

const getCustomPresetsStorageKey = (slug) => `tool-custom-presets:${slug}`

const MULTI_FILE_TOOL_SLUGS = new Set([
  'merge-pdf',
  'merge-pdf-smart',
  'split-pdf-batch',
])

const MAX_UPLOAD_SIZE_BYTES = 50 * 1024 * 1024

const supportsMultipleFiles = (toolConfig) => {
  if (!toolConfig) {
    return false
  }

  if (MULTI_FILE_TOOL_SLUGS.has(toolConfig.slug)) {
    return true
  }

  return String(toolConfig.from_format || toolConfig.fromFormat || '').toLowerCase().includes('multiple')
}

const formatFileSize = (bytes) => `${(bytes / 1024 / 1024).toFixed(2)} MB`

const parseAcceptedExtensions = (acceptString) => {
  if (!acceptString) {
    return null
  }

  const extensions = acceptString
    .split(',')
    .map((value) => value.trim().toLowerCase())
    .filter((value) => value.startsWith('.'))
    .map((value) => value.replace(/^\./, ''))

  return extensions.length ? new Set(extensions) : null
}

const validateSelectedFiles = (selectedFiles, toolConfig) => {
  const acceptedExtensions = parseAcceptedExtensions(getAcceptedFormats(toolConfig))

  for (const file of selectedFiles) {
    if (file.size > MAX_UPLOAD_SIZE_BYTES) {
      return `${file.name} exceeds the 50MB file size limit.`
    }

    if (acceptedExtensions) {
      const extension = file.name.split('.').pop()?.toLowerCase()
      if (!extension || !acceptedExtensions.has(extension)) {
        return `${file.name} is not a supported file type for this tool.`
      }
    }
  }

  return null
}

const getNormalizedTargetFormat = (toolConfig, params, selectedFile) => {
  const directTarget = (toolConfig?.output_format && !['auto', 'variable'].includes(toolConfig.output_format))
    ? toolConfig.output_format
    : params.output_format || params.format

  if (directTarget) {
    return String(directTarget).toLowerCase().replace(/[^a-z0-9]/g, '')
  }

  const toolTarget = toolConfig?.to_format || toolConfig?.toFormat || ''
  const normalizedToolTarget = String(toolTarget).toLowerCase()

  if (normalizedToolTarget.includes('pdf')) return 'pdf'
  if (normalizedToolTarget.includes('docx')) return 'docx'
  if (normalizedToolTarget.includes('pptx') || normalizedToolTarget.includes('powerpoint')) return 'pptx'
  if (normalizedToolTarget.includes('xlsx') || normalizedToolTarget.includes('excel')) return 'xlsx'
  if (normalizedToolTarget.includes('csv')) return 'csv'
  if (normalizedToolTarget.includes('zip')) return 'zip'
  if (normalizedToolTarget.includes('png')) return 'png'
  if (normalizedToolTarget.includes('jpg') || normalizedToolTarget.includes('jpeg')) return 'jpg'
  if (normalizedToolTarget.includes('webm')) return 'webm'
  if (normalizedToolTarget.includes('webp')) return 'webp'
  if (normalizedToolTarget.includes('tiff') || normalizedToolTarget.includes('tif')) return 'tiff'
  if (normalizedToolTarget.includes('wav')) return 'wav'
  if (normalizedToolTarget.includes('mp4')) return 'mp4'
  if (normalizedToolTarget.includes('html')) return 'html'
  if (normalizedToolTarget.includes('json')) return 'json'
  if (normalizedToolTarget.includes('text')) return 'txt'

  if (toolConfig?.slug === 'extract-extended') {
    return 'txt'
  }

  if (toolConfig?.slug === 'zip-extractor') {
    return 'zip'
  }

  if (toolConfig?.slug === 'split-sheets') {
    return params.output_format === 'csv' ? 'zip' : 'zip'
  }

  if (toolConfig?.slug === 'data-validator' || toolConfig?.slug === 'convert-history') {
    return 'json'
  }

  if (toolConfig?.slug === 'formulas-to-values' || toolConfig?.slug === 'clean-charts' || toolConfig?.slug === 'normalize-data') {
    return params.output_format === 'csv' ? 'csv' : 'xlsx'
  }

  if (toolConfig?.slug === 'audio-converter') {
    return 'wav'
  }

  if (toolConfig?.slug === 'database-export') {
    return (params.format || 'csv').toLowerCase().replace(/[^a-z0-9]/g, '')
  }

  if (toolConfig?.category === 'image' && selectedFile?.name) {
    const sourceExtension = selectedFile.name.split('.').pop()?.toLowerCase()
    if (sourceExtension && ['jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff', 'tif', 'webp'].includes(sourceExtension)) {
      return sourceExtension === 'tif' ? 'tiff' : sourceExtension
    }
  }

  return ''
}

const getAcceptedFormats = (toolConfig) => {
  if (toolConfig?.supported_formats?.length) {
    return toolConfig.supported_formats.map((format) => `.${String(format).toLowerCase().replace(/^\./, '')}`).join(',')
  }

  const sourceText = String(toolConfig?.from_format || toolConfig?.fromFormat || '').toLowerCase()
  if (sourceText.includes('jpg') || sourceText.includes('jpeg')) return '.jpg,.jpeg'
  if (sourceText.includes('png')) return '.png'
  if (sourceText.includes('webp')) return '.webp'
  if (sourceText.includes('image')) return '.jpg,.jpeg,.png,.webp,.bmp,.gif,.tiff,.tif'
  if (sourceText.includes('pdf')) return '.pdf'
  if (sourceText.includes('docx')) return '.docx'
  if (sourceText.includes('pptx') || sourceText.includes('powerpoint')) return '.ppt,.pptx'
  if (sourceText.includes('xlsx') || sourceText.includes('excel') || sourceText.includes('spreadsheet')) return '.xls,.xlsx,.csv,.ods'
  if (sourceText.includes('html')) return '.html,.htm'
  if (sourceText.includes('text')) return '.txt'
  if (sourceText.includes('audio')) return '.mp3,.wav'
  if (sourceText.includes('multiple')) return '.txt,.html,.docx,.xlsx,.csv,.pptx,.png,.jpg,.pdf'
  if (sourceText.includes('document')) return '.pdf,.docx,.txt,.html,.htm,.ppt,.pptx'
  if (sourceText.includes('workbook')) return '.xlsx,.xls,.csv'
  if (sourceText.includes('dataset')) return '.xlsx,.xls,.csv,.json'
  if (sourceText.includes('operational data')) return '.xlsx,.xls,.csv,.json'
  if (sourceText.includes('database export')) return '.csv,.json,.xlsx'
  if (sourceText.includes('mixed files')) return '.txt,.html,.docx,.xlsx,.csv,.png,.jpg,.pdf'

  return undefined
}

const getDownloadFilename = (response, fallbackName) => {
  const disposition = response.headers.get('Content-Disposition') || ''
  const match = disposition.match(/filename="?([^";]+)"?/i)
  return match?.[1] || fallbackName
}

const getResultKind = (downloadName, blobType) => {
  const normalizedName = String(downloadName || '').toLowerCase()
  const normalizedType = String(blobType || '').toLowerCase()

  if (normalizedType.includes('application/zip') || normalizedName.endsWith('.zip')) return 'archive'
  if (normalizedType.includes('application/json') || normalizedName.endsWith('.json')) return 'json'
  if (normalizedType.includes('application/pdf') || normalizedName.endsWith('.pdf')) return 'pdf'
  if (normalizedType.startsWith('audio/') || normalizedName.endsWith('.wav') || normalizedName.endsWith('.mp3')) return 'audio'
  if (normalizedType.startsWith('video/') || normalizedName.endsWith('.mp4') || normalizedName.endsWith('.webm')) return 'video'
  if (normalizedType.includes('spreadsheet') || normalizedName.endsWith('.xlsx') || normalizedName.endsWith('.csv')) return 'spreadsheet'
  if (normalizedType.includes('text/html') || normalizedName.endsWith('.html')) return 'html'
  if (normalizedType.includes('text/plain') || normalizedName.endsWith('.txt')) return 'text'
  return 'file'
}

const getSuccessMessage = (downloadName, blobType) => {
  const resultKind = getResultKind(downloadName, blobType)

  if (resultKind === 'archive') return `Downloaded archive ${downloadName}`
  if (resultKind === 'json') return `Downloaded JSON export ${downloadName}`
  if (resultKind === 'pdf') return `Downloaded PDF output ${downloadName}`
  if (resultKind === 'audio') return `Downloaded audio file ${downloadName}`
  if (resultKind === 'video') return `Downloaded video file ${downloadName}`
  if (resultKind === 'spreadsheet') return `Downloaded spreadsheet output ${downloadName}`
  if (resultKind === 'html') return `Downloaded HTML report ${downloadName}`
  if (resultKind === 'text') return `Downloaded text output ${downloadName}`
  return `Downloaded ${downloadName}`
}

const ToolPage = () => {
  const navigate = useNavigate()
  const { toolSlug } = useParams() // e.g., 'jpg-to-png'
  const importInputRef = useRef(null)
  const fileInputRef = useRef(null)
  const [dragActive, setDragActive] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [tool, setTool] = useState(null)
  const [relatedTools, setRelatedTools] = useState([])
  const [paramValues, setParamValues] = useState({})
  const [customPresets, setCustomPresets] = useState({})
  const [activeSettingsTab, setActiveSettingsTab] = useState('basic')
  const [conversionState, setConversionState] = useState('idle')
  const [conversionMessage, setConversionMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Fetch tool data from API
  useEffect(() => {
    const fetchToolData = async () => {
      if (!toolSlug) return

      const catalogTool = getCatalogTool(toolSlug)
      
      try {
        setLoading(true)
        setError(null)
        
        // Fetch tool metadata (use relative path so Vite proxies /api to backend)
        const toolResponse = await fetch(`/api/tools/${toolSlug}`)
        if (!toolResponse.ok) {
          throw new Error(`Tool not found: ${toolSlug}`)
        }
        const toolData = await toolResponse.json()
        setTool(normalizeTool(toolData.tool, catalogTool, toolSlug))
        
        // Fetch related tools
        try {
          const relatedResponse = await fetch(`/api/tools/${toolSlug}/related?limit=3`)
          if (relatedResponse.ok) {
            const relatedData = await relatedResponse.json()
            const normalizedRelatedTools = mapRelatedTools(relatedData.related_tools || [])
            setRelatedTools(normalizedRelatedTools.length > 0 ? normalizedRelatedTools : mapRelatedTools(catalogTool?.related_tools || []))
          }
        } catch (err) {
          console.warn('Could not fetch related tools:', err)
          setRelatedTools(mapRelatedTools(catalogTool?.related_tools || []))
        }
        
      } catch (err) {
        console.error('Error fetching tool data:', err)
        setError(err.message)
        setTool(normalizeTool(null, catalogTool, toolSlug))
        setRelatedTools(mapRelatedTools(catalogTool?.related_tools || []))
      } finally {
        setLoading(false)
      }
    }

    fetchToolData()
  }, [toolSlug])

  useEffect(() => {
    if (!tool?.slug) {
      setParamValues({})
      setCustomPresets({})
      setUploadedFiles([])
      return
    }

    setParamValues(getDefaultParamValues(tool))
    setUploadedFiles([])

    try {
      const savedPresets = JSON.parse(localStorage.getItem(getCustomPresetsStorageKey(tool.slug)) || '{}')
      setCustomPresets(savedPresets)
    } catch (storageError) {
      console.warn('Could not load custom tool presets:', storageError)
      setCustomPresets({})
    }

    setActiveSettingsTab('basic')
  }, [tool])

  // Apply SEO configuration when tool data is loaded
  // Use current window location as base URL (removes /slug path)
  const baseUrl = window.location.protocol + '//' + window.location.host
  const seoConfig = tool ? generateToolSEOConfig(tool, baseUrl) : {}
  useSEO(seoConfig)

  // Drag handlers
  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      const nextFiles = supportsMultipleFiles(tool) ? Array.from(files) : [files[0]]
      const validationError = validateSelectedFiles(nextFiles, tool)
      if (validationError) {
        setUploadedFiles([])
        setConversionState('error')
        setConversionMessage(validationError)
        return
      }
      setUploadedFiles(nextFiles)
      setConversionState('idle')
      setConversionMessage('')
    }
  }

  const handleFileSelection = (event) => {
    const selectedFiles = Array.from(event.target.files || [])
    if (!selectedFiles.length) {
      return
    }

    const nextFiles = supportsMultipleFiles(tool) ? selectedFiles : [selectedFiles[0]]
    const validationError = validateSelectedFiles(nextFiles, tool)
    if (validationError) {
      setUploadedFiles([])
      setConversionState('error')
      setConversionMessage(validationError)
      event.target.value = ''
      return
    }

    setUploadedFiles(nextFiles)
    setConversionState('idle')
    setConversionMessage('')
  }

  const handleParamValueChange = (paramName, value) => {
    setParamValues((currentValues) => ({
      ...currentValues,
      [paramName]: value,
    }))
  }

  const applyPreset = (presetValues) => {
    setParamValues((currentValues) => ({
      ...currentValues,
      ...presetValues,
    }))
  }

  const resetSettings = () => {
    setParamValues(getDefaultParamValues(tool))
  }

  const saveCustomPreset = () => {
    if (!tool?.slug || !tool?.params?.length) {
      return
    }

    const presetName = window.prompt('Preset name')?.trim()
    if (!presetName) {
      return
    }

    const nextPresets = {
      ...customPresets,
      [presetName]: {
        params: paramValues,
        description: 'Saved from the Vite tool page',
      },
    }

    localStorage.setItem(getCustomPresetsStorageKey(tool.slug), JSON.stringify(nextPresets))
    setCustomPresets(nextPresets)
    setActiveSettingsTab('presets')
  }

  const deleteCustomPreset = (presetName) => {
    const nextPresets = { ...customPresets }
    delete nextPresets[presetName]
    localStorage.setItem(getCustomPresetsStorageKey(tool.slug), JSON.stringify(nextPresets))
    setCustomPresets(nextPresets)
  }

  const exportSettings = () => {
    if (!tool?.slug || !tool?.params?.length) {
      return
    }

    const exportPayload = {
      tool: tool.slug,
      params: paramValues,
    }

    const blob = new Blob([JSON.stringify(exportPayload, null, 2)], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${tool.slug}-settings.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  const importSettings = async (event) => {
    const file = event.target.files?.[0]
    if (!file) {
      return
    }

    try {
      const contents = await file.text()
      const imported = JSON.parse(contents)
      if (imported.tool && imported.tool !== tool?.slug) {
        window.alert(`Preset is for ${imported.tool}, current tool is ${tool?.slug}`)
        return
      }

      applyPreset(imported.params || {})
    } catch (importError) {
      console.error('Could not import settings:', importError)
      window.alert('Could not import settings file.')
    } finally {
      event.target.value = ''
    }
  }

  const renderParameterInput = (param) => {
    const currentValue = paramValues[param.name] ?? param.default ?? ''

    if (param.type === 'select') {
      return (
        <select
          id={param.name}
          value={currentValue}
          onChange={(event) => handleParamValueChange(param.name, event.target.value)}
          className="tool-param-input"
        >
          {(param.values || []).map((value) => (
            <option key={value} value={value}>{value}</option>
          ))}
        </select>
      )
    }

    if (param.type === 'checkbox') {
      return (
        <label className="tool-param-checkbox">
          <input
            id={param.name}
            type="checkbox"
            checked={Boolean(currentValue)}
            onChange={(event) => handleParamValueChange(param.name, event.target.checked)}
          />
          <span>Enabled</span>
        </label>
      )
    }

    if (param.type === 'range') {
      return (
        <div className="tool-param-range-wrap">
          <input
            id={param.name}
            type="range"
            min={param.min}
            max={param.max}
            step={param.step || 1}
            value={currentValue}
            onChange={(event) => handleParamValueChange(param.name, event.target.value)}
            className="tool-param-range"
          />
          <span className="tool-param-value">{String(currentValue)}</span>
        </div>
      )
    }

    return (
      <input
        id={param.name}
        type={param.type || 'text'}
        min={param.min}
        max={param.max}
        step={param.step}
        value={currentValue}
        onChange={(event) => handleParamValueChange(param.name, event.target.value)}
        className="tool-param-input"
      />
    )
  }

  const parameterList = tool?.params || []
  const basicParams = parameterList.slice(0, Math.min(4, parameterList.length))
  const advancedParams = parameterList.slice(Math.min(4, parameterList.length))
  const builtInPresets = Object.entries(tool?.presets || {})
  const customPresetEntries = Object.entries(customPresets || {})
  const hasPresetTab = builtInPresets.length > 0 || customPresetEntries.length > 0
  const supportedFormatText = tool?.supported_formats?.length
    ? tool.supported_formats.map((format) => String(format).toUpperCase()).join(', ')
    : tool?.from_format || tool?.fromFormat || 'Source Format'
  const acceptedFileTypes = getAcceptedFormats(tool)
  const allowsMultipleFiles = supportsMultipleFiles(tool)
  const primaryUploadedFile = uploadedFiles[0] || null
  const totalUploadedBytes = uploadedFiles.reduce((total, file) => total + file.size, 0)

  const handleConvert = async () => {
    if (!uploadedFiles.length || !tool) {
      return
    }

    const targetFormat = getNormalizedTargetFormat(tool, paramValues, primaryUploadedFile)
    if (!targetFormat) {
      setConversionState('error')
      setConversionMessage('This tool does not have a runnable output format yet.')
      return
    }

    try {
      setConversionState('uploading')
      setConversionMessage(`Uploading ${uploadedFiles.length} file${uploadedFiles.length === 1 ? '' : 's'}...`)

      const uploads = []
      for (const [index, file] of uploadedFiles.entries()) {
        const uploadId = `${tool.slug}-${Date.now()}-${index}`
        const uploadForm = new FormData()
        uploadForm.append('upload_id', uploadId)
        uploadForm.append('filename', file.name)
        uploadForm.append('index', '0')
        uploadForm.append('total', '1')
        uploadForm.append('chunk', file, file.name)

        const uploadResponse = await fetch('/api/upload-chunk', {
          method: 'POST',
          body: uploadForm,
        })
        const uploadPayload = await uploadResponse.json()
        if (!uploadResponse.ok || !uploadPayload.success) {
          throw new Error(uploadPayload.error || 'Upload failed')
        }

        uploads.push({ upload_id: uploadId, filename: file.name })
      }

      setConversionState('converting')
      setConversionMessage('Applying selected settings and converting...')

      const convertResponse = await fetch('/api/convert-uploaded', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tool_slug: tool.slug,
          uploads,
          target_format: targetFormat,
          parameters: paramValues,
        }),
      })

      if (!convertResponse.ok) {
        let errorText = 'Conversion failed'
        try {
          const errorPayload = await convertResponse.json()
          errorText = errorPayload.error || errorText
        } catch (jsonError) {
          errorText = await convertResponse.text()
        }
        throw new Error(errorText)
      }

      const convertedBlob = await convertResponse.blob()
      const downloadName = getDownloadFilename(
        convertResponse,
        `${primaryUploadedFile.name.replace(/\.[^.]+$/, '') || tool.slug}.${targetFormat}`,
      )
      const downloadUrl = window.URL.createObjectURL(convertedBlob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = downloadName
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)

      setConversionState('success')
      setConversionMessage(getSuccessMessage(downloadName, convertedBlob.type))
    } catch (convertError) {
      console.error('Tool conversion failed:', convertError)
      setConversionState('error')
      setConversionMessage(convertError.message || 'Conversion failed')
    }
  }

  // Show loading state
  if (loading) {
    return (
      <div className="tool-page">
        <nav className="tool-navbar">
          <div className="tool-nav-container">
            <button className="back-button" onClick={() => navigate('/tools')}>← Back to Tools</button>
          </div>
        </nav>
        <section className="tool-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '300px' }}>
          <h2>Loading tool...</h2>
        </section>
      </div>
    )
  }

  // Show error state
  if (error && !tool) {
    return (
      <div className="tool-page">
        <nav className="tool-navbar">
          <div className="tool-nav-container">
            <button className="back-button" onClick={() => navigate('/tools')}>← Back to Tools</button>
          </div>
        </nav>
        <section className="tool-header" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '300px', gap: '20px' }}>
          <h2>Tool Not Found</h2>
          <p>{error}</p>
          <button className="btn-primary-large" onClick={() => navigate('/')}>Browse All Tools</button>
        </section>
      </div>
    )
  }

  return (
    <div className="tool-page">
      {/* Navigation */}
      <nav className="tool-navbar">
        <div className="tool-nav-container">
          <button 
            className="back-button"
            onClick={() => navigate('/tools')}
          >
            ← Back to Tools
          </button>
          <div className="tool-nav-actions">
            <button 
              className="btn-link"
              onClick={() => navigate('/login')}
            >
              Login
            </button>
            <button 
              className="btn-small"
              onClick={() => navigate('/register')}
            >
              Sign Up
            </button>
          </div>
        </div>
      </nav>

      {/* Tool Header */}
      <section className="tool-header">
        <div className="tool-header-container">
          {tool?.icon ? <UniversalIcon icon={tool.icon} size={48} /> : <UniversalIcon icon="🔄" size={48} />}
          <h1>{tool?.title || 'Converter'}</h1>
          <p className="tool-description">{tool?.description || 'Convert your files with ease'}</p>
        </div>
      </section>

      {/* Upload Section */}
      <section className="tool-upload-section">
        <div className="tool-container">
          <div 
            className={`tool-upload-box ${dragActive ? 'drag-active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className="upload-inner">
              <input
                ref={fileInputRef}
                type="file"
                accept={acceptedFileTypes}
                multiple={allowsMultipleFiles}
                onChange={handleFileSelection}
                hidden
              />
              <UniversalIcon icon="📁" size={48} />
              <h3>Drag & Drop Your {allowsMultipleFiles ? 'Files' : 'File'}</h3>
              <p>or</p>
              <button className="btn-upload-file" onClick={() => fileInputRef.current?.click()}>
                Choose {allowsMultipleFiles ? 'Files' : 'File'} from Computer
              </button>
              <p className="upload-format">
                Supported format: <strong>{supportedFormatText}</strong>
              </p>
              <p className="upload-limit">
                Maximum file size: 50MB
              </p>
              {uploadedFiles.length > 0 && (
                <div className="file-preview">
                  <div className="file-info">
                    <UniversalIcon icon="📄" size={20} />
                    <div>
                      <div className="file-name">{uploadedFiles.length === 1 ? primaryUploadedFile.name : `${uploadedFiles.length} files selected`}</div>
                      <div className="file-size">
                        {uploadedFiles.length === 1
                          ? formatFileSize(primaryUploadedFile.size)
                          : `${formatFileSize(totalUploadedBytes)} total`}
                      </div>
                      {uploadedFiles.length > 1 && (
                        <div className="file-size">{uploadedFiles.map((file) => file.name).join(', ')}</div>
                      )}
                    </div>
                  </div>
                  <button className="btn-convert" onClick={handleConvert} disabled={conversionState === 'uploading' || conversionState === 'converting'}>
                    Convert to {(tool?.to_format || tool?.toFormat || 'Target Format').split('(')[0].trim()}
                  </button>
                </div>
              )}
              {conversionMessage && (
                <p className={`tool-conversion-message ${conversionState}`}>
                  {conversionMessage}
                </p>
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="tool-settings">
        <div className="tool-container">
          <div className="tool-settings-header">
            <div>
              <p className="tool-settings-kicker">Migrated from the legacy template</p>
              <h2>{tool?.settings_label || 'Tool Settings'}</h2>
              <p className="tool-settings-copy">
                These controls mirror the old Index.html tool options so premium and advanced workflows are available directly in the Vite app.
              </p>
            </div>
            <div className="tool-settings-actions">
              <button className="tool-settings-btn" onClick={resetSettings} disabled={!parameterList.length}>Reset</button>
              <button className="tool-settings-btn" onClick={saveCustomPreset} disabled={!parameterList.length}>Save Preset</button>
              <button className="tool-settings-btn" onClick={exportSettings} disabled={!parameterList.length}>Export</button>
              <button className="tool-settings-btn" onClick={() => importInputRef.current?.click()} disabled={!parameterList.length}>Import</button>
              <input ref={importInputRef} type="file" accept="application/json" onChange={importSettings} hidden />
            </div>
          </div>

          {parameterList.length > 0 ? (
            <>
              <div className="tool-settings-tabs">
                <button
                  className={`tool-settings-tab ${activeSettingsTab === 'basic' ? 'active' : ''}`}
                  onClick={() => setActiveSettingsTab('basic')}
                >
                  Basic
                </button>
                {advancedParams.length > 0 && (
                  <button
                    className={`tool-settings-tab ${activeSettingsTab === 'advanced' ? 'active' : ''}`}
                    onClick={() => setActiveSettingsTab('advanced')}
                  >
                    Advanced
                  </button>
                )}
                {hasPresetTab && (
                  <button
                    className={`tool-settings-tab ${activeSettingsTab === 'presets' ? 'active' : ''}`}
                    onClick={() => setActiveSettingsTab('presets')}
                  >
                    Presets
                  </button>
                )}
              </div>

              {activeSettingsTab === 'basic' && (
                <div className="tool-param-grid">
                  {basicParams.map((param) => (
                    <div key={param.name} className="tool-param-card">
                      <label htmlFor={param.name} className="tool-param-label">{param.label}</label>
                      {renderParameterInput(param)}
                      {param.help && <p className="tool-param-help">{param.help}</p>}
                    </div>
                  ))}
                </div>
              )}

              {activeSettingsTab === 'advanced' && advancedParams.length > 0 && (
                <div className="tool-param-grid">
                  {advancedParams.map((param) => (
                    <div key={param.name} className="tool-param-card">
                      <label htmlFor={param.name} className="tool-param-label">{param.label}</label>
                      {renderParameterInput(param)}
                      {param.help && <p className="tool-param-help">{param.help}</p>}
                    </div>
                  ))}
                </div>
              )}

              {activeSettingsTab === 'presets' && hasPresetTab && (
                <div className="tool-preset-sections">
                  {builtInPresets.length > 0 && (
                    <div>
                      <h3 className="tool-preset-title">Built-in Presets</h3>
                      <div className="tool-preset-grid">
                        {builtInPresets.map(([presetName, presetValues]) => (
                          <div key={presetName} className="tool-preset-card">
                            <div>
                              <h4>{presetName}</h4>
                              <p>Apply the legacy preset values for this workflow.</p>
                            </div>
                            <button className="tool-preset-action" onClick={() => applyPreset(presetValues)}>Apply</button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {customPresetEntries.length > 0 && (
                    <div>
                      <h3 className="tool-preset-title">Custom Presets</h3>
                      <div className="tool-preset-grid">
                        {customPresetEntries.map(([presetName, presetConfig]) => (
                          <div key={presetName} className="tool-preset-card custom">
                            <div>
                              <h4>{presetName}</h4>
                              <p>{presetConfig.description || 'Saved from this tool page.'}</p>
                            </div>
                            <div className="tool-preset-card-actions">
                              <button className="tool-preset-action" onClick={() => applyPreset(presetConfig.params || {})}>Apply</button>
                              <button className="tool-preset-delete" onClick={() => deleteCustomPreset(presetName)}>Delete</button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          ) : (
            <div className="tool-settings-empty">
              <p>This tool does not expose additional controls yet. The shared catalog is already active, so backend and frontend metadata will still stay aligned.</p>
            </div>
          )}
        </div>
      </section>

      {/* Supported Formats */}
      <section className="tool-formats">
        <div className="tool-container">
          <h2>Supported Formats</h2>
          <div className="formats-grid">
            <div className="format-box">
              <h4>From</h4>
              <p>{tool?.from_format || tool?.fromFormat || 'Source Format'}</p>
            </div>
            <div className="format-arrow">→</div>
            <div className="format-box">
              <h4>To</h4>
              <p>{tool?.to_format || tool?.toFormat || 'Target Format'}</p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="tool-how-it-works">
        <div className="tool-container">
          <h2>How It Works</h2>
          <div className="tool-steps">
            {(tool?.steps || []).map((step, idx) => {
              const stepNum = typeof step === 'object' ? step.num : idx + 1
              const stepTitle = typeof step === 'object' ? step.title : `Step ${idx + 1}`
              const stepDesc = typeof step === 'object' ? step.description : step
              
              return (
                <div key={`step-${idx}-${stepNum}`} className="step-item">
                  <div className="step-number">{stepNum}</div>
                  <div className="step-content">
                    <h4>{stepTitle}</h4>
                    <p>{stepDesc}</p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Key Features */}
      <section className="tool-features">
        <div className="tool-container">
          <h2>Key Features</h2>
          <div className="features-list">
            {(tool?.key_features || tool?.keyFeatures || []).map((feature, idx) => (
              <div key={`feature-${idx}-${feature}`} className="feature-item">
                <UniversalIcon icon="✓" size={18} />
                <span className="feature-text">{feature}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Quality Indicators */}
      <section className="tool-quality">
        <div className="tool-container">
          <h2>Why Use Our Converter?</h2>
          <div className="quality-grid">
            {(tool?.quality_indicators || tool?.qualityIndicators || DEFAULT_QUALITY_INDICATORS).map((card, idx) => (
              <div key={`quality-${idx}-${card.title}`} className="quality-card">
                <UniversalIcon icon={card.icon} size={32} />
                <h4>{card.title}</h4>
                <p>{card.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="tool-faq">
        <div className="tool-container">
          <h2>Frequently Asked Questions</h2>
          <div className="faq-list">
            {(tool?.faq || DEFAULT_FAQ).map((faq, idx) => (
              <div key={`faq-${idx}-${faq.q}`} className="faq-item">
                <h4>{faq.q}</h4>
                <p>{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Related Tools */}
      {(relatedTools.length > 0 || (tool?.related_tools?.length > 0) || (tool?.relatedTools?.length > 0)) && (
        <section className="related-tools">
          <div className="tool-container">
            <h2>Related Tools</h2>
            <div className="related-tools-grid">
              {(relatedTools.length > 0 ? relatedTools : (tool?.related_tools || tool?.relatedTools || [])).map((relTool, idx) => (
                <div 
                  key={`tool-${idx}-${relTool.slug}`} 
                  className="related-tool-card"
                  onClick={() => navigate(`/${relTool.slug}`)}
                >
                  {relTool.icon ? <UniversalIcon icon={relTool.icon} size={32} /> : <UniversalIcon icon="🔄" size={32} />}
                  <h4>{relTool.title || relTool.name}</h4>
                  <p>Convert now →</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* CTA Section */}
      <section className="tool-cta">
        <div className="tool-container">
          <h2>Ready to Convert?</h2>
          <p>Start converting now, no registration needed</p>
          <button className="btn-primary-large">Start Converting Now</button>
        </div>
      </section>
    </div>
  )
}

export default ToolPage
