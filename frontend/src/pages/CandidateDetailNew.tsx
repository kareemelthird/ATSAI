import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { candidateApi } from '@/lib/api'
import { 
  Mail, Phone, MapPin, Linkedin, Github, Globe, Download, ArrowLeft, 
  ExternalLink, Briefcase, GraduationCap, Award, Code, Languages,
  TrendingUp, Calendar, DollarSign, Clock, BarChart3, Users
} from 'lucide-react'
import { 
  BarChart, Bar, PieChart, Pie, Cell, LineChart, Line,

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  AreaChart, Area
} from 'recharts'

const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899']

const CandidateDetailNew = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const { data: fullData, isLoading } = useQuery({
    queryKey: ['candidate-complete', id],
    queryFn: () => candidateApi.getComplete(id!),
    enabled: !!id,
  })

  const handleDownloadResume = (candidateId: string) => {
    const downloadUrl = `${API_BASE_URL}/api/v1/candidates/${candidateId}/resume/download`
    window.open(downloadUrl, '_blank')
  }

  const fixUrl = (url: string | undefined) => {
    if (!url) return ''
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url
    }
    return `https://${url}`
  }

  const formatCurrency = (amount: number | null, currency: string | null) => {
    if (!amount) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'USD',
      minimumFractionDigits: 0
    }).format(amount)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const candidate = fullData?.data?.candidate
  const stats = fullData?.data?.statistics
  const skills = fullData?.data?.skills || []
  const workExperiences = fullData?.data?.work_experiences || []
  const educations = fullData?.data?.educations || []
  const projects = fullData?.data?.projects || []
  const certifications = fullData?.data?.certifications || []
  const languages = fullData?.data?.languages || []

  // Prepare chart data
  const skillsProficiencyData = Object.entries(stats?.skills_by_proficiency || {}).map(([level, count]) => ({
    level,
    count: count as number
  }))

  const skillsCategoryData = Object.entries(stats?.skills_by_category || {}).map(([category, skillsList]: [string, any]) => ({
    category,
    count: Array.isArray(skillsList) ? skillsList.length : 0
  }))

  const topSkillsData = (stats?.top_skills || []).slice(0, 8).map((skill: any) => ({
    name: skill.name,
    years: skill.years
  }))

  const industriesData = Object.entries(stats?.industries || {}).map(([industry, count]) => ({
    industry,
    count: count as number
  }))

  const topTechData = (stats?.top_technologies || []).slice(0, 10)

  // Career progression data for line chart
  const careerProgressionData = (stats?.career_progression || []).map((item: any, index: number) => ({
    position: index + 1,
    level: item.level,
    title: item.title,
    company: item.company,
    date: item.date
  }))

  // Experience timeline data
  const experienceTimelineData = workExperiences.map((exp: any) => {
    const start = exp.start_date ? new Date(exp.start_date).getFullYear() : 0
    const end = exp.end_date ? new Date(exp.end_date).getFullYear() : new Date().getFullYear()
    return {
      company: exp.company_name ? exp.company_name.substring(0, 20) : 'Unknown',
      start,
      end,
      duration: end - start
    }
  })

  // Education timeline
  const educationTimelineData = educations.map((edu: any) => ({
    institution: edu.institution ? edu.institution.substring(0, 25) : 'Unknown',
    degree: edu.degree || 'Not specified',
    year: edu.graduation_year || (edu.end_date ? new Date(edu.end_date).getFullYear() : 0)
  }))

  return (
    <div className="max-w-[1600px] mx-auto h-full overflow-y-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/candidates')}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white mb-4"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Candidates
        </button>
        
        <div className="card p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-6">
              {/* Avatar */}
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-white text-3xl font-bold shadow-lg">
                {candidate?.first_name?.[0]}{candidate?.last_name?.[0]}
              </div>
              
              <div>
                <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                  {candidate?.first_name} {candidate?.last_name}
                </h1>
                <div className="flex items-center gap-3 mb-3">
                  <span
                    className={`px-4 py-1.5 text-sm font-medium rounded-full ${
                      candidate?.status === 'active'
                        ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                        : candidate?.status === 'hired'
                        ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                        : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                    }`}
                  >
                    {candidate?.status}
                  </span>
                  {candidate?.career_level && (
                    <span className="px-4 py-1.5 text-sm font-medium rounded-full bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300">
                      {candidate.career_level}
                    </span>
                  )}
                  {stats?.total_years_experience && (
                    <span className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400">
                      <Briefcase className="w-4 h-4" />
                      {stats.total_years_experience} years exp.
                    </span>
                  )}
                </div>
                
                {/* Key Contact Info */}
                <div className="flex items-center gap-6 text-sm">
                  {candidate?.email && (
                    <div className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
                      <Mail className="w-4 h-4" />
                      {candidate.email}
                    </div>
                  )}
                  {candidate?.phone && (
                    <div className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
                      <Phone className="w-4 h-4" />
                      {candidate.phone}
                    </div>
                  )}
                  {candidate?.current_location && (
                    <div className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
                      <MapPin className="w-4 h-4" />
                      {candidate.current_location}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="flex gap-3">
              <button
                onClick={() => handleDownloadResume(id!)}
                className="btn-primary"
              >
                <Download className="w-4 h-4" />
                Download CV
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="card p-5 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-600 dark:text-blue-400">Total Skills</p>
              <p className="text-3xl font-bold text-blue-900 dark:text-blue-100 mt-1">{skills.length}</p>
            </div>
            <Code className="w-12 h-12 text-blue-500 opacity-20" />
          </div>
        </div>

        <div className="card p-5 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-600 dark:text-green-400">Companies Worked</p>
              <p className="text-3xl font-bold text-green-900 dark:text-green-100 mt-1">{stats?.total_companies || 0}</p>
            </div>
            <Briefcase className="w-12 h-12 text-green-500 opacity-20" />
          </div>
        </div>

        <div className="card p-5 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-purple-600 dark:text-purple-400">Certifications</p>
              <p className="text-3xl font-bold text-purple-900 dark:text-purple-100 mt-1">{stats?.active_certifications || 0}</p>
            </div>
            <Award className="w-12 h-12 text-purple-500 opacity-20" />
          </div>
        </div>

        <div className="card p-5 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-orange-600 dark:text-orange-400">Projects</p>
              <p className="text-3xl font-bold text-orange-900 dark:text-orange-100 mt-1">{stats?.total_projects || 0}</p>
            </div>
            <BarChart3 className="w-12 h-12 text-orange-500 opacity-20" />
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Info & Charts */}
        <div className="lg:col-span-2 space-y-6">
          {/* Professional Summary */}
          {candidate?.professional_summary && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <Users className="w-5 h-5 text-primary-600" />
                Professional Summary
              </h2>
              <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                {candidate.professional_summary}
              </p>
            </div>
          )}

          {/* Skills Proficiency Chart */}
          {skillsProficiencyData.length > 0 && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Skills by Proficiency Level
              </h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={skillsProficiencyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
                  <XAxis dataKey="level" stroke="#6b7280" />
                  <YAxis stroke="#6b7280" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1f2937', 
                      border: 'none', 
                      borderRadius: '8px',
                      color: '#fff'
                    }} 
                  />
                  <Bar dataKey="count" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Top Skills by Experience */}
          {topSkillsData.length > 0 && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Top Skills by Years of Experience
              </h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={topSkillsData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
                  <XAxis type="number" stroke="#6b7280" />
                  <YAxis dataKey="name" type="category" width={120} stroke="#6b7280" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1f2937', 
                      border: 'none', 
                      borderRadius: '8px',
                      color: '#fff'
                    }} 
                  />
                  <Bar dataKey="years" fill="#10b981" radius={[0, 8, 8, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Skills by Category */}
          {skillsCategoryData.length > 0 && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Skills Distribution by Category
              </h2>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={skillsCategoryData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ category, count }) => `${category}: ${count}`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {skillsCategoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Top Technologies */}
          {topTechData.length > 0 && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Most Used Technologies
              </h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={topTechData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
                  <XAxis dataKey="name" stroke="#6b7280" angle={-45} textAnchor="end" height={100} />
                  <YAxis stroke="#6b7280" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1f2937', 
                      border: 'none', 
                      borderRadius: '8px',
                      color: '#fff'
                    }} 
                  />
                  <Bar dataKey="count" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Industry Experience Distribution */}
          {industriesData.length > 0 && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Industry Experience
              </h2>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={industriesData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry: any) => `${entry.industry}: ${entry.count}`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {industriesData.map((_entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Experience Timeline Chart */}
          {experienceTimelineData.length > 0 && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Work Experience Timeline
              </h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={experienceTimelineData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
                  <XAxis type="number" stroke="#6b7280" domain={[2010, 2025]} />
                  <YAxis dataKey="company" type="category" width={150} stroke="#6b7280" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1f2937', 
                      border: 'none', 
                      borderRadius: '8px',
                      color: '#fff'
                    }}
                    labelFormatter={(value) => `Company: ${value}`}
                  />
                  <Bar dataKey="duration" fill="#f59e0b" radius={[0, 8, 8, 0]} />
                </BarChart>
              </ResponsiveContainer>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2 text-center">
                Duration in years at each company
              </p>
            </div>
          )}

          {/* Education Timeline */}
          {educationTimelineData.length > 0 && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Education Timeline
              </h2>
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={educationTimelineData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
                  <XAxis dataKey="year" stroke="#6b7280" />
                  <YAxis hide />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1f2937', 
                      border: 'none', 
                      borderRadius: '8px',
                      color: '#fff'
                    }}
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="bg-gray-900 p-3 rounded-lg border border-gray-700">
                            <p className="text-white font-semibold">{payload[0].payload.degree}</p>
                            <p className="text-gray-300 text-sm">{payload[0].payload.institution}</p>
                            <p className="text-gray-400 text-xs mt-1">Year: {payload[0].payload.year}</p>
                          </div>
                        )
                      }
                      return null
                    }}
                  />
                  <Area type="monotone" dataKey="year" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Skills Radar Chart - Top 6 Skills */}
          {topSkillsData.length >= 3 && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Skills Expertise Radar
              </h2>
              <ResponsiveContainer width="100%" height={400}>
                <RadarChart data={topSkillsData.slice(0, 6)}>
                  <PolarGrid stroke="#374151" />
                  <PolarAngleAxis dataKey="name" stroke="#6b7280" />
                  <PolarRadiusAxis stroke="#6b7280" />
                  <Radar name="Years of Experience" dataKey="years" stroke="#10b981" fill="#10b981" fillOpacity={0.6} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1f2937', 
                      border: 'none', 
                      borderRadius: '8px',
                      color: '#fff'
                    }} 
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Work Experience Details */}
          {workExperiences.length > 0 && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-primary-600" />
                Work Experience ({workExperiences.length})
              </h2>
              <div className="space-y-6">
                {workExperiences.map((exp: any, index: number) => (
                  <div key={exp.id} className="border-l-4 border-primary-500 pl-6 pb-6 relative">
                    <div className="absolute -left-2.5 top-0 w-5 h-5 rounded-full bg-primary-500 border-4 border-white dark:border-gray-900"></div>
                    
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          {exp.job_title}
                        </h3>
                        <p className="text-primary-600 dark:text-primary-400 font-medium">
                          {exp.company_name}
                        </p>
                      </div>
                      {exp.is_current && (
                        <span className="px-3 py-1 bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 rounded-full text-xs font-medium">
                          Current
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mb-3">
                      {exp.start_date && (
                        <span className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          {new Date(exp.start_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                          {' - '}
                          {exp.end_date ? new Date(exp.end_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' }) : 'Present'}
                        </span>
                      )}
                      {exp.duration_months && (
                        <span className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          {Math.floor(exp.duration_months / 12)}y {exp.duration_months % 12}m
                        </span>
                      )}
                      {exp.job_level && (
                        <span className="px-2 py-0.5 bg-gray-200 dark:bg-gray-700 rounded text-xs">
                          {exp.job_level}
                        </span>
                      )}
                      {exp.company_industry && (
                        <span className="px-2 py-0.5 bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 rounded text-xs">
                          {exp.company_industry}
                        </span>
                      )}
                    </div>

                    {exp.responsibilities && (
                      <p className="text-gray-700 dark:text-gray-300 mb-3">
                        {exp.responsibilities}
                      </p>
                    )}

                    {exp.achievements && exp.achievements.length > 0 && (
                      <div className="mb-3">
                        <p className="text-sm font-semibold text-gray-900 dark:text-white mb-1">Key Achievements:</p>
                        <ul className="list-disc list-inside text-sm text-gray-700 dark:text-gray-300 space-y-1">
                          {exp.achievements.map((achievement: string, idx: number) => (
                            <li key={idx}>{achievement}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {exp.technologies_used && exp.technologies_used.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-3">
                        {exp.technologies_used.map((tech: string, idx: number) => (
                          <span
                            key={idx}
                            className="px-2 py-1 bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 rounded text-xs"
                          >
                            {tech}
                          </span>
                        ))}
                      </div>
                    )}

                    {(exp.team_size || exp.managed_team_size) && (
                      <div className="flex items-center gap-4 mt-3 text-sm text-gray-600 dark:text-gray-400">
                        {exp.team_size && (
                          <span className="flex items-center gap-1">
                            <Users className="w-4 h-4" />
                            Team Size: {exp.team_size}
                          </span>
                        )}
                        {exp.managed_team_size && (
                          <span className="flex items-center gap-1">
                            <Users className="w-4 h-4" />
                            Managed: {exp.managed_team_size}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Education Details */}
          {educations.length > 0 && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                <GraduationCap className="w-5 h-5 text-primary-600" />
                Education ({educations.length})
              </h2>
              <div className="space-y-4">
                {educations.map((edu: any) => (
                  <div key={edu.id} className="p-5 bg-gradient-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          {edu.degree && edu.field_of_study ? `${edu.degree} in ${edu.field_of_study}` : 
                           edu.degree || edu.field_of_study || 'Education Record'}
                        </h3>
                        {edu.specialization && (
                          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                            Specialization: {edu.specialization}
                          </p>
                        )}
                        <p className="text-primary-600 dark:text-primary-400 font-medium mt-2">
                          {edu.institution}
                        </p>
                        <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mt-2">
                          {edu.graduation_year && (
                            <span className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              Graduated: {edu.graduation_year}
                            </span>
                          )}
                          {edu.grade_value && (
                            <span className="px-2 py-1 bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 rounded text-xs font-medium">
                              Grade: {edu.grade_value} {edu.grade_type && `(${edu.grade_type})`}
                            </span>
                          )}
                        </div>
                        {edu.achievements && edu.achievements.length > 0 && (
                          <div className="mt-3">
                            <p className="text-sm font-semibold text-gray-900 dark:text-white mb-1">Achievements:</p>
                            <div className="flex flex-wrap gap-2">
                              {edu.achievements.map((achievement: string, idx: number) => (
                                <span
                                  key={idx}
                                  className="px-2 py-1 bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 rounded text-xs"
                                >
                                  {achievement}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        {edu.relevant_coursework && edu.relevant_coursework.length > 0 && (
                          <div className="mt-3">
                            <p className="text-sm font-semibold text-gray-900 dark:text-white mb-1">Relevant Coursework:</p>
                            <div className="flex flex-wrap gap-2">
                              {edu.relevant_coursework.map((course: string, idx: number) => (
                                <span
                                  key={idx}
                                  className="px-2 py-1 bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300 rounded text-xs"
                                >
                                  {course}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Projects */}
          {projects.length > 0 && (
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
                Projects
              </h2>
              <div className="space-y-4">
                {projects.map((project: any) => (
                  <div key={project.id} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          {project.project_name}
                        </h3>
                        {project.role && (
                          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                            Role: {project.role}
                          </p>
                        )}
                        {project.description && (
                          <p className="text-gray-700 dark:text-gray-300 mt-2">
                            {project.description}
                          </p>
                        )}
                        {project.technologies_used && project.technologies_used.length > 0 && (
                          <div className="flex flex-wrap gap-2 mt-3">
                            {project.technologies_used.map((tech: string, idx: number) => (
                              <span
                                key={idx}
                                className="px-2 py-1 bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300 rounded text-xs"
                              >
                                {tech}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      {project.github_url && (
                        <a
                          href={fixUrl(project.github_url)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="ml-4 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
                        >
                          <Github className="w-5 h-5" />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column - Sidebar Info */}
        <div className="space-y-6">
          {/* Links */}
          {(candidate?.linkedin_url || candidate?.github_url || candidate?.portfolio_url || candidate?.personal_website) && (
            <div className="card p-5">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Social Links
              </h3>
              <div className="space-y-3">
                {candidate?.linkedin_url && (
                  <a
                    href={fixUrl(candidate.linkedin_url)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-3 text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 group"
                  >
                    <Linkedin className="w-5 h-5" />
                    <span className="flex-1">LinkedIn</span>
                    <ExternalLink className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </a>
                )}
                {candidate?.github_url && (
                  <a
                    href={fixUrl(candidate.github_url)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-3 text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 group"
                  >
                    <Github className="w-5 h-5" />
                    <span className="flex-1">GitHub</span>
                    <ExternalLink className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </a>
                )}
                {candidate?.portfolio_url && (
                  <a
                    href={fixUrl(candidate.portfolio_url)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-3 text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 group"
                  >
                    <Globe className="w-5 h-5" />
                    <span className="flex-1">Portfolio</span>
                    <ExternalLink className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </a>
                )}
                {candidate?.personal_website && (
                  <a
                    href={fixUrl(candidate.personal_website)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-3 text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 group"
                  >
                    <Globe className="w-5 h-5" />
                    <span className="flex-1">Website</span>
                    <ExternalLink className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </a>
                )}
              </div>
            </div>
          )}

          {/* Salary Expectations */}
          {(candidate?.expected_salary_amount || candidate?.current_salary_amount) && (
            <div className="card p-5">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <DollarSign className="w-5 h-5 text-primary-600" />
                Compensation
              </h3>
              <div className="space-y-3">
                {candidate?.current_salary_amount && (
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Current Salary</p>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white">
                      {formatCurrency(candidate.current_salary_amount, candidate.current_salary_currency)}
                    </p>
                  </div>
                )}
                {candidate?.expected_salary_amount && (
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Expected Salary</p>
                    <p className="text-lg font-semibold text-primary-600 dark:text-primary-400">
                      {formatCurrency(candidate.expected_salary_amount, candidate.expected_salary_currency)}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Availability */}
          {(candidate?.availability_status || candidate?.notice_period_days) && (
            <div className="card p-5">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Availability
              </h3>
              <div className="space-y-3">
                {candidate?.availability_status && (
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Status</p>
                    <p className="text-base font-medium text-gray-900 dark:text-white">
                      {candidate.availability_status}
                    </p>
                  </div>
                )}
                {candidate?.notice_period_days && (
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Notice Period</p>
                    <p className="text-base font-medium text-gray-900 dark:text-white">
                      {candidate.notice_period_days} days
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Certifications */}
          {certifications.length > 0 && (
            <div className="card p-5">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <Award className="w-5 h-5 text-primary-600" />
                Certifications
              </h3>
              <div className="space-y-3">
                {certifications.map((cert: any) => (
                  <div key={cert.id} className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <p className="font-medium text-gray-900 dark:text-white text-sm">
                      {cert.certification_name}
                    </p>
                    {cert.issuing_organization && (
                      <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                        {cert.issuing_organization}
                      </p>
                    )}
                    {cert.issue_date && (
                      <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                        {new Date(cert.issue_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Languages */}
          {languages.length > 0 && (
            <div className="card p-5">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <Languages className="w-5 h-5 text-primary-600" />
                Languages
              </h3>
              <div className="space-y-2">
                {languages.map((lang: any) => (
                  <div key={lang.id} className="flex items-center justify-between">
                    <span className="text-gray-900 dark:text-white font-medium">
                      {lang.language_name}
                    </span>
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {lang.proficiency_level}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Additional Info */}
          <div className="card p-5">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Additional Information
            </h3>
            <div className="space-y-3 text-sm">
              {candidate?.open_to_relocation !== undefined && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Open to Relocation</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {candidate.open_to_relocation ? 'Yes' : 'No'}
                  </span>
                </div>
              )}
              {candidate?.willing_to_travel !== undefined && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Willing to Travel</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {candidate.willing_to_travel ? 'Yes' : 'No'}
                  </span>
                </div>
              )}
              {candidate?.created_at && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Added to System</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {new Date(candidate.created_at).toLocaleDateString()}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CandidateDetailNew
