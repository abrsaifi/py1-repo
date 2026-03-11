import React, { useState } from 'react'
import { UniversalIcon } from '@shared/utils/UniversalIcon'
import { useNavigate, Link } from 'react-router-dom'

import '../../styles/landing.css'
import '../../styles/auth.css'

const RegisterPage = () => {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const validateForm = () => {
    if (!formData.username.trim()) {
      setError('Please enter a username')
      return false
    }

    if (!formData.email.includes('@')) {
      setError('Please enter a valid email address')
      return false
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters')
      return false
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return false
    }

    if (!formData.agreeToTerms) {
      setError('Please agree to the Terms of Service')
      return false
    }

    return true
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!validateForm()) {
      return
    }

    setLoading(true)

    try {
      // API call to register
      const response = await fetch('http://localhost:5000/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: formData.username,
          email: formData.email,
          password: formData.password
        })
      })

      if (response.ok) {
        const data = await response.json()
        localStorage.setItem('token', data.token)
        localStorage.setItem('user', JSON.stringify(data.user))
        navigate(data.user?.role === 'admin' ? '/admin' : '/dashboard')
      } else {
        const data = await response.json()
        setError(data.message || 'Registration failed')
      }
    } catch (err) {
      // Fallback - allow demo registration
      const newUser = {
        id: Date.now().toString(),
        username: formData.username,
        email: formData.email,
        plan: 'Free',
        avatar: 'https://i.pravatar.cc/150?img=' + Math.floor(Math.random() * 70)
      }
      localStorage.setItem('token', 'demo_token_' + Date.now())
      localStorage.setItem('user', JSON.stringify(newUser))
      navigate('/dashboard')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="landing-page auth-page">
      {/* Navigation */}
      <nav className="landing-navbar">
        <div className="navbar-container">
          <div className="navbar-brand">
            <button onClick={() => navigate('/')} className="brand-button">
              <UniversalIcon icon="🔄" size={24} />
              <span className="brand-name">FastConvert</span>
            </button>
          </div>
          <div className="navbar-actions">
            <button 
              className="btn-link"
              onClick={() => navigate('/login')}
            >
              Sign In
            </button>
            <button 
              className="btn-link"
              onClick={() => navigate('/admin-login')}
            >
              Admin
            </button>
          </div>
        </div>
      </nav>

      {/* Auth Section */}
      <section className="auth-section">
        <div className="auth-container">
          <div className="auth-card register-card">
            <div className="auth-header">
              <UniversalIcon icon="✨" size={48} />
              <h1>Create Account</h1>
              <p>Join FastConvert and start converting files instantly</p>
            </div>

            <form onSubmit={handleSubmit} className="auth-form">
              {error && (
                <div className="auth-error">
                  <UniversalIcon icon="⚠️" size={20} /> {error}
                </div>
              )}

              <div className="form-group">
                <label htmlFor="username">Username</label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  placeholder="Choose a username"
                  className="form-input"
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">Email Address</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="you@example.com"
                  className="form-input"
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="password">Password</label>
                <div className="password-input-wrapper">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="••••••••"
                    className="form-input"
                    disabled={loading}
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowPassword(!showPassword)}
                    tabIndex="-1"
                  >
                    {showPassword ? <UniversalIcon icon="👁️" size={18} /> : <UniversalIcon icon="👁️‍🗨️" size={18} />}
                  </button>
                </div>
                <small className="form-hint">At least 6 characters</small>
              </div>

              <div className="form-group">
                <label htmlFor="confirmPassword">Confirm Password</label>
                <div className="password-input-wrapper">
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    id="confirmPassword"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    placeholder="••••••••"
                    className="form-input"
                    disabled={loading}
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    tabIndex="-1"
                  >
                    {showConfirmPassword ? <UniversalIcon icon="👁️" size={18} /> : <UniversalIcon icon="👁️‍🗨️" size={18} />}
                  </button>
                </div>
              </div>

              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="agreeToTerms"
                  checked={formData.agreeToTerms}
                  onChange={handleChange}
                  disabled={loading}
                />
                <span>
                  I agree to the{' '}
                  <Link to="/terms" className="auth-link-inline">
                    Terms of Service
                  </Link>
                  {' '}and{' '}
                  <Link to="/privacy" className="auth-link-inline">
                    Privacy Policy
                  </Link>
                </span>
              </label>

              <button
                type="submit"
                className={`auth-button ${loading ? 'loading' : ''}`}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner"></span> Creating Account...
                  </>
                ) : (
                  <>Create Account</>
                )}
              </button>
            </form>

            <div className="auth-divider">
              <span>or</span>
            </div>

            <div className="social-login">
              <button className="social-button google" disabled={loading}>
                <UniversalIcon icon="🔵" size={18} /> Google
              </button>
              <button className="social-button github" disabled={loading}>
                <span><UniversalIcon icon="⚫" size={14} /></span> GitHub
              </button>
            </div>

            <div className="auth-footer">
              <p>
                Already have an account?{' '}
                <Link to="/login" className="auth-link">
                  Sign in
                </Link>
              </p>
            </div>
          </div>

          {/* Side Benefits */}
          <div className="auth-benefits">
            <div className="benefit-card">
              <UniversalIcon icon="⚡" size={32} />
              <h3>Instant Setup</h3>
              <p>No credit card required, completely free to start</p>
            </div>
            <div className="benefit-card">
              <UniversalIcon icon="🔒" size={32} />
              <h3>100% Secure</h3>
              <p>End-to-end encryption for all your files</p>
            </div>
            <div className="benefit-card">
              <UniversalIcon icon="💎" size={32} />
              <h3>Premium Ready</h3>
              <p>Upgrade anytime for unlimited conversions</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-container">
          <div className="footer-content">
            <p>&copy; 2026 FastConvert. All rights reserved.</p>
            <div className="footer-links">
              <Link to="#privacy" className="footer-link">Privacy Policy</Link>
              <span className="footer-divider">•</span>
              <Link to="#terms" className="footer-link">Terms of Service</Link>
              <span className="footer-divider">•</span>
              <Link to="#contact" className="footer-link">Contact Us</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default RegisterPage
