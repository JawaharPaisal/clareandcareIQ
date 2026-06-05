import React, { createContext, useContext, useState, useEffect } from 'react'
import toast from 'react-hot-toast'

const AuthContext = createContext()

// Backend API configuration
const API_BASE = 'http://localhost:5000'

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check for existing session
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/auth/me`, {
        credentials: 'include' // Include cookies for JWT
      })
      
      if (response.ok) {
        const data = await response.json()
        setUser(data.user)
        // Also save to sessionStorage for persistence
        sessionStorage.setItem('clareCareIQ_user', JSON.stringify(data.user))
      } else {
        // Clear any invalid session
        setUser(null)
        sessionStorage.removeItem('clareCareIQ_user')
      }
    } catch (error) {
      console.error('Auth check failed:', error)
      setUser(null)
      sessionStorage.removeItem('clareCareIQ_user')
    } finally {
      setLoading(false)
    }
  }

  const loginWithGoogle = () => {
    // Redirect to our Flask OAuth endpoint
    window.location.href = `${API_BASE}/auth/google`
  }

  const login = async (userData) => {
    try {
      // For development, use dev login endpoint
      const response = await fetch(`${API_BASE}/auth/dev-login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(userData)
      })
      
      if (response.ok) {
        const data = await response.json()
        // Check auth status to get user details
        await checkAuthStatus()
        toast.success('Welcome to Clare & CareIQ!')
        return true
      } else {
        throw new Error('Login failed')
      }
    } catch (error) {
      console.error('Login error:', error)
      toast.error('Login failed. Please try again.')
      return false
    }
  }

  const logout = async () => {
    try {
      // Call backend logout endpoint
      await fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        credentials: 'include'
      })
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setUser(null)
      sessionStorage.removeItem('clareCareIQ_user')
      toast.success('Logged out successfully')
    }
  }

  const updateProfile = async (updates) => {
    try {
      const response = await fetch(`${API_BASE}/profile/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(updates)
      })
      
      if (response.ok) {
        // Refresh user data from backend
        await checkAuthStatus()
        toast.success('Profile updated successfully!')
        return true
      } else {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to update profile')
      }
    } catch (error) {
      console.error('Profile update error:', error)
      toast.error(error.message || 'Failed to update profile. Please try again.')
      return false
    }
  }

  const value = {
    user,
    loading,
    login,
    loginWithGoogle,
    logout,
    updateProfile,
    checkAuthStatus
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
} 