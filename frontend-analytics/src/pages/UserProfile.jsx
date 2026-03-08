import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import '../styles/dashboard.css'

const UserProfile = () => {
  const navigate = useNavigate()
  const [profile, setProfile] = useState({
    firstName: 'John',
    lastName: 'Doe',
    email: 'john.doe@example.com',
    avatar: '👤',
    phone: '+1 (555) 123-4567',
    company: 'Acme Corporation',
    country: 'United States',
    city: 'San Francisco',
    bio: 'Digital professional working with file conversions daily'
  })

  const [editMode, setEditMode] = useState(false)
  const [formData, setFormData] = useState(profile)
  const [message, setMessage] = useState('')

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData({ ...formData, [name]: value })
  }

  const handleSaveProfile = () => {
    setProfile(formData)
    setEditMode(false)
    setMessage('✅ Profile updated successfully!')
    setTimeout(() => setMessage(''), 3000)
  }

  const handleCancel = () => {
    setFormData(profile)
    setEditMode(false)
  }

  const handleUploadAvatar = () => {
    alert('Avatar upload functionality would be implemented here')
  }

  return (
    <div className="user-dashboard">
      <div className="profile-container">
        {message && <div className="success-message">{message}</div>}

        {/* Avatar Section */}
        <section className="profile-section avatar-section">
          <div className="avatar-box">
            <div className="avatar-large">{profile.avatar}</div>
            <button className="btn-secondary" onClick={handleUploadAvatar}>
              Change Avatar
            </button>
          </div>
        </section>

        {/* Profile Form */}
        <section className="profile-section form-section">
          <div className="section-title">
            <h2>Personal Information</h2>
            {!editMode && (
              <button 
                className="btn-link"
                onClick={() => setEditMode(true)}
              >
                Edit Profile
              </button>
            )}
          </div>

          <div className="form-grid">
            <div className="form-group">
              <label>First Name</label>
              <input 
                type="text" 
                name="firstName"
                value={editMode ? formData.firstName : profile.firstName}
                onChange={handleInputChange}
                disabled={!editMode}
                className={editMode ? 'editable' : 'disabled'}
              />
            </div>

            <div className="form-group">
              <label>Last Name</label>
              <input 
                type="text" 
                name="lastName"
                value={editMode ? formData.lastName : profile.lastName}
                onChange={handleInputChange}
                disabled={!editMode}
                className={editMode ? 'editable' : 'disabled'}
              />
            </div>

            <div className="form-group full">
              <label>Email Address</label>
              <input 
                type="email" 
                name="email"
                value={editMode ? formData.email : profile.email}
                onChange={handleInputChange}
                disabled={!editMode}
                className={editMode ? 'editable' : 'disabled'}
              />
            </div>

            <div className="form-group">
              <label>Phone Number</label>
              <input 
                type="tel" 
                name="phone"
                value={editMode ? formData.phone : profile.phone}
                onChange={handleInputChange}
                disabled={!editMode}
                className={editMode ? 'editable' : 'disabled'}
              />
            </div>

            <div className="form-group">
              <label>Company</label>
              <input 
                type="text" 
                name="company"
                value={editMode ? formData.company : profile.company}
                onChange={handleInputChange}
                disabled={!editMode}
                className={editMode ? 'editable' : 'disabled'}
              />
            </div>

            <div className="form-group">
              <label>Country</label>
              <input 
                type="text" 
                name="country"
                value={editMode ? formData.country : profile.country}
                onChange={handleInputChange}
                disabled={!editMode}
                className={editMode ? 'editable' : 'disabled'}
              />
            </div>

            <div className="form-group">
              <label>City</label>
              <input 
                type="text" 
                name="city"
                value={editMode ? formData.city : profile.city}
                onChange={handleInputChange}
                disabled={!editMode}
                className={editMode ? 'editable' : 'disabled'}
              />
            </div>

            <div className="form-group full">
              <label>Bio</label>
              <textarea 
                name="bio"
                rows="4"
                value={editMode ? formData.bio : profile.bio}
                onChange={handleInputChange}
                disabled={!editMode}
                className={editMode ? 'editable' : 'disabled'}
              />
            </div>
          </div>

          {editMode && (
            <div className="form-actions">
              <button className="btn-primary" onClick={handleSaveProfile}>
                Save Changes
              </button>
              <button className="btn-secondary" onClick={handleCancel}>
                Cancel
              </button>
            </div>
          )}
        </section>

        {/* Account Stats */}
        <section className="profile-section stats-section">
          <div className="stats-minimal">
            <div className="stat-item">
              <div className="stat-value">156</div>
              <div className="stat-text">Total Conversions</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">42</div>
              <div className="stat-text">This Month</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">99.8%</div>
              <div className="stat-text">Success Rate</div>
            </div>
          </div>
        </section>

        {/* Preferences */}
        <section className="profile-section preferences-section">
          <h2>Notification Preferences</h2>
          <div className="preference-list">
            <div className="preference-item">
              <div>
                <div className="pref-title">Email Notifications</div>
                <div className="pref-desc">Receive conversion completion emails</div>
              </div>
              <input type="checkbox" defaultChecked />
            </div>
            <div className="preference-item">
              <div>
                <div className="pref-title">Marketing Emails</div>
                <div className="pref-desc">Learn about new features and offers</div>
              </div>
              <input type="checkbox" defaultChecked />
            </div>
            <div className="preference-item">
              <div>
                <div className="pref-title">Security Alerts</div>
                <div className="pref-desc">Get notified of login attempts and important changes</div>
              </div>
              <input type="checkbox" defaultChecked />
            </div>
          </div>
        </section>
      </div>

      <style>{`
        .profile-container {
          max-width: 1400px;
          margin: 0 auto;
          padding: 30px 20px;
          width: 100%;
        }

        .success-message {
          background: #e8f5e9;
          color: #2e7d32;
          padding: 12px 16px;
          border-radius: 6px;
          margin-bottom: 20px;
          border-left: 4px solid #2e7d32;
        }

        .profile-section {
          background: white;
          padding: 30px;
          border-radius: 12px;
          margin-bottom: 20px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }

        .avatar-section {
          display: flex;
          justify-content: center;
        }

        .avatar-box {
          text-align: center;
        }

        .avatar-large {
          font-size: 120px;
          margin-bottom: 20px;
          display: inline-block;
          padding: 20px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 50%;
          width: 160px;
          height: 160px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .section-title {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 25px;
          border-bottom: 1px solid #e0e0e0;
          padding-bottom: 15px;
        }

        .section-title h2 {
          margin: 0;
          font-size: 20px;
        }

        .form-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 20px;
          margin-bottom: 20px;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .form-group.full {
          grid-column: 1 / -1;
        }

        .form-group label {
          font-weight: 600;
          color: #333;
          font-size: 14px;
        }

        .form-group input,
        .form-group textarea {
          padding: 12px;
          border: 1px solid #ddd;
          border-radius: 6px;
          font-size: 14px;
          font-family: inherit;
          transition: all 0.2s ease;
        }

        .form-group input.editable,
        .form-group textarea.editable {
          background: white;
          border-color: #667eea;
          cursor: text;
        }

        .form-group input.editable:focus,
        .form-group textarea.editable:focus {
          outline: none;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .form-group input.disabled,
        .form-group textarea.disabled {
          background: #f5f5f5;
          color: #666;
          cursor: not-allowed;
        }

        .form-actions {
          display: flex;
          gap: 12px;
          margin-top: 20px;
        }

        .stats-minimal {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
          gap: 16px;
        }

        .stat-item {
          text-align: center;
          padding: 16px 12px;
        }

        .stat-value {
          font-size: 28px;
          font-weight: 700;
          color: #3b82f6;
          margin-bottom: 6px;
        }

        .stat-text {
          font-size: 12px;
          color: #6b7280;
          font-weight: 500;
        }

        .preference-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .preference-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px;
          background: #f9f9f9;
          border-radius: 8px;
        }

        .pref-title {
          font-weight: 600;
          color: #333;
          margin-bottom: 4px;
        }

        .pref-desc {
          font-size: 13px;
          color: #666;
        }

        .preference-item input[type="checkbox"] {
          width: 24px;
          height: 24px;
          cursor: pointer;
        }

        @media (max-width: 768px) {
          .profile-container {
            padding: 20px 12px;
          }

          .profile-section {
            padding: 20px;
          }

          .form-grid {
            grid-template-columns: 1fr;
          }

          .avatar-large {
            font-size: 80px;
            width: 120px;
            height: 120px;
          }

          .section-title {
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
          }

          .stats-minimal {
            grid-template-columns: repeat(2, 1fr);
          }

          .form-actions {
            flex-direction: column-reverse;
          }

          .form-actions button {
            width: 100%;
          }
        }
      `}</style>
    </div>
  )
}

export default UserProfile
