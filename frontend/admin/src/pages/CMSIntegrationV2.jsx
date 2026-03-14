import React, { useEffect, useMemo, useState } from 'react'
import '../styles/admin.css'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import { cmsAPI } from '../services/cms'

const DEFAULT_PAGES = [
  {
    title: 'Home',
    slug: 'home',
    description: 'Homepage',
    status: 'published',
    widgets: [
      { name: 'hero', widget_type: 'hero', position: 0, config: { title: 'Convert Files Online', subtitle: 'Fast and Secure', cta: 'Get Started' } },
      { name: 'features', widget_type: 'features', position: 1, config: { items: ['Instant Conversion', '100+ Formats', 'Secure Upload'] } },
    ],
  },
  {
    title: 'Pricing',
    slug: 'pricing',
    description: 'Pricing page',
    status: 'draft',
    widgets: [
      { name: 'hero', widget_type: 'hero', position: 0, config: { title: 'Simple Pricing', subtitle: 'No hidden fees' } },
      { name: 'plans', widget_type: 'pricing', position: 1, config: { plans: [{ name: 'Free', price: '$0' }, { name: 'Pro', price: '$9' }] } },
    ],
  },
]

const BLOCK_TEMPLATES = {
  hero: { title: 'Hero Section', template: { title: 'Section Title', subtitle: 'Subtitle text', cta: 'Button Text' } },
  text: { title: 'Text Block', template: { heading: 'Heading', body: 'Body text' } },
  features: { title: 'Features', template: { items: ['Feature 1', 'Feature 2'] } },
  faq: { title: 'FAQ', template: { items: [{ q: 'Question?', a: 'Answer here' }] } },
  pricing: { title: 'Pricing', template: { plans: [{ name: 'Plan', price: '$0' }] } },
  cta: { title: 'CTA', template: { text: 'Call to action', button: 'Start now' } },
  converter: { title: 'Converter', template: { tool: 'pdf-to-docx', title: 'Converter Widget' } },
}

function buildState(pages) {
  const pageMeta = {}
  const blocks = {}
  const order = {}
  const types = {}

  pages.forEach((page) => {
    pageMeta[page.slug] = {
      id: page.id,
      title: page.title,
      slug: page.slug,
      description: page.description || '',
      status: page.status || 'draft',
      page_type: page.page_type || 'landing',
      custom_css: page.custom_css || '',
      seo_metadata: page.seo_metadata || {},
    }
    blocks[page.slug] = {}
    order[page.slug] = []
    types[page.slug] = {}

    ;(page.widgets || [])
      .slice()
      .sort((left, right) => (left.position || 0) - (right.position || 0))
      .forEach((widget) => {
        blocks[page.slug][widget.name] = widget.config || {}
        order[page.slug].push(widget.name)
        types[page.slug][widget.name] = widget.widget_type || 'text'
      })
  })

  return { pageMeta, blocks, order, types }
}

function ContentManager() {
  const [activeTab, setActiveTab] = useState('pages')
  const [pagesLoading, setPagesLoading] = useState(false)
  const [toolsLoading, setToolsLoading] = useState(false)
  const [selectedPage, setSelectedPage] = useState('')
  const [selectedBlock, setSelectedBlock] = useState('')
  const [pageMetaData, setPageMetaData] = useState({})
  const [contentBlocks, setContentBlocks] = useState({})
  const [blockOrder, setBlockOrder] = useState({})
  const [widgetTypesByPage, setWidgetTypesByPage] = useState({})
  const [customCSS, setCustomCSS] = useState('')
  const [tools, setTools] = useState([])
  const [showAddPageForm, setShowAddPageForm] = useState(false)
  const [showAddBlockForm, setShowAddBlockForm] = useState(false)
  const [showPageSettings, setShowPageSettings] = useState(false)
  const [newPageName, setNewPageName] = useState('')
  const [newBlockName, setNewBlockName] = useState('')
  const [newBlockType, setNewBlockType] = useState('hero')
  const [pageSettings, setPageSettings] = useState({ title: '', slug: '', description: '' })

  const pages = useMemo(() => Object.keys(pageMetaData), [pageMetaData])
  const currentPageMeta = pageMetaData[selectedPage] || null
  const currentPageBlocks = contentBlocks[selectedPage] || {}
  const orderedBlockNames = blockOrder[selectedPage] || []

  const applyPageState = (pagesPayload) => {
    const nextState = buildState(pagesPayload)
    setPageMetaData(nextState.pageMeta)
    setContentBlocks(nextState.blocks)
    setBlockOrder(nextState.order)
    setWidgetTypesByPage(nextState.types)
    const firstPage = Object.keys(nextState.pageMeta)[0] || ''
    setSelectedPage((current) => (nextState.pageMeta[current] ? current : firstPage))
    setCustomCSS(nextState.pageMeta[firstPage]?.custom_css || '')
  }

  const loadPages = async () => {
    try {
      setPagesLoading(true)
      let response = await cmsAPI.listPages()
      let pagesPayload = response.data?.pages || []

      if (pagesPayload.length === 0) {
        for (const page of DEFAULT_PAGES) {
          await cmsAPI.createPage(page)
        }
        response = await cmsAPI.listPages()
        pagesPayload = response.data?.pages || []
      }

      applyPageState(pagesPayload)
    } catch (error) {
      console.error('Failed to load CMS pages:', error)
      alert('Failed to load CMS pages')
    } finally {
      setPagesLoading(false)
    }
  }

  const loadTools = async () => {
    try {
      setToolsLoading(true)
      const response = await fetch('http://localhost:5000/api/tools')
      if (!response.ok) {
        throw new Error('Failed to load tools')
      }
      const data = await response.json()
      setTools(data.tools || [])
    } catch (error) {
      console.error('Failed to load tools:', error)
      setTools([])
    } finally {
      setToolsLoading(false)
    }
  }

  useEffect(() => {
    loadPages()
  }, [])

  useEffect(() => {
    if (activeTab === 'tools') {
      loadTools()
    }
  }, [activeTab])

  useEffect(() => {
    if (currentPageMeta) {
      setCustomCSS(currentPageMeta.custom_css || '')
    }
  }, [currentPageMeta])

  const buildPayload = (pageKey, nextBlocks, nextOrder, nextTypes, metaOverride = null, cssOverride = null) => {
    const meta = metaOverride || pageMetaData[pageKey]
    return {
      title: meta?.title || pageKey,
      slug: meta?.slug || pageKey,
      description: meta?.description || '',
      status: meta?.status || 'draft',
      page_type: meta?.page_type || 'landing',
      custom_css: typeof cssOverride === 'string' ? cssOverride : (meta?.custom_css || ''),
      content: { block_order: nextOrder },
      seo_metadata: meta?.seo_metadata || {},
      widgets: nextOrder.map((blockName, index) => ({
        name: blockName,
        widget_type: nextTypes[blockName] || 'text',
        position: index,
        config: nextBlocks[blockName] || {},
        is_enabled: true,
      })),
    }
  }

  const persistPage = async (pageKey, nextBlocks, nextOrder, nextTypes, metaOverride = null, cssOverride = null) => {
    const meta = metaOverride || pageMetaData[pageKey]
    if (!meta?.id) {
      throw new Error('Missing page id')
    }

    const response = await cmsAPI.updatePage(
      meta.id,
      buildPayload(pageKey, nextBlocks, nextOrder, nextTypes, metaOverride, cssOverride)
    )
    return response.data?.page
  }

  const handleAddPage = async () => {
    if (!newPageName.trim()) {
      alert('Please enter a page name')
      return
    }

    const slug = newPageName.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-')
    if (pageMetaData[slug]) {
      alert('Page already exists')
      return
    }

    try {
      const response = await cmsAPI.createPage({
        title: newPageName.trim(),
        slug,
        description: `Page: ${newPageName.trim()}`,
        status: 'draft',
        widgets: [],
      })
      const page = response.data?.page
      setPageMetaData((prev) => ({
        ...prev,
        [page.slug]: {
          id: page.id,
          title: page.title,
          slug: page.slug,
          description: page.description || '',
          status: page.status || 'draft',
          page_type: page.page_type || 'landing',
          custom_css: page.custom_css || '',
          seo_metadata: page.seo_metadata || {},
        },
      }))
      setContentBlocks((prev) => ({ ...prev, [page.slug]: {} }))
      setBlockOrder((prev) => ({ ...prev, [page.slug]: [] }))
      setWidgetTypesByPage((prev) => ({ ...prev, [page.slug]: {} }))
      setSelectedPage(page.slug)
      setNewPageName('')
      setShowAddPageForm(false)
      alert('Page created successfully')
    } catch (error) {
      console.error('Failed to create page:', error)
      alert('Failed to create page')
    }
  }

  const handleDeletePage = async (pageKey) => {
    if (!window.confirm(`Delete page "${pageKey}"?`)) {
      return
    }

    try {
      const pageId = pageMetaData[pageKey]?.id
      await cmsAPI.deletePage(pageId)
      setPageMetaData((prev) => {
        const updated = { ...prev }
        delete updated[pageKey]
        return updated
      })
      setContentBlocks((prev) => {
        const updated = { ...prev }
        delete updated[pageKey]
        return updated
      })
      setBlockOrder((prev) => {
        const updated = { ...prev }
        delete updated[pageKey]
        return updated
      })
      setWidgetTypesByPage((prev) => {
        const updated = { ...prev }
        delete updated[pageKey]
        return updated
      })
      if (selectedPage === pageKey) {
        const remaining = pages.filter((item) => item !== pageKey)
        setSelectedPage(remaining[0] || '')
        setSelectedBlock('')
      }
    } catch (error) {
      console.error('Failed to delete page:', error)
      alert('Failed to delete page')
    }
  }

  const openPageSettings = (pageKey) => {
    setPageSettings({
      title: pageMetaData[pageKey]?.title || '',
      slug: pageMetaData[pageKey]?.slug || pageKey,
      description: pageMetaData[pageKey]?.description || '',
    })
    setSelectedPage(pageKey)
    setShowPageSettings(true)
  }

  const savePageSettings = async () => {
    try {
      const oldKey = selectedPage
      const nextMeta = {
        ...pageMetaData[oldKey],
        title: pageSettings.title,
        slug: pageSettings.slug,
        description: pageSettings.description,
      }
      const savedPage = await persistPage(
        oldKey,
        contentBlocks[oldKey] || {},
        blockOrder[oldKey] || [],
        widgetTypesByPage[oldKey] || {},
        nextMeta
      )
      const newKey = savedPage?.slug || pageSettings.slug || oldKey

      if (newKey !== oldKey) {
        setPageMetaData((prev) => {
          const updated = {
            ...prev,
            [newKey]: {
              ...nextMeta,
              id: prev[oldKey]?.id,
              slug: newKey,
            },
          }
          delete updated[oldKey]
          return updated
        })
        setContentBlocks((prev) => {
          const updated = { ...prev, [newKey]: prev[oldKey] || {} }
          delete updated[oldKey]
          return updated
        })
        setBlockOrder((prev) => {
          const updated = { ...prev, [newKey]: prev[oldKey] || [] }
          delete updated[oldKey]
          return updated
        })
        setWidgetTypesByPage((prev) => {
          const updated = { ...prev, [newKey]: prev[oldKey] || {} }
          delete updated[oldKey]
          return updated
        })
        setSelectedPage(newKey)
      } else {
        setPageMetaData((prev) => ({ ...prev, [oldKey]: nextMeta }))
      }
      setShowPageSettings(false)
      alert('Page settings saved')
    } catch (error) {
      console.error('Failed to save page settings:', error)
      alert('Failed to save page settings')
    }
  }

  const handleAddBlock = async () => {
    if (!newBlockName.trim() || !selectedPage) {
      alert('Select a page and enter a block name')
      return
    }

    const blockKey = newBlockName.trim().toLowerCase().replace(/\s+/g, '_')
    const nextBlocks = {
      ...(contentBlocks[selectedPage] || {}),
      [blockKey]: structuredClone(BLOCK_TEMPLATES[newBlockType].template),
    }
    const nextOrder = [...(blockOrder[selectedPage] || []), blockKey]
    const nextTypes = {
      ...(widgetTypesByPage[selectedPage] || {}),
      [blockKey]: newBlockType,
    }

    setContentBlocks((prev) => ({ ...prev, [selectedPage]: nextBlocks }))
    setBlockOrder((prev) => ({ ...prev, [selectedPage]: nextOrder }))
    setWidgetTypesByPage((prev) => ({ ...prev, [selectedPage]: nextTypes }))

    try {
      await persistPage(selectedPage, nextBlocks, nextOrder, nextTypes)
      setSelectedBlock(blockKey)
      setNewBlockName('')
      setNewBlockType('hero')
      setShowAddBlockForm(false)
    } catch (error) {
      console.error('Failed to add block:', error)
      alert('Failed to add block')
    }
  }

  const handleDeleteBlock = async (blockName) => {
    const nextBlocks = { ...(contentBlocks[selectedPage] || {}) }
    delete nextBlocks[blockName]
    const nextOrder = (blockOrder[selectedPage] || []).filter((item) => item !== blockName)
    const nextTypes = { ...(widgetTypesByPage[selectedPage] || {}) }
    delete nextTypes[blockName]

    setContentBlocks((prev) => ({ ...prev, [selectedPage]: nextBlocks }))
    setBlockOrder((prev) => ({ ...prev, [selectedPage]: nextOrder }))
    setWidgetTypesByPage((prev) => ({ ...prev, [selectedPage]: nextTypes }))

    try {
      await persistPage(selectedPage, nextBlocks, nextOrder, nextTypes)
      if (selectedBlock === blockName) {
        setSelectedBlock('')
      }
    } catch (error) {
      console.error('Failed to delete block:', error)
      alert('Failed to delete block')
    }
  }

  const handleMoveBlock = async (blockName, direction) => {
    const currentOrder = [...(blockOrder[selectedPage] || [])]
    const index = currentOrder.indexOf(blockName)
    if (index === -1) {
      return
    }

    if (direction === 'up' && index > 0) {
      ;[currentOrder[index - 1], currentOrder[index]] = [currentOrder[index], currentOrder[index - 1]]
    }
    if (direction === 'down' && index < currentOrder.length - 1) {
      ;[currentOrder[index + 1], currentOrder[index]] = [currentOrder[index], currentOrder[index + 1]]
    }

    setBlockOrder((prev) => ({ ...prev, [selectedPage]: currentOrder }))
    try {
      await persistPage(selectedPage, contentBlocks[selectedPage] || {}, currentOrder, widgetTypesByPage[selectedPage] || {})
    } catch (error) {
      console.error('Failed to reorder blocks:', error)
      alert('Failed to reorder blocks')
    }
  }

  const handleJsonChange = (event) => {
    if (!selectedBlock) {
      return
    }

    try {
      const parsed = JSON.parse(event.target.value)
      setContentBlocks((prev) => ({
        ...prev,
        [selectedPage]: {
          ...(prev[selectedPage] || {}),
          [selectedBlock]: parsed,
        },
      }))
    } catch {
      // Keep editing until JSON is valid.
    }
  }

  const handleSaveBlock = async () => {
    try {
      await persistPage(selectedPage, contentBlocks[selectedPage] || {}, blockOrder[selectedPage] || [], widgetTypesByPage[selectedPage] || {}, {
        ...pageMetaData[selectedPage],
        custom_css: customCSS,
      }, customCSS)
      setPageMetaData((prev) => ({
        ...prev,
        [selectedPage]: {
          ...prev[selectedPage],
          custom_css: customCSS,
        },
      }))
      alert('Block changes saved')
    } catch (error) {
      console.error('Failed to save block:', error)
      alert('Failed to save block changes')
    }
  }

  const handleExportTemplate = () => {
    const payload = {
      pageMetaData: pageMetaData[selectedPage],
      blocks: contentBlocks[selectedPage] || {},
      blockOrder: blockOrder[selectedPage] || [],
      widgetTypes: widgetTypesByPage[selectedPage] || {},
      exportedAt: new Date().toISOString(),
    }
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `${selectedPage || 'page'}-template.json`
    anchor.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="🧠" size={24} /> Content Manager</h2>
      <p className="section-subtitle">Database-backed CMS pages and content blocks</p>

      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', borderBottom: '2px solid #eee' }}>
        <button className="action-button primary" onClick={() => setActiveTab('pages')}>Pages</button>
        <button className="action-button primary" onClick={() => setActiveTab('tools')}>Tools</button>
      </div>

      {activeTab === 'tools' ? (
        <div className="admin-section-content">
          <h3><UniversalIcon icon="🔧" size={20} /> Tool Inventory</h3>
          <p style={{ color: '#666' }}>Read-only tool list from the backend metadata endpoint.</p>
          {toolsLoading ? <p>Loading tools...</p> : (
            <div className="jobs-table-wrapper">
              <table className="jobs-table">
                <thead>
                  <tr>
                    <th>Slug</th>
                    <th>Title</th>
                    <th>Category</th>
                  </tr>
                </thead>
                <tbody>
                  {tools.map((tool) => (
                    <tr key={tool.slug}>
                      <td>{tool.slug}</td>
                      <td>{tool.title}</td>
                      <td>{tool.category || 'utility'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      ) : (
        <>
          <div className="admin-stats-grid" style={{ marginBottom: '20px' }}>
            <div className="admin-stat-card metric-info">
              <div className="stat-content">
                <h3>Pages</h3>
                <p className="stat-value">{pagesLoading ? '...' : pages.length}</p>
                <p className="stat-detail">Persisted CMS pages</p>
              </div>
            </div>
            <div className="admin-stat-card metric-primary">
              <div className="stat-content">
                <h3>Blocks</h3>
                <p className="stat-value">{orderedBlockNames.length}</p>
                <p className="stat-detail">On current page</p>
              </div>
            </div>
            <div className="admin-stat-card metric-success">
              <div className="stat-content">
                <h3>Status</h3>
                <p className="stat-value">{currentPageMeta?.status || 'n/a'}</p>
                <p className="stat-detail">Current page state</p>
              </div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '20px' }}>
            <div style={{ background: '#f9f9f9', borderRadius: '4px', padding: '16px', border: '1px solid #eee' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h4 style={{ margin: 0 }}>Pages</h4>
                <button className="action-button primary" onClick={() => setShowAddPageForm((value) => !value)}>Add</button>
              </div>

              {showAddPageForm && (
                <div style={{ marginBottom: '12px' }}>
                  <input className="form-input" type="text" value={newPageName} onChange={(event) => setNewPageName(event.target.value)} placeholder="New page name" />
                  <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
                    <button className="action-button primary" onClick={handleAddPage}>Create</button>
                    <button className="action-button cancel" onClick={() => setShowAddPageForm(false)}>Cancel</button>
                  </div>
                </div>
              )}

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px' }}>
                {pages.map((pageKey) => (
                  <div key={pageKey} style={{ background: selectedPage === pageKey ? '#eef3ff' : '#fff', border: '1px solid #ddd', borderRadius: '4px', padding: '10px' }}>
                    <button onClick={() => { setSelectedPage(pageKey); setSelectedBlock('') }} style={{ border: 'none', background: 'transparent', cursor: 'pointer', width: '100%', textAlign: 'left', fontWeight: 'bold' }}>
                      {pageMetaData[pageKey]?.title || pageKey}
                    </button>
                    <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
                      <button className="action-btn retry" onClick={() => openPageSettings(pageKey)}>Settings</button>
                      <button className="action-btn cancel" onClick={() => handleDeletePage(pageKey)}>Delete</button>
                    </div>
                  </div>
                ))}
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h4 style={{ margin: 0 }}>Blocks</h4>
                <button className="action-button primary" onClick={() => setShowAddBlockForm((value) => !value)} disabled={!selectedPage}>Add</button>
              </div>

              {showAddBlockForm && (
                <div style={{ marginBottom: '12px' }}>
                  <input className="form-input" type="text" value={newBlockName} onChange={(event) => setNewBlockName(event.target.value)} placeholder="Block name" />
                  <select className="form-input" value={newBlockType} onChange={(event) => setNewBlockType(event.target.value)} style={{ marginTop: '8px' }}>
                    {Object.entries(BLOCK_TEMPLATES).map(([key, value]) => (
                      <option key={key} value={key}>{value.title}</option>
                    ))}
                  </select>
                  <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
                    <button className="action-button primary" onClick={handleAddBlock}>Create</button>
                    <button className="action-button cancel" onClick={() => setShowAddBlockForm(false)}>Cancel</button>
                  </div>
                </div>
              )}

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {orderedBlockNames.map((blockName, index) => (
                  <div key={blockName} style={{ background: selectedBlock === blockName ? '#edfdf7' : '#fff', border: '1px solid #ddd', borderRadius: '4px', padding: '10px' }}>
                    <button onClick={() => setSelectedBlock(blockName)} style={{ border: 'none', background: 'transparent', cursor: 'pointer', width: '100%', textAlign: 'left', fontWeight: 'bold' }}>
                      {blockName}
                    </button>
                    <div style={{ display: 'flex', gap: '6px', marginTop: '8px' }}>
                      <button className="action-btn retry" disabled={index === 0} onClick={() => handleMoveBlock(blockName, 'up')}>Up</button>
                      <button className="action-btn retry" disabled={index === orderedBlockNames.length - 1} onClick={() => handleMoveBlock(blockName, 'down')}>Down</button>
                      <button className="action-btn cancel" onClick={() => handleDeleteBlock(blockName)}>Delete</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              {showPageSettings && currentPageMeta && (
                <div style={{ background: '#fff', border: '1px solid #ddd', borderRadius: '4px', padding: '16px', marginBottom: '16px' }}>
                  <h3 style={{ marginTop: 0 }}>Page Settings</h3>
                  <input className="form-input" type="text" value={pageSettings.title} onChange={(event) => setPageSettings((prev) => ({ ...prev, title: event.target.value }))} placeholder="Page title" />
                  <input className="form-input" type="text" value={pageSettings.slug} onChange={(event) => setPageSettings((prev) => ({ ...prev, slug: event.target.value }))} placeholder="Page slug" style={{ marginTop: '8px' }} />
                  <textarea className="form-input" value={pageSettings.description} onChange={(event) => setPageSettings((prev) => ({ ...prev, description: event.target.value }))} placeholder="Page description" style={{ marginTop: '8px', minHeight: '80px' }} />
                  <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
                    <button className="action-button primary" onClick={savePageSettings}>Save</button>
                    <button className="action-button cancel" onClick={() => setShowPageSettings(false)}>Close</button>
                  </div>
                </div>
              )}

              <div style={{ background: '#fff', border: '1px solid #ddd', borderRadius: '4px', padding: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <h3 style={{ margin: 0 }}>Block Editor</h3>
                  <button className="action-button primary" onClick={handleSaveBlock} disabled={!selectedPage}>Save Changes</button>
                </div>

                {!selectedBlock ? (
                  <p style={{ color: '#666' }}>Select a block to edit its JSON config.</p>
                ) : (
                  <>
                    <p style={{ color: '#666' }}>Editing <strong>{selectedBlock}</strong> on <strong>{selectedPage}</strong>.</p>
                    <textarea
                      value={JSON.stringify(currentPageBlocks[selectedBlock] || {}, null, 2)}
                      onChange={handleJsonChange}
                      style={{ width: '100%', minHeight: '320px', fontFamily: 'monospace', fontSize: '12px', padding: '12px', border: '1px solid #ddd', borderRadius: '4px' }}
                    />
                  </>
                )}

                <div style={{ marginTop: '16px' }}>
                  <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '8px' }}>Custom CSS</label>
                  <textarea
                    value={customCSS}
                    onChange={(event) => setCustomCSS(event.target.value)}
                    style={{ width: '100%', minHeight: '120px', fontFamily: 'monospace', fontSize: '12px', padding: '12px', border: '1px solid #ddd', borderRadius: '4px' }}
                  />
                </div>

                <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
                  <button className="action-button primary" onClick={handleExportTemplate} disabled={!selectedPage}>Export Template</button>
                  <button className="action-button primary" onClick={loadPages}>Refresh</button>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default ContentManager
