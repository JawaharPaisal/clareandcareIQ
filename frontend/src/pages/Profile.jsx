import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  User, 
  Mail, 
  Phone, 
  Calendar, 
  MapPin, 
  Edit, 
  Save, 
  X,
  Heart,
  Activity,
  Shield,
  Award,
  Camera,
  Upload
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import toast from 'react-hot-toast'

const Profile = () => {
  const { user, updateProfile } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [profileImage, setProfileImage] = useState(user?.avatar || '')
  const [isUploading, setIsUploading] = useState(false)
  const [errors, setErrors] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  // Helper function to convert medical data arrays to strings
  const formatMedicalData = (data) => {
    if (!data) return ''
    if (typeof data === 'string') return data
    if (Array.isArray(data)) {
      return data.map(item => typeof item === 'object' ? item.name : item).join(', ')
    }
    return ''
  }

  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    dateOfBirth: user?.dateOfBirth || '',
    address: user?.address || '',
    emergencyContact: user?.emergencyContact || '',
    bloodType: user?.bloodType || '',
    allergies: formatMedicalData(user?.allergies),
    medications: formatMedicalData(user?.medications),
    conditions: formatMedicalData(user?.medicalConditions)
  })

  const healthStats = [
    {
      title: "Health Score",
      value: "85%",
      icon: Heart,
      color: "from-red-500 to-pink-500",
      description: "Excellent"
    },
    {
      title: "Active Days",
      value: "28",
      icon: Activity,
      color: "from-green-500 to-emerald-500",
      description: "This month"
    },
    {
      title: "Insurance",
      value: "Active",
      icon: Shield,
      color: "from-blue-500 to-cyan-500",
      description: "Premium Plan"
    },
    {
      title: "Achievements",
      value: "12",
      icon: Award,
      color: "from-purple-500 to-violet-500",
      description: "Badges earned"
    }
  ]

  const handleSave = async () => {
    // Validate all fields before saving
    const allFieldsValid = Object.keys(formData).every(field => {
      if (field === 'email') return true // Email is read-only, skip validation
      return validateField(field, formData[field])
    })
    
    if (!allFieldsValid) {
      toast.error('Please fix the validation errors before saving')
      return
    }
    
    setIsSubmitting(true)
    try {
      const success = await updateProfile(formData)
      if (success) {
        setIsEditing(false)
        setErrors({}) // Clear errors on successful save
      }
    } catch (error) {
      console.error('Save error:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCancel = () => {
    setFormData({
      name: user?.name || '',
      email: user?.email || '',
      phone: user?.phone || '',
      dateOfBirth: user?.dateOfBirth || '',
      address: user?.address || '',
      emergencyContact: user?.emergencyContact || '',
      bloodType: user?.bloodType || '',
      allergies: formatMedicalData(user?.allergies),
      medications: formatMedicalData(user?.medications),
      conditions: formatMedicalData(user?.medicalConditions)
    })
    setErrors({}) // Clear all errors
    setIsEditing(false)
  }

  // Validation functions
  const validateField = (field, value) => {
    const newErrors = { ...errors }
    
    switch (field) {
      case 'name':
        if (!value.trim()) {
          newErrors.name = 'Name is required'
        } else if (value.trim().length < 2) {
          newErrors.name = 'Name must be at least 2 characters'
        } else if (value.trim().length > 50) {
          newErrors.name = 'Name must be less than 50 characters'
        } else {
          delete newErrors.name
        }
        break
        
      case 'phone':
        if (value && !/^[\+]?[1-9][\d]{0,15}$/.test(value.replace(/[\s\-\(\)]/g, ''))) {
          newErrors.phone = 'Please enter a valid phone number'
        } else {
          delete newErrors.phone
        }
        break
        
      case 'dateOfBirth':
        if (value) {
          const birthDate = new Date(value)
          const today = new Date()
          const age = today.getFullYear() - birthDate.getFullYear()
          
          if (birthDate > today) {
            newErrors.dateOfBirth = 'Date of birth cannot be in the future'
          } else if (age > 120) {
            newErrors.dateOfBirth = 'Please enter a valid date of birth'
          } else if (age < 0) {
            newErrors.dateOfBirth = 'Date of birth cannot be in the future'
          } else {
            delete newErrors.dateOfBirth
          }
        } else {
          delete newErrors.dateOfBirth
        }
        break
        
      case 'address':
        if (value && value.length > 200) {
          newErrors.address = 'Address must be less than 200 characters'
        } else {
          delete newErrors.address
        }
        break
        
      case 'emergencyContact':
        if (value && value.length > 100) {
          newErrors.emergencyContact = 'Emergency contact must be less than 100 characters'
        } else {
          delete newErrors.emergencyContact
        }
        break
        
      case 'allergies':
        if (value && value.length > 500) {
          newErrors.allergies = 'Allergies must be less than 500 characters'
        } else {
          delete newErrors.allergies
        }
        break
        
      case 'medications':
        if (value && value.length > 500) {
          newErrors.medications = 'Medications must be less than 500 characters'
        } else {
          delete newErrors.medications
        }
        break
        
      case 'conditions':
        if (value && value.length > 500) {
          newErrors.conditions = 'Medical conditions must be less than 500 characters'
        } else {
          delete newErrors.conditions
        }
        break
        
      default:
        break
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
    
    // Real-time validation
    validateField(field, value)
  }

  const handleImageUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast.error('Please select a valid image file')
      return
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Image size should be less than 5MB')
      return
    }

    setIsUploading(true)
    
    try {
      const formData = new FormData()
      formData.append('profileImage', file)

      const response = await fetch('http://localhost:5000/profile/upload-image', {
        method: 'POST',
        credentials: 'include',
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        setProfileImage(data.imageUrl)
        toast.success('Profile image updated successfully!')
      } else {
        throw new Error('Upload failed')
      }
    } catch (error) {
      console.error('Image upload error:', error)
      toast.error('Failed to upload image. Please try again.')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-healthcare-500 to-primary-500 rounded-2xl p-6 text-white"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center overflow-hidden">
                {profileImage ? (
                  <img 
                    src={profileImage} 
                    alt="Profile" 
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <User className="w-10 h-10" />
                )}
              </div>
              {isEditing && (
                <label className="absolute -bottom-1 -right-1 bg-white rounded-full p-2 cursor-pointer hover:bg-gray-100 transition-colors">
                  <Camera className="w-4 h-4 text-gray-600" />
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                    disabled={isUploading}
                  />
                </label>
              )}
            </div>
            <div>
              <h1 className="text-2xl font-bold">{user?.name || 'New User'}</h1>
              <p className="text-white/80">Patient Profile</p>
              {isUploading && (
                <p className="text-white/60 text-sm">Uploading image...</p>
              )}
            </div>
          </div>
          <button
            onClick={() => setIsEditing(!isEditing)}
            className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
          >
            {isEditing ? <X className="w-4 h-4" /> : <Edit className="w-4 h-4" />}
            <span>{isEditing ? 'Cancel' : 'Edit Profile'}</span>
          </button>
        </div>
      </motion.div>

      {/* Health Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {healthStats.map((stat, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700 card-hover"
          >
            <div className={`w-12 h-12 bg-gradient-to-r ${stat.color} rounded-lg flex items-center justify-center mb-4`}>
              <stat.icon className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-gray-600 dark:text-gray-400 text-sm font-medium">
                {stat.title}
              </p>
              <div className="flex items-baseline space-x-1">
                <span className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stat.value}
                </span>
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {stat.description}
              </p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* New User Message */}
      {(!user?.phone && !user?.dateOfBirth && !user?.address) && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4"
        >
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-100 dark:bg-blue-800 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h4 className="text-blue-900 dark:text-blue-100 font-medium">Complete Your Profile</h4>
              <p className="text-blue-700 dark:text-blue-300 text-sm">
                Add your personal and medical information to get the most out of Clare & CareIQ. Click "Edit Profile" to get started.
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Profile Information */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Personal Information */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700"
        >
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Personal Information
            </h3>
          </div>
          <div className="p-6 space-y-4">
            <div className="flex items-center space-x-3">
              <User className="w-5 h-5 text-gray-400" />
              <div className="flex-1">
                <label className="text-sm text-gray-500 dark:text-gray-400">Full Name</label>
                {isEditing ? (
                  <div>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      className={`w-full mt-1 px-3 py-2 border rounded-lg focus:ring-2 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                        errors.name 
                          ? 'border-red-500 focus:ring-red-500' 
                          : 'border-gray-300 dark:border-gray-600 focus:ring-primary-500'
                      }`}
                      placeholder="Enter your full name"
                    />
                    {errors.name && (
                      <p className="text-red-500 text-xs mt-1">{errors.name}</p>
                    )}
                  </div>
                ) : (
                  <p className="text-gray-900 dark:text-white font-medium">{formData.name}</p>
                )}
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <Mail className="w-5 h-5 text-gray-400" />
              <div className="flex-1">
                <label className="text-sm text-gray-500 dark:text-gray-400">Email</label>
                <div className="relative">
                  <input
                    type="email"
                    value={formData.email}
                    readOnly
                    className="w-full mt-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-100 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed"
                  />
                  <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                    <span className="text-xs text-gray-400 bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">
                      Read Only
                    </span>
                  </div>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Email cannot be changed. Contact support if needed.
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <Phone className="w-5 h-5 text-gray-400" />
              <div className="flex-1">
                <label className="text-sm text-gray-500 dark:text-gray-400">Phone</label>
                {isEditing ? (
                  <div>
                    <input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => handleInputChange('phone', e.target.value)}
                      className={`w-full mt-1 px-3 py-2 border rounded-lg focus:ring-2 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                        errors.phone 
                          ? 'border-red-500 focus:ring-red-500' 
                          : 'border-gray-300 dark:border-gray-600 focus:ring-primary-500'
                      }`}
                      placeholder="e.g., +1 (555) 123-4567"
                    />
                    {errors.phone && (
                      <p className="text-red-500 text-xs mt-1">{errors.phone}</p>
                    )}
                  </div>
                ) : (
                  <p className="text-gray-900 dark:text-white font-medium">
                    {formData.phone || <span className="text-gray-400 italic">Not provided</span>}
                  </p>
                )}
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <Calendar className="w-5 h-5 text-gray-400" />
              <div className="flex-1">
                <label className="text-sm text-gray-500 dark:text-gray-400">Date of Birth</label>
                {isEditing ? (
                  <div>
                    <input
                      type="date"
                      value={formData.dateOfBirth}
                      onChange={(e) => handleInputChange('dateOfBirth', e.target.value)}
                      className={`w-full mt-1 px-3 py-2 border rounded-lg focus:ring-2 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                        errors.dateOfBirth 
                          ? 'border-red-500 focus:ring-red-500' 
                          : 'border-gray-300 dark:border-gray-600 focus:ring-primary-500'
                      }`}
                    />
                    {errors.dateOfBirth && (
                      <p className="text-red-500 text-xs mt-1">{errors.dateOfBirth}</p>
                    )}
                  </div>
                ) : (
                  <p className="text-gray-900 dark:text-white font-medium">
                    {formData.dateOfBirth || <span className="text-gray-400 italic">Not provided</span>}
                  </p>
                )}
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <MapPin className="w-5 h-5 text-gray-400" />
              <div className="flex-1">
                <label className="text-sm text-gray-500 dark:text-gray-400">Address</label>
                {isEditing ? (
                  <div>
                    <textarea
                      value={formData.address}
                      onChange={(e) => handleInputChange('address', e.target.value)}
                      rows={2}
                      className={`w-full mt-1 px-3 py-2 border rounded-lg focus:ring-2 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                        errors.address 
                          ? 'border-red-500 focus:ring-red-500' 
                          : 'border-gray-300 dark:border-gray-600 focus:ring-primary-500'
                      }`}
                      placeholder="Enter your full address"
                    />
                    {errors.address && (
                      <p className="text-red-500 text-xs mt-1">{errors.address}</p>
                    )}
                  </div>
                ) : (
                  <p className="text-gray-900 dark:text-white font-medium">
                    {formData.address || <span className="text-gray-400 italic">Not provided</span>}
                  </p>
                )}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Medical Information */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700"
        >
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Medical Information
            </h3>
          </div>
          <div className="p-6 space-y-4">
            <div>
              <label className="text-sm text-gray-500 dark:text-gray-400">Emergency Contact</label>
              {isEditing ? (
                <div>
                  <input
                    type="text"
                    value={formData.emergencyContact}
                    onChange={(e) => handleInputChange('emergencyContact', e.target.value)}
                    className={`w-full mt-1 px-3 py-2 border rounded-lg focus:ring-2 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                      errors.emergencyContact 
                        ? 'border-red-500 focus:ring-red-500' 
                        : 'border-gray-300 dark:border-gray-600 focus:ring-primary-500'
                    }`}
                    placeholder="Name and phone number"
                  />
                  {errors.emergencyContact && (
                    <p className="text-red-500 text-xs mt-1">{errors.emergencyContact}</p>
                  )}
                </div>
              ) : (
                <p className="text-gray-900 dark:text-white font-medium">
                  {formData.emergencyContact || <span className="text-gray-400 italic">Not provided</span>}
                </p>
              )}
            </div>

            <div>
              <label className="text-sm text-gray-500 dark:text-gray-400">Blood Type</label>
              {isEditing ? (
                <select
                  value={formData.bloodType}
                  onChange={(e) => handleInputChange('bloodType', e.target.value)}
                  className="w-full mt-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="A+">A+</option>
                  <option value="A-">A-</option>
                  <option value="B+">B+</option>
                  <option value="B-">B-</option>
                  <option value="AB+">AB+</option>
                  <option value="AB-">AB-</option>
                  <option value="O+">O+</option>
                  <option value="O-">O-</option>
                </select>
              ) : (
                <p className="text-gray-900 dark:text-white font-medium">
                  {formData.bloodType || <span className="text-gray-400 italic">Not provided</span>}
                </p>
              )}
            </div>

            <div>
              <label className="text-sm text-gray-500 dark:text-gray-400">Allergies</label>
              {isEditing ? (
                <div>
                  <textarea
                    value={formData.allergies}
                    onChange={(e) => handleInputChange('allergies', e.target.value)}
                    rows={2}
                    className={`w-full mt-1 px-3 py-2 border rounded-lg focus:ring-2 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                      errors.allergies 
                        ? 'border-red-500 focus:ring-red-500' 
                        : 'border-gray-300 dark:border-gray-600 focus:ring-primary-500'
                    }`}
                    placeholder="List any known allergies"
                  />
                  {errors.allergies && (
                    <p className="text-red-500 text-xs mt-1">{errors.allergies}</p>
                  )}
                </div>
              ) : (
                <p className="text-gray-900 dark:text-white font-medium">
                  {formData.allergies || <span className="text-gray-400 italic">Not provided</span>}
                </p>
              )}
            </div>

            <div>
              <label className="text-sm text-gray-500 dark:text-gray-400">Current Medications</label>
              {isEditing ? (
                <div>
                  <textarea
                    value={formData.medications}
                    onChange={(e) => handleInputChange('medications', e.target.value)}
                    rows={2}
                    className={`w-full mt-1 px-3 py-2 border rounded-lg focus:ring-2 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                      errors.medications 
                        ? 'border-red-500 focus:ring-red-500' 
                        : 'border-gray-300 dark:border-gray-600 focus:ring-primary-500'
                    }`}
                    placeholder="List current medications and dosages"
                  />
                  {errors.medications && (
                    <p className="text-red-500 text-xs mt-1">{errors.medications}</p>
                  )}
                </div>
              ) : (
                <p className="text-gray-900 dark:text-white font-medium">
                  {formData.medications || <span className="text-gray-400 italic">Not provided</span>}
                </p>
              )}
            </div>

            <div>
              <label className="text-sm text-gray-500 dark:text-gray-400">Medical Conditions</label>
              {isEditing ? (
                <div>
                  <textarea
                    value={formData.conditions}
                    onChange={(e) => handleInputChange('conditions', e.target.value)}
                    rows={2}
                    className={`w-full mt-1 px-3 py-2 border rounded-lg focus:ring-2 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                      errors.conditions 
                        ? 'border-red-500 focus:ring-red-500' 
                        : 'border-gray-300 dark:border-gray-600 focus:ring-primary-500'
                    }`}
                    placeholder="List any medical conditions"
                  />
                  {errors.conditions && (
                    <p className="text-red-500 text-xs mt-1">{errors.conditions}</p>
                  )}
                </div>
              ) : (
                <p className="text-gray-900 dark:text-white font-medium">
                  {formData.conditions || <span className="text-gray-400 italic">Not provided</span>}
                </p>
              )}
            </div>
          </div>
        </motion.div>
      </div>

      {/* Save/Cancel Buttons */}
      {isEditing && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-end space-x-4"
        >
          <button
            onClick={handleCancel}
            className="px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={isSubmitting || Object.keys(errors).length > 0}
            className={`px-6 py-3 rounded-lg transition-all duration-300 ${
              isSubmitting || Object.keys(errors).length > 0
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-healthcare-500 to-primary-500 hover:shadow-lg hover:scale-105'
            } text-white`}
          >
            {isSubmitting ? 'Saving...' : 'Save Changes'}
          </button>
        </motion.div>
      )}
    </div>
  )
}

export default Profile 