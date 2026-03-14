import React, { useEffect, useState } from 'react'
import { UniversalIcon } from '../utils/UniversalIcon'
import '../styles/admin.css'

function AEOEngine() {
  const [loading, setLoading] = useState(true)
  const [summary, setSummary] = useState({
    totalPages: 0,
    answerReadyPages: 0,
    needsWorkPages: 0,
    schemaCoverage: '0%',
    faqCoverage: '0%',
    averageReadiness: 0,
  })
  const [pages, setPages] = useState([])
  const [questions, setQuestions] = useState([])

  const authHeaders = {
    Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
  }

  const loadAEOData = async () => {
    try {
      setLoading(true)
      const [summaryResponse, pagesResponse, questionsResponse] = await Promise.all([
        fetch('/api/aeo/summary', { headers: authHeaders }),
        fetch('/api/aeo/pages', { headers: authHeaders }),
        fetch('/api/aeo/questions', { headers: authHeaders }),
      ])

      if (!summaryResponse.ok || !pagesResponse.ok || !questionsResponse.ok) {
        throw new Error('Failed to load AEO data')
      }

      const summaryData = await summaryResponse.json()
      const pagesData = await pagesResponse.json()
      const questionsData = await questionsResponse.json()

      setSummary(summaryData.summary || {})
      setPages(pagesData.pages || [])
      setQuestions(questionsData.questions || [])
    } catch (error) {
      console.error('Failed to load AEO data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAEOData()
  }, [])

  const postAction = async (url, message) => {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders,
        },
      })
      if (!response.ok) {
        throw new Error('Request failed')
      }
      const payload = await response.json()
      alert(payload.message || message)
      loadAEOData()
    } catch (error) {
      console.error('AEO action failed:', error)
      alert('Action failed')
    }
  }

  return (
    <div className="admin-section">
      <h2><UniversalIcon icon="🧠" size={24} /> AEO Engine</h2>
      <p className="section-subtitle">Answer-readiness scoring for CMS and tool pages</p>

      <div className="admin-stats-grid">
        <div className="admin-stat-card metric-primary">
          <UniversalIcon icon="📄" size={32} />
          <div className="stat-content">
            <h3>Total Pages</h3>
            <p className="stat-value">{loading ? '...' : summary.totalPages}</p>
            <p className="stat-detail">Pages evaluated for answer engines</p>
          </div>
        </div>
        <div className="admin-stat-card metric-success">
          <UniversalIcon icon="✅" size={32} />
          <div className="stat-content">
            <h3>Answer Ready</h3>
            <p className="stat-value">{loading ? '...' : summary.answerReadyPages}</p>
            <p className="stat-detail">Pages ready for direct answers</p>
          </div>
        </div>
        <div className="admin-stat-card metric-warning">
          <UniversalIcon icon="🛠️" size={32} />
          <div className="stat-content">
            <h3>Needs Work</h3>
            <p className="stat-value">{loading ? '...' : summary.needsWorkPages}</p>
            <p className="stat-detail">Pages missing answer signals</p>
          </div>
        </div>
        <div className="admin-stat-card metric-info">
          <UniversalIcon icon="🧩" size={32} />
          <div className="stat-content">
            <h3>Schema Coverage</h3>
            <p className="stat-value">{loading ? '...' : summary.schemaCoverage}</p>
            <p className="stat-detail">Structured data coverage</p>
          </div>
        </div>
        <div className="admin-stat-card metric-revenue">
          <UniversalIcon icon="❓" size={32} />
          <div className="stat-content">
            <h3>FAQ Coverage</h3>
            <p className="stat-value">{loading ? '...' : summary.faqCoverage}</p>
            <p className="stat-detail">Pages with FAQ signals</p>
          </div>
        </div>
        <div className="admin-stat-card metric-success">
          <UniversalIcon icon="📈" size={32} />
          <div className="stat-content">
            <h3>Average Readiness</h3>
            <p className="stat-value">{loading ? '...' : summary.averageReadiness}</p>
            <p className="stat-detail">Composite readiness score</p>
          </div>
        </div>
      </div>

      <div className="quick-actions" style={{ marginTop: '30px', marginBottom: '30px' }}>
        <button className="action-button primary" onClick={() => postAction('/api/aeo/actions/generate', 'AEO recommendations refreshed')}>
          <UniversalIcon icon="🔄" size={16} /> Refresh Recommendations
        </button>
        <button className="action-button primary" onClick={() => postAction('/api/aeo/actions/expand-faqs', 'FAQ expansion suggestions queued')}>
          <UniversalIcon icon="➕" size={16} /> Expand FAQs
        </button>
      </div>

      <div className="admin-section-content" style={{ marginBottom: '30px' }}>
        <h3>Question Opportunities</h3>
        <div className="jobs-table-wrapper">
          <table className="jobs-table">
            <thead>
              <tr>
                <th>Page</th>
                <th>Question</th>
                <th>Source</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {questions.map((item) => (
                <tr key={`${item.pageId}-${item.question}`} className="job-row processing">
                  <td><strong>{item.title}</strong></td>
                  <td>{item.question}</td>
                  <td style={{ textTransform: 'capitalize' }}>{item.source}</td>
                  <td><strong>{item.score}</strong></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {!loading && questions.length === 0 && <div className="no-data"><p>No question opportunities found yet.</p></div>}
      </div>

      <div className="admin-section-content">
        <h3>AEO Coverage by Page</h3>
        <div className="jobs-table-wrapper">
          <table className="jobs-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Source</th>
                <th>Status</th>
                <th>Score</th>
                <th>Primary Question</th>
                <th>Recommended Action</th>
              </tr>
            </thead>
            <tbody>
              {pages.map((page) => (
                <tr key={page.id} className={`job-row ${page.status === 'answer-ready' ? 'indexed' : 'failed'}`}>
                  <td><strong>{page.title}</strong></td>
                  <td style={{ textTransform: 'capitalize' }}>{page.source}</td>
                  <td>
                    <span className="status-badge" style={{ backgroundColor: page.status === 'answer-ready' ? '#11998e' : '#fa709a' }}>
                      {page.status === 'answer-ready' ? 'Ready' : 'Needs Work'}
                    </span>
                  </td>
                  <td><strong>{page.readinessScore}</strong></td>
                  <td>{page.primaryQuestion}</td>
                  <td>{page.recommendedAction}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {!loading && pages.length === 0 && <div className="no-data"><p>No AEO pages found yet.</p></div>}
      </div>
    </div>
  )
}

export default AEOEngine