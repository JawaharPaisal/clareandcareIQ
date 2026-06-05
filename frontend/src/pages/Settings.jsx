import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Settings as SettingsIcon, 
  Bell, 
  Shield, 
  User, 
  Moon, 
  Sun,
  Smartphone,
  Mail,
  Lock,
  Eye,
  EyeOff,
  Download,
  Trash2,
  Save,
  X,
  Heart,
  Pill,
  AlertTriangle,
  Plus,
  Edit3
} from 'lucide-react'
import { useTheme } from '../contexts/ThemeContext'
import { useAuth } from '../contexts/AuthContext'
import toast from 'react-hot-toast'

const Settings = () => {
  const { isDark, toggleTheme } = useTheme()
  const { user } = useAuth()
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    sms: false,
    reminders: true,
    updates: false,
    marketing: false
  })
  const [privacy, setPrivacy] = useState({
    profileVisibility: 'public',
    dataSharing: false,
    analytics: true,
    location: false
  })
  const [showPassword, setShowPassword] = useState(false)
  const [passwordData, setPasswordData] = useState({
    current: '',
    new: '',
    confirm: ''
  })
  const [medicalProfile, setMedicalProfile] = useState({
    conditions: [],
    medications: [],
    allergies: []
  })
  const [isLoadingMedical, setIsLoadingMedical] = useState(false)
  const [showAddModal, setShowAddModal] = useState(false)
  const [newItem, setNewItem] = useState({ type: '', name: '' })

  const handleNotificationChange = (key) => {
    setNotifications(prev => ({
      ...prev,
      [key]: !prev[key]
    }))
    toast.success(`${key.charAt(0).toUpperCase() + key.slice(1)} notifications ${!notifications[key] ? 'enabled' : 'disabled'}`)
  }

  const handlePrivacyChange = (key, value) => {
    setPrivacy(prev => ({
      ...prev,
      [key]: value
    }))
    toast.success('Privacy settings updated')
  }

  const handlePasswordChange = () => {
    if (passwordData.new !== passwordData.confirm) {
      toast.error('New passwords do not match')
      return
    }
    if (passwordData.new.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }
    toast.success('Password updated successfully')
    setPasswordData({ current: '', new: '', confirm: '' })
  }

  const exportData = () => {
    toast.success('Data export started. You will receive an email shortly.')
  }

  const deleteAccount = () => {
    if (window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      toast.success('Account deletion request submitted')
    }
  }

  // Medical Profile Functions
  const loadMedicalProfile = async () => {
    setIsLoadingMedical(true)
    try {
      const response = await fetch('http://localhost:5000/chat/medical-profile', {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        setMedicalProfile(data)
      }
    } catch (error) {
      console.error('Failed to load medical profile:', error)
      toast.error('Failed to load medical profile')
    } finally {
      setIsLoadingMedical(false)
    }
  }

  const deleteMedicalItem = async (type, name) => {
    if (!window.confirm(`Are you sure you want to remove ${name} from your ${type}?`)) {
      return
    }

    try {
      const response = await fetch(`http://localhost:5000/chat/medical-profile/${type}/${encodeURIComponent(name)}`, {
        method: 'DELETE',
        credentials: 'include'
      })
      
      if (response.ok) {
        toast.success(`${name} removed from ${type}`)
        loadMedicalProfile() // Reload the profile
      } else {
        toast.error('Failed to remove item')
      }
    } catch (error) {
      console.error('Failed to delete medical item:', error)
      toast.error('Failed to remove item')
    }
  }

  const clearMedicalProfile = async () => {
    if (!window.confirm('Are you sure you want to clear all your medical information? This action cannot be undone.')) {
      return
    }

    try {
      const response = await fetch('http://localhost:5000/chat/medical-profile/clear', {
        method: 'DELETE',
        credentials: 'include'
      })
      
      if (response.ok) {
        toast.success('Medical profile cleared')
        setMedicalProfile({ conditions: [], medications: [], allergies: [] })
      } else {
        toast.error('Failed to clear medical profile')
      }
    } catch (error) {
      console.error('Failed to clear medical profile:', error)
      toast.error('Failed to clear medical profile')
    }
  }

  const addMedicalItem = async () => {
    if (!newItem.name.trim()) {
      toast.error('Please enter a name')
      return
    }

    try {
      // For now, we'll just add to local state
      // In a real implementation, you'd send this to the backend
      const item = {
        name: newItem.name.trim(),
        mentioned_date: new Date().toISOString(),
        source: 'manual'
      }

      setMedicalProfile(prev => ({
        ...prev,
        [newItem.type]: [...prev[newItem.type], item]
      }))

      setNewItem({ type: '', name: '' })
      setShowAddModal(false)
      toast.success(`${newItem.name} added to ${newItem.type}`)
    } catch (error) {
      console.error('Failed to add medical item:', error)
      toast.error('Failed to add item')
    }
  }

  // Load medical profile on component mount
  React.useEffect(() => {
    loadMedicalProfile()
  }, [])

  const settingsSections = [
    {
      title: "Appearance",
      icon: isDark ? Moon : Sun,
      items: [
        {
          title: "Dark Mode",
          description: "Switch between light and dark themes",
          type: "toggle",
          value: isDark,
          onChange: toggleTheme
        }
      ]
    },
    {
      title: "Notifications",
      icon: Bell,
      items: [
        {
          title: "Email Notifications",
          description: "Receive updates via email",
          type: "toggle",
          value: notifications.email,
          onChange: () => handleNotificationChange('email')
        },
        {
          title: "Push Notifications",
          description: "Receive push notifications on your device",
          type: "toggle",
          value: notifications.push,
          onChange: () => handleNotificationChange('push')
        },
        {
          title: "SMS Notifications",
          description: "Receive updates via SMS",
          type: "toggle",
          value: notifications.sms,
          onChange: () => handleNotificationChange('sms')
        },
        {
          title: "Health Reminders",
          description: "Get reminded about medications and appointments",
          type: "toggle",
          value: notifications.reminders,
          onChange: () => handleNotificationChange('reminders')
        },
        {
          title: "App Updates",
          description: "Receive notifications about app updates",
          type: "toggle",
          value: notifications.updates,
          onChange: () => handleNotificationChange('updates')
        },
        {
          title: "Marketing Communications",
          description: "Receive promotional emails and offers",
          type: "toggle",
          value: notifications.marketing,
          onChange: () => handleNotificationChange('marketing')
        }
      ]
    },
    {
      title: "Medical Profile",
      icon: Heart,
      items: [
        {
          title: "Manage Medical Information",
          description: "View and manage your tracked medical conditions, medications, and allergies",
          type: "medical_profile",
          value: medicalProfile
        }
      ]
    },
    {
      title: "Privacy & Security",
      icon: Shield,
      items: [
        {
          title: "Profile Visibility",
          description: "Control who can see your profile",
          type: "select",
          value: privacy.profileVisibility,
          onChange: (value) => handlePrivacyChange('profileVisibility', value),
          options: [
            { value: 'public', label: 'Public' },
            { value: 'friends', label: 'Friends Only' },
            { value: 'private', label: 'Private' }
          ]
        },
        {
          title: "Data Sharing",
          description: "Allow sharing of anonymized health data for research",
          type: "toggle",
          value: privacy.dataSharing,
          onChange: () => handlePrivacyChange('dataSharing', !privacy.dataSharing)
        },
        {
          title: "Analytics",
          description: "Help improve the app by sharing usage analytics",
          type: "toggle",
          value: privacy.analytics,
          onChange: () => handlePrivacyChange('analytics', !privacy.analytics)
        },
        {
          title: "Location Services",
          description: "Allow location access for nearby healthcare services",
          type: "toggle",
          value: privacy.location,
          onChange: () => handlePrivacyChange('location', !privacy.location)
        }
      ]
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-healthcare-500 to-primary-500 rounded-2xl p-6 text-white"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2">Settings</h1>
            <p className="text-white/80">
              Manage your account preferences and privacy
            </p>
          </div>
          <div className="hidden md:block">
                           <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
                 <SettingsIcon className="w-8 h-8" />
               </div>
          </div>
        </div>
      </motion.div>

      {/* Account Information */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700"
      >
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
            <User className="w-5 h-5 mr-2" />
            Account Information
          </h3>
        </div>
        <div className="p-6">
          <div className="flex items-center space-x-4 mb-6">
            <img
              src={user?.avatar}
              alt={user?.name}
              className="w-16 h-16 rounded-full"
            />
            <div>
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white">
                {user?.name}
              </h4>
              <p className="text-gray-600 dark:text-gray-400">{user?.email}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Member since {new Date(user?.createdAt).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Settings Sections */}
      {settingsSections.map((section, sectionIndex) => (
        <motion.div
          key={section.title}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 + sectionIndex * 0.1 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700"
        >
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
              <section.icon className="w-5 h-5 mr-2" />
              {section.title}
            </h3>
          </div>
          <div className="p-6 space-y-6">
            {section.items.map((item, itemIndex) => (
              <div key={itemIndex} className="flex items-center justify-between">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900 dark:text-white">
                    {item.title}
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {item.description}
                  </p>
                </div>
                <div className="ml-4">
                  {item.type === 'toggle' && (
                    <button
                      onClick={item.onChange}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        item.value
                          ? 'bg-primary-500'
                          : 'bg-gray-200 dark:bg-gray-700'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          item.value ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  )}
                  {item.type === 'select' && (
                    <select
                      value={item.value}
                      onChange={(e) => item.onChange(e.target.value)}
                      className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      {item.options.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  )}
                  {item.type === 'medical_profile' && (
                    <button
                      onClick={() => setShowAddModal(true)}
                      className="flex items-center space-x-2 px-4 py-2 bg-primary-100 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400 rounded-lg hover:bg-primary-200 dark:hover:bg-primary-900/40 transition-colors"
                    >
                      <Edit3 className="w-4 h-4" />
                      <span>Manage</span>
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      ))}

      {/* Password Change */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700"
      >
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
            <Lock className="w-5 h-5 mr-2" />
            Change Password
          </h3>
        </div>
        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Current Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={passwordData.current}
                onChange={(e) => setPasswordData(prev => ({ ...prev, current: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="Enter current password"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              New Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={passwordData.new}
                onChange={(e) => setPasswordData(prev => ({ ...prev, new: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="Enter new password"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Confirm New Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={passwordData.confirm}
                onChange={(e) => setPasswordData(prev => ({ ...prev, confirm: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="Confirm new password"
              />
              <button
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>
          <div className="flex justify-end">
            <button
              onClick={handlePasswordChange}
              className="bg-gradient-to-r from-healthcare-500 to-primary-500 text-white px-6 py-3 rounded-lg hover:shadow-lg transition-all duration-300 hover:scale-105"
            >
              Update Password
            </button>
          </div>
        </div>
      </motion.div>

      {/* Data Management */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700"
      >
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Data Management
          </h3>
        </div>
        <div className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white">
                Export Data
              </h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Download a copy of your health data
              </p>
            </div>
            <button
              onClick={exportData}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-100 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/40 transition-colors"
            >
              <Download className="w-4 h-4" />
              <span>Export</span>
            </button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white">
                Delete Account
              </h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Permanently delete your account and all data
              </p>
            </div>
            <button
              onClick={deleteAccount}
              className="flex items-center space-x-2 px-4 py-2 bg-red-100 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-200 dark:hover:bg-red-900/40 transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              <span>Delete</span>
            </button>
          </div>
        </div>
      </motion.div>

      {/* Medical Profile Modal */}
      {showAddModal && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
          onClick={() => setShowAddModal(false)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-4xl h-[80vh] flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-healthcare-500 to-primary-500 rounded-t-2xl">
              <div>
                <h3 className="text-xl font-semibold text-white">Medical Profile Management</h3>
                <p className="text-sm text-white/80">Manage your tracked medical information</p>
              </div>
              <button
                onClick={() => setShowAddModal(false)}
                className="p-2 text-white/80 hover:text-white hover:bg-white/20 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {/* Add New Item */}
              <div className="mb-8 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Add New Item</h4>
                <div className="flex space-x-4">
                  <select
                    value={newItem.type}
                    onChange={(e) => setNewItem(prev => ({ ...prev, type: e.target.value }))}
                    className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value="">Select type...</option>
                    <option value="conditions">Medical Condition</option>
                    <option value="medications">Medication</option>
                    <option value="allergies">Allergy</option>
                  </select>
                  <input
                    type="text"
                    value={newItem.name}
                    onChange={(e) => setNewItem(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Enter name..."
                    className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                  <button
                    onClick={addMedicalItem}
                    disabled={!newItem.type || !newItem.name.trim()}
                    className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Medical Conditions */}
              <div className="mb-6">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                    <Heart className="w-5 h-5 mr-2 text-red-500" />
                    Medical Conditions ({medicalProfile.conditions.length})
                  </h4>
                </div>
                <div className="space-y-2">
                  {medicalProfile.conditions.length > 0 ? (
                    medicalProfile.conditions.map((condition, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg">
                        <div>
                          <span className="font-medium text-gray-900 dark:text-white">{condition.name}</span>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            Added: {new Date(condition.mentioned_date).toLocaleDateString()}
                          </p>
                        </div>
                        <button
                          onClick={() => deleteMedicalItem('condition', condition.name)}
                          className="p-2 text-red-500 hover:bg-red-100 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500 dark:text-gray-400 text-center py-4">No medical conditions tracked</p>
                  )}
                </div>
              </div>

              {/* Medications */}
              <div className="mb-6">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                    <Pill className="w-5 h-5 mr-2 text-blue-500" />
                    Medications ({medicalProfile.medications.length})
                  </h4>
                </div>
                <div className="space-y-2">
                  {medicalProfile.medications.length > 0 ? (
                    medicalProfile.medications.map((medication, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg">
                        <div>
                          <span className="font-medium text-gray-900 dark:text-white">{medication.name}</span>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            Added: {new Date(medication.mentioned_date).toLocaleDateString()}
                          </p>
                        </div>
                        <button
                          onClick={() => deleteMedicalItem('medication', medication.name)}
                          className="p-2 text-red-500 hover:bg-red-100 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500 dark:text-gray-400 text-center py-4">No medications tracked</p>
                  )}
                </div>
              </div>

              {/* Allergies */}
              <div className="mb-6">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                    <AlertTriangle className="w-5 h-5 mr-2 text-yellow-500" />
                    Allergies ({medicalProfile.allergies.length})
                  </h4>
                </div>
                <div className="space-y-2">
                  {medicalProfile.allergies.length > 0 ? (
                    medicalProfile.allergies.map((allergy, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg">
                        <div>
                          <span className="font-medium text-gray-900 dark:text-white">{allergy.name}</span>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            Added: {new Date(allergy.mentioned_date).toLocaleDateString()}
                          </p>
                        </div>
                        <button
                          onClick={() => deleteMedicalItem('allergy', allergy.name)}
                          className="p-2 text-red-500 hover:bg-red-100 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500 dark:text-gray-400 text-center py-4">No allergies tracked</p>
                  )}
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-between">
              <button
                onClick={clearMedicalProfile}
                className="px-4 py-2 bg-red-100 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-200 dark:hover:bg-red-900/40 transition-colors"
              >
                Clear All Data
              </button>
              <button
                onClick={() => setShowAddModal(false)}
                className="px-6 py-2 bg-gradient-to-r from-healthcare-500 to-primary-500 text-white rounded-lg hover:shadow-lg transition-all duration-300"
              >
                Done
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  )
}

export default Settings 