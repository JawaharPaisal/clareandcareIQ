import React, { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { useChat } from '../contexts/ChatContext'
import { 
  FileText, 
  Upload, 
  Download, 
  Eye, 
  Search, 
  Filter,
  Calendar,
  AlertCircle,
  CheckCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  Brain,
  Heart,
  Activity,
  X,
  Loader,
  MessageCircle
} from 'lucide-react'

const Reports = () => {
  const { openChat } = useChat()
  const [selectedReport, setSelectedReport] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [reportName, setReportName] = useState('')
  const [reportType, setReportType] = useState('general')
  const fileInputRef = useRef(null)

  // Fetch reports from backend
  useEffect(() => {
    fetchReports()
  }, [])

  const fetchReports = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:5000/reports', {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setReports(data.reports || [])
      } else {
        toast.error('Failed to load reports')
      }
    } catch (error) {
      console.error('Error fetching reports:', error)
      toast.error('Failed to connect to server')
    } finally {
      setLoading(false)
    }
  }

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      // Validate file type
      const allowedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg']
      if (!allowedTypes.includes(file.type)) {
        toast.error('Only PDF, PNG, and JPG files are supported')
        return
      }

      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        toast.error('File size must be less than 10MB')
        return
      }

      setSelectedFile(file)
      // Auto-populate report name from filename (remove extension)
      const nameWithoutExt = file.name.replace(/\.[^/.]+$/, "")
      setReportName(nameWithoutExt)
      setShowUploadModal(true)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile || !reportName.trim()) {
      toast.error('Please provide a file and report name')
      return
    }

    setUploading(true)
    
    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('reportName', reportName.trim())
      formData.append('reportType', reportType)

      const response = await fetch('http://localhost:5000/reports', {
        method: 'POST',
        credentials: 'include',
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        toast.success(`${reportName} analyzed successfully!`)
        setShowUploadModal(false)
        setSelectedFile(null)
        setReportName('')
        setReportType('general')
        fetchReports() // Refresh list
        
        // Show AI insights
        if (data.aiSummary) {
          setTimeout(() => {
            toast.success(`AI Analysis: ${data.aiSummary.substring(0, 100)}...`, { duration: 5000 })
          }, 1000)
        }
      } else {
        const error = await response.json()
        toast.error(error.error || 'Upload failed')
      }
    } catch (error) {
      console.error('Upload error:', error)
      toast.error('Upload failed: ' + error.message)
    } finally {
      setUploading(false)
    }
  }

  const closeUploadModal = () => {
    setShowUploadModal(false)
    setSelectedFile(null)
    setReportName('')
    setReportType('general')
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'normal':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'abnormal':
        return <AlertCircle className="w-5 h-5 text-orange-500" />
      case 'pending':
        return <Clock className="w-5 h-5 text-blue-500" />
      default:
        return <CheckCircle className="w-5 h-5 text-gray-500" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'normal':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
      case 'abnormal':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400'
      case 'pending':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'
    }
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'lab':
        return <Activity className="w-5 h-5" />
      case 'cardiology':
        return <Heart className="w-5 h-5" />
      case 'radiology':
        return <Brain className="w-5 h-5" />
      default:
        return <FileText className="w-5 h-5" />
    }
  }

  const filteredReports = reports.filter(report => {
    const matchesSearch = 
      report.reportName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.fileName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.aiSummary?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesFilter = filterType === 'all' || report.reportType === filterType
    return matchesSearch && matchesFilter
  })

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
            <h1 className="text-2xl font-bold mb-2">Medical Reports</h1>
            <p className="text-white/80">
              View and analyze your medical reports with AI insights
            </p>
          </div>
                     <div className="hidden md:flex items-center space-x-4">
             <button
               onClick={openChat}
               className="p-3 rounded-full bg-white/20 hover:bg-white/30 transition-colors"
               title="Chat with Clare"
             >
               <MessageCircle className="w-6 h-6" />
             </button>
             <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
               <FileText className="w-8 h-8" />
             </div>
           </div>
        </div>
      </motion.div>

      {/* Upload Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700"
      >
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-healthcare-500 to-primary-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <Upload className="w-8 h-8 text-white" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Upload New Report
          </h3>
          <p className="text-gray-600 dark:text-gray-300 mb-4">
            Upload medical reports (PDF, PNG, JPG) for AI-powered analysis
          </p>
          <input
            type="file"
            ref={fileInputRef}
            accept=".pdf,.jpg,.jpeg,.png"
            onChange={handleFileSelect}
            className="hidden"
          />
          <button 
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="bg-gradient-to-r from-healthcare-500 to-primary-500 text-white px-6 py-3 rounded-lg hover:shadow-lg transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? 'Uploading...' : 'Select Report'}
          </button>
        </div>
      </motion.div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-md shadow-2xl"
          >
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                Upload Medical Report
              </h3>
              <button
                onClick={closeUploadModal}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              {/* File Info */}
              <div className="p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  <strong>File:</strong> {selectedFile?.name}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                  <strong>Size:</strong> {(selectedFile?.size / 1024).toFixed(2)} KB
                </p>
              </div>

              {/* Report Name Input */}
              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  Report Name *
                </label>
                <input
                  type="text"
                  value={reportName}
                  onChange={(e) => setReportName(e.target.value)}
                  placeholder="e.g., Blood Test - January 2025"
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  required
                />
              </div>

              {/* Report Type Select */}
              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                  Report Type
                </label>
                <select
                  value={reportType}
                  onChange={(e) => setReportType(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="general">General Medical Document</option>
                  <option value="prescription">Prescription</option>
                  <option value="lab_report">Laboratory Report</option>
                  <option value="xray">X-Ray</option>
                  <option value="ct_scan">CT Scan</option>
                  <option value="mri">MRI</option>
                  <option value="ultrasound">Ultrasound</option>
                </select>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-4">
                <button
                  onClick={handleUpload}
                  disabled={uploading || !reportName.trim()}
                  className="flex-1 bg-gradient-to-r from-healthcare-500 to-primary-500 text-white px-6 py-3 rounded-lg font-medium hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {uploading ? (
                    <>
                      <Loader className="w-5 h-5 animate-spin" />
                      <span>Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <Upload className="w-5 h-5" />
                      <span>Upload & Analyze</span>
                    </>
                  )}
                </button>
                <button
                  onClick={closeUploadModal}
                  disabled={uploading}
                  className="px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* Search and Filter */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700"
      >
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search reports..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">All Types</option>
              <option value="general">General</option>
              <option value="prescription">Prescription</option>
              <option value="lab_report">Lab Report</option>
              <option value="xray">X-Ray</option>
              <option value="ct_scan">CT Scan</option>
              <option value="mri">MRI</option>
              <option value="ultrasound">Ultrasound</option>
            </select>
          </div>
        </div>
      </motion.div>

      {/* Reports List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Reports List */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="space-y-4"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Recent Reports ({filteredReports.length})
          </h3>
          
          {loading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader className="w-8 h-8 animate-spin text-primary-500 mb-4" />
              <p className="text-gray-600 dark:text-gray-400">Loading reports...</p>
            </div>
          ) : filteredReports.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 bg-white dark:bg-gray-800 rounded-xl p-6">
              <FileText className="w-16 h-16 text-gray-400 mb-4" />
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                No Reports Yet
              </h4>
              <p className="text-gray-600 dark:text-gray-400 text-center">
                Upload your first medical report to get AI-powered analysis
              </p>
            </div>
          ) : (
            filteredReports.map((report, index) => (
              <motion.div
                key={report._id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 + index * 0.1 }}
                onClick={() => setSelectedReport(report)}
                className={`bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 cursor-pointer transition-all duration-300 hover:shadow-xl hover:scale-105 ${
                  selectedReport?._id === report._id ? 'ring-2 ring-primary-500' : ''
                }`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-r from-healthcare-500 to-primary-500 rounded-lg flex items-center justify-center">
                      {getTypeIcon(report.reportType || 'general')}
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900 dark:text-white">
                        {report.reportName || report.fileName}
                      </h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {report.reportType?.replace('_', ' ').toUpperCase() || 'Medical Document'}
                      </p>
                    </div>
                  </div>
                  {getStatusIcon(report.status || 'completed')}
                </div>
                
                <div className="flex items-center justify-between text-sm mb-2">
                  <div className="flex items-center space-x-2 text-gray-500 dark:text-gray-400">
                    <Calendar className="w-4 h-4" />
                    <span>{new Date(report.createdAt).toLocaleDateString()}</span>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(report.status || 'completed')}`}>
                    {report.status || 'completed'}
                  </span>
                </div>
                
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-2 line-clamp-2">
                  {report.aiSummary || 'AI analysis completed'}
                </p>

                {/* Show extracted info badges */}
                {report.extracted && (
                  <div className="flex flex-wrap gap-2 mt-3">
                    {report.extracted.conditions && Array.isArray(report.extracted.conditions) && report.extracted.conditions.length > 0 && (
                      <span className="px-2 py-1 bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-400 rounded-full text-xs">
                        {report.extracted.conditions.length} condition(s)
                      </span>
                    )}
                    {report.extracted.medications && Array.isArray(report.extracted.medications) && report.extracted.medications.length > 0 && (
                      <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-400 rounded-full text-xs">
                        {report.extracted.medications.length} medication(s)
                      </span>
                    )}
                    {report.extracted.vitals && typeof report.extracted.vitals === 'object' && Object.keys(report.extracted.vitals).length > 0 && (
                      <span className="px-2 py-1 bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-400 rounded-full text-xs">
                        Vitals
                      </span>
                    )}
                    {report.extracted.labs && typeof report.extracted.labs === 'object' && Object.keys(report.extracted.labs).length > 0 && (
                      <span className="px-2 py-1 bg-purple-100 dark:bg-purple-900/20 text-purple-800 dark:text-purple-400 rounded-full text-xs">
                        Lab Values
                      </span>
                    )}
                    {report.extracted.blood_type && (
                      <span className="px-2 py-1 bg-orange-100 dark:bg-orange-900/20 text-orange-800 dark:text-orange-400 rounded-full text-xs">
                        Blood Type: {report.extracted.blood_type}
                      </span>
                    )}
                  </div>
                )}
              </motion.div>
            ))
          )}
        </motion.div>

        {/* Report Details */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700"
        >
          {selectedReport ? (
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                  {selectedReport.reportName || selectedReport.fileName}
                </h3>
                <div className="flex space-x-2">
                  <button
                    onClick={() => openChat()}
                    className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors flex items-center gap-2"
                  >
                    <Brain className="w-4 h-4" />
                    <span>Ask AI</span>
                  </button>
                </div>
              </div>

              <div className="space-y-6">
                {/* Report Info */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Date:</span>
                    <p className="font-medium">{new Date(selectedReport.createdAt).toLocaleDateString()}</p>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">File:</span>
                    <p className="font-medium">{selectedReport.fileName}</p>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Type:</span>
                    <p className="font-medium capitalize">{selectedReport.reportType?.replace('_', ' ')}</p>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Status:</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedReport.status || 'completed')}`}>
                      {selectedReport.status || 'completed'}
                    </span>
                  </div>
                  {selectedReport.modelUsed && (
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Analyzed by:</span>
                      <p className="font-medium">{selectedReport.modelUsed}</p>
                    </div>
                  )}
                </div>

                {/* AI Summary */}
                <div>
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-2 flex items-center">
                    <Brain className="w-5 h-5 mr-2 text-primary-500" />
                    AI Analysis
                  </h4>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">
                    {selectedReport.aiSummary || 'Analysis completed successfully'}
                  </p>
                </div>

                {/* Extracted Conditions */}
                {selectedReport.extracted?.conditions && selectedReport.extracted.conditions.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Medical Conditions Found</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedReport.extracted.conditions.map((condition, index) => (
                        <span key={index} className="px-3 py-1 bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-400 rounded-full text-sm">
                          {typeof condition === 'string' ? condition : condition.name || condition.condition || JSON.stringify(condition)}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Extracted Medications */}
                {selectedReport.extracted?.medications && selectedReport.extracted.medications.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Medications Found</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedReport.extracted.medications.map((med, index) => (
                        <span key={index} className="px-3 py-1 bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-400 rounded-full text-sm">
                          {typeof med === 'string' ? med : med.name || med.medication || JSON.stringify(med)}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Vital Signs */}
                {selectedReport.extracted?.vitals && Object.keys(selectedReport.extracted.vitals).length > 0 && (
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                      <Activity className="w-5 h-5 mr-2 text-green-500" />
                      Vital Signs
                    </h4>
                    <div className="grid grid-cols-2 gap-3">
                      {Object.entries(selectedReport.extracted.vitals).map(([key, value]) => (
                        <div key={key} className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                          <p className="text-xs text-gray-600 dark:text-gray-400 capitalize">{key.replace('_', ' ')}</p>
                          <p className="text-lg font-semibold text-green-800 dark:text-green-400">
                            {typeof value === 'string' || typeof value === 'number' ? value : 
                             value.value || value.measurement || JSON.stringify(value)}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Lab Values */}
                {selectedReport.extracted?.labs && Object.keys(selectedReport.extracted.labs).length > 0 && (
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                      <Activity className="w-5 h-5 mr-2 text-purple-500" />
                      Laboratory Values
                    </h4>
                    <div className="grid grid-cols-2 gap-3">
                      {Object.entries(selectedReport.extracted.labs).map(([key, value]) => (
                        <div key={key} className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                          <p className="text-xs text-gray-600 dark:text-gray-400 capitalize">{key.replace('_', ' ')}</p>
                          <p className="text-lg font-semibold text-purple-800 dark:text-purple-400">
                            {typeof value === 'string' || typeof value === 'number' ? value : 
                             value.value || value.measurement || JSON.stringify(value)}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Blood Type */}
                {selectedReport.extracted?.blood_type && (
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                      <Heart className="w-5 h-5 mr-2 text-red-500" />
                      Blood Type
                    </h4>
                    <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                      <p className="text-2xl font-bold text-red-800 dark:text-red-400">
                        {selectedReport.extracted.blood_type}
                      </p>
                      <p className="text-sm text-red-600 dark:text-red-300 mt-1">
                        Blood type extracted from analysis
                      </p>
                    </div>
                  </div>
                )}

                {/* Tags */}
                {selectedReport.tags && selectedReport.tags.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Tags</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedReport.tags.map((tag, index) => (
                        <span key={index} className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300 rounded-full text-sm">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="p-6 text-center">
              <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Select a Report
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Choose a report from the list to view detailed analysis
              </p>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}

export default Reports 