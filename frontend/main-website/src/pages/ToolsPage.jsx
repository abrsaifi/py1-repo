import React, { useState } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import { useNavigate } from 'react-router-dom'
import '../styles/tools-page.css'

const ToolsPage = ({ onTitleChange }) => {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')

  // All available tools
  const allTools = [
    // Document Conversion
    { id: 1, slug: 'pdf-to-docx', name: 'PDF to DOCX', icon: '📄', from: 'PDF', to: 'DOCX', category: 'document', description: 'Convert PDF documents to Microsoft Word format' },
    { id: 2, slug: 'docx-to-pdf', name: 'DOCX to PDF', icon: '📋', from: 'DOCX', to: 'PDF', category: 'document', description: 'Convert Word documents to PDF format' },
    { id: 3, slug: 'pdf-to-excel', name: 'PDF to Excel', icon: '📊', from: 'PDF', to: 'XLSX', category: 'document', description: 'Extract data from PDF to Excel spreadsheets' },
    { id: 4, slug: 'excel-to-pdf', name: 'Excel to PDF', icon: '📈', from: 'XLSX', to: 'PDF', category: 'document', description: 'Convert Excel spreadsheets to PDF' },
    { id: 5, slug: 'pptx-to-pdf', name: 'PPTX to PDF', icon: '🎞️', from: 'PPTX', to: 'PDF', category: 'document', description: 'Convert PowerPoint presentations to PDF' },
    
    // Image Conversion
    { id: 6, slug: 'jpg-to-png', name: 'JPG to PNG', icon: '🖼️', from: 'JPG', to: 'PNG', category: 'image', description: 'Convert JPEG images to PNG format' },
    { id: 7, slug: 'png-to-jpg', name: 'PNG to JPG', icon: '🎨', from: 'PNG', to: 'JPG', category: 'image', description: 'Convert PNG images to JPG format' },
    { id: 8, slug: 'image-resizer', name: 'Image Resizer', icon: '📐', from: 'Multiple', to: 'Multiple', category: 'image', description: 'Resize images to any dimensions' },
    { id: 9, slug: 'image-to-pdf', name: 'Image to PDF', icon: '🖨️', from: 'Image', to: 'PDF', category: 'image', description: 'Combine images into a single PDF' },
    
    // Archive Tools
    { id: 10, slug: 'zip-extractor', name: 'ZIP Extractor', icon: '📦', from: 'ZIP', to: 'Multiple', category: 'archive', description: 'Extract files from ZIP archives' },
    { id: 11, slug: 'create-zip', name: 'Create ZIP', icon: '📫', from: 'Multiple', to: 'ZIP', category: 'archive', description: 'Compress files into ZIP archives' },
    
    // Video & Audio
    { id: 12, slug: 'mp4-converter', name: 'MP4 Converter', icon: '🎬', from: 'Video', to: 'MP4', category: 'media', description: 'Convert videos to MP4 format' },
    { id: 13, slug: 'audio-converter', name: 'Audio Converter', icon: '🎵', from: 'Audio', to: 'Multiple', category: 'media', description: 'Convert audio files between formats' },
    
    // Text & Data
    { id: 14, slug: 'text-formatter', name: 'Text Formatter', icon: '✏️', from: 'Text', to: 'Text', category: 'text', description: 'Format and clean text data' },
    { id: 15, slug: 'csv-to-excel', name: 'CSV to Excel', icon: '📑', from: 'CSV', to: 'XLSX', category: 'text', description: 'Convert CSV files to Excel format' },
    { id: 16, slug: 'json-formatter', name: 'JSON Formatter', icon: '{}', from: 'JSON', to: 'JSON', category: 'text', description: 'Validate and format JSON data' },
  ]

  // Filter tools
  const categories = ['all', 'document', 'image', 'archive', 'media', 'text']
  const categoryLabels = {
    all: 'All Tools',
    document: 'Documents',
    image: 'Images',
    archive: 'Archives',
    media: 'Media',
    text: 'Text & Data'
  }

  const filteredTools = allTools.filter(tool => {
    const matchesCategory = selectedCategory === 'all' || tool.category === selectedCategory
    const matchesSearch = tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         tool.description.toLowerCase().includes(searchQuery.toLowerCase())
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
            {categoryLabels[cat]}
          </button>
        ))}
      </div>

      {/* Tools Grid */}
      <div className="tools-grid">
        {filteredTools.length > 0 ? (
          filteredTools.map(tool => (
            <div
              key={tool.id}
              className="tool-card"
              onClick={() => handleToolClick(tool.slug)}
            >
              <div className="tool-icon">{tool.icon}</div>
              <h3 className="tool-name">{tool.name}</h3>
              <p className="tool-formats">
                <span className="format">{tool.from}</span>
                <span className="arrow">→</span>
                <span className="format">{tool.to}</span>
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
