import { useState, useCallback, useEffect } from 'react'

export const useAuth = () => {
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('user')
    return stored ? JSON.parse(stored) : null
  })
  const [isAuthenticated, setIsAuthenticated] = useState(!!token)
  const [loading, setLoading] = useState(false)

  const login = useCallback((accessToken, userData) => {
    setToken(accessToken)
    setUser(userData)
    setIsAuthenticated(true)
    
    localStorage.setItem('token', accessToken)
    localStorage.setItem('user', JSON.stringify(userData))
  }, [])

  const logout = useCallback(() => {
    setToken(null)
    setUser(null)
    setIsAuthenticated(false)
    
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }, [])

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
