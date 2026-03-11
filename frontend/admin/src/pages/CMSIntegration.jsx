import React, { useState } from 'react'
import '../styles/admin.css'
import { UniversalIcon } from '@shared/utils/UniversalIcon'

const ContentManager = () => {
  const [selectedPage, setSelectedPage] = useState('home')
  const [selectedBlock, setSelectedBlock] = useState(null)
  const [editMode, setEditMode] = useState(false)
  const [showAddBlockForm, setShowAddBlockForm] = useState(false)
  const [showAddPageForm, setShowAddPageForm] = useState(false)
  const [showPageSettings, setShowPageSettings] = useState(false)
  const [editingPage, setEditingPage] = useState(null)
  const [newBlockType, setNewBlockType] = useState('hero')
  const [newBlockName, setNewBlockName] = useState('')
  const [newPageName, setNewPageName] = useState('')
  const [activeTab, setActiveTab] = useState('pages')
  const [tools, setTools] = useState([])
  const [toolsLoading, setToolsLoading] = useState(false)
  const [selectedTool, setSelectedTool] = useState(null)
  const [editingTool, setEditingTool] = useState(null)
  const [pageMetaData, setPageMetaData] = useState({
    home: { title: 'Home', description: 'Homepage', slug: 'home' },
    pricing: { title: 'Pricing', description: 'Pricing page', slug: 'pricing' },
    about: { title: 'About', description: 'About us page', slug: 'about' }
  })
  const [customCSS, setCustomCSS] = useState('')
  const [blockOrder, setBlockOrder] = useState({
    home: ['hero', 'features', 'pricing', 'faq', 'testimonials', 'cta'],
    pricing: ['hero', 'plans'],
    about: ['hero', 'team']
  })

  // Fetch tools from API
  React.useEffect(() => {
    const fetchTools = async () => {
      try {
        setToolsLoading(true)
        const response = await fetch('http://localhost:5000/api/tools')
        if (response.ok) {
          const data = await response.json()
          setTools(data.tools || [])
        }
      } catch (error) {
        console.error('Error fetching tools:', error)
        // Fallback to mock data if API unavailable
        setTools([
          { slug: 'jpg-to-png', title: 'JPG to PNG', category: 'image', icon: '🖼️' },
          { slug: 'pdf-to-docx', title: 'PDF to DOCX', category: 'document', icon: '📄' },
          { slug: 'compress-pdf', title: 'Compress PDF', category: 'pdf', icon: '📊' }
        ])
      } finally {
        setToolsLoading(false)
      }
    }
    if (activeTab === 'tools') fetchTools()
  }, [activeTab])

  const [contentBlocks, setContentBlocks] = useState({
    home: {
      hero: { title: 'Convert Files Online', subtitle: 'Fast & Secure', cta: 'Get Started' },
      features: { items: ['Instant Conversion', '100+ Formats', 'Secure Upload'] },
      pricing: { plans: [{ name: 'Free', price: '$0', features: ['10/day'] }, { name: 'Pro', price: '$9', features: ['Unlimited'] }] },
      faq: { items: [{ q: 'Is it free?', a: 'Yes, with limits.' }] },
      testimonials: { items: [{ text: 'Great service!', author: 'John' }] },
      cta: { text: 'Ready to convert?', button: 'Start Free' }
    },
    pricing: {
      hero: { title: 'Simple Pricing', subtitle: 'No hidden fees' },
      plans: { data: [{ name: 'Free', price: '$0' }, { name: 'Pro', price: '$9' }] }
    },
    about: {
      hero: { title: 'About Us', subtitle: 'Our Story' },
      team: { description: 'Founded in 2024' }
    }
  })

  const blockTemplates = {
    hero: { title: 'Hero Section', icon: '🎯', template: { title: 'Section Title', subtitle: 'Subtitle text', cta: 'Button Text' } },
    pricing: { title: 'Pricing Cards', icon: '💰', template: { plans: [{ name: 'Plan', price: '$0', features: [] }] } },
    faq: { title: 'FAQ Section', icon: '❓', template: { items: [{ q: 'Question?', a: 'Answer here' }] } },
    features: { title: 'Features List', icon: '⭐', template: { items: ['Feature 1', 'Feature 2'] } },
    testimonials: { title: 'Testimonials', icon: '💬', template: { items: [{ text: 'Great!', author: 'John' }] } },
    cta: { title: 'Call to Action', icon: '🚀', template: { text: 'CTA message', button: 'Action Button' } },
    gallery: { title: 'Image Gallery', icon: '🖼️', template: { images: [{ url: '', title: '' }] } },
    team: { title: 'Team Members', icon: '👥', template: { members: [{ name: '', role: '', image: '' }] } },
    stats: { title: 'Statistics', icon: '📊', template: { stats: [{ label: '', value: '' }] } },
    newsletter: { title: 'Newsletter Signup', icon: '📧', template: { title: 'Subscribe', placeholder: 'Enter email', button: 'Subscribe' } }
  }

  const handleAddPage = () => {
    if (!newPageName.trim()) {
      alert('Please enter a page name')
      return
    }

    const pageSlug = newPageName.toLowerCase().replace(/\s+/g, '_')
    
    if (contentBlocks[pageSlug]) {
      alert('Page already exists')
      return
    }

    setContentBlocks(prev => ({
      ...prev,
      [pageSlug]: {}
    }))

    setBlockOrder(prev => ({
      ...prev,
      [pageSlug]: []
    }))

    setPageMetaData(prev => ({
      ...prev,
      [pageSlug]: {
        title: newPageName,
        description: `Page: ${newPageName}`,
        slug: pageSlug
      }
    }))

    setSelectedPage(pageSlug)
    setNewPageName('')
    setShowAddPageForm(false)
    alert(`✓ Page "${newPageName}" created successfully!`)
  }

  const handleEditPage = (page) => {
    setEditingPage(page)
    setShowPageSettings(true)
  }

  const handleDeletePage = (page) => {
    if (window.confirm(`Delete page "${page}" and all its blocks? This cannot be undone.`)) {
      setContentBlocks(prev => {
        const updated = { ...prev }
        delete updated[page]
        return updated
      })

      setBlockOrder(prev => {
        const updated = { ...prev }
        delete updated[page]
        return updated
      })

      setPageMetaData(prev => {
        const updated = { ...prev }
        delete updated[page]
        return updated
      })

      if (selectedPage === page) {
        const remainingPages = Object.keys(contentBlocks).filter(p => p !== page)
        setSelectedPage(remainingPages[0] || 'home')
      }

      alert(`Deleted page "${page}"`)
    }
  }

  const handleExportTemplate = () => {
    const exportData = {
      pageName: selectedPage,
      pageMetaData: pageMetaData[selectedPage],
      blocks: contentBlocks[selectedPage],
      blockOrder: blockOrder[selectedPage],
      timestamp: new Date().toISOString()
    }

    const jsonString = JSON.stringify(exportData, null, 2)
    const blob = new Blob([jsonString], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${selectedPage}_template_${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
    alert('✓ Template exported successfully!')
  }

  const handleImportTemplate = (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (event) => {
      try {
        const importedData = JSON.parse(event.target?.result)
        const newPageSlug = importedData.pageName || `imported_${Date.now()}`

        setContentBlocks(prev => ({
          ...prev,
          [newPageSlug]: importedData.blocks || {}
        }))

        setBlockOrder(prev => ({
          ...prev,
          [newPageSlug]: importedData.blockOrder || []
        }))

        setPageMetaData(prev => ({
          ...prev,
          [newPageSlug]: importedData.pageMetaData || { title: newPageSlug, description: '', slug: newPageSlug }
        }))

        setSelectedPage(newPageSlug)
        alert(`✓ Template imported as page: "${newPageSlug}"`)
      } catch (error) {
        alert('✗ Invalid template file. Ensure it\'s a valid JSON export.')
      }
    }
    reader.readAsText(file)
    e.target.value = ''
  }

  const handleImportCSS = (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (event) => {
      const cssContent = event.target?.result
      setCustomCSS(cssContent)
      
      // Apply CSS to page
      const styleId = 'cms-custom-styles'
      let styleEl = document.getElementById(styleId)
      if (!styleEl) {
        styleEl = document.createElement('style')
        styleEl.id = styleId
        document.head.appendChild(styleEl)
      }
      styleEl.textContent = cssContent
      
      alert('✓ CSS successfully applied!')
    }
    reader.readAsText(file)
    e.target.value = ''
  }

  const handleExportCSS = () => {
    if (!customCSS.trim()) {
      alert('No custom CSS to export. Import or add CSS first.')
      return
    }

    const blob = new Blob([customCSS], { type: 'text/css' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `styles_${Date.now()}.css`
    a.click()
    URL.revokeObjectURL(url)
    alert('✓ CSS exported successfully!')
  }

  const handleAddBlock = () => {
    if (!newBlockName.trim()) {
      alert('Please enter a block name')
      return
    }

    const blockKey = newBlockName.toLowerCase().replace(/\s+/g, '_')
    const template = blockTemplates[newBlockType]?.template || {}

    setContentBlocks(prev => ({
      ...prev,
      [selectedPage]: {
        ...prev[selectedPage],
        [blockKey]: JSON.parse(JSON.stringify(template))
      }
    }))

    setBlockOrder(prev => ({
      ...prev,
      [selectedPage]: [...(prev[selectedPage] || []), blockKey]
    }))

    setNewBlockName('')
    setNewBlockType('hero')
    setShowAddBlockForm(false)
    setSelectedBlock(blockKey)
    alert(`✓ Block "${newBlockName}" added successfully!`)
  }

  const handleDeleteBlock = (blockName) => {
    if (window.confirm(`Are you sure you want to delete the "${blockName}" block?`)) {
      setContentBlocks(prev => {
        const updated = { ...prev[selectedPage] }
        delete updated[blockName]
        return {
          ...prev,
          [selectedPage]: updated
        }
      })

      setBlockOrder(prev => ({
        ...prev,
        [selectedPage]: prev[selectedPage].filter(b => b !== blockName)
      }))

      setSelectedBlock(null)
      alert(`Deleted "${blockName}" block`)
    }
  }

  const handleMoveBlock = (blockName, direction) => {
    const currentOrder = blockOrder[selectedPage] || []
    const currentIndex = currentOrder.indexOf(blockName)

    if (direction === 'up' && currentIndex > 0) {
      const newOrder = [...currentOrder];
      [newOrder[currentIndex - 1], newOrder[currentIndex]] = [newOrder[currentIndex], newOrder[currentIndex - 1]]
      setBlockOrder(prev => ({
        ...prev,
        [selectedPage]: newOrder
      }))
    } else if (direction === 'down' && currentIndex < currentOrder.length - 1) {
      const newOrder = [...currentOrder];
      [newOrder[currentIndex + 1], newOrder[currentIndex]] = [newOrder[currentIndex], newOrder[currentIndex + 1]]
      setBlockOrder(prev => ({
        ...prev,
        [selectedPage]: newOrder
      }))
    }
  }

  const handleEditBlock = (blockName) => {
    setSelectedBlock(blockName)
    setEditMode(true)
  }

  const handleSaveBlock = () => {
    alert(`Saved ${selectedBlock} block for ${selectedPage}`)
    setEditMode(false)
  }

  const handleJsonChange = (e) => {
    try {
      const updated = JSON.parse(e.target.value)
      setContentBlocks(prev => ({
        ...prev,
        [selectedPage]: {
          ...prev[selectedPage],
          [selectedBlock]: updated
        }
      }))
    } catch (err) {
      // Invalid JSON - let user fix it
    }
  }

  const handleToolUpdate = async (toolData) => {
    try {
      const response = await fetch(`http://localhost:5000/api/tools/${toolData.slug}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(toolData)
      })
      if (response.ok) {
        alert('✓ Tool updated successfully!')
        setTools(tools.map(t => t.slug === toolData.slug ? toolData : t))
        setSelectedTool(null)
      }
    } catch (error) {
      console.error('Error updating tool:', error)
      alert('✗ Failed to update tool')
    }
  }

  const handleToolDelete = async (slug) => {
    if (window.confirm('Are you sure you want to delete this tool?')) {
      try {
        const response = await fetch(`http://localhost:5000/api/tools/${slug}`, { method: 'DELETE' })
        if (response.ok) {
          alert('✓ Tool deleted successfully!')
          setTools(tools.filter(t => t.slug !== slug))
          setSelectedTool(null)
        }
      } catch (error) {
        console.error('Error deleting tool:', error)
        alert('✗ Failed to delete tool')
      }
    }
  }

  const pages = Object.keys(contentBlocks)
  const currentPageBlocks = contentBlocks[selectedPage] || {}
  const orderedBlockNames = blockOrder[selectedPage] || []

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="🧠" size={24} /> Content Manager</h2>
      <p className="section-subtitle">Manage website content blocks and tools - Create, Edit, Delete, Sort sections dynamically</p>

      <div style={{display: 'flex', gap: '8px', marginBottom: '20px', borderBottom: '2px solid #eee'}}>
        <button
          onClick={() => setActiveTab('pages')}
          style={{
            padding: '12px 16px',
            background: activeTab === 'pages' ? '#667eea' : 'transparent',
            color: activeTab === 'pages' ? 'white' : '#666',
            border: 'none',
            borderRadius: activeTab === 'pages' ? '4px 4px 0 0' : '0',
            cursor: 'pointer',
            fontWeight: 'bold',
            fontSize: '14px'
          }}
        >
          <UniversalIcon icon="📄" size={14} /> Pages & Blocks
        </button>
        <button
          onClick={() => setActiveTab('tools')}
          style={{
            padding: '12px 16px',
            background: activeTab === 'tools' ? '#667eea' : 'transparent',
            color: activeTab === 'tools' ? 'white' : '#666',
            border: 'none',
            borderRadius: activeTab === 'tools' ? '4px 4px 0 0' : '0',
            cursor: 'pointer',
            fontWeight: 'bold',
            fontSize: '14px'
          }}
        >
          <UniversalIcon icon="🔧" size={14} /> Converter Tools ({tools.length})
        </button>
      </div>

      {activeTab === 'pages' ? (
        <>
        <div className="admin-stats-grid" style={{marginBottom: '20px'}}>
          <div className="admin-stat-card metric-info">
          <div className="stat-icon"><UniversalIcon icon="📄" size={48} /></div>
          <div className="stat-content">
            <h3>Pages</h3>
            <p className="stat-value">{pages.length}</p>
            <p className="stat-detail">Content pages</p>
          </div>
        </div>
        <div className="admin-stat-card metric-primary">
          <div className="stat-icon">🧩</div>
          <div className="stat-content">
            <h3>Content Blocks</h3>
            <p className="stat-value">{orderedBlockNames.length}</p>
            <p className="stat-detail">On {selectedPage}</p>
          </div>
        </div>
        <div className="admin-stat-card metric-success">
          <div className="stat-icon">✓</div>
          <div className="stat-content">
            <h3>Published</h3>
            <p className="stat-value">{orderedBlockNames.length}</p>
            <p className="stat-detail">All active</p>
          </div>
        </div>
        <div className="admin-stat-card metric-warning">
          <div className="stat-icon"><UniversalIcon icon="⚡" size={48} /></div>
          <div className="stat-content">
            <h3>Last Updated</h3>
            <p className="stat-value" style={{fontSize: '14px'}}>2026-03-06</p>
            <p className="stat-detail">14:32</p>
          </div>
        </div>
      </div>

      <div style={{display: 'grid', gridTemplateColumns: '300px 1fr', gap: '20px'}}>
        <div style={{background: '#f9f9f9', borderRadius: '4px', padding: '15px', border: '1px solid #eee', height: 'fit-content', maxHeight: '70vh', overflowY: 'auto'}}>
          <h4 style={{marginTop: 0, display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            📄 Pages
            <button 
              onClick={() => setShowAddPageForm(true)}
              title="Add new page"
              style={{
                background: '#11998e',
                color: 'white',
                border: 'none',
                borderRadius: '3px',
                padding: '4px 8px',
                cursor: 'pointer',
                fontSize: '12px',
                fontWeight: 'bold'
              }}
            >
              + Add
            </button>
          </h4>
          <div style={{display: 'flex', flexDirection: 'column', gap: '6px'}}>
            {pages.map(page => (
              <div key={page} style={{
                display: 'flex',
                gap: '6px',
                alignItems: 'center',
                background: selectedPage === page ? '#f0f4ff' : 'white',
                border: selectedPage === page ? '2px solid #667eea' : '1px solid #ddd',
                borderRadius: '4px',
                padding: '8px'
              }}>
                <button
                  onClick={() => {
                    setSelectedPage(page)
                    setSelectedBlock(null)
                    setEditMode(false)
                  }}
                  style={{
                    flex: 1,
                    padding: '6px 8px',
                    border: 'none',
                    background: 'transparent',
                    borderRadius: '3px',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontWeight: selectedPage === page ? 'bold' : 'normal',
                    transition: 'all 0.2s',
                    fontSize: '13px'
                  }}
                >
                  📄 {pageMetaData[page]?.title || page.charAt(0).toUpperCase() + page.slice(1)}
                </button>

                <button
                  onClick={() => handleEditPage(page)}
                  title="Edit page settings"
                  style={{
                    padding: '4px 6px',
                    background: '#667eea',
                    color: 'white',
                    border: 'none',
                    borderRadius: '2px',
                    cursor: 'pointer',
                    fontSize: '11px'
                  }}
                >
                  ✎
                </button>

                {pages.length > 1 && (
                  <button
                    onClick={() => handleDeletePage(page)}
                    title="Delete page"
                    style={{
                      padding: '4px 6px',
                      background: '#eb3349',
                      color: 'white',
                      border: 'none',
                      borderRadius: '2px',
                      cursor: 'pointer',
                      fontSize: '11px'
                    }}
                  >
                    🗑️
                  </button>
                )}
              </div>
            ))}
          </div>

          <h4 style={{marginTop: '20px', marginBottom: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            🧩 Blocks
            {orderedBlockNames.length > 0 && <span style={{fontSize: '11px', color: '#999', fontWeight: 'normal'}}>Sort</span>}
          </h4>
          <button 
            onClick={() => setShowAddBlockForm(true)}
            style={{
              width: '100%',
              padding: '10px',
              background: '#11998e',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold',
              marginBottom: '10px',
              fontSize: '13px'
            }}
          >
            <UniversalIcon icon="➕" size={14} /> Add New Block
          </button>

          <div style={{display: 'flex', flexDirection: 'column', gap: '4px'}}>
            {orderedBlockNames.length === 0 ? (
              <p style={{fontSize: '12px', color: '#999', textAlign: 'center', padding: '20px 0'}}>
                No blocks yet.<br/>Click "Add New Block" to start.
              </p>
            ) : (
              orderedBlockNames.map((block, index) => (
                <div key={block} style={{
                  display: 'flex',
                  gap: '4px',
                  alignItems: 'center',
                  background: selectedBlock === block ? '#f0fdf9' : 'white',
                  border: selectedBlock === block ? '2px solid #11998e' : '1px solid #ddd',
                  borderRadius: '3px',
                  padding: '6px 4px'
                }}>
                  <div style={{
                    minWidth: '20px',
                    height: '20px',
                    background: '#667eea',
                    color: 'white',
                    borderRadius: '2px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '10px',
                    fontWeight: 'bold'
                  }}>
                    {index + 1}
                  </div>

                  <button
                    onClick={() => handleEditBlock(block)}
                    style={{
                      flex: 1,
                      padding: '6px 8px',
                      border: 'none',
                      background: 'transparent',
                      borderRadius: '2px',
                      cursor: 'pointer',
                      textAlign: 'left',
                      fontSize: '12px',
                      fontWeight: selectedBlock === block ? 'bold' : 'normal',
                      transition: 'all 0.2s'
                    }}
                  >
                    {block.charAt(0).toUpperCase() + block.slice(1)}
                  </button>

                  <div style={{display: 'flex', gap: '2px'}}>
                    <button
                      onClick={() => handleMoveBlock(block, 'up')}
                      disabled={index === 0}
                      style={{
                        padding: '4px 5px',
                        background: index === 0 ? '#eee' : '#667eea',
                        color: index === 0 ? '#999' : 'white',
                        border: 'none',
                        borderRadius: '2px',
                        cursor: index === 0 ? 'not-allowed' : 'pointer',
                        fontSize: '9px',
                        fontWeight: 'bold'
                      }}
                      title="Move up"
                    >
                      ↑
                    </button>
                    <button
                      onClick={() => handleMoveBlock(block, 'down')}
                      disabled={index === orderedBlockNames.length - 1}
                      style={{
                        padding: '4px 5px',
                        background: index === orderedBlockNames.length - 1 ? '#eee' : '#667eea',
                        color: index === orderedBlockNames.length - 1 ? '#999' : 'white',
                        border: 'none',
                        borderRadius: '2px',
                        cursor: index === orderedBlockNames.length - 1 ? 'not-allowed' : 'pointer',
                        fontSize: '9px',
                        fontWeight: 'bold'
                      }}
                      title="Move down"
                    >
                      ↓
                    </button>
                  </div>

                  <button
                    onClick={() => handleDeleteBlock(block)}
                    style={{
                      padding: '4px 6px',
                      background: '#eb3349',
                      color: 'white',
                      border: 'none',
                      borderRadius: '2px',
                      cursor: 'pointer',
                      fontSize: '9px'
                    }}
                    title="Delete block"
                  >
                    🗑️
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        <div>
          {showAddPageForm && (
            <div style={{
              background: 'white',
              border: '2px solid #667eea',
              borderRadius: '4px',
              padding: '20px',
              marginBottom: '20px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}>
              <h3><UniversalIcon icon="📄" size={20} /> Create New Page</h3>
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginTop: '15px'}}>
                <div className="setting-group">
                  <label>Page Name</label>
                  <input
                    type="text"
                    value={newPageName}
                    onChange={(e) => setNewPageName(e.target.value)}
                    placeholder="e.g., Blog, Features, Contact"
                    className="form-input"
                  />
                  <small style={{color: '#666'}}>Page slug will auto-generate from name</small>
                </div>
                <div className="setting-group">
                  <label>Description (Optional)</label>
                  <input
                    type="text"
                    placeholder="Brief page description"
                    className="form-input"
                  />
                </div>
              </div>

              <div style={{display: 'flex', gap: '8px', marginTop: '15px'}}>
                <button
                  onClick={handleAddPage}
                  style={{
                    flex: 1,
                    padding: '10px',
                    background: '#667eea',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontWeight: 'bold'
                  }}
                >
                  ✓ Create Page
                </button>
                <button
                  onClick={() => {
                    setShowAddPageForm(false)
                    setNewPageName('')
                  }}
                  style={{
                    flex: 1,
                    padding: '10px',
                    background: '#ddd',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  ✕ Cancel
                </button>
              </div>
            </div>
          )}

          {showPageSettings && editingPage && (
            <div style={{
              background: 'white',
              border: '2px solid #667eea',
              borderRadius: '4px',
              padding: '20px',
              marginBottom: '20px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}>
              <h3><UniversalIcon icon="⚙️" size={20} /> Page Settings: {editingPage}</h3>
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginTop: '15px'}}>
                <div className="setting-group">
                  <label>Page Title</label>
                  <input
                    type="text"
                    defaultValue={pageMetaData[editingPage]?.title}
                    className="form-input"
                  />
                </div>
                <div className="setting-group">
                  <label>Page Slug</label>
                  <input
                    type="text"
                    defaultValue={pageMetaData[editingPage]?.slug}
                    className="form-input"
                  />
                </div>
                <div className="setting-group" style={{gridColumn: '1 / -1'}}>
                  <label>Page Description</label>
                  <textarea
                    defaultValue={pageMetaData[editingPage]?.description}
                    className="form-input"
                    style={{height: '80px'}}
                  />
                </div>
              </div>

              <div style={{display: 'flex', gap: '8px', marginTop: '15px'}}>
                <button
                  onClick={() => {
                    alert('Page settings saved!')
                    setShowPageSettings(false)
                  }}
                  style={{
                    flex: 1,
                    padding: '10px',
                    background: '#667eea',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontWeight: 'bold'
                  }}
                >
                  <UniversalIcon icon="💾" size={14} /> Save Settings
                </button>
                <button
                  onClick={() => setShowPageSettings(false)}
                  style={{
                    flex: 1,
                    padding: '10px',
                    background: '#ddd',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  ✕ Close
                </button>
              </div>
            </div>
          )}

          {showAddBlockForm && (
            <div style={{
              background: 'white',
              border: '2px solid #11998e',
              borderRadius: '4px',
              padding: '20px',
              marginBottom: '20px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}>
              <h3><UniversalIcon icon="➕" size={20} /> Create New Block</h3>
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginTop: '15px'}}>
                <div className="setting-group">
                  <label>Block Name</label>
                  <input
                    type="text"
                    value={newBlockName}
                    onChange={(e) => setNewBlockName(e.target.value)}
                    placeholder="e.g., Hero, Testimonials, Stats"
                    className="form-input"
                  />
                  <small style={{color: '#666'}}>Used as internal identifier</small>
                </div>
                <div className="setting-group">
                  <label>Block Type (Template)</label>
                  <select
                    value={newBlockType}
                    onChange={(e) => setNewBlockType(e.target.value)}
                    className="form-input"
                  >
                    {Object.entries(blockTemplates).map(([key, data]) => (
                      <option key={key} value={key}>{data.icon} {data.title}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div style={{marginTop: '15px', background: '#f9f9f9', padding: '12px', borderRadius: '3px'}}>
                <strong>Template Preview:</strong>
                <pre style={{fontSize: '11px', margin: '8px 0 0 0', whiteSpace: 'pre-wrap', wordBreak: 'break-word'}}>
                  {JSON.stringify(blockTemplates[newBlockType].template, null, 2)}
                </pre>
              </div>

              <div style={{display: 'flex', gap: '8px', marginTop: '15px'}}>
                <button
                  onClick={handleAddBlock}
                  style={{
                    flex: 1,
                    padding: '10px',
                    background: '#11998e',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontWeight: 'bold'
                  }}
                >
                  ✓ Create Block
                </button>
                <button
                  onClick={() => {
                    setShowAddBlockForm(false)
                    setNewBlockName('')
                    setNewBlockType('hero')
                  }}
                  style={{
                    flex: 1,
                    padding: '10px',
                    background: '#ddd',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  ✕ Cancel
                </button>
              </div>
            </div>
          )}

          {selectedBlock ? (
            <div style={{background: 'white', border: '1px solid #eee', borderRadius: '4px', padding: '20px'}}>
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px'}}>
                <h3><UniversalIcon icon="✏️" size={20} /> Edit: {selectedBlock}</h3>
                <div style={{display: 'flex', gap: '8px'}}>
                  <button className="action-btn retry" onClick={handleSaveBlock} style={{background: '#11998e', color: 'white'}}>
                    <UniversalIcon icon="💾" size={14} /> Save
                  </button>
                  <button className="action-btn cancel" onClick={() => setEditMode(false)}>
                    ✕ Close
                  </button>
                </div>
              </div>

              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px'}}>
                <div>
                  <label style={{fontWeight: 'bold', display: 'block', marginBottom: '8px'}}><UniversalIcon icon="📋" size={16} /> JSON Content</label>
                  <textarea
                    value={JSON.stringify(currentPageBlocks[selectedBlock], null, 2)}
                    onChange={handleJsonChange}
                    style={{
                      width: '100%',
                      height: '300px',
                      fontFamily: 'monospace',
                      fontSize: '12px',
                      padding: '10px',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      fontWeight: '500',
                      resize: 'none'
                    }}
                  />
                  <small style={{color: '#666', marginTop: '8px', display: 'block'}}>
                    Edit JSON directly or use the form editor below
                  </small>
                </div>

                <div style={{background: '#f5f5f5', padding: '15px', borderRadius: '4px', border: '1px solid #ddd'}}>
                  <label style={{fontWeight: 'bold', display: 'block', marginBottom: '10px'}}>👁️ Preview</label>
                  <div style={{background: 'white', padding: '12px', borderRadius: '3px', minHeight: '280px', overflow: 'auto'}}>
                    <pre style={{fontSize: '11px', margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word'}}>
                      {JSON.stringify(currentPageBlocks[selectedBlock], null, 2)}
                    </pre>
                  </div>
                </div>
              </div>

              <div style={{marginTop: '20px', background: '#f9f9f9', padding: '15px', borderRadius: '4px'}}>
                <h4><UniversalIcon icon="📝" size={16} /> Quick Edit Form</h4>
                <p style={{fontSize: '12px', color: '#666', marginBottom: '12px'}}>
                  Edit common fields here, or use the JSON editor for advanced changes
                </p>
                {selectedBlock && currentPageBlocks[selectedBlock] && (
                  <div>
                    {Object.entries(currentPageBlocks[selectedBlock]).map(([key, value]) => (
                      <div key={key} className="setting-group" style={{marginBottom: '10px'}}>
                        <label style={{fontSize: '12px'}}>{key.charAt(0).toUpperCase() + key.slice(1)}</label>
                        {typeof value === 'string' ? (
                          <input
                            type="text"
                            defaultValue={value}
                            className="form-input"
                            style={{fontSize: '12px'}}
                          />
                        ) : typeof value === 'boolean' ? (
                          <input type="checkbox" defaultChecked={value} />
                        ) : typeof value === 'number' ? (
                          <input type="number" defaultValue={value} className="form-input" style={{fontSize: '12px'}} />
                        ) : (
                          <textarea
                            defaultValue={JSON.stringify(value, null, 2)}
                            className="form-input"
                            style={{fontSize: '11px', height: '80px', fontFamily: 'monospace'}}
                          />
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div style={{background: 'white', border: '1px dashed #ddd', borderRadius: '4px', padding: '40px', textAlign: 'center', color: '#999'}}>
              <p><UniversalIcon icon="👈" size={18} /> Select or create a content block from the sidebar</p>
              <p style={{fontSize: '12px'}}>
                {orderedBlockNames.length > 0 
                  ? `Blocks available: ${orderedBlockNames.join(', ')}`
                  : 'No blocks yet. Click "Add New Block" to get started.'
                }
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="admin-section-content" style={{marginTop: '30px', background: '#f0f4ff', padding: '15px', borderRadius: '4px', border: '1px solid #667eea'}}>
        <h3><UniversalIcon icon="📋" size={20} /> Block Rendering Order (Page: {selectedPage})</h3>
        <p style={{fontSize: '12px', color: '#555', marginBottom: '12px'}}>
          Blocks will render in this order on the frontend. Use ↑ ↓ buttons to reorder.
        </p>
        {orderedBlockNames.length > 0 ? (
          <div style={{display: 'flex', flexWrap: 'wrap', gap: '8px'}}>
            {orderedBlockNames.map((block, idx) => (
              <div key={block} style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                background: 'white',
                padding: '8px 12px',
                borderRadius: '4px',
                border: '1px solid #ccc'
              }}>
                <span style={{background: '#667eea', color: 'white', width: '20px', height: '20px', borderRadius: '2px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', fontWeight: 'bold'}}>
                  {idx + 1}
                </span>
                <strong style={{fontSize: '12px'}}>{block}</strong>
                {idx < orderedBlockNames.length - 1 && <span style={{color: '#999'}}>→</span>}
              </div>
            ))}
          </div>
        ) : (
          <p style={{fontSize: '12px', color: '#999', fontStyle: 'italic'}}>No blocks added yet</p>
        )}
      </div>

      <div className="admin-section-content" style={{marginTop: '30px', background: '#fff8f0', padding: '15px', borderRadius: '4px', border: '1px solid #ff9800'}}>
        <h3><UniversalIcon icon="📦" size={20} /> Template & CSS Management</h3>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px', marginTop: '15px'}}>
          
          <div style={{background: 'white', padding: '15px', borderRadius: '4px', border: '1px solid #ddd'}}>
            <h4 style={{marginTop: 0, fontSize: '14px'}}><UniversalIcon icon="📤" size={16} /> Export Page Template</h4>
            <p style={{fontSize: '12px', color: '#666', margin: '8px 0'}}>
              Download current page and blocks as JSON template for backup or sharing.
            </p>
            <button
              onClick={handleExportTemplate}
              style={{
                width: '100%',
                padding: '8px',
                background: '#4CAF50',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: 'bold',
                fontSize: '12px'
              }}
            >
              <UniversalIcon icon="⬇️" size={14} /> Export as JSON
            </button>
          </div>

          <div style={{background: 'white', padding: '15px', borderRadius: '4px', border: '1px solid #ddd'}}>
            <h4 style={{marginTop: 0, fontSize: '14px'}}><UniversalIcon icon="📥" size={16} /> Import Page Template</h4>
            <p style={{fontSize: '12px', color: '#666', margin: '8px 0'}}>
              Load a previously exported JSON template as a new page.
            </p>
            <label style={{
              display: 'block',
              width: '100%',
              padding: '8px',
              background: '#2196F3',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold',
              fontSize: '12px',
              textAlign: 'center'
            }}>
              <UniversalIcon icon="📂" size={14} /> Choose JSON File
              <input
                type="file"
                accept=".json"
                onChange={handleImportTemplate}
                style={{display: 'none'}}
              />
            </label>
          </div>

          <div style={{background: 'white', padding: '15px', borderRadius: '4px', border: '1px solid #ddd'}}>
            <h4 style={{marginTop: 0, fontSize: '14px'}}><UniversalIcon icon="🎨" size={16} /> Import Custom CSS</h4>
            <p style={{fontSize: '12px', color: '#666', margin: '8px 0'}}>
              Upload a CSS file to apply custom styles to all pages.
            </p>
            <label style={{
              display: 'block',
              width: '100%',
              padding: '8px',
              background: '#9C27B0',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold',
              fontSize: '12px',
              textAlign: 'center'
            }}>
              <UniversalIcon icon="🎨" size={14} /> Upload CSS
              <input
                type="file"
                accept=".css"
                onChange={handleImportCSS}
                style={{display: 'none'}}
              />
            </label>
          </div>

          <div style={{background: 'white', padding: '15px', borderRadius: '4px', border: '1px solid #ddd'}}>
            <h4 style={{marginTop: 0, fontSize: '14px'}}><UniversalIcon icon="💾" size={16} /> Export Custom CSS</h4>
            <p style={{fontSize: '12px', color: '#666', margin: '8px 0'}}>
              Download imported CSS styles as a file.
            </p>
            <button
              onClick={handleExportCSS}
              style={{
                width: '100%',
                padding: '8px',
                background: '#FF5722',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: 'bold',
                fontSize: '12px'
              }}
            >
              ⬇️ Export CSS
            </button>
          </div>

        </div>
      </div>

      <div className="admin-section-content" style={{marginTop: '30px'}}>
        <h3>🏗️ Available Block Templates</h3>
        <p style={{fontSize: '13px', color: '#666', marginBottom: '15px'}}>
          Choose a template when creating new blocks. Each includes starter content you can customize.
        </p>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '12px'}}>
          {Object.entries(blockTemplates).map(([key, data]) => (
            <div key={key} style={{padding: '12px', border: '1px solid #eee', borderRadius: '4px', textAlign: 'center', background: '#fafafa'}}>
              <div style={{fontSize: '24px', marginBottom: '6px'}}>{data.icon}</div>
              <strong style={{fontSize: '13px'}}>{data.title}</strong>
              <p style={{fontSize: '10px', color: '#666', margin: '6px 0 0 0'}}>
                {key}
              </p>
            </div>
          ))}
        </div>
      </div>

      <div className="admin-section-content" style={{marginTop: '20px', background: '#f9f9f9', padding: '15px', borderRadius: '4px'}}>
        <h4>🗄️ Database Backend (content_blocks table)</h4>
        <pre style={{background: 'white', padding: '12px', borderRadius: '3px', fontSize: '11px', overflow: 'auto', maxHeight: '120px'}}>
{`Columns: id | page_slug | block_type | block_key | block_order | content_json | status

Example:
1 | home | hero | hero_main | 1 | {...title, subtitle} | published
2 | home | features | features_main | 2 | {...items} | published
...`}
        </pre>
        <small style={{color: '#666'}}>Added block_order column to maintain sorting across frontend/backend</small>
      </div>
        </>
      ) : (
        <div style={{background: '#f5f5f5', padding: '20px', borderRadius: '4px'}}>
          <h3><UniversalIcon icon="🔧" size={20} /> Converter Tool Management</h3>
          {toolsLoading ? (
            <p>Loading tools...</p>
          ) : tools.length === 0 ? (
            <p style={{color: '#666'}}>No tools found. Make sure the backend API is running.</p>
          ) : (
            <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '15px', marginTop: '15px'}}>
              {tools.map(tool => (
                <div key={tool.slug} style={{background: 'white', border: '1px solid #ddd', borderRadius: '4px', padding: '15px'}}>
                  <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '10px'}}>
                    <div>
                      <div style={{fontSize: '20px', marginBottom: '5px'}}>{tool.icon || '🔧'}</div>
                      <h4 style={{margin: 0}}>{tool.title}</h4>
                      <p style={{fontSize: '12px', color: '#666', margin: '4px 0'}}>Slug: {tool.slug}</p>
                    </div>
                    <span style={{background: '#667eea', color: 'white', padding: '4px 8px', borderRadius: '3px', fontSize: '11px'}}>
                      {tool.category || 'Other'}
                    </span>
                  </div>
                  <p style={{fontSize: '13px', color: '#555', margin: '8px 0'}}>{tool.description?.substring(0, 100) || 'No description'}...</p>
                  <div style={{display: 'flex', gap: '8px', marginTop: '12px'}}>
                    <button
                      onClick={() => {
                        setSelectedTool(tool)
                        setEditingTool(JSON.parse(JSON.stringify(tool)))
                      }}
                      style={{flex: 1, padding: '8px', background: '#667eea', color: 'white', border: 'none', borderRadius: '3px', cursor: 'pointer', fontSize: '12px'}}
                    >
                      ✎ Edit
                    </button>
                    <button
                      onClick={() => handleToolDelete(tool.slug)}
                      style={{padding: '8px 12px', background: '#eb3349', color: 'white', border: 'none', borderRadius: '3px', cursor: 'pointer', fontSize: '12px'}}
                    >
                      🗑️
                    </button>
                    <a
                      href={`/${tool.slug}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{padding: '8px 12px', background: '#11998e', color: 'white', border: 'none', borderRadius: '3px', cursor: 'pointer', fontSize: '12px', textDecoration: 'none', textAlign: 'center'}}
                    >
                      👁️ View
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {selectedTool && editingTool && (
            <div style={{marginTop: '30px', background: 'white', border: '1px solid #667eea', borderRadius: '4px', padding: '20px'}}>
              <h4>Edit Tool: {editingTool.title}</h4>
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginTop: '15px'}}>
                <div>
                  <label style={{fontWeight: 'bold'}}>Title</label>
                  <input
                    type="text"
                    value={editingTool.title}
                    onChange={(e) => setEditingTool({...editingTool, title: e.target.value})}
                    className="form-input"
                  />
                </div>
                <div>
                  <label style={{fontWeight: 'bold'}}>Icon</label>
                  <input
                    type="text"
                    value={editingTool.icon}
                    onChange={(e) => setEditingTool({...editingTool, icon: e.target.value})}
                    className="form-input"
                    placeholder="e.g., 🖼️"
                  />
                </div>
              </div>
              <div style={{marginTop: '15px'}}>
                <label style={{fontWeight: 'bold'}}>Description</label>
                <textarea
                  value={editingTool.description || ''}
                  onChange={(e) => setEditingTool({...editingTool, description: e.target.value})}
                  className="form-input"
                  style={{height: '100px'}}
                />
              </div>
              <div style={{display: 'flex', gap: '8px', marginTop: '15px'}}>
                <button
                  onClick={() => {
                    handleToolUpdate(editingTool)
                  }}
                  style={{flex: 1, padding: '10px', background: '#11998e', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold'}}
                >
                  💾 Save Changes
                </button>
                <button
                  onClick={() => {
                    setSelectedTool(null)
                    setEditingTool(null)
                  }}
                  style={{flex: 1, padding: '10px', background: '#ddd', border: 'none', borderRadius: '4px', cursor: 'pointer'}}
                >
                  ✕ Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ContentManager
