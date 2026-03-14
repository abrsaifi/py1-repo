import '@testing-library/jest-dom/vitest'
import { afterEach, beforeEach, vi } from 'vitest'

beforeEach(() => {
  vi.restoreAllMocks()

  if (!window.URL.createObjectURL) {
    window.URL.createObjectURL = vi.fn(() => 'blob:tool-page-test')
  } else {
    vi.spyOn(window.URL, 'createObjectURL').mockReturnValue('blob:tool-page-test')
  }

  if (!window.URL.revokeObjectURL) {
    window.URL.revokeObjectURL = vi.fn()
  } else {
    vi.spyOn(window.URL, 'revokeObjectURL').mockImplementation(() => {})
  }

  vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})
})

afterEach(() => {
  document.head.innerHTML = ''
  document.body.innerHTML = ''
})
