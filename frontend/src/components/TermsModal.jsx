import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, FileText, AlertTriangle, Shield, Users, Database, Scale, Edit, Gavel } from 'lucide-react'

const TermsModal = ({ isOpen, onClose }) => {
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
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-healthcare-500 to-primary-500">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                <FileText className="w-6 h-6 text-healthcare-500" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">Terms & Conditions</h2>
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
              <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <div className="flex items-start space-x-3">
                  <AlertTriangle className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-blue-800 dark:text-blue-200">
                      <strong>Effective Date:</strong> [November 2025]
                    </p>
                    <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                      Welcome to Clare & CareIQ. By accessing or using our service, you agree to the following Terms & Conditions. Please read carefully before proceeding.
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                {/* Section 1 */}
                <div className="border-l-4 border-healthcare-500 pl-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                    <Shield className="w-5 h-5 mr-2 text-healthcare-500" />
                    1. Purpose of the Service
                  </h3>
                  <p className="text-gray-700 dark:text-gray-300 mb-3">
                    Clare & CareIQ is an AI-enabled smart assistant designed to:
                  </p>
                  <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
                    <li>Answer general medical-related questions</li>
                    <li>Provide clarifications on medical reports</li>
                    <li>Track personal medical history summaries</li>
                  </ul>
                  <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                    <p className="text-sm text-red-800 dark:text-red-200">
                      <strong>⚠️ Important:</strong> This service is for informational and educational purposes only. It is not a replacement for professional medical advice, diagnosis, or treatment.
                    </p>
                  </div>
                </div>

                {/* Section 2 */}
                <div className="border-l-4 border-primary-500 pl-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                    <Users className="w-5 h-5 mr-2 text-primary-500" />
                    2. User Eligibility
                  </h3>
                  <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
                    <li>Users must be 18 years or older to use this service.</li>
                    <li>If you are under 18, you must use the service with parental/guardian consent.</li>
                  </ul>
                </div>

                {/* Section 3 */}
                <div className="border-l-4 border-accent-500 pl-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                    <Shield className="w-5 h-5 mr-2 text-accent-500" />
                    3. User Responsibilities
                  </h3>
                  <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
                    <li>You agree not to misuse the service (e.g., entering false information, attempting to hack, etc.).</li>
                    <li>You understand that AI-generated responses may not always be accurate and should not be solely relied upon for critical health decisions.</li>
                    <li>You agree to consult a licensed medical professional for urgent or serious health issues.</li>
                  </ul>
                </div>

                {/* Section 4 */}
                <div className="border-l-4 border-healthcare-500 pl-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                    <Database className="w-5 h-5 mr-2 text-healthcare-500" />
                    4. Data Usage & Storage
                  </h3>
                  <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
                    <li>Users may upload medical reports and enter health information.</li>
                    <li>Only summarized data (not raw files) is stored in our database.</li>
                    <li>Your consent is required before any medical history is saved.</li>
                  </ul>
                </div>

                {/* Section 5 */}
                <div className="border-l-4 border-red-500 pl-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                    <Scale className="w-5 h-5 mr-2 text-red-500" />
                    5. Limitations of Liability
                  </h3>
                  <ul className="list-disc list-inside space-y-2 text-gray-700 dark:text-gray-300 ml-4">
                    <li>Clare & CareIQ and its developers are not responsible for any decisions, damages, or outcomes resulting from reliance on the chatbot's responses.</li>
                    <li>The service is provided "as is" without warranties of accuracy, reliability, or suitability for specific purposes.</li>
                  </ul>
                </div>

                {/* Section 6 */}
                <div className="border-l-4 border-primary-500 pl-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                    <Edit className="w-5 h-5 mr-2 text-primary-500" />
                    6. Modifications
                  </h3>
                  <p className="text-gray-700 dark:text-gray-300">
                    We reserve the right to update these Terms at any time. Users will be notified of significant changes.
                  </p>
                </div>

                {/* Section 7 */}
                <div className="border-l-4 border-accent-500 pl-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                    <Gavel className="w-5 h-5 mr-2 text-accent-500" />
                    7. Governing Law
                  </h3>
                  <p className="text-gray-700 dark:text-gray-300">
                    These Terms are governed by the laws of India (or insert your jurisdiction).
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

export default TermsModal
