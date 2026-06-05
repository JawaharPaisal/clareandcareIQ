import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { 
  Heart, 
  Activity, 
  TrendingUp, 
  Calendar, 
  Clock, 
  AlertCircle,
  CheckCircle,
  ArrowUp,
  ArrowDown,
  Users,
  FileText,
  MessageCircle
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { useChat } from '../contexts/ChatContext'
import { Line, Doughnut } from 'react-chartjs-2'
import toast from 'react-hot-toast'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

const Dashboard = () => {
  const { user } = useAuth()
  const { openChat } = useChat()
  const navigate = useNavigate()
  const [showAppointmentModal, setShowAppointmentModal] = useState(false)
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [appointment, setAppointment] = useState({ date: '', time: '', doctor: '', reason: '' })

  // Sample health data
  const healthMetrics = [
    {
      title: "Heart Rate",
      value: "72",
      unit: "bpm",
      change: "+2",
      trend: "up",
      icon: Heart,
      color: "from-red-500 to-pink-500"
    },
    {
      title: "Blood Pressure",
      value: "120/80",
      unit: "mmHg",
      change: "-5",
      trend: "down",
      icon: Activity,
      color: "from-blue-500 to-cyan-500"
    },
    {
      title: "Steps Today",
      value: "8,432",
      unit: "steps",
      change: "+12%",
      trend: "up",
      icon: TrendingUp,
      color: "from-green-500 to-emerald-500"
    },
    {
      title: "Sleep Quality",
      value: "85",
      unit: "%",
      change: "+3",
      trend: "up",
      icon: Clock,
      color: "from-purple-500 to-violet-500"
    },
    {
      title: "Weight",
      value: "68.5",
      unit: "kg",
      change: "-0.5",
      trend: "down",
      icon: Activity,
      color: "from-orange-500 to-red-500"
    },
    {
      title: "BMI",
      value: "22.1",
      unit: "",
      change: "-0.2",
      trend: "down",
      icon: TrendingUp,
      color: "from-indigo-500 to-purple-500"
    },
    {
      title: "Water Intake",
      value: "2.1",
      unit: "L",
      change: "+0.3",
      trend: "up",
      icon: Heart,
      color: "from-cyan-500 to-blue-500"
    },
    {
      title: "Calories Burned",
      value: "1,847",
      unit: "cal",
      change: "+156",
      trend: "up",
      icon: Activity,
      color: "from-yellow-500 to-orange-500"
    }
  ]

  const recentActivities = [
    {
      id: 1,
      type: "appointment",
      title: "Doctor Appointment",
      description: "Annual checkup with Dr. Smith",
      time: "2 hours ago",
      status: "upcoming"
    },
    {
      id: 2,
      type: "medication",
      title: "Medication Reminder",
      description: "Take your daily vitamins",
      time: "4 hours ago",
      status: "completed"
    },
    {
      id: 3,
      type: "report",
      title: "Lab Results Ready",
      description: "Blood test results available",
      time: "1 day ago",
      status: "new"
    },
    {
      id: 4,
      type: "chat",
      title: "AI Consultation",
      description: "Discussed symptoms with Clare",
      time: "2 days ago",
      status: "completed"
    }
  ]

  const chartData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Heart Rate',
        data: [68, 72, 70, 75, 72, 69, 71],
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4
      },
      {
        label: 'Steps',
        data: [6000, 8000, 7500, 9000, 8500, 7000, 8432],
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4
      }
    ]
  }

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Weekly Health Trends'
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }

  const doughnutData = {
    labels: ['Excellent', 'Good', 'Fair', 'Poor'],
    datasets: [
      {
        data: [45, 30, 20, 5],
        backgroundColor: [
          'rgb(34, 197, 94)',
          'rgb(59, 130, 246)',
          'rgb(245, 158, 11)',
          'rgb(239, 68, 68)'
        ],
        borderWidth: 0
      }
    ]
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'upcoming':
        return <Clock className="w-4 h-4 text-blue-500" />
      case 'new':
        return <AlertCircle className="w-4 h-4 text-orange-500" />
      default:
        return <CheckCircle className="w-4 h-4 text-gray-500" />
    }
  }

  const getActivityIcon = (type) => {
    switch (type) {
      case 'appointment':
        return <Calendar className="w-5 h-5" />
      case 'medication':
        return <FileText className="w-5 h-5" />
      case 'report':
        return <FileText className="w-5 h-5" />
      case 'chat':
        return <MessageCircle className="w-5 h-5" />
      default:
        return <Activity className="w-5 h-5" />
    }
  }

  // Replace quick action handlers:
  // Schedule Appointment
  const handleScheduleAppointment = () => setShowAppointmentModal(true)
  // Upload Reports
  const handleUploadReports = () => setShowUploadModal(true)

  return (
    <div className="space-y-3 sm:space-y-4 w-full -mx-2 sm:-mx-4 lg:-mx-6 px-2 sm:px-4 lg:px-6">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="hero-gradient rounded-xl sm:rounded-2xl card-spacing text-white card-glow"
      >
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex-1">
            <h1 className="text-xl sm:text-2xl md:text-3xl font-bold mb-2">
              Welcome back, {user?.name?.split(' ')[0]}! 👋
            </h1>
            <p className="text-white/80 text-sm sm:text-base">
              Here's your health overview for today
            </p>
          </div>
          <div className="hidden sm:block">
            <div className="w-12 h-12 sm:w-16 sm:h-16 bg-white/20 rounded-full flex items-center justify-center">
              <Heart className="w-6 h-6 sm:w-8 sm:h-8" />
            </div>
          </div>
        </div>
      </motion.div>

      {/* Health Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 2xl:grid-cols-8 gap-3 sm:gap-4">
        {healthMetrics.map((metric, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="gradient-card rounded-xl p-3 sm:p-4 shadow-lg card-hover"
          >
            <div className="flex items-center justify-between mb-3 sm:mb-4">
              <div className={`w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-r ${metric.color} rounded-lg flex items-center justify-center`}>
                <metric.icon className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
              </div>
              <div className={`flex items-center space-x-1 text-xs sm:text-sm ${
                metric.trend === 'up' ? 'text-green-500' : 'text-red-500'
              }`}>
                {metric.trend === 'up' ? <ArrowUp className="w-3 h-3 sm:w-4 sm:h-4" /> : <ArrowDown className="w-3 h-3 sm:w-4 sm:h-4" />}
                <span>{metric.change}</span>
              </div>
            </div>
            <div>
              <p className="text-gray-600 dark:text-gray-400 text-xs sm:text-sm font-medium">
                {metric.title}
              </p>
              <div className="flex items-baseline space-x-1">
                <span className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
                  {metric.value}
                </span>
                <span className="text-xs sm:text-sm text-gray-500 dark:text-gray-400">
                  {metric.unit}
                </span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-4">
        {/* Health Trends Chart */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="lg:col-span-2 xl:col-span-3 gradient-card rounded-xl p-3 sm:p-4 shadow-lg"
        >
          <div className="chart-container">
            <Line data={chartData} options={chartOptions} />
          </div>
        </motion.div>

        {/* Health Score */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="gradient-card rounded-xl p-3 sm:p-4 shadow-lg"
        >
          <h3 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white mb-3 sm:mb-4">
            Overall Health Score
          </h3>
          <div className="w-24 h-24 sm:w-32 sm:h-32 mx-auto mb-3 sm:mb-4">
            <Doughnut data={doughnutData} />
          </div>
          <div className="text-center">
            <div className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-2">
              85%
            </div>
            <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
              Excellent health status
            </p>
          </div>
        </motion.div>
      </div>

      {/* Recent Activities */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="gradient-card rounded-xl shadow-lg"
      >
        <div className="p-4 sm:p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">
            Recent Activities
          </h3>
        </div>
        <div className="p-4 sm:p-6">
          <div className="space-y-3 sm:space-y-4">
            {recentActivities.map((activity, index) => (
              <motion.div
                key={activity.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.7 + index * 0.1 }}
                className="flex items-center space-x-3 sm:space-x-4 p-3 sm:p-4 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-r from-healthcare-500 to-primary-500 rounded-lg flex items-center justify-center flex-shrink-0">
                  {getActivityIcon(activity.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-gray-900 dark:text-white text-sm sm:text-base truncate">
                      {activity.title}
                    </h4>
                    {getStatusIcon(activity.status)}
                  </div>
                  <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 truncate">
                    {activity.description}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {activity.time}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-3 sm:gap-4"
      >
        <motion.div 
          whileHover={{ scale: 1.05, y: -5 }}
          className="bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl p-4 sm:p-6 text-white cursor-pointer card-glow touch-target"
          onClick={handleScheduleAppointment}
        >
          <div className="flex items-center space-x-2 sm:space-x-3 mb-3 sm:mb-4">
            <Calendar className="w-5 h-5 sm:w-6 sm:h-6" />
            <h3 className="font-semibold text-sm sm:text-base">Schedule Appointment</h3>
          </div>
          <p className="text-blue-100 mb-3 sm:mb-4 text-xs sm:text-sm">
            Book your next checkup with ease
          </p>
          <button className="bg-white/20 hover:bg-white/30 px-3 py-2 sm:px-4 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors">
            Book Now
          </button>
        </motion.div>

        <motion.div 
          whileHover={{ scale: 1.05, y: -5 }}
          className="bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl p-4 sm:p-6 text-white cursor-pointer card-glow touch-target"
          onClick={handleUploadReports}
        >
          <div className="flex items-center space-x-2 sm:space-x-3 mb-3 sm:mb-4">
            <FileText className="w-5 h-5 sm:w-6 sm:h-6" />
            <h3 className="font-semibold text-sm sm:text-base">Upload Reports</h3>
          </div>
          <p className="text-green-100 mb-3 sm:mb-4 text-xs sm:text-sm">
            Get AI analysis of your medical reports
          </p>
          <button className="bg-white/20 hover:bg-white/30 px-3 py-2 sm:px-4 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors">
            Upload
          </button>
        </motion.div>

        <motion.div 
          whileHover={{ scale: 1.05, y: -5 }}
          className="bg-gradient-to-r from-purple-500 to-violet-500 rounded-xl p-4 sm:p-6 text-white cursor-pointer card-glow touch-target"
          onClick={openChat}
        >
          <div className="flex items-center space-x-2 sm:space-x-3 mb-3 sm:mb-4">
            <MessageCircle className="w-5 h-5 sm:w-6 sm:h-6" />
            <h3 className="font-semibold text-sm sm:text-base">Chat with Clare</h3>
          </div>
          <p className="text-purple-100 mb-3 sm:mb-4 text-xs sm:text-sm">
            Get instant answers to health questions
          </p>
          <button className="bg-white/20 hover:bg-white/30 px-3 py-2 sm:px-4 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors">
            Start Chat
          </button>
        </motion.div>

        <motion.div 
          whileHover={{ scale: 1.05, y: -5 }}
          className="bg-gradient-to-r from-teal-500 to-cyan-500 rounded-xl p-4 sm:p-6 text-white cursor-pointer card-glow touch-target"
          onClick={() => navigate('/reports')}
        >
          <div className="flex items-center space-x-2 sm:space-x-3 mb-3 sm:mb-4">
            <FileText className="w-5 h-5 sm:w-6 sm:h-6" />
            <h3 className="font-semibold text-sm sm:text-base">View Reports</h3>
          </div>
          <p className="text-teal-100 mb-3 sm:mb-4 text-xs sm:text-sm">
            Access your medical reports and history
          </p>
          <button className="bg-white/20 hover:bg-white/30 px-3 py-2 sm:px-4 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors">
            View All
          </button>
        </motion.div>

        <motion.div 
          whileHover={{ scale: 1.05, y: -5 }}
          className="bg-gradient-to-r from-pink-500 to-rose-500 rounded-xl p-4 sm:p-6 text-white cursor-pointer card-glow touch-target"
          onClick={() => navigate('/analytics')}
        >
          <div className="flex items-center space-x-2 sm:space-x-3 mb-3 sm:mb-4">
            <Activity className="w-5 h-5 sm:w-6 sm:h-6" />
            <h3 className="font-semibold text-sm sm:text-base">Health Analytics</h3>
          </div>
          <p className="text-pink-100 mb-3 sm:mb-4 text-xs sm:text-sm">
            Track your health trends and insights
          </p>
          <button className="bg-white/20 hover:bg-white/30 px-3 py-2 sm:px-4 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors">
            View Analytics
          </button>
        </motion.div>

        <motion.div 
          whileHover={{ scale: 1.05, y: -5 }}
          className="bg-gradient-to-r from-amber-500 to-orange-500 rounded-xl p-4 sm:p-6 text-white cursor-pointer card-glow touch-target"
          onClick={() => navigate('/profile')}
        >
          <div className="flex items-center space-x-2 sm:space-x-3 mb-3 sm:mb-4">
            <Users className="w-5 h-5 sm:w-6 sm:h-6" />
            <h3 className="font-semibold text-sm sm:text-base">My Profile</h3>
          </div>
          <p className="text-amber-100 mb-3 sm:mb-4 text-xs sm:text-sm">
            Manage your personal health information
          </p>
          <button className="bg-white/20 hover:bg-white/30 px-3 py-2 sm:px-4 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors">
            Edit Profile
          </button>
        </motion.div>
      </motion.div>

      {/* Appointment Modal */}
      {showAppointmentModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-white dark:bg-gray-800 rounded-xl sm:rounded-2xl shadow-2xl w-full max-w-sm sm:max-w-md lg:max-w-lg border border-gray-200 dark:border-gray-700 max-h-[90vh] overflow-y-auto"
          >
            <div className="p-4 sm:p-6">
              <div className="flex items-center justify-between mb-4 sm:mb-6">
                <h2 className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white">Schedule Appointment</h2>
                <button 
                  onClick={() => setShowAppointmentModal(false)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 touch-target"
                >
                  ✕
                </button>
              </div>
              <form onSubmit={e => {
                e.preventDefault()
                setShowAppointmentModal(false)
                toast.success('Appointment scheduled successfully!')
                setAppointment({ date: '', time: '', doctor: '', reason: '' })
              }} className="space-y-4 sm:space-y-6">
                <div className="space-y-2 sm:space-y-3">
                  <label className="block text-xs sm:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 sm:mb-2">Date</label>
                  <input type="date" required className="input-field" value={appointment.date} onChange={e => setAppointment(a => ({ ...a, date: e.target.value }))} />
                </div>
                <div className="space-y-2 sm:space-y-3">
                  <label className="block text-xs sm:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 sm:mb-2">Time</label>
                  <input type="time" required className="input-field" value={appointment.time} onChange={e => setAppointment(a => ({ ...a, time: e.target.value }))} />
                </div>
                <div className="space-y-2 sm:space-y-3">
                  <label className="block text-xs sm:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 sm:mb-2">Doctor's Name</label>
                  <input type="text" required placeholder="Enter doctor's name" className="input-field" value={appointment.doctor} onChange={e => setAppointment(a => ({ ...a, doctor: e.target.value }))} />
                </div>
                <div className="space-y-2 sm:space-y-3">
                  <label className="block text-xs sm:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 sm:mb-2">Reason</label>
                  <input type="text" required placeholder="Enter appointment reason" className="input-field" value={appointment.reason} onChange={e => setAppointment(a => ({ ...a, reason: e.target.value }))} />
                </div>
                <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 justify-end pt-4">
                  <button type="button" onClick={() => setShowAppointmentModal(false)} className="button-secondary">Cancel</button>
                  <button type="submit" className="button-primary">Book Appointment</button>
                </div>
              </form>
            </div>
          </motion.div>
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-white dark:bg-gray-800 rounded-xl sm:rounded-2xl shadow-2xl w-full max-w-sm sm:max-w-md lg:max-w-lg border border-gray-200 dark:border-gray-700 max-h-[90vh] overflow-y-auto"
          >
            <div className="p-4 sm:p-6">
              <div className="flex items-center justify-between mb-4 sm:mb-6">
                <h2 className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white">Upload Medical Report</h2>
                <button 
                  onClick={() => setShowUploadModal(false)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 touch-target"
                >
                  ✕
                </button>
              </div>
              <form onSubmit={e => {
                e.preventDefault()
                setShowUploadModal(false)
                toast.success('Report uploaded successfully! AI analysis will be available shortly.')
              }} className="space-y-4 sm:space-y-6">
                <div className="space-y-2 sm:space-y-3">
                  <label className="block text-xs sm:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 sm:mb-2">Select File</label>
                  <input type="file" required className="input-field" accept=".pdf,.jpg,.png,.doc,.docx" />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Accepted formats: PDF, JPG, PNG, DOC, DOCX</p>
                </div>
                <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 justify-end pt-4">
                  <button type="button" onClick={() => setShowUploadModal(false)} className="button-secondary">Cancel</button>
                  <button type="submit" className="button-primary">Upload Report</button>
                </div>
              </form>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  )
}

export default Dashboard 