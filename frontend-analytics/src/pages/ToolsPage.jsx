import React, { useState } from 'react'
import { UniversalIcon } from '../utils/UniversalIcon'
import { useNavigate } from 'react-router-dom'
import { CATEGORY_LABELS, CATEGORY_ORDER, getAllCatalogTools } from '../config/toolRoutes'
import '../styles/tools-page.css'

const ToolsPage = ({ onTitleChange }) => {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')

  const allTools = getAllCatalogTools()

  // Filter tools
  const categories = CATEGORY_ORDER.filter((category) => category === 'all' || allTools.some((tool) => tool.category === category))

  const filteredTools = allTools.filter(tool => {
    const matchesCategory = selectedCategory === 'all' || tool.category === selectedCategory
    const query = searchQuery.toLowerCase()
    const matchesSearch = tool.title.toLowerCase().includes(query) ||
                         tool.description.toLowerCase().includes(query) ||
                         tool.from_format.toLowerCase().includes(query) ||
                         tool.to_format.toLowerCase().includes(query)
    return matchesCategory && matchesSearch
  })

  const handleToolClick = (toolSlug) => {
    navigate(`/${toolSlug}`)
  }

  React.useEffect(() => {
    onTitleChange?.('Tools')
  }, [onTitleChange])

  return (
    <div className="tools-page">
      {/* Header */}
      <div className="tools-header">
        <h1>File Conversion Tools</h1>
        <p>Choose from {allTools.length} powerful tools to convert your files</p>
      </div>

      {/* Search Bar */}
      <div className="tools-search-container">
        <div className="search-box">
          <UniversalIcon icon="fas fa-search" size={18} />
          <input
            type="text"
            placeholder="Search tools..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>
      </div>

      {/* Category Filter */}
      <div className="tools-categories">
        {categories.map(cat => (
          <button
            key={cat}
            className={`category-btn ${selectedCategory === cat ? 'active' : ''}`}
            onClick={() => setSelectedCategory(cat)}
          >
            {CATEGORY_LABELS[cat]}
          </button>
        ))}
      </div>

      {/* Tools Grid */}
      <div className="tools-grid">
        {filteredTools.length > 0 ? (
          filteredTools.map(tool => (
            <div
              key={tool.slug}
              className="tool-card"
              onClick={() => handleToolClick(tool.slug)}
            >
              <div className="tool-icon">{tool.icon}</div>
              <h3 className="tool-name">{tool.title}</h3>
              <p className="tool-formats">
                <span className="format">{tool.from_format}</span>
                <span className="arrow">→</span>
                <span className="format">{tool.to_format}</span>
              </p>
              <p className="tool-description">{tool.description}</p>
              <button className="tool-button">
                Open Tool
                <UniversalIcon icon="fas fa-arrow-right" size={16} />
              </button>
            </div>
          ))
        ) : (
          <div className="no-tools">
            <UniversalIcon icon="fas fa-search" size={48} style={{ marginBottom: '20px' }} />
            <p>No tools found matching your search</p>
            <button 
              className="reset-btn"
              onClick={() => {
                setSearchQuery('')
                setSelectedCategory('all')
              }}
            >
              Reset Search
            </button>
          </div>
        )}
      </div>

      {/* Stats Section */}
      <div className="tools-stats">
        <div className="stat-item">
          <div className="stat-icon"><UniversalIcon icon="⚡" size={32} /></div>
          <div className="stat-content">
            <h4>Fast Processing</h4>
            <p>Convert files in seconds</p>
          </div>
        </div>
        <div className="stat-item">
          <div className="stat-icon"><UniversalIcon icon="🔒" size={32} /></div>
          <div className="stat-content">
            <h4>Secure & Private</h4>
            <p>Your files are deleted after conversion</p>
          </div>
        </div>
        <div className="stat-item">
          <div className="stat-icon"><UniversalIcon icon="💾" size={32} /></div>
          <div className="stat-content">
            <h4>No Size Limits</h4>
            <p>Convert files of any size</p>
          </div>
        </div>
        <div className="stat-item">
          <div className="stat-icon"><UniversalIcon icon="∞️" size={32} /></div>
          <div className="stat-content">
            <h4>Unlimited Access</h4>
            <p>Convert as many files as you need</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ToolsPage
