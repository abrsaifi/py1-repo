import React, { useState } from 'react'

const StatisticalAnalysis = () => {
  const [selectedDataset, setSelectedDataset] = useState('sales')
  const [statsResults, setStatsResults] = useState(null)

  const datasets = [
    { id: 'sales', name: 'Sales Data' },
    { id: 'traffic', name: 'Website Traffic' },
    { id: 'users', name: 'User Metrics' },
    { id: 'performance', name: 'System Performance' }
  ]

  const performanceAnalysis = () => {
    const mockResults = {
      descriptive: {
        mean: 4250.75,
        median: 4100,
        mode: 4000,
        stdDev: 892.34,
        variance: 796272.39,
        min: 1200,
        max: 8500,
        range: 7300,
        q1: 3200,
        q3: 5400,
        iqr: 2200
      },
      distribution: {
        skewness: 0.82,
        kurtosis: 1.23,
        normality: 'Non-normal (Shapiro-Wilk p < 0.05)'
      },
      inferential: {
        sampleSize: 156,
        stderr: 71.4,
        ci95Lower: 4110.6,
        ci95Upper: 4390.9,
        testStatistic: 59.6,
        pValue: 0.0001
      },
      correlation: [
        { variable: 'Time Period', correlation: 0.87, pValue: 0.0001 },
        { variable: 'Product Category', correlation: 0.65, pValue: 0.001 },
        { variable: 'User Segment', correlation: 0.52, pValue: 0.012 }
      ],
      regression: {
        rSquared: 0.89,
        adjustedRSquared: 0.87,
        fValue: 78.5,
        pValue: 0.0001,
        coefficients: [
          { variable: 'Intercept', value: 250.42, stderr: 125.3 },
          { variable: 'Time Period', value: 125.67, stderr: 14.2 },
          { variable: 'Product Cat.', value: 89.34, stderr: 18.9 }
        ]
      }
    }
    setStatsResults(mockResults)
  }

  return (
    <div className="statistical-analysis">
      <div className="analysis-controls">
        <div className="control-group">
          <label>Select Dataset</label>
          <select
            value={selectedDataset}
            onChange={(e) => setSelectedDataset(e.target.value)}
            className="form-input"
          >
            {datasets.map(ds => (
              <option key={ds.id} value={ds.id}>{ds.name}</option>
            ))}
          </select>
        </div>
        <button className="btn-primary" onClick={performanceAnalysis}>
          <UniversalIcon icon="📊" size={14} /> Perform Analysis
        </button>
      </div>

      {statsResults && (
        <div className="stats-results">
          {/* Descriptive Statistics */}
          <section className="stats-section">
            <h2><UniversalIcon icon="📈" size={24} /> Descriptive Statistics</h2>
            <div className="stats-grid">
              <div className="stat-item">
                <span className="stat-label">Mean</span>
                <span className="stat-value">{statsResults.descriptive.mean.toFixed(2)}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Median</span>
                <span className="stat-value">{statsResults.descriptive.median}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Mode</span>
                <span className="stat-value">{statsResults.descriptive.mode}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Std Dev</span>
                <span className="stat-value">{statsResults.descriptive.stdDev.toFixed(2)}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Variance</span>
                <span className="stat-value">{statsResults.descriptive.variance.toFixed(2)}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Min</span>
                <span className="stat-value">{statsResults.descriptive.min}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Max</span>
                <span className="stat-value">{statsResults.descriptive.max}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Range</span>
                <span className="stat-value">{statsResults.descriptive.range}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Q1</span>
                <span className="stat-value">{statsResults.descriptive.q1}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Q3</span>
                <span className="stat-value">{statsResults.descriptive.q3}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">IQR</span>
                <span className="stat-value">{statsResults.descriptive.iqr}</span>
              </div>
            </div>
          </section>

          {/* Distribution Analysis */}
          <section className="stats-section">
            <h2><UniversalIcon icon="📊" size={24} /> Distribution Analysis</h2>
            <div className="distribution-table">
              <div className="table-row">
                <span className="label">Skewness:</span>
                <span className="value">{statsResults.distribution.skewness} (Right-skewed)</span>
              </div>
              <div className="table-row">
                <span className="label">Kurtosis:</span>
                <span className="value">{statsResults.distribution.kurtosis} (Leptokurtic)</span>
              </div>
              <div className="table-row">
                <span className="label">Normality Test:</span>
                <span className="value">{statsResults.distribution.normality}</span>
              </div>
            </div>
          </section>

          {/* Inferential Statistics */}
          <section className="stats-section">
            <h2><UniversalIcon icon="🎯" size={24} /> Inferential Statistics</h2>
            <div className="inference-table">
              <div className="table-row">
                <span className="label">Sample Size:</span>
                <span className="value">{statsResults.inferential.sampleSize}</span>
              </div>
              <div className="table-row">
                <span className="label">Standard Error:</span>
                <span className="value">{statsResults.inferential.stderr}</span>
              </div>
              <div className="table-row">
                <span className="label">95% CI Lower:</span>
                <span className="value">{statsResults.inferential.ci95Lower.toFixed(2)}</span>
              </div>
              <div className="table-row">
                <span className="label">95% CI Upper:</span>
                <span className="value">{statsResults.inferential.ci95Upper.toFixed(2)}</span>
              </div>
              <div className="table-row">
                <span className="label">Test Statistic:</span>
                <span className="value">{statsResults.inferential.testStatistic}</span>
              </div>
              <div className="table-row">
                <span className="label">P-Value:</span>
                <span className="value">{statsResults.inferential.pValue} (Significant)</span>
              </div>
            </div>
          </section>

          {/* Correlation Analysis */}
          <section className="stats-section">
            <h2><UniversalIcon icon="🔗" size={24} /> Correlation Analysis</h2>
            <div className="analysis-table">
              <div className="table-header">
                <span>Variable</span>
                <span>Correlation</span>
                <span>P-Value</span>
                <span>Significance</span>
              </div>
              {statsResults.correlation.map((item, idx) => (
                <div key={`corr-${idx}-${item.variable}`} className="table-row">
                  <span>{item.variable}</span>
                  <span>{item.correlation.toFixed(3)}</span>
                  <span>{item.pValue}</span>
                  <span className={item.pValue < 0.05 ? 'significant' : ''}>
                    {item.pValue < 0.05 ? <><UniversalIcon icon="✓" size={14} /> Significant</> : 'Not Significant'}
                  </span>
                </div>
              ))}
            </div>
          </section>

          {/* Regression Analysis */}
          <section className="stats-section">
            <h2><UniversalIcon icon="🐠" size={24} /> Regression Analysis</h2>
            <div className="regression-summary">
              <div className="summary-item">
                <span className="label">R²:</span>
                <span className="value">{statsResults.regression.rSquared.toFixed(3)}</span>
              </div>
              <div className="summary-item">
                <span className="label">Adjusted R²:</span>
                <span className="value">{statsResults.regression.adjustedRSquared.toFixed(3)}</span>
              </div>
              <div className="summary-item">
                <span className="label">F-Value:</span>
                <span className="value">{statsResults.regression.fValue}</span>
              </div>
              <div className="summary-item">
                <span className="label">P-Value:</span>
                <span className="value">{statsResults.regression.pValue}</span>
              </div>
            </div>
            <div className="analysis-table" style={{ marginTop: '20px' }}>
              <div className="table-header">
                <span>Variable</span>
                <span>Coefficient</span>
                <span>Std Error</span>
                <span>T-Value</span>
              </div>
              {statsResults.regression.coefficients.map((coef, idx) => (
                <div key={`coef-${idx}-${coef.variable}`} className="table-row">
                  <span>{coef.variable}</span>
                  <span>{coef.value.toFixed(3)}</span>
                  <span>{coef.stderr.toFixed(3)}</span>
                  <span>{(coef.value / coef.stderr).toFixed(3)}</span>
                </div>
              ))}
            </div>
          </section>

          <div className="export-section">
            <button className="btn-primary"><UniversalIcon icon="📍" size={14} /> Export Results as PDF</button>
            <button className="btn-secondary"><UniversalIcon icon="ud83d\udcbe" size={14} /> Save Analysis</button>
          </div>
        </div>
      )}

      {!statsResults && (
        <div className="empty-state">
          <p>Select a dataset and click "Perform Analysis" to get started</p>
        </div>
      )}
    </div>
  )
}

export default StatisticalAnalysis
