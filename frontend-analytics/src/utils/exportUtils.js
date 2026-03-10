/**
 * Export utilities for CSV, PDF, and Excel formats
 */

export const exportToCSV = (data, filename = 'export.csv') => {
  if (!data || data.length === 0) {
    console.warn('No data to export')
    return
  }

  const headers = Object.keys(data[0])
  const csvContent = [
    headers.join(','),
    ...data.map(row =>
      headers.map(header => {
        const value = row[header]
        // Escape quotes and wrap in quotes if contains comma
        if (value === null || value === undefined) return ''
        const stringValue = String(value).replace(/"/g, '""')
        return stringValue.includes(',') ? `"${stringValue}"` : stringValue
      }).join(',')
    )
  ].join('\n')

  downloadFile(csvContent, filename, 'text/csv')
}

export const exportToJSON = (data, filename = 'export.json') => {
  const jsonContent = JSON.stringify(data, null, 2)
  downloadFile(jsonContent, filename, 'application/json')
}

export const exportToTSV = (data, filename = 'export.tsv') => {
  if (!data || data.length === 0) {
    console.warn('No data to export')
    return
  }

  const headers = Object.keys(data[0])
  const tsvContent = [
    headers.join('\t'),
    ...data.map(row =>
      headers.map(header => row[header] ?? '').join('\t')
    )
  ].join('\n')

  downloadFile(tsvContent, filename, 'text/tab-separated-values')
}

export const downloadFile = (content, filename, mimeType) => {
  const blob = new Blob([content], { type: mimeType })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.style.display = 'none'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

export const generateChartImage = async (chartRef) => {
  // This would require chart.js with image export plugin
  // For now, returning placeholder
  console.warn('Chart image export requires additional configuration')
  return null
}

export const tableToCSV = (tableElement, filename = 'table.csv') => {
  const rows = Array.from(tableElement.querySelectorAll('tr'))
  const csvContent = rows
    .map(row =>
      Array.from(row.querySelectorAll('th, td'))
        .map(cell => `"${cell.textContent.trim()}"`)
        .join(',')
    )
    .join('\n')

  downloadFile(csvContent, filename, 'text/csv')
}

export default {
  exportToCSV,
  exportToJSON,
  exportToTSV,
  downloadFile,
  generateChartImage,
  tableToCSV,
}
