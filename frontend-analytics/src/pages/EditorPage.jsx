import React, { useRef, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import '../styles/tool-page.css'

function EditorPage() {
  const canvasRef = useRef(null)
  const fileInputRef = useRef(null)
  const [drawing, setDrawing] = useState(false)
  const [message, setMessage] = useState('')
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
  }

  const handleLoadImage = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const img = new Image()
    img.onload = () => {
      const canvas = canvasRef.current
      const ctx = canvas.getContext('2d')
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
    }
    img.src = URL.createObjectURL(file)
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

  const uploadToBackend = async () => {
    setMessage('Uploading...')
    const canvas = canvasRef.current
    canvas.toBlob(async (blob) => {
      if (!blob) {
        setMessage('Could not capture image')
        return
      }

      try {
        const uploadId = `editor-${Date.now()}`
        const form = new FormData()
        form.append('upload_id', uploadId)
        form.append('filename', 'edited.png')
        form.append('index', '0')
        form.append('total', '1')
        form.append('chunk', blob, 'edited.png')

        const resp = await fetch('/api/upload-chunk', { method: 'POST', body: form })
        const payload = await resp.json()
        if (!resp.ok || !payload.success) {
          throw new Error(payload.error || 'Upload failed')
        }

        setMessage('Upload complete — requesting conversion...')

        // Call the convert endpoint to run the existing conversion pipeline on the uploaded file
        try {
          const convResp = await fetch('/api/convert-uploaded', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              tool_slug: 'editor',
              uploads: [{ upload_id: uploadId, filename: 'edited.png' }],
              target_format: null,
              parameters: {}
            })
          })

          const convJson = await convResp.json()
          if (!convResp.ok) {
            throw new Error(convJson.error || 'Conversion request failed')
          }

          // If conversion returned outputs with download URLs, surface them
          if (convJson.outputs && Array.isArray(convJson.outputs) && convJson.outputs.length) {
            const out = convJson.outputs[0]
            if (out.download_url) {
              setMessage('Conversion complete — ready. Click to download.')
              // create a temporary link for the first output
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
        } catch (cErr) {
          console.error(cErr)
          setMessage('Conversion request failed: ' + (cErr.message || String(cErr)))
        }

      } catch (err) {
        console.error(err)
        setMessage('Upload failed: ' + (err.message || String(err)))
      }
    }, 'image/png')
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
              <input ref={fileInputRef} type="file" accept="image/*" onChange={handleLoadImage} style={{ display: 'none' }} />
              <button className="btn-small" onClick={() => fileInputRef.current?.click()}>Load Image</button>
              <button className="btn-small" onClick={handleClear}>Clear</button>
              <button className="btn-primary-large" onClick={downloadLocal}>Save Locally</button>
              <button className="btn-primary-large" onClick={uploadToBackend}>Upload to Backend</button>
            </div>
            {message && <div style={{ marginTop: 8 }}>{message}</div>}
          </div>
        </div>
      </section>
    </div>
  )
}

export default EditorPage
