import { motion } from 'framer-motion'
import { NavLink, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Upload, 
  Video, 
  MessageSquare, 
  BarChart3, 
  Settings,
  FileText,
  Zap
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { useVideo } from '../contexts/VideoContext'

const navigationItems = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
    description: 'Overview and analytics'
  },
  {
    name: 'Upload Video',
    href: '/upload',
    icon: Upload,
    description: 'Upload new videos for analysis'
  },
  {
    name: 'Videos',
    href: '/videos',
    icon: Video,
    description: 'Manage your video library'
  },
  {
    name: 'AI Chat',
    href: '/chat',
    icon: MessageSquare,
    description: 'Chat with AI about your videos',
    badge: 'New'
  },
  {
    name: 'Analytics',
    href: '/analytics',
    icon: BarChart3,
    description: 'Detailed insights and reports'
  },
  {
    name: 'Reports',
    href: '/reports',
    icon: FileText,
    description: 'Generate and export reports'
  },
]

const quickActions = [
  {
    name: 'Quick Analysis',
    icon: Zap,
    description: 'Start instant video analysis',
    action: 'quick-analysis'
  },
  {
    name: 'Settings',
    icon: Settings,
    description: 'Configure preferences',
    action: 'settings'
  },
]

export default function Sidebar() {
  const location = useLocation()
  const { videos } = useVideo()
  
  const processingVideos = videos.filter(video => video.status === 'processing').length

  return (
    <motion.aside
      initial={{ x: -300, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="h-full bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 overflow-y-auto"
    >
      <div className="p-6">
        {/* Navigation */}
        <nav className="space-y-2">
          <div className="mb-6">
            <h2 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
              Navigation
            </h2>
            {navigationItems.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={({ isActive }) =>
                    `group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${
                      isActive
                        ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 border-r-2 border-blue-600'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white'
                    }`
                  }
                >
                  <motion.div
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                    className="flex items-center w-full"
                  >
                    <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
                    <span className="flex-1">{item.name}</span>
                    {item.badge && (
                      <Badge variant="secondary" className="ml-2 text-xs">
                        {item.badge}
                      </Badge>
                    )}
                    {item.name === 'Videos' && processingVideos > 0 && (
                      <Badge variant="default" className="ml-2 text-xs bg-orange-500">
                        {processingVideos}
                      </Badge>
                    )}
                  </motion.div>
                </NavLink>
              )
            })}
          </div>

          {/* Quick Actions */}
          <div className="mb-6">
            <h2 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
              Quick Actions
            </h2>
            {quickActions.map((item) => (
              <motion.button
                key={item.name}
                whileHover={{ scale: 1.02, x: 4 }}
                whileTap={{ scale: 0.98 }}
                className="group flex items-center w-full px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white transition-all duration-200"
              >
                <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
                <span className="flex-1 text-left">{item.name}</span>
              </motion.button>
            ))}
          </div>

          {/* Status Section */}
          <div className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
              System Status
            </h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-600 dark:text-gray-400">AI Models</span>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                  <span className="text-green-600 dark:text-green-400">Online</span>
                </div>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-600 dark:text-gray-400">Processing Queue</span>
                <span className="text-gray-900 dark:text-white font-medium">
                  {processingVideos} active
                </span>
              </div>
            </div>
          </div>
        </nav>
      </div>
    </motion.aside>
  )
}

