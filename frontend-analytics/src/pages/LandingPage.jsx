import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { UniversalIcon } from '../utils/UniversalIcon'
import '../styles/landing.css'

const LandingPage = () => {
  const navigate = useNavigate()
  const [dragActive, setDragActive] = useState(false)
  const [expandedFAQ, setExpandedFAQ] = useState(null)

  // Drag and drop handlers
  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      alert(`Ready to convert ${files.length} file(s)! Please login or register to start.`)
    }
  }

  // Features data
  const features = [
    {
      icon: '⚡',
      title: 'Fast Conversion',
      description: 'Convert your files in seconds, not minutes'
    },
    {
      icon: '🔒',
      title: 'Secure & Private',
      description: 'Your files are encrypted and deleted after conversion'
    },
    {
      icon: '📱',
      title: 'All Devices',
      description: 'Works seamlessly on desktop, tablet, and mobile'
    },
    {
      icon: '🎯',
      title: '100+ Formats',
      description: 'Convert between images, documents, videos, and more'
    },
    {
      icon: '☁️',
      title: 'Cloud Based',
      description: 'No software installation required, access anywhere'
    },
    {
      icon: '💰',
      title: 'Always Free',
      description: 'Basic conversions are completely free, no ads'
    }
  ]

  // How it works data
  const steps = [
    {
      num: '1',
      title: 'Upload',
      description: 'Drag and drop your file or click to browse'
    },
    {
      num: '2',
      title: 'Select Format',
      description: 'Choose the output format you need'
    },
    {
      num: '3',
      title: 'Convert',
      description: 'Click convert and wait for processing'
    },
    {
      num: '4',
      title: 'Download',
      description: 'Get your converted file instantly'
    }
  ]

  // Testimonials data
  const testimonials = [
    {
      text: 'This tool saved me hours of work. So easy to use!',
      author: 'Sarah Johnson',
      role: 'Designer',
      avatar: '👩‍💼'
    },
    {
      text: 'Fast, reliable, and absolutely free. Highly recommended.',
      author: 'Mike Chen',
      role: 'Student',
      avatar: '👨‍💻'
    },
    {
      text: 'Best file converter I have ever used. Incredible quality.',
      author: 'Emma Rodriguez',
      role: 'Marketing Manager',
      avatar: '👩‍🔬'
    }
  ]

  // FAQ data
  const faqs = [
    {
      q: 'Is my file secure?',
      a: 'Yes, your file is encrypted during upload and deleted immediately after conversion. We never store your files.'
    },
    {
      q: 'What formats do you support?',
      a: 'We support 100+ formats including Images (JPG, PNG, GIF), Documents (PDF, DOCX, XLSX), Video, Audio, and more.'
    },
    {
      q: 'How long does conversion take?',
      a: 'Most files convert in seconds. Speed depends on file size and conversion complexity.'
    },
    {
      q: 'Is there a file size limit?',
      a: 'Free users can convert up to 50MB per file. Premium users get up to 500MB.'
    },
    {
      q: 'Do I need to create an account?',
      a: 'No account required for basic conversions. Create an account to save history and access premium features.'
    },
    {
      q: 'Can I use this offline?',
      a: 'No, conversion requires internet connection. You can download the desktop app for offline use (premium).'
    }
  ]

  return (
    <div className="landing-page">
      {/* Navigation */}
      <nav className="landing-navbar">
        <div className="navbar-container">
          <div className="navbar-brand">
            <UniversalIcon icon="🔄" size={24} />
            <span className="brand-name">FileConverter Pro</span>
          </div>
          <div className="navbar-actions">
            <button 
              className="btn-link"
              onClick={() => navigate('/login')}
            >
              Login
            </button>
            <button 
              className="btn-primary"
              onClick={() => navigate('/register')}
            >
              Sign Up Free
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-container">
          <div className="hero-content">
            <h1>Convert Files Online Instantly</h1>
            <p className="hero-subtitle">
              Fast, secure, and free file conversion. No software installation. No hidden limits.
            </p>
            
            {/* Upload Widget */}
            <div 
              className={`upload-box ${dragActive ? 'drag-active' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <div className="upload-content">
                <UniversalIcon icon="📁" size={48} />
                <h3>Drag & Drop Your File Here</h3>
                <p className="upload-text">or</p>
                <button className="btn-upload">
                  Click to Browse Files
                </button>
                <p className="upload-hint">
                  Maximum file size: 50MB | Supported: 100+ formats
                </p>
              </div>
            </div>

            <div className="hero-features">
              <div className="hero-feature">
                <UniversalIcon icon="✓" size={18} />
                <span>100% Free & Secure</span>
              </div>
              <div className="hero-feature">
                <UniversalIcon icon="✓" size={18} />
                <span>No Account Required</span>
              </div>
              <div className="hero-feature">
                <UniversalIcon icon="✓" size={18} />
                <span>Works on All Devices</span>
              </div>
            </div>
          </div>

          <div className="hero-stats">
            <div className="stat-item">
              <div className="stat-number">10M+</div>
              <div className="stat-label">Conversions/Month</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">100+</div>
              <div className="stat-label">Formats Supported</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">99.9%</div>
              <div className="stat-label">Uptime</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">4.8★</div>
              <div className="stat-label">User Rating</div>
            </div>
          </div>
        </div>
      </section>

      {/* Trust Logos */}
      <section className="trust-section">
        <div className="trust-container">
          <p className="trust-label">Trusted by millions worldwide</p>
          <div className="trust-logos">
            <div className="trust-logo">Google</div>
            <div className="trust-logo">Microsoft</div>
            <div className="trust-logo">Adobe</div>
            <div className="trust-logo">AWS</div>
            <div className="trust-logo">GitHub</div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="section-container">
          <div className="section-header">
            <h2>Why Choose Us?</h2>
            <p>The most powerful and reliable file conversion tool</p>
          </div>

          <div className="features-grid">
            {features.map((feature, idx) => (
              <div key={idx} className="feature-card">
                <div className="feature-icon-large">{feature.icon}</div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="how-it-works">
        <div className="section-container">
          <div className="section-header">
            <h2>How It Works</h2>
            <p>Simple 4-step conversion process</p>
          </div>

          <div className="steps-container">
            {steps.map((step, idx) => (
              <div key={idx} className="step-card">
                <div className="step-number">{step.num}</div>
                <h3>{step.title}</h3>
                <p>{step.description}</p>
                {idx < steps.length - 1 && <div className="step-arrow">→</div>}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tool Categories */}
      <section className="tools">
        <div className="section-container">
          <div className="section-header">
            <h2>Popular Conversions</h2>
            <p>Browse our most used conversion tools</p>
          </div>

          <div className="tools-grid">
            <div className="tool-card">
              <div className="tool-icon"><UniversalIcon icon="🖸️" size={32} /></div>
              <h4>Image Converter</h4>
              <p>JPG, PNG, GIF, WebP, BMP</p>
            </div>
            <div className="tool-card">
              <div className="tool-icon"><UniversalIcon icon="📄" size={48} /></div>
              <h4>Document Converter</h4>
              <p>PDF, DOCX, XLSX, PPTX</p>
            </div>
            <div className="tool-card">
              <div className="tool-icon"><UniversalIcon icon="📉" size={32} /></div>
              <h4>Video Converter</h4>
              <p>MP4, AVI, MOV, FLV, MKV</p>
            </div>
            <div className="tool-card">
              <div className="tool-icon"><UniversalIcon icon="🎵" size={32} /></div>
              <h4>Audio Converter</h4>
              <p>MP3, WAV, AAC, FLAC, OGG</p>
            </div>
            <div className="tool-card">
              <div className="tool-icon"><UniversalIcon icon="🗜️" size={48} /></div>
              <h4>Compression</h4>
              <p>ZIP, RAR, 7Z, TAR</p>
            </div>
            <div className="tool-card">
              <div className="tool-icon"><UniversalIcon icon="📜" size={32} /></div>
              <h4>Image Tools</h4>
              <p>Resize, Crop, Compress, Watermark</p>
            </div>
          </div>

          <div className="tools-cta">
            <button className="btn-primary-large">
              View All Tools (100+)
            </button>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="testimonials">
        <div className="section-container">
          <div className="section-header">
            <h2>What Users Say</h2>
            <p>Join millions of satisfied users</p>
          </div>

          <div className="testimonials-grid">
            {testimonials.map((test, idx) => (
              <div key={idx} className="testimonial-card">
                <div className="testimonial-stars"><UniversalIcon icon="⭐" size={18} /><UniversalIcon icon="⭐" size={18} /><UniversalIcon icon="⭐" size={18} /><UniversalIcon icon="⭐" size={18} /><UniversalIcon icon="⭐" size={18} /></div>
                <p className="testimonial-text">"{test.text}"</p>
                <div className="testimonial-author">
                  <div className="author-avatar">{test.avatar}</div>
                  <div>
                    <div className="author-name">{test.author}</div>
                    <div className="author-role">{test.role}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="faq">
        <div className="section-container">
          <div className="section-header">
            <h2>Frequently Asked Questions</h2>
            <p>Get answers to common questions</p>
          </div>

          <div className="faq-container">
            {faqs.map((faq, idx) => (
              <div key={idx} className="faq-item">
                <button 
                  className="faq-question"
                  onClick={() => setExpandedFAQ(expandedFAQ === idx ? null : idx)}
                >
                  <span className="faq-icon">
                    {expandedFAQ === idx ? '−' : '+'}
                  </span>
                  {faq.q}
                </button>
                {expandedFAQ === idx && (
                  <div className="faq-answer">
                    {faq.a}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="pricing">
        <div className="section-container">
          <div className="section-header">
            <h2>Simple, Transparent Pricing</h2>
            <p>Choose the plan that fits your needs</p>
          </div>

          <div className="pricing-grid">
            <div className="pricing-card">
              <div className="pricing-badge">Most Popular</div>
              <h3>Free</h3>
              <div className="pricing-price">$0<span>/month</span></div>
              <ul className="pricing-features">
                <li>✓ 50MB file size limit</li>
                <li>✓ 100+ file formats</li>
                <li>✓ Unlimited conversions</li>
                <li>✓ No registration required</li>
                <li>✗ Batch conversion</li>
                <li>✗ Priority support</li>
              </ul>
              <button className="btn-secondary">
                Get Started
              </button>
            </div>

            <div className="pricing-card premium">
              <div className="pricing-badge premium">Best Value</div>
              <h3>Pro</h3>
              <div className="pricing-price">$9.99<span>/month</span></div>
              <ul className="pricing-features">
                <li>✓ 500MB file size limit</li>
                <li>✓ 100+ file formats</li>
                <li>✓ Unlimited conversions</li>
                <li>✓ Cloud storage (10GB)</li>
                <li>✓ Batch conversion</li>
                <li>✓ Priority support</li>
              </ul>
              <button className="btn-primary">
                Start Free Trial
              </button>
            </div>

            <div className="pricing-card">
              <h3>Business</h3>
              <div className="pricing-price">Custom</div>
              <ul className="pricing-features">
                <li>✓ Unlimited file size</li>
                <li>✓ 100+ file formats</li>
                <li>✓ Unlimited conversions</li>
                <li>✓ Cloud storage (1TB)</li>
                <li>✓ API access</li>
                <li>✓ Dedicated support</li>
              </ul>
              <button className="btn-secondary">
                Contact Sales
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-container">
          <h2>Ready to Convert Files?</h2>
          <p>Start converting now, no credit card required</p>
          <div className="cta-buttons">
            <button 
              className="btn-primary-large"
              onClick={() => navigate('/convert')}
            >
              Start Converting Now
            </button>
            <button className="btn-secondary-large">
              View All Tools
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-container">
          <div className="footer-section">
            <h4>Product</h4>
            <ul>
              <li><a href="#features">Features</a></li>
              <li><a href="#tools">Tools</a></li>
              <li><a href="#pricing">Pricing</a></li>
              <li><a href="#security">Security</a></li>
            </ul>
          </div>

          <div className="footer-section">
            <h4>Company</h4>
            <ul>
              <li><a href="#about">About Us</a></li>
              <li><a href="#blog">Blog</a></li>
              <li><a href="#careers">Careers</a></li>
              <li><a href="#contact">Contact</a></li>
            </ul>
          </div>

          <div className="footer-section">
            <h4>Legal</h4>
            <ul>
              <li><a href="#privacy">Privacy Policy</a></li>
              <li><a href="#terms">Terms of Service</a></li>
              <li><a href="#cookies">Cookie Policy</a></li>
              <li><a href="#gdpr">GDPR Compliance</a></li>
            </ul>
          </div>

          <div className="footer-section">
            <h4>Follow Us</h4>
            <div className="social-links">
              <a href="#facebook">Facebook</a>
              <a href="#twitter">Twitter</a>
              <a href="#instagram">Instagram</a>
              <a href="#linkedin">LinkedIn</a>
            </div>
          </div>
        </div>

        <div className="footer-bottom">
          <p>&copy; 2026 FileConverter Pro. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage
