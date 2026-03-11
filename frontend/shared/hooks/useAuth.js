import { useState, useCallback, useEffect } from 'react'

export const useAuth = () => {
  const [token, setToken] = useState(() => {
    try {
      return localStorage.getItem('token') || null
    } catch {
      return null
    }
  })
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('user')
      // Handle both null and the string 'undefined'
      if (!stored || stored === 'undefined' || stored === 'null') {
        return null
      }
      return JSON.parse(stored)
    } catch (e) {
      console.warn('Failed to parse user from localStorage:', e)
      return null
    }
  })
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    try {
      return !!localStorage.getItem('token')
    } catch {
      return false
    }
  })
  const [loading, setLoading] = useState(false)

  // Sync auth state with localStorage changes (handles login/logout from other tabs/windows)
  useEffect(() => {
    const handleStorageChange = () => {
      try {
        const newToken = localStorage.getItem('token')
        const newUserStr = localStorage.getItem('user')
        
        setToken(newToken || null)
        setIsAuthenticated(!!newToken)
        
        // Handle both null and the string 'undefined'
        if (newUserStr && newUserStr !== 'undefined' && newUserStr !== 'null') {
          try {
            setUser(JSON.parse(newUserStr))
          } catch (e) {
            console.warn('Failed to parse user from storage', e)
            setUser(null)
          }
        } else {
          setUser(null)
        }
      } catch (e) {
        console.warn('Storage sync failed:', e)
      }
    }

    // Listen for storage changes from other tabs/windows
    window.addEventListener('storage', handleStorageChange)
    
    return () => window.removeEventListener('storage', handleStorageChange)
  }, [])

  const login = useCallback((accessToken, userData) => {
    setToken(accessToken)
    setUser(userData)
    setIsAuthenticated(true)
    
    localStorage.setItem('token', accessToken)
    localStorage.setItem('user', JSON.stringify(userData))
  }, [])

  const logout = useCallback(async () => {
    try {
      setLoading(true)
      
      // Call backend logout endpoint to clear server session
      const response = await fetch('/api/auth/logout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        credentials: 'include' // Include cookies for session handling
      })
      
      console.log('Logout API response:', response.status)
    } catch (error) {
      console.warn('Logout API call failed:', error)
    } finally {
      // Store user role BEFORE clearing state (for redirect routing)
      const userRole = user?.role
      
      // Clear local state and storage synchronously
      setToken(null)
      setUser(null)
      setIsAuthenticated(false)
      setLoading(false)
      
      // Clear all auth-related localStorage items
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('user_id')
      localStorage.removeItem('api_key')
      localStorage.removeItem('username')
      localStorage.removeItem('authenticated')
      
      // Route based on user role
      const redirectPath = userRole === 'admin' ? '/admin-login' : '/login'
      
      // Use a small delay to ensure state updates are batched, then redirect
      setTimeout(() => {
        window.location.href = redirectPath
      }, 100)
    }
  }, [token, user])

  const generateTestToken = useCallback(() => {
    // For development: generate a test JWT
    const testToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXIiLCJpYXQiOjE3MDgwMDAwMDB9.simulated_token'
    login(testToken, {
      id: 'test-user',
      email: 'test@example.com',
      name: 'Test User',
      role: 'admin'
    })
  }, [login])

  return {
    token,
    user,
    isAuthenticated,
    loading,
    login,
    logout,
    generateTestToken,
  }
}

export default useAuth
