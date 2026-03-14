import React from 'react'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import ToolPage from '../ToolPage'

const createFetchMock = ({ uploadResponse, convertResponse } = {}) => vi.fn((input, init = {}) => {
  const url = typeof input === 'string' ? input : input.url

  if (url === '/api/tools/image-resize') {
    return Promise.resolve(new Response(JSON.stringify({ tool: { slug: 'image-resize' } }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }))
  }

  if (url === '/api/tools/merge-pdf-smart') {
    return Promise.resolve(new Response(JSON.stringify({ tool: { slug: 'merge-pdf-smart' } }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }))
  }

  if (url === '/api/tools/unrunnable-tool') {
    return Promise.resolve(new Response(JSON.stringify({ tool: {
      slug: 'unrunnable-tool',
      title: 'Unrunnable Tool',
      from_format: 'Text',
      to_format: 'Target Format',
      output_format: 'auto',
      params: [],
    } }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }))
  }

  if (url === '/api/tools/image-resize/related?limit=3') {
    return Promise.resolve(new Response(JSON.stringify({ related_tools: [] }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }))
  }

  if (url === '/api/tools/merge-pdf-smart/related?limit=3') {
    return Promise.resolve(new Response(JSON.stringify({ related_tools: [] }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }))
  }

  if (url === '/api/tools/unrunnable-tool/related?limit=3') {
    return Promise.resolve(new Response(JSON.stringify({ related_tools: [] }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }))
  }

  if (url === '/api/upload-chunk') {
    if (uploadResponse) {
      return uploadResponse(url, init)
    }

    return Promise.resolve(new Response(JSON.stringify({ success: true, assembled: true }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }))
  }

  if (url === '/api/convert-uploaded') {
    if (convertResponse) {
      return convertResponse(url, init)
    }

    return Promise.resolve(new Response(new Blob(['converted']), {
      status: 200,
      headers: { 'Content-Disposition': 'attachment; filename="resized.png"' },
    }))
  }

  throw new Error(`Unexpected fetch: ${url} ${init.method || 'GET'}`)
})

const renderToolPage = (initialEntry = '/image-resize') => {
  return render(
    <MemoryRouter
      initialEntries={[initialEntry]}
      future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
    >
      <Routes>
        <Route path="/:toolSlug" element={<ToolPage />} />
      </Routes>
    </MemoryRouter>,
  )
}

describe('ToolPage', () => {
  beforeEach(() => {
    global.fetch = createFetchMock()
  })

  it('uploads the selected file and sends tool parameters for conversion', async () => {
    const { container } = renderToolPage()

    await screen.findByRole('heading', { name: 'Image Resize' })

    const uploadInput = Array.from(container.querySelectorAll('input[type="file"]')).find(
      (input) => input.getAttribute('accept') !== 'application/json',
    )

    const file = new File(['png-data'], 'photo.png', { type: 'image/png' })
    fireEvent.change(uploadInput, { target: { files: [file] } })

    fireEvent.click(await screen.findByRole('button', { name: /convert to resized image/i }))

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/convert-uploaded',
        expect.objectContaining({ method: 'POST' }),
      )
    })

    const convertCall = global.fetch.mock.calls.find(([url]) => url === '/api/convert-uploaded')
    const payload = JSON.parse(convertCall[1].body)

    expect(payload.target_format).toBe('png')
    expect(payload.parameters).toMatchObject({
      width: 800,
      height: 600,
    })
    expect(payload.uploads).toEqual([
      { upload_id: expect.stringMatching(/^image-resize-/), filename: 'photo.png' },
    ])

    await screen.findByText(/Downloaded .*resized\.png/i)
    expect(window.URL.createObjectURL).toHaveBeenCalled()
    expect(window.URL.revokeObjectURL).toHaveBeenCalled()
  })

  it('uploads multiple files for merge tools and includes the tool slug in the process request', async () => {
    render(
      <MemoryRouter
        initialEntries={['/merge-pdf-smart']}
        future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
      >
        <Routes>
          <Route path="/:toolSlug" element={<ToolPage />} />
        </Routes>
      </MemoryRouter>,
    )

    await screen.findByRole('heading', { name: 'Merge PDF (Smart)' })

    const uploadInputs = Array.from(document.querySelectorAll('input[type="file"]'))
    const uploadInput = uploadInputs.find((input) => input.getAttribute('accept') !== 'application/json')

    const firstFile = new File(['pdf-1'], 'first.pdf', { type: 'application/pdf' })
    const secondFile = new File(['pdf-2'], 'second.pdf', { type: 'application/pdf' })
    fireEvent.change(uploadInput, { target: { files: [firstFile, secondFile] } })

    fireEvent.click(await screen.findByRole('button', { name: /convert to smart combined pdf/i }))

    await waitFor(() => {
      const uploadCalls = global.fetch.mock.calls.filter(([url]) => url === '/api/upload-chunk')
      expect(uploadCalls).toHaveLength(2)
    })

    const convertCall = global.fetch.mock.calls.find(([url]) => url === '/api/convert-uploaded')
    const payload = JSON.parse(convertCall[1].body)

    expect(payload.tool_slug).toBe('merge-pdf-smart')
    expect(payload.target_format).toBe('pdf')
    expect(payload.uploads).toEqual([
      { upload_id: expect.stringMatching(/^merge-pdf-smart-/), filename: 'first.pdf' },
      { upload_id: expect.stringMatching(/^merge-pdf-smart-/), filename: 'second.pdf' },
    ])
  })

  it('rejects unsupported files before upload starts', async () => {
    const { container } = renderToolPage()

    await screen.findByRole('heading', { name: 'Image Resize' })

    const uploadInput = Array.from(container.querySelectorAll('input[type="file"]')).find(
      (input) => input.getAttribute('accept') !== 'application/json',
    )

    const invalidFile = new File(['text-data'], 'notes.txt', { type: 'text/plain' })
    fireEvent.change(uploadInput, { target: { files: [invalidFile] } })

    await screen.findByText('notes.txt is not a supported file type for this tool.')

    const uploadCalls = global.fetch.mock.calls.filter(([url]) => url === '/api/upload-chunk')
    expect(uploadCalls).toHaveLength(0)
  })

  it('surfaces upload failures from the backend', async () => {
    global.fetch = createFetchMock({
      uploadResponse: () => Promise.resolve(new Response(JSON.stringify({ success: false, error: 'file_too_large' }), {
        status: 413,
        headers: { 'Content-Type': 'application/json' },
      })),
    })

    const { container } = renderToolPage()

    await screen.findByRole('heading', { name: 'Image Resize' })

    const uploadInput = Array.from(container.querySelectorAll('input[type="file"]')).find(
      (input) => input.getAttribute('accept') !== 'application/json',
    )

    const file = new File(['png-data'], 'photo.png', { type: 'image/png' })
    fireEvent.change(uploadInput, { target: { files: [file] } })

    fireEvent.click(await screen.findByRole('button', { name: /convert to resized image/i }))

    await screen.findByText('file_too_large')
  })

  it('surfaces conversion failures from the backend', async () => {
    global.fetch = createFetchMock({
      convertResponse: () => Promise.resolve(new Response(JSON.stringify({ error: 'unsupported_target' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      })),
    })

    const { container } = renderToolPage()

    await screen.findByRole('heading', { name: 'Image Resize' })

    const uploadInput = Array.from(container.querySelectorAll('input[type="file"]')).find(
      (input) => input.getAttribute('accept') !== 'application/json',
    )

    const file = new File(['png-data'], 'photo.png', { type: 'image/png' })
    fireEvent.change(uploadInput, { target: { files: [file] } })

    fireEvent.click(await screen.findByRole('button', { name: /convert to resized image/i }))

    await screen.findByText('unsupported_target')
  })

  it('shows a clear message when a tool has no runnable output format', async () => {
    const { container } = renderToolPage('/unrunnable-tool')

    await screen.findByRole('heading', { name: 'Unrunnable Tool' })

    const uploadInput = Array.from(container.querySelectorAll('input[type="file"]')).find(
      (input) => input.getAttribute('accept') !== 'application/json',
    )

    const file = new File(['text-data'], 'notes.txt', { type: 'text/plain' })
    fireEvent.change(uploadInput, { target: { files: [file] } })

    fireEvent.click(await screen.findByRole('button', { name: /convert to target format/i }))

    await screen.findByText('This tool does not have a runnable output format yet.')

    const uploadCalls = global.fetch.mock.calls.filter(([url]) => url === '/api/upload-chunk')
    expect(uploadCalls).toHaveLength(0)
  })
})
