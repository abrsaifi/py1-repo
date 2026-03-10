import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/index.css'
import './styles/darkmode.css'
import './styles/refinements.css'

const root = ReactDOM.createRoot(document.getElementById('root'))
root.render(
  // Temporarily disabled StrictMode to debug React DevTools node tracking issue
  <App />
)
