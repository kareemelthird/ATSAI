import { Outlet, Link, useLocation } from 'react-router-dom'
import { Users, Briefcase, FileText, MessageSquare, Upload, LayoutDashboard, LogOut, User, Settings, Shield, Menu, X } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { useState, useEffect } from 'react'
import axios from 'axios'

// Get the correct API base URL for the environment
const getAPIBaseURL = () => {
  if (import.meta.env.PROD) {
    return window.location.origin
  }
  return import.meta.env.VITE_API_URL || 'http://localhost:8000'
}

const API_BASE_URL = getAPIBaseURL();

const Layout = () => {
  const location = useLocation()
  const { user, isAdmin, logout } = useAuth()
  const [projectName, setProjectName] = useState('ATS/AI')
  const [projectSubtitle, setProjectSubtitle] = useState('Applicant Tracking System')
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  useEffect(() => {
    // Fetch project info from backend
    const fetchProjectInfo = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/v1/settings/public/project-info`, {
          timeout: 5000 // 5 second timeout
        })
        const name = response.data.project_name || 'ATS/AI'
        setProjectName(name)
        
        // Update document title
        document.title = name
        
        // Extract subtitle if project name contains separator
        if (name.includes(' - ')) {
          const parts = name.split(' - ')
          setProjectName(parts[0])
          setProjectSubtitle(parts[1])
          document.title = `${parts[0]} - ${parts[1]}`
        } else if (name.includes('/')) {
          setProjectSubtitle('Applicant Tracking System')
          document.title = `${name} - Applicant Tracking System`
        } else {
          setProjectSubtitle('')
        }
      } catch (error) {
        console.error('Failed to fetch project info:', error)
        // Keep default values - don't block UI
        setProjectName('ATS/AI')
        setProjectSubtitle('Applicant Tracking System')
        document.title = 'ATS/AI - Applicant Tracking System'
      }
    }
    
    fetchProjectInfo()
  }, [])

  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/candidates', icon: Users, label: 'Candidates' },
    { path: '/jobs', icon: Briefcase, label: 'Jobs' },
    { path: '/applications', icon: FileText, label: 'Applications' },
    { path: '/ai-chat', icon: MessageSquare, label: 'AI Chat' },
    { path: '/upload', icon: Upload, label: 'Upload Resume' },
    { path: '/profile', icon: User, label: 'My Profile' },
  ]

  // Admin navigation items (only shown to admins)
  const adminNavItems = isAdmin ? [
    { path: '/admin/users', icon: Shield, label: 'User Management' },
    { path: '/admin/settings', icon: Settings, label: 'Settings' },
  ] : []

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      {/* Mobile header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-primary-600 dark:text-primary-400">
              {projectName}
            </h1>
            {projectSubtitle && (
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {projectSubtitle}
              </p>
            )}
          </div>
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 rounded-md text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile overlay */}
      {isMobileMenuOpen && (
        <div 
          className="lg:hidden fixed inset-0 z-40 bg-black bg-opacity-50"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 z-40 h-screen bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-transform duration-300
        lg:translate-x-0 lg:w-64
        w-64 ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="h-full px-3 py-4 overflow-y-auto flex flex-col">
          <div className="mb-8 lg:block hidden">
            <h1 className="text-2xl font-bold text-primary-600 dark:text-primary-400">
              {projectName}
            </h1>
            {projectSubtitle && (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {projectSubtitle}
              </p>
            )}
          </div>
          
          {/* Mobile header in sidebar */}
          <div className="mb-8 lg:hidden block pt-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-xl font-bold text-primary-600 dark:text-primary-400">
                  {projectName}
                </h1>
                {projectSubtitle && (
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {projectSubtitle}
                  </p>
                )}
              </div>
              <button
                onClick={() => setIsMobileMenuOpen(false)}
                className="p-2 rounded-md text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
          
          <ul className="space-y-2 flex-1">
            {/* Main navigation */}
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              
              return (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    onClick={() => setIsMobileMenuOpen(false)} // Close menu on mobile when item is clicked
                    className={`flex items-center p-3 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
                        : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                    }`}
                  >
                    <Icon className="w-5 h-5 mr-3" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                </li>
              )
            })}

            {/* Admin section */}
            {adminNavItems.length > 0 && (
              <>
                <li className="pt-4 mt-4 border-t border-gray-200 dark:border-gray-700">
                  <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider px-3 mb-2">
                    Administration
                  </p>
                </li>
                {adminNavItems.map((item) => {
                  const Icon = item.icon
                  const isActive = location.pathname === item.path
                  
                  return (
                    <li key={item.path}>
                      <Link
                        to={item.path}
                        onClick={() => setIsMobileMenuOpen(false)} // Close menu on mobile when item is clicked
                        className={`flex items-center p-3 rounded-lg transition-colors ${
                          isActive
                            ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
                            : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                        }`}
                      >
                        <Icon className="w-5 h-5 mr-3" />
                        <span className="font-medium">{item.label}</span>
                      </Link>
                    </li>
                  )
                })}
              </>
            )}
          </ul>

          {/* User Info & Logout */}
          <div className="mt-auto pt-4 border-t border-gray-200 dark:border-gray-700">
            {user && (
              <div className="mb-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center mb-2">
                  <User className="w-4 h-4 mr-2 text-gray-600 dark:text-gray-400" />
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {user.first_name} {user.last_name}
                  </span>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400">{user.email}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Role: <span className="font-medium text-blue-600 dark:text-blue-400">{user.role}</span>
                </p>
              </div>
            )}
            <button
              onClick={logout}
              className="w-full flex items-center p-3 rounded-lg text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20 transition-colors"
            >
              <LogOut className="w-5 h-5 mr-3" />
              <span className="font-medium">Logout</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="lg:ml-64 ml-0 h-screen flex flex-col">
        {/* Add top padding on mobile to account for fixed header */}
        <main className="flex-1 p-4 lg:p-8 pt-20 lg:pt-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default Layout
