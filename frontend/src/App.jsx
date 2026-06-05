import React, { useState, useEffect } from 'react'
import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { ThemeProvider } from './contexts/ThemeContext'
import { AuthProvider } from './contexts/AuthContext'
import { ChatProvider } from './contexts/ChatContext'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Profile from './pages/Profile'
import Reports from './pages/Reports'
import Analytics from './pages/Analytics'
import Settings from './pages/Settings'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  const location = useLocation()
  
  // Handle OAuth success redirect
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search)
    if (urlParams.get('auth_success') === 'true') {
      // Clear the URL parameters
      window.history.replaceState({}, document.title, window.location.pathname)
      // The AuthContext will handle checking the JWT cookie
    }
  }, [location])

  return (
    <ThemeProvider>
      <AuthProvider>
        <ChatProvider>
          <div className="App">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/" element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }>
                <Route index element={<Dashboard />} />
                <Route path="profile" element={<Profile />} />
                <Route path="reports" element={<Reports />} />
                <Route path="analytics" element={<Analytics />} />
                <Route path="settings" element={<Settings />} />
              </Route>
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </ChatProvider>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App 