import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Shield, User, Database, Eye, Share2, Download, Trash2, AlertTriangle, Edit, Lock } from 'lucide-react'

const PrivacyModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden border border-gray-200 dark:border-gray-700"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-primary-500 to-healthcare-500">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                <Shield className="w-6 h-6 text-primary-500" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">Privacy Policy</h2>
                <p className="text-sm text-white/80">Clare & CareIQ</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-full hover:bg-white/20 transition-colors text-white"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
            <div className="prose prose-gray dark:prose-invert max-w-none">
              <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                <div className="flex items-start space-x-3">
                  <Lock className="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-green-800 dark:text-green-200">
                      <strong>Effective Date:</strong> [November 2025]
                    </p>
                    <p className="text-sm text-green-700 dark:text-green-300 mt-1">
                      Clare & CareIQ values your privacy. This policy explains how we collect, use, and protect your personal and medical data.
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                {/* Section 1 */}
                <div className="border-l-4 border-primary-500 pl-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                    <User className="w-5 h-5 mr-2 text-primary-500" />
                    1. Information We Collect
                  </h3>
                  <div className="space-y-3">
                    <div className="bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg">
                      <h4 className="font-medium text-gray-900 dark:text-white mb-2">Personal Information:</h4>
                      <p className="text-sm text-gray-700 dark:text-gray-300">Name, email, profile image (via Google OAuth).</p>
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg">
                      <h4 className="font-medium text-gray-900 dark:text-white mb-2">Medical Data:</h4>
                      <p className="text-sm text-gray-700 dark:text-gray-300">Summaries of uploaded reports, chat-based medical history.</p>
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg">
                      <h4 className="font-medium text-gray-900 dark:text-white mb-2">Usage Data:</h4>
                      <p className="text-sm text-gray-700 dark:text-gray-300">Chat interactions, timestamps, technical logs.</p>
                    </div>
                  </div>
                </div>

                {/* Section 2 */}
                <div className="border-l-4 border-healthcare-500 pl-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                    <Eye className="w-5 h-5 mr-2 text-healthcare-500" />
                    2. How We Use Your Information
                  </h3>
                  <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
                    <li>To provide personalized health clarifications.</li>
                    <li>To maintain your medical history summaries.</li>
                    <li>To improve chatbot responses and accuracy.</li>
                    <li>To enhance future features (e.g., Google Fit integration).</li>
                  </ul>
                </div>

                {/* Section 3 */}
                <div className="border-l-4 border-accent-500 pl-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                    <Database className="w-5 h-5 mr-2 text-accent-500" />
                    3. Data Storage & Security
                  </h3>
                  <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
                    <li>Data is stored securely in MongoDB with encryption for sensitive fields.</li>
                    <li>Only summarized medical data is stored, not original reports.</li>
                    <li>We use authentication (Google OAuth) to ensure only you can access your data.</li>
                  </ul>
                </div>

                {/* Section 4 */}
                <div className="border-l-4 border-red-500 pl-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                    <Share2 className="w-5 h-5 mr-2 text-red-500" />
                    4. Sharing of Data
                  </h3>
                  <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
                    <li>We do not share your personal or medical data with third parties without your explicit consent.</li>
                    <li>Data may be shared only if required by law or legal process.</li>
                  </ul>
                </div>

                {/* Section 5 */}
                <div className="border-l-4 border-primary-500 pl-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                    <Download className="w-5 h-5 mr-2 text-primary-500" />
                    5. User Rights
                  </h3>
                  <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
                    <li>You can request a copy of your stored data.</li>
                    <li>You can request deletion of your medical history at any time.</li>
                    <li>You can withdraw consent — but this may limit your use of the service.</li>
                  </ul>
                </div>

                {/* Section 6 */}
                <div className="border-l-4 border-yellow-500 pl-4">
                  <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                      <AlertTriangle className="w-5 h-5 mr-2 text-yellow-600 dark:text-yellow-400" />
                      6. Disclaimer
                    </h3>
                    <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
                      <li>Clare & CareIQ may provide medical information and advice, but it is generated by AI.</li>
                      <li>Always consult a licensed healthcare professional before making health decisions.</li>
                    </ul>
                  </div>
                </div>

                {/* Section 7 */}
                <div className="border-l-4 border-healthcare-500 pl-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                    <Edit className="w-5 h-5 mr-2 text-healthcare-500" />
                    7. Changes to This Policy
                  </h3>
                  <p className="text-gray-700 dark:text-gray-300">
                    We may update this Privacy Policy from time to time. Users will be notified of major changes.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700/50">
            <div className="flex justify-end">
              <button
                onClick={onClose}
                className="px-6 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors"
              >
                I Understand
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

export default PrivacyModal
