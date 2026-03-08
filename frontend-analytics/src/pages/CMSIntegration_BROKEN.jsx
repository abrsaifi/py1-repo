import React, { useState } from 'react'
import '../styles/admin.css'

const ContentManager = () => {
  const [selectedPage, setSelectedPage] = useState('home')
  const [selectedBlock, setSelectedBlock] = useState(null)
  const [editMode, setEditMode] = useState(false)
  const [showAddBlockForm, setShowAddBlockForm] = useState(false)
  const [newBlockType, setNewBlockType] = useState('hero')
  const [newBlockName, setNewBlockName] = useState('')
  const [blockOrder, setBlockOrder] = useState({
    home: ['hero', 'features', 'pricing', 'faq', 'testimonials', 'cta'],
    pricing: ['hero', 'plans'],
    about: ['hero', 'team']
  })

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

    // Add to block order
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

      // Remove from block order
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
      const newOrder = [...currentOrder]
      [newOrder[currentIndex - 1], newOrder[currentIndex]] = [newOrder[currentIndex], newOrder[currentIndex - 1]]
      setBlockOrder(prev => ({
        ...prev,
        [selectedPage]: newOrder
      }))
    } else if (direction === 'down' && currentIndex < currentOrder.length - 1) {
      const newOrder = [...currentOrder]
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

  const pages = Object.keys(contentBlocks)
  const currentPageBlocks = contentBlocks[selectedPage] || {}
  const orderedBlockNames = blockOrder[selectedPage] || []

  return (
    <div className="admin-section">
      <h2>🧠 Content Manager</h2>
      <p className="section-subtitle">Manage website content blocks - Create, Edit, Delete, Sort sections dynamically</p>

      <div className="admin-stats-grid" style={{marginBottom: '20px'}}>
        <div className="admin-stat-card metric-info">
          <div className="stat-icon">📄</div>
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
          <div className="stat-icon">⚡</div>
          <div className="stat-content">
            <h3>Last Updated</h3>
            <p className="stat-value" style={{fontSize: '14px'}}>2026-03-06</p>
            <p className="stat-detail">14:32</p>
          </div>
        </div>
      </div>

      <div style={{display: 'grid', gridTemplateColumns: '300px 1fr', gap: '20px'}}>
        {/* PAGES & BLOCKS SIDEBAR */}
        <div style={{background: '#f9f9f9', borderRadius: '4px', padding: '15px', border: '1px solid #eee', height: 'fit-content', maxHeight: '70vh', overflowY: 'auto'}}>
          <h4 style={{marginTop: 0}}>📄 Pages</h4>
          <div style={{display: 'flex', flexDirection: 'column', gap: '8px'}}>
            {pages.map(page => (
              <button
                key={page}
                onClick={() => {
                  setSelectedPage(page)
                  setSelectedBlock(null)
                  setEditMode(false)
                }}
                style={{
                  padding: '10px 12px',
                  border: selectedPage === page ? '2px solid #667eea' : '1px solid #ddd',
                  background: selectedPage === page ? '#f0f4ff' : 'white',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  textAlign: 'left',
                  fontWeight: selectedPage === page ? 'bold' : 'normal',
                  transition: 'all 0.2s'
                }}
              >
                📄 {page.charAt(0).toUpperCase() + page.slice(1)}
              </button>
            ))}
          </div>

          <h4 style={{marginTop: '20px', marginBottom: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            🧩 Blocks
            {orderedBlockNames.length > 0 && <span style={{fontSize: '11px', color: '#999', fontWeight: 'normal'}}>Drag to sort</span>}
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
            ➕ Add New Block
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
                  {/* POSITION INDICATOR */}
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

                  {/* BLOCK NAME */}
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

                  {/* SORT BUTTONS */}
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

                  {/* DELETE BUTTON */}
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

        {/* EDITOR PANEL */}
        <div>
          {/* ADD BLOCK FORM */}
          {showAddBlockForm && (
            <div style={{
              background: 'white',
              border: '2px solid #11998e',
              borderRadius: '4px',
              padding: '20px',
              marginBottom: '20px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}>
              <h3>➕ Create New Block</h3>
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

          {/* BLOCK EDITOR */}
          {selectedBlock ? (
            <div style={{background: 'white', border: '1px solid #eee', borderRadius: '4px', padding: '20px'}}>
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px'}}>
                <h3>✏️ Edit: {selectedBlock}</h3>
                <div style={{display: 'flex', gap: '8px'}}>
                  <button className="action-btn retry" onClick={handleSaveBlock} style={{background: '#11998e', color: 'white'}}>
                    💾 Save
                  </button>
                  <button className="action-btn cancel" onClick={() => setEditMode(false)}>
                    ✕ Close
                  </button>
                </div>
              </div>

              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px'}}>
                {/* JSON EDITOR */}
                <div>
                  <label style={{fontWeight: 'bold', display: 'block', marginBottom: '8px'}}>📋 JSON Content</label>
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

                {/* PREVIEW */}
                <div style={{background: '#f5f5f5', padding: '15px', borderRadius: '4px', border: '1px solid #ddd'}}>
                  <label style={{fontWeight: 'bold', display: 'block', marginBottom: '10px'}}>👁️ Preview</label>
                  <div style={{background: 'white', padding: '12px', borderRadius: '3px', minHeight: '280px', overflow: 'auto'}}>
                    <pre style={{fontSize: '11px', margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word'}}>
                      {JSON.stringify(currentPageBlocks[selectedBlock], null, 2)}
                    </pre>
                  </div>
                </div>
              </div>

              {/* FORM EDITOR */}
              <div style={{marginTop: '20px', background: '#f9f9f9', padding: '15px', borderRadius: '4px'}}>
                <h4>📝 Quick Edit Form</h4>
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
              <p>👈 Select or create a content block from the sidebar</p>
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

      {/* RENDERING ORDER */}
      <div className="admin-section-content" style={{marginTop: '30px', background: '#f0f4ff', padding: '15px', borderRadius: '4px', border: '1px solid #667eea'}}>
        <h3>📋 Block Rendering Order (Page: {selectedPage})</h3>
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

      {/* BLOCK TEMPLATES LIBRARY */}
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

      {/* DATABASE SCHEMA */}
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
    </div>
  )
}

export default ContentManager


  return (
    <div className="admin-section">
      <h2>🧠 Content Manager</h2>
      <p className="section-subtitle">Manage website content blocks - Create, Edit, Delete sections dynamically</p>

      <div className="admin-stats-grid" style={{marginBottom: '20px'}}>
        <div className="admin-stat-card metric-info">
          <div className="stat-icon">📄</div>
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
            <p className="stat-value">{blockNames.length}</p>
            <p className="stat-detail">On {selectedPage}</p>
          </div>
        </div>
        <div className="admin-stat-card metric-success">
          <div className="stat-icon">✓</div>
          <div className="stat-content">
            <h3>Published</h3>
            <p className="stat-value">{blockNames.length}</p>
            <p className="stat-detail">All active</p>
          </div>
        </div>
        <div className="admin-stat-card metric-warning">
          <div className="stat-icon">⚡</div>
          <div className="stat-content">
            <h3>Last Updated</h3>
            <p className="stat-value" style={{fontSize: '14px'}}>2026-03-06</p>
            <p className="stat-detail">14:32</p>
          </div>
        </div>
      </div>

      <div style={{display: 'grid', gridTemplateColumns: '300px 1fr', gap: '20px'}}>
        {/* PAGES & BLOCKS SIDEBAR */}
        <div style={{background: '#f9f9f9', borderRadius: '4px', padding: '15px', border: '1px solid #eee', height: 'fit-content'}}>
          <h4 style={{marginTop: 0}}>📄 Pages</h4>
          <div style={{display: 'flex', flexDirection: 'column', gap: '8px'}}>
            {pages.map(page => (
              <button
                key={page}
                onClick={() => {
                  setSelectedPage(page)
                  setSelectedBlock(null)
                  setEditMode(false)
                }}
                style={{
                  padding: '10px 12px',
                  border: selectedPage === page ? '2px solid #667eea' : '1px solid #ddd',
                  background: selectedPage === page ? '#f0f4ff' : 'white',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  textAlign: 'left',
                  fontWeight: selectedPage === page ? 'bold' : 'normal',
                  transition: 'all 0.2s'
                }}
              >
                📄 {page.charAt(0).toUpperCase() + page.slice(1)}
              </button>
            ))}
          </div>

          <h4 style={{marginTop: '20px', marginBottom: '10px'}}>🧩 Blocks on "{selectedPage}"</h4>
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
            ➕ Add New Block
          </button>

          <div style={{display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: '400px', overflowY: 'auto'}}>
            {blockNames.length === 0 ? (
              <p style={{fontSize: '12px', color: '#999', textAlign: 'center', padding: '20px 0'}}>
                No blocks yet.<br/>Click "Add New Block" to start.
              </p>
            ) : (
              blockNames.map(block => (
                <div key={block} style={{display: 'flex', gap: '4px', alignItems: 'center'}}>
                  <button
                    onClick={() => handleEditBlock(block)}
                    style={{
                      flex: 1,
                      padding: '8px 10px',
                      border: selectedBlock === block ? '2px solid #11998e' : '1px solid #ddd',
                      background: selectedBlock === block ? '#f0fdf9' : 'white',
                      borderRadius: '3px',
                      cursor: 'pointer',
                      textAlign: 'left',
                      fontSize: '13px',
                      fontWeight: selectedBlock === block ? 'bold' : 'normal'
                    }}
                  >
                    {block.charAt(0).toUpperCase() + block.slice(1)}
                  </button>
                  <button
                    onClick={() => handleDeleteBlock(block)}
                    style={{
                      padding: '6px 8px',
                      background: '#eb3349',
                      color: 'white',
                      border: 'none',
                      borderRadius: '3px',
                      cursor: 'pointer',
                      fontSize: '11px'
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

        {/* EDITOR PANEL */}
        <div>
          {/* ADD BLOCK FORM */}
          {showAddBlockForm && (
            <div style={{
              background: 'white',
              border: '2px solid #11998e',
              borderRadius: '4px',
              padding: '20px',
              marginBottom: '20px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}>
              <h3>➕ Create New Block</h3>
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

          {/* BLOCK EDITOR */}
          {selectedBlock ? (
            <div style={{background: 'white', border: '1px solid #eee', borderRadius: '4px', padding: '20px'}}>
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px'}}>
                <h3>✏️ Edit: {selectedBlock}</h3>
                <div style={{display: 'flex', gap: '8px'}}>
                  <button className="action-btn retry" onClick={handleSaveBlock} style={{background: '#11998e', color: 'white'}}>
                    💾 Save
                  </button>
                  <button className="action-btn cancel" onClick={() => setEditMode(false)}>
                    ✕ Close
                  </button>
                </div>
              </div>

              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px'}}>
                {/* JSON EDITOR */}
                <div>
                  <label style={{fontWeight: 'bold', display: 'block', marginBottom: '8px'}}>📋 JSON Content</label>
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

                {/* PREVIEW */}
                <div style={{background: '#f5f5f5', padding: '15px', borderRadius: '4px', border: '1px solid #ddd'}}>
                  <label style={{fontWeight: 'bold', display: 'block', marginBottom: '10px'}}>👁️ Preview</label>
                  <div style={{background: 'white', padding: '12px', borderRadius: '3px', minHeight: '280px', overflow: 'auto'}}>
                    <pre style={{fontSize: '11px', margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word'}}>
                      {JSON.stringify(currentPageBlocks[selectedBlock], null, 2)}
                    </pre>
                  </div>
                </div>
              </div>

              {/* FORM EDITOR */}
              <div style={{marginTop: '20px', background: '#f9f9f9', padding: '15px', borderRadius: '4px'}}>
                <h4>📝 Quick Edit Form</h4>
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
              <p>👈 Select or create a content block from the sidebar</p>
              <p style={{fontSize: '12px'}}>
                {blockNames.length > 0 
                  ? `Blocks available: ${blockNames.join(', ')}`
                  : 'No blocks yet. Click "Add New Block" to get started.'
                }
              </p>
            </div>
          )}
        </div>
      </div>

      {/* BLOCK TEMPLATES LIBRARY */}
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

      {/* DATABASE SCHEMA */}
      <div className="admin-section-content" style={{marginTop: '20px', background: '#f9f9f9', padding: '15px', borderRadius: '4px'}}>
        <h4>🗄️ Database Backend (content_blocks table)</h4>
        <pre style={{background: 'white', padding: '12px', borderRadius: '3px', fontSize: '11px', overflow: 'auto', maxHeight: '120px'}}>
{`Columns: id | page_slug | block_type | block_key | content_json | status | updated_at

Example:
1 | home | hero | hero_main | {...title, subtitle} | published | 2026-03-06
2 | home | features | features_main | {...items} | published | 2026-03-06
...`}
        </pre>
        <small style={{color: '#666'}}>Content blocks are stored as JSON and pulled by Flask templates</small>
      </div>
    </div>
  )
}

export default ContentManager


