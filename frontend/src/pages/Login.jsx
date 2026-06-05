import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Heart, Brain, Activity, Shield, ArrowRight, Sparkles, Check } from 'lucide-react'
import TermsModal from '../components/TermsModal'
import PrivacyModal from '../components/PrivacyModal'

const Login = () => {
  const navigate = useNavigate()
  const { login, loginWithGoogle } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [agreedToTerms, setAgreedToTerms] = useState(false)
  const [showTermsModal, setShowTermsModal] = useState(false)
  const [showPrivacyModal, setShowPrivacyModal] = useState(false)

  const handleGoogleLogin = async () => {
    if (!agreedToTerms) return
    
    setIsLoading(true)
    
    try {
      // Use real Google OAuth from our backend
      loginWithGoogle()
      // The redirect will happen automatically
    } catch (error) {
      console.error('OAuth error:', error)
      setIsLoading(false)
    }
  }

  const handleDevLogin = async () => {
    if (!agreedToTerms) return
    
    setIsLoading(true)
    
    try {
      const success = await login({
        name: 'Test User',
        email: 'test@example.com',
        avatar: 'https://via.placeholder.com/150'
      })
      
      if (success) {
        navigate('/')
      }
    } catch (error) {
      console.error('Dev login error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const features = [
    {
      icon: Heart,
      title: "Personalized Care",
      description: "Get tailored health insights and recommendations"
    },
    {
      icon: Brain,
      title: "AI-Powered Analysis",
      description: "Understand complex medical reports with ease"
    },
    {
      icon: Activity,
      title: "Health Monitoring",
      description: "Track your health metrics and progress"
    },
    {
      icon: Shield,
      title: "Secure & Private",
      description: "Your health data is protected and confidential"
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-healthcare-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex">
      {/* Left Side - Features */}
      <div className="hidden lg:flex lg:w-1/2 p-12 items-center justify-center">
        <div className="max-w-md space-y-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-center"
          >
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Your AI Healthcare Companion
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300">
              Clare & CareIQ helps you understand your health better with intelligent insights and personalized guidance.
            </p>
          </motion.div>

          <div className="space-y-6">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + index * 0.1 }}
                className="flex items-start space-x-4"
              >
                <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-healthcare-500 to-primary-500 rounded-xl flex items-center justify-center">
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    {feature.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="w-full max-w-md"
        >
          {/* Logo */}
          <div className="text-center mb-8">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.3, type: "spring", stiffness: 200 }}
              className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-healthcare-500 via-primary-500 to-accent-500 rounded-2xl mb-6 shadow-lg"
            >
              <Sparkles className="w-10 h-10 text-white" />
            </motion.div>
            
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-4xl font-bold logo-text mb-2"
            >
              Clare & CareIQ
            </motion.h1>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="text-gray-600 dark:text-gray-300"
            >
              AI-Powered Healthcare Assistant
            </motion.p>
          </div>

          {/* Login Card */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 border border-gray-200 dark:border-gray-700"
          >
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Welcome Back
              </h2>
              <p className="text-gray-600 dark:text-gray-300">
                Sign in to access your personalized healthcare dashboard
              </p>
            </div>

            <motion.button
              whileHover={agreedToTerms ? { scale: 1.02 } : {}}
              whileTap={agreedToTerms ? { scale: 0.98 } : {}}
              onClick={handleGoogleLogin}
              disabled={isLoading || !agreedToTerms}
              className={`w-full flex items-center justify-center space-x-3 border rounded-xl px-6 py-4 font-medium transition-all duration-300 ${
                agreedToTerms 
                  ? 'bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:shadow-lg hover:border-gray-400 dark:hover:border-gray-500' 
                  : 'bg-gray-100 dark:bg-gray-600 border-gray-200 dark:border-gray-500 text-gray-400 dark:text-gray-500 cursor-not-allowed'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {isLoading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-500"></div>
              ) : (
                <>
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  <span>Continue with Google</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </motion.button>

            {/* Dev Login Button for Testing */}
            <motion.button
              whileHover={agreedToTerms ? { scale: 1.02 } : {}}
              whileTap={agreedToTerms ? { scale: 0.98 } : {}}
              onClick={handleDevLogin}
              disabled={isLoading || !agreedToTerms}
              className={`w-full mt-4 flex items-center justify-center space-x-3 rounded-xl px-6 py-4 font-medium transition-all duration-300 ${
                agreedToTerms 
                  ? 'bg-primary-500 hover:bg-primary-600 text-white hover:shadow-lg' 
                  : 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {isLoading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Dev Login (Testing)</span>
                </>
              )}
            </motion.button>

            {/* Terms Agreement Checkbox */}
            <div className="mt-6">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <button
                    onClick={() => setAgreedToTerms(!agreedToTerms)}
                    className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all duration-200 ${
                      agreedToTerms
                        ? 'bg-primary-500 border-primary-500 text-white'
                        : 'border-gray-300 dark:border-gray-600 hover:border-primary-500'
                    }`}
                  >
                    {agreedToTerms && <Check className="w-3 h-3" />}
                  </button>
                </div>
                <div className="flex-1">
                  <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
                    By signing in, you agree to our{' '}
                    <button
                      onClick={() => setShowTermsModal(true)}
                      className="text-primary-500 hover:underline font-medium"
                    >
                      Terms of Service
                    </button>
                    {' '}and{' '}
                    <button
                      onClick={() => setShowPrivacyModal(true)}
                      className="text-primary-500 hover:underline font-medium"
                    >
                      Privacy Policy
                    </button>
                  </p>
                </div>
              </div>
              
              {!agreedToTerms && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-3 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg"
                >
                  <p className="text-xs text-amber-800 dark:text-amber-200 flex items-center">
                    <Shield className="w-4 h-4 mr-2 flex-shrink-0" />
                    Please read and agree to our terms before signing in
                  </p>
                </motion.div>
              )}
            </div>
          </motion.div>

          {/* Demo Info */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="mt-6 text-center"
          >
            <p className="text-sm text-gray-500 dark:text-gray-400">
              💡 <strong>Real AI Integration!</strong> Use "Dev Login" for testing or "Continue with Google" for full OAuth experience.
            </p>
          </motion.div>
        </motion.div>
      </div>

      {/* Floating Elements */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <motion.div
          animate={{ 
            y: [0, -20, 0],
            rotate: [0, 5, 0]
          }}
          transition={{ 
            duration: 6,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute top-20 left-20 w-4 h-4 bg-healthcare-400 rounded-full opacity-20"
        />
        <motion.div
          animate={{ 
            y: [0, 20, 0],
            rotate: [0, -5, 0]
          }}
          transition={{ 
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute top-40 right-32 w-6 h-6 bg-primary-400 rounded-full opacity-20"
        />
        <motion.div
          animate={{ 
            y: [0, -15, 0],
            x: [0, 10, 0]
          }}
          transition={{ 
            duration: 7,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute bottom-32 left-32 w-3 h-3 bg-accent-400 rounded-full opacity-20"
        />
      </div>

      {/* Modals */}
      <TermsModal 
        isOpen={showTermsModal} 
        onClose={() => setShowTermsModal(false)} 
      />
      <PrivacyModal 
        isOpen={showPrivacyModal} 
        onClose={() => setShowPrivacyModal(false)} 
      />
    </div>
  )
}

export default Login 