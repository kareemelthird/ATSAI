import { useQuery } from '@tanstack/react-query'
import { candidateApi, jobApi, applicationApi, api } from '@/lib/api'
import { Users, Briefcase, FileText, TrendingUp, AlertTriangle } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useState, useEffect } from 'react'

const Dashboard = () => {
  const [showApiKeyBanner, setShowApiKeyBanner] = useState(false)

  const { data: candidates } = useQuery({
    queryKey: ['candidates'],
    queryFn: () => candidateApi.getAll({ limit: 100 }),
  })

  const { data: jobs } = useQuery({
    queryKey: ['jobs'],
    queryFn: () => jobApi.getAll({ limit: 100 }),
  })

  const { data: applications } = useQuery({
    queryKey: ['applications'],
    queryFn: () => applicationApi.getAll({ limit: 100 }),
  })

  // Check if user has personal API key configured
  const { data: aiSettings } = useQuery({
    queryKey: ['profile-ai-settings'],
    queryFn: async () => {
      const response = await api.get('/profile/ai-settings')
      return response.data
    }
  })

  useEffect(() => {
    // Show banner if user doesn't have personal key or hasn't enabled it
    if (aiSettings && (!aiSettings.has_personal_key || !aiSettings.use_personal_ai_key)) {
      setShowApiKeyBanner(true)
    } else {
      setShowApiKeyBanner(false)
    }
  }, [aiSettings])

  // Calculate active today (candidates updated or created today)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  const activeToday = candidates?.data?.filter((candidate: any) => {
    const updatedAt = new Date(candidate.updated_at || candidate.created_at)
    const createdAt = new Date(candidate.created_at)
    return updatedAt >= today || createdAt >= today
  }).length || 0

  const stats = [
    {
      title: 'Total Candidates',
      value: candidates?.data?.length || 0,
      icon: Users,
      color: 'bg-blue-500',
    },
    {
      title: 'Open Jobs',
      value: jobs?.data?.filter((j: any) => j.status === 'open').length || 0,
      icon: Briefcase,
      color: 'bg-green-500',
    },
    {
      title: 'Applications',
      value: applications?.data?.length || 0,
      icon: FileText,
      color: 'bg-purple-500',
    },
    {
      title: 'Active Today',
      value: activeToday,
      icon: TrendingUp,
      color: 'bg-orange-500',
    },
  ]

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
        Dashboard
      </h1>

      {/* API Key Warning Banner */}
      {showApiKeyBanner && (
        <div className="mb-6 bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-400 p-4 rounded-lg">
          <div className="flex items-start">
            <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-3 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200 mb-1">
                ⚠️ Personal Groq API Key Required
              </h3>
              <p className="text-sm text-yellow-700 dark:text-yellow-300 mb-3">
                The system API key has very limited usage. To use AI features (resume parsing, AI chat) without restrictions, 
                please add your <strong>free</strong> personal Groq API key.
              </p>
              <div className="flex gap-3">
                <Link
                  to="/profile"
                  className="inline-flex items-center px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white text-sm font-medium rounded-lg transition-colors"
                >
                  🔑 Add Personal API Key
                </Link>
                <button
                  onClick={() => setShowApiKeyBanner(false)}
                  className="text-sm text-yellow-700 dark:text-yellow-300 hover:text-yellow-900 dark:hover:text-yellow-100"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.title} className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {stat.title}
                  </p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                    {stat.value}
                  </p>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Recent Candidates
          </h2>
          <div className="space-y-3">
            {candidates?.data?.slice(0, 5).map((candidate: any) => (
              <div
                key={candidate.id}
                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
              >
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {candidate.first_name} {candidate.last_name}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {candidate.email}
                  </p>
                </div>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {new Date(candidate.created_at).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Open Positions
          </h2>
          <div className="space-y-3">
            {jobs?.data
              ?.filter((job: any) => job.status === 'open')
              .slice(0, 5)
              .map((job: any) => (
                <div
                  key={job.id}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {job.title}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {job.location || 'Remote'}
                    </p>
                  </div>
                  <span className="px-2 py-1 text-xs font-medium text-green-700 bg-green-100 rounded-full dark:bg-green-900 dark:text-green-300">
                    {job.status}
                  </span>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
