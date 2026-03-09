import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { UniversalIcon } from '../utils/UniversalIcon'
import '../styles/tool-page.css'
import { useSEO, generateToolSEOConfig } from '../hooks/useSEO'

const ToolPage = () => {
  const navigate = useNavigate()
  const { toolSlug } = useParams() // e.g., 'jpg-to-png'
  const [dragActive, setDragActive] = useState(false)
  const [uploadedFile, setUploadedFile] = useState(null)
  const [tool, setTool] = useState(null)
  const [relatedTools, setRelatedTools] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Fetch tool data from API
  useEffect(() => {
    const fetchToolData = async () => {
      if (!toolSlug) return
      
      try {
        setLoading(true)
        setError(null)
        
        // Fetch tool metadata (use relative path so Vite proxies /api to backend)
        const toolResponse = await fetch(`/api/tools/${toolSlug}`)
        if (!toolResponse.ok) {
          throw new Error(`Tool not found: ${toolSlug}`)
        }
        const toolData = await toolResponse.json()
        setTool(toolData.tool)
        
        // Fetch related tools
        try {
          const relatedResponse = await fetch(`/api/tools/${toolSlug}/related?limit=3`)
          if (relatedResponse.ok) {
            const relatedData = await relatedResponse.json()
            setRelatedTools(relatedData.related_tools || [])
          }
        } catch (err) {
          console.warn('Could not fetch related tools:', err)
        }
        
      } catch (err) {
        console.error('Error fetching tool data:', err)
        setError(err.message)
        // Set fallback tool data (include keys expected by SEO generator)
        setTool({
          slug: toolSlug,
          title: `${toolSlug} Converter`,
          description: 'Convert your files with ease',
          icon: '🔄',
          from_format: 'Source Format',
          to_format: 'Target Format',
          key_features: ['Fast conversion', 'High quality', 'Secure', 'No registration'],
          steps: [
            { num: 1, title: 'Upload', description: 'Select your file' },
            { num: 2, title: 'Process', description: 'Configure settings' },
            { num: 3, title: 'Convert', description: 'Start conversion' },
            { num: 4, title: 'Download', description: 'Get your file' }
          ],
          related_tools: [],
          faq: []
        })
      } finally {
        setLoading(false)
      }
    }

    fetchToolData()
  }, [toolSlug])

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
      setUploadedFile(files[0])
    }
  }

  // Show loading state
  if (loading) {
    return (
      <div className="tool-page">
        <nav className="tool-navbar">
          <div className="tool-nav-container">
            <button className="back-button" onClick={() => navigate('/')}>← Back to Tools</button>
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
            <button className="back-button" onClick={() => navigate('/')}>← Back to Tools</button>
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
            onClick={() => navigate('/')}
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
              <UniversalIcon icon="📁" size={48} />
              <h3>Drag & Drop Your File</h3>
              <p>or</p>
              <button className="btn-upload-file">
                Choose File from Computer
              </button>
              <p className="upload-format">
                Supported format: <strong>{tool.fromFormat}</strong>
              </p>
              <p className="upload-limit">
                Maximum file size: 50MB
              </p>
              {uploadedFile && (
                <div className="file-preview">
                  <div className="file-info">
                    <UniversalIcon icon="📄" size={20} />
                    <div>
                      <div className="file-name">{uploadedFile.name}</div>
                      <div className="file-size">
                        {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                      </div>
                    </div>
                  </div>
                  <button className="btn-convert">
                    Convert to {(tool?.to_format || tool?.toFormat || 'Target Format').split('(')[0].trim()}
                  </button>
                </div>
              )}
            </div>
          </div>
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
                <div key={idx} className="step-item">
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
            {(tool?.keyFeatures || []).map((feature, idx) => (
              <div key={idx} className="feature-item">
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
            {(tool?.quality_indicators || [
              { icon: '⚡', title: 'Lightning Fast', description: 'Convert files in seconds' },
              { icon: '🔒', title: '100% Secure', description: 'Files encrypted and deleted after conversion' },
              { icon: '💯', title: 'High Quality', description: 'Best quality conversion with no loss' },
              { icon: '📱', title: 'Works Everywhere', description: 'Desktop, tablet, mobile supported' }
            ]).map((card, idx) => (
              <div key={idx} className="quality-card">
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
            {(tool?.faq || [
              { q: 'Is the conversion free?', a: 'Yes! Basic conversions are completely free. No registration or credit card required.' },
              { q: 'What happens to my file?', a: 'Your file is uploaded securely, converted, and then automatically deleted. We never store your files.' },
              { q: 'Is there a file size limit?', a: 'Free users can convert files up to 50MB. Premium users get up to 500MB.' }
            ]).map((faq, idx) => (
              <div key={idx} className="faq-item">
                <h4>{faq.q}</h4>
                <p>{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Related Tools */}
      {(relatedTools.length > 0 || (tool?.relatedTools?.length > 0)) && (
        <section className="related-tools">
          <div className="tool-container">
            <h2>Related Tools</h2>
            <div className="related-tools-grid">
              {(relatedTools.length > 0 ? relatedTools : (tool?.relatedTools || [])).map((relTool, idx) => (
                <div 
                  key={idx} 
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
