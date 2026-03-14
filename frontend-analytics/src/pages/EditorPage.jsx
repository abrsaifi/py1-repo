import React, { useRef, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import '../styles/tool-page.css'

function EditorPage() {
  const canvasRef = useRef(null)
  const fileInputRef = useRef(null)
  const previewRef = useRef(null)
  const [drawing, setDrawing] = useState(false)
  const [message, setMessage] = useState('')
  const [uploadProgress, setUploadProgress] = useState(0)
  const [currentFileType, setCurrentFileType] = useState('image')
  const navigate = useNavigate()

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
  }, [])

  const startDraw = (e) => {
    const rect = canvasRef.current.getBoundingClientRect()
    const ctx = canvasRef.current.getContext('2d')
    ctx.beginPath()
    ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top)
    setDrawing(true)
  }

  const draw = (e) => {
    if (!drawing) return
    const rect = canvasRef.current.getBoundingClientRect()
    const ctx = canvasRef.current.getContext('2d')
    ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top)
    ctx.strokeStyle = '#ff0000'
    ctx.lineWidth = 2
    ctx.stroke()
  }

  const endDraw = () => {
    setDrawing(false)
  }

  const handleClear = () => {
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    setMessage('Cleared canvas')
    setUploadProgress(0)
  }

  // Handles loading images, PDFs, and other file types for preview/annotation
  const handleFileInput = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const type = file.type || ''
    setUploadProgress(0)

    if (type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
      setCurrentFileType('pdf')
      setMessage('Rendering PDF preview...')
      try {
        const url = URL.createObjectURL(file)
        // use pdfjs via dynamic import and CDN worker
        const pdfjs = await import('pdfjs-dist')
        pdfjs.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.8.162/pdf.worker.min.js'
        const loadingTask = pdfjs.getDocument(url)
        const pdf = await loadingTask.promise
        const page = await pdf.getPage(1)
        const viewport = page.getViewport({ scale: 1.5 })
        const canvas = canvasRef.current
        canvas.width = Math.min(1200, viewport.width)
        canvas.height = Math.min(1600, viewport.height)
        const ctx = canvas.getContext('2d')
        const renderContext = { canvasContext: ctx, viewport }
        await page.render(renderContext).promise
        setMessage('PDF page rendered — annotate on canvas')
        URL.revokeObjectURL(url)
      } catch (err) {
        console.error(err)
        setMessage('PDF preview failed: ' + (err.message || String(err)))
      }
      return
    }

    // For images (jpeg/png/gif) — draw to canvas
    if (type.startsWith('image/')) {
      setCurrentFileType('image')
      const img = new Image()
      img.onload = () => {
        const canvas = canvasRef.current
        const ctx = canvas.getContext('2d')
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        // draw with aspect-fit
        const scale = Math.min(canvas.width / img.width, canvas.height / img.height)
        const w = img.width * scale
        const h = img.height * scale
        ctx.drawImage(img, 0, 0, img.width, img.height, 0, 0, canvas.width, canvas.height)
        setMessage('Image loaded — annotate on canvas')
      }
      img.src = URL.createObjectURL(file)
      return
    }

    // For other document types (docx, xlsx, csv), show a simple preview in the preview pane
    setCurrentFileType('other')
    setMessage('Previewing file — you can upload for server-side conversion')
    const p = previewRef.current
    if (!p) return
    p.innerHTML = ''
    const url = URL.createObjectURL(file)
    // DOCX -> HTML preview via mammoth if available
    if (file.name.toLowerCase().endsWith('.docx')) {
      try {
        const mammoth = await import('mammoth')
        const arrayBuffer = await file.arrayBuffer()
        const { value: html } = await mammoth.convertToHtml({ arrayBuffer })
        p.innerHTML = html
        setMessage('DOCX preview rendered — upload to convert/export')
        URL.revokeObjectURL(url)
        return
      } catch (err) {
        console.error(err)
        p.textContent = 'DOCX preview failed.'
      }
    }

    // CSV preview + simple editable table
    if (file.name.toLowerCase().endsWith('.csv')) {
      try {
        const text = await file.text()
        const rows = text.split(/\r?\n/).filter(Boolean).map(r => r.split(','))
        const table = document.createElement('table')
        table.style.borderCollapse = 'collapse'
        table.style.width = '100%'
        table.style.maxHeight = '400px'
        table.style.overflow = 'auto'
        rows.forEach((cols) => {
          const tr = document.createElement('tr')
          cols.forEach((c) => {
            const td = document.createElement('td')
            td.contentEditable = 'true'
            td.style.border = '1px solid #ddd'
            td.style.padding = '6px'
            td.textContent = c
            tr.appendChild(td)
          })
          table.appendChild(tr)
        })
        const btn = document.createElement('button')
        btn.textContent = 'Export & Upload CSV'
        btn.className = 'btn-primary-large'
        btn.onclick = async () => {
          // serialize table back to CSV
          const lines = Array.from(table.querySelectorAll('tr')).map(tr => {
            const cols = Array.from(tr.querySelectorAll('td')).map(td => td.textContent.replace(/\"/g, '"'))
            return cols.map(c => c.includes(',') ? `"${c.replace(/"/g, '""')}` + '"' : c).join(',')
          })
          const csv = lines.join('\n')
          const blob = new Blob([csv], { type: 'text/csv' })
          await uploadBlobAndConvert(blob, 'edited.csv')
        }
        const p = previewRef.current
        p.innerHTML = ''
        p.appendChild(btn)
        p.appendChild(table)
        setMessage('CSV loaded — edit cells then Export & Upload')
        return
      } catch (err) {
        console.error(err)
        setMessage('CSV preview failed')
      }
    }
    if (type.startsWith('text/') || file.name.toLowerCase().endsWith('.csv')) {
      try {
        const txt = await file.text()
        const pre = document.createElement('pre')
        pre.style.maxHeight = '400px'
        pre.style.overflow = 'auto'
        pre.textContent = txt.slice(0, 10000)
        p.appendChild(pre)
      } catch (err) {
        p.textContent = 'Could not load preview.'
      }
    } else {
      // embed via iframe for docx/xlsx fallback preview (browser may not render)
      const iframe = document.createElement('iframe')
      iframe.src = url
      iframe.style.width = '100%'
      iframe.style.height = '400px'
      p.appendChild(iframe)
    }
  }

  const downloadLocal = () => {
    const canvas = canvasRef.current
    canvas.toBlob((blob) => {
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'edited.png'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    }, 'image/png')
  }

  // Uploads a blob in chunks to the backend using existing chunk API
  const uploadBlobInChunks = async (blob, filename, uploadId) => {
    const chunkSize = 5 * 1024 * 1024 // 5MB
    const total = Math.ceil(blob.size / chunkSize)
    for (let i = 0; i < total; i++) {
      const start = i * chunkSize
      const end = Math.min(blob.size, start + chunkSize)
      const chunk = blob.slice(start, end)
      const form = new FormData()
      form.append('upload_id', uploadId)
      form.append('filename', filename)
      form.append('index', String(i))
      form.append('total', String(total))
      form.append('chunk', chunk, filename)

      const resp = await fetch('/api/upload-chunk', { method: 'POST', body: form })
      const payload = await resp.json().catch(() => ({}))
      if (!resp.ok || !payload.success) {
        throw new Error(payload.error || `Chunk upload failed at index ${i}`)
      }
      setUploadProgress(Math.round(((i + 1) / total) * 100))
    }
    setUploadProgress(100)
  }

  // Upload a blob and then request conversion (reused by CSV export)
  const uploadBlobAndConvert = async (blob, filename) => {
    try {
      setMessage('Uploading in chunks...')
      const uploadId = `editor-${Date.now()}`
      await uploadBlobInChunks(blob, filename, uploadId)
      setMessage('Upload complete — requesting conversion...')
      const convResp = await fetch('/api/convert-uploaded', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool_slug: 'editor',
          uploads: [{ upload_id: uploadId, filename }],
          target_format: null,
          parameters: {}
        })
      })
      const convJson = await convResp.json().catch(() => ({}))
      if (!convResp.ok) throw new Error(convJson.error || 'Conversion request failed')
      if (convJson.outputs && Array.isArray(convJson.outputs) && convJson.outputs.length && convJson.outputs[0].download_url) {
        setMessage('Conversion complete — ready. Click to download.')
        const link = document.createElement('a')
        link.href = convJson.outputs[0].download_url
        link.target = '_blank'
        link.rel = 'noopener'
        link.textContent = 'Download result'
        const container = document.createElement('div')
        container.appendChild(link)
        const root = document.querySelector('.tool-upload-section .tool-container div')
        if (root) root.appendChild(container)
      } else {
        setMessage('Conversion requested — job id: ' + (convJson.job_id || 'unknown'))
      }
    } catch (err) {
      console.error(err)
      setMessage('Upload/convert failed: ' + (err.message || String(err)))
    }
  }

  const uploadToBackend = async () => {
    setMessage('Preparing upload...')
    // For images/pdf canvas capture -> blob. For other file types rely on file input.
    try {
      let blob
      let filename = 'upload.bin'
      if (currentFileType === 'image' || currentFileType === 'pdf') {
        const canvas = canvasRef.current
        blob = await new Promise((res) => canvas.toBlob(res, 'image/png'))
        filename = 'edited.png'
      } else {
        // try to grab file from file input
        const f = fileInputRef.current?.files?.[0]
        if (!f) {
          setMessage('No file selected for upload')
          return
        }
        blob = f
        filename = f.name
      }

      if (!blob) {
        setMessage('Could not capture upload data')
        return
      }

      setMessage('Uploading in chunks...')
      const uploadId = `editor-${Date.now()}`
      await uploadBlobInChunks(blob, filename, uploadId)

      setMessage('Upload complete — requesting conversion...')

      const convResp = await fetch('/api/convert-uploaded', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool_slug: 'editor',
          uploads: [{ upload_id: uploadId, filename }],
          target_format: null,
          parameters: {}
        })
      })
      const convJson = await convResp.json().catch(() => ({}))
      if (!convResp.ok) {
        throw new Error(convJson.error || 'Conversion request failed')
      }

      if (convJson.outputs && Array.isArray(convJson.outputs) && convJson.outputs.length) {
        const out = convJson.outputs[0]
        if (out.download_url) {
          setMessage('Conversion complete — ready. Click to download.')
          const link = document.createElement('a')
          link.href = out.download_url
          link.target = '_blank'
          link.rel = 'noopener'
          link.textContent = 'Download result'
          link.style.display = 'inline-block'
          link.style.marginTop = '8px'
          const container = document.createElement('div')
          container.appendChild(link)
          const root = document.querySelector('.tool-upload-section .tool-container div')
          if (root) root.appendChild(container)
        } else {
          setMessage('Conversion requested — job id: ' + (convJson.job_id || 'unknown'))
        }
      } else {
        setMessage('Conversion requested — job id: ' + (convJson.job_id || 'unknown'))
      }

    } catch (err) {
      console.error(err)
      setMessage('Upload/convert failed: ' + (err.message || String(err)))
    }
  }



  return (
    <div className="tool-page">
      <nav className="tool-navbar">
        <div className="tool-nav-container">
          <button className="back-button" onClick={() => navigate('/tools')}>← Back to Tools</button>
        </div>
      </nav>

      <section className="tool-header">
        <div className="tool-header-container">
          <h1>Editor</h1>
          <p className="tool-description">Simple canvas editor. Load an image, draw, then save or upload.</p>
        </div>
      </section>

      <section className="tool-upload-section">
        <div className="tool-container">
          <div style={{ display: 'flex', gap: '16px', flexDirection: 'column', alignItems: 'center' }}>
            <canvas
              ref={canvasRef}
              width={900}
              height={600}
              style={{ border: '1px solid #ccc', cursor: 'crosshair' }}
              onMouseDown={startDraw}
              onMouseMove={draw}
              onMouseUp={endDraw}
              onMouseLeave={endDraw}
            />

            <div style={{ display: 'flex', gap: '8px' }}>
              <input ref={fileInputRef} type="file" accept="image/*,application/pdf,.pdf,.docx,.doc,.xlsx,.xls,.csv" onChange={handleFileInput} style={{ display: 'none' }} />
              <button className="btn-small" onClick={() => fileInputRef.current?.click()}>Load File</button>
              <button className="btn-small" onClick={handleClear}>Clear</button>
              <button className="btn-primary-large" onClick={downloadLocal}>Save Locally</button>
              <button className="btn-primary-large" onClick={uploadToBackend}>Upload to Backend</button>
            </div>
            {message && <div style={{ marginTop: 8 }}>{message}</div>}
            <div style={{ width: '100%', maxWidth: 900, marginTop: 8 }}>
              <div style={{ height: 8, background: '#eee', borderRadius: 4, overflow: 'hidden' }}>
                <div style={{ width: `${uploadProgress}%`, height: '100%', background: '#4caf50' }} />
              </div>
              <div style={{ marginTop: 6 }} ref={previewRef} />
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default EditorPage
