import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { UniversalIcon } from '../utils/UniversalIcon'
import '../styles/landing.css'
import '../styles/auth.css'

const LoginPage = ({ onLogin, onTestLogin }) => {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showPassword, setShowPassword] = useState(false)

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    
    if (!email || !password) {
      setError('Please fill in all fields')
      return
    }

    if (!email.includes('@')) {
      setError('Please enter a valid email address')
      return
    }

    setLoading(true)

    try {
      // API call to authenticate user
      const response = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      if (response.ok) {
        const data = await response.json()
        localStorage.setItem('token', data.token)
        localStorage.setItem('user', JSON.stringify(data.user))
        
        // Role-based redirect
        const userRole = data.user?.role
        if (userRole === 'admin') {
          navigate('/admin')
        } else {
          navigate('/dashboard')
        }
      } else {
        setError('Invalid email or password')
      }
    } catch (err) {
      // Fallback - allow demo login (for development only)
      if (email && password.length >= 6) {
        // Determine role based on email
        const isAdmin = email === 'admin@fastconvert.com'
        const userData = {
          id: 'user_' + Date.now(),
          email,
          name: email.split('@')[0],
          role: isAdmin ? 'admin' : 'subscriber'
        }
        localStorage.setItem('token', 'user_token_' + Date.now())
        localStorage.setItem('user', JSON.stringify(userData))
        
        // Redirect based on role
        navigate(isAdmin ? '/admin' : '/dashboard')
      } else {
        setError('Login failed. Please try again.')
      }
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
              onClick={() => navigate('/register')}
            >
              Create Account
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
          <div className="auth-card login-card">
            <div className="auth-header">
              <UniversalIcon icon="👤" size={48} />
              <h1>Welcome Back</h1>
              <p>Sign in to access your conversion history and premium features</p>
            </div>

            {error && (
              <div className="auth-error">
                <UniversalIcon icon="⚠️" size={20} /> {error}
              </div>
            )}

            <form onSubmit={handleLogin} className="auth-form">
              <div className="form-group">
                <label htmlFor="email">Email Address</label>
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
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
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
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
              </div>

              <div className="remember-forgot">
                <label className="checkbox-label">
                  <input type="checkbox" />
                  <span>Remember me</span>
                </label>
                <Link to="/forgot-password" className="auth-link-primary">
                  Forgot password?
                </Link>
              </div>

              <button
                type="submit"
                className={`auth-button ${loading ? 'loading' : ''}`}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner"></span> Signing in...
                  </>
                ) : (
                  <>Sign In</>
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
                <span><UniversalIcon icon="⚫" size={14} /> GitHub</span>
              </button>
            </div>

            <div className="auth-footer">
              <p>
                Don't have an account?{' '}
                <Link to="/register" className="auth-link">
                  Create one now
                </Link>
              </p>
            </div>
          </div>

          {/* Side Benefits */}
          <div className="auth-benefits">
            <div className="benefit-card">
              <UniversalIcon icon="⚡" size={32} />
              <h3>Fast & Easy</h3>
              <p>Convert files in seconds with just a few clicks</p>
            </div>
            <div className="benefit-card">
              <UniversalIcon icon="🔒" size={32} />
              <h3>Secure & Private</h3>
              <p>Your files are encrypted and automatically deleted</p>
            </div>
            <div className="benefit-card">
              <UniversalIcon icon="💾" size={32} />
              <h3>Save History</h3>
              <p>Keep track of all your conversions in one place</p>
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

export default LoginPage
